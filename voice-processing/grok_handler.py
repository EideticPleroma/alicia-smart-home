#!/usr/bin/env python3
"""
Grok API Handler for Alicia Voice Assistant
Provides OpenAI-compatible interface to Grok models with context management
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ConversationContext:
    """Manages conversation context and session state"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation_history: List[Dict[str, Any]] = []
        self.device_context: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {}
        self.system_context: Dict[str, Any] = {}
        self.max_context_length = 4000  # Tokens
        self.session_start = time.time()
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        
        # Trim history if too long
        self._trim_history()
    
    def _trim_history(self):
        """Trim conversation history to stay within token limits"""
        # Simple token estimation (4 chars per token)
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)
        if total_chars > self.max_context_length * 4:
            # Remove oldest messages, keep system context
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            other_messages = [msg for msg in self.conversation_history if msg["role"] != "system"]
            
            # Keep recent messages and all system messages
            keep_count = max(10, len(system_messages))  # Keep at least 10 recent messages
            self.conversation_history = system_messages + other_messages[-keep_count:]
    
    def get_context_summary(self) -> str:
        """Get a summary of current context for prompt generation"""
        context_parts = []
        
        # Device states
        if self.device_context:
            device_info = ", ".join([f"{k}: {v}" for k, v in self.device_context.items()])
            context_parts.append(f"Current device states: {device_info}")
        
        # Recent conversation
        recent_messages = self.conversation_history[-5:]  # Last 5 messages
        if recent_messages:
            recent_context = " | ".join([f"{msg['role']}: {msg['content'][:100]}" for msg in recent_messages])
            context_parts.append(f"Recent conversation: {recent_context}")
        
        return " | ".join(context_parts)

class PromptGenerator:
    """Generates contextual prompts for Grok API"""
    
    def __init__(self, context_manager: ConversationContext):
        self.context_manager = context_manager
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Alicia with personality"""
        base_prompt = """You are Alicia, a witty and helpful AI voice assistant for a smart home system. You have the following capabilities:

1. **Smart Home Control**: Control lights, temperature, and other IoT devices
2. **Information**: Answer questions about weather, time, and general topics
3. **Conversation**: Engage in natural, witty, and entertaining conversation
4. **Context Awareness**: Remember recent interactions and device states

**Current Context**: {context}

**Guidelines**:
- Be concise but helpful in responses (aim for 1-2 sentences for voice output)
- Use natural, conversational language with personality
- Add wit and humor when appropriate
- Be slightly sarcastic for common requests
- When controlling devices, confirm the action with personality
- If you don't understand something, ask for clarification with humor
- Remember this is a voice interface, so keep responses engaging but brief

**Available Devices**: Kitchen light, Living room light, Bedroom light, Temperature sensor, Motion sensor

**Current Time**: {current_time}

Respond naturally, helpfully, and with personality to the user's request."""
        
        return base_prompt

    def generate_prompt(self, user_input: str, device_context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Generate a complete prompt for Grok API with personality enhancement"""
        
        # Update device context if provided
        if device_context:
            self.context_manager.device_context.update(device_context)
        
        # Add user message to context
        self.context_manager.add_message("user", user_input)
        
        # Build system prompt with current context
        context_summary = self.context_manager.get_context_summary()
        current_time = datetime.now().strftime("%I:%M %p on %B %d, %Y")
        
        # Get personality-enhanced prompt if available
        if hasattr(self, 'personality_manager') and self.personality_manager:
            system_prompt = self.personality_manager.get_personality_prompt(
                self.system_prompt, user_input, device_context
            ).format(
                context=context_summary,
                current_time=current_time
            )
        else:
            system_prompt = self.system_prompt.format(
                context=context_summary,
                current_time=current_time
            )
        
        # Build messages for API
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add recent conversation history
        for msg in self.context_manager.conversation_history[-10:]:  # Last 10 messages
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages

class GrokHandler:
    """Handles Grok API interactions with context management"""
    
    def __init__(self, api_key: str, model: str = "grok-4-0709", rate_limit: float = 1.0):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.context_manager = ConversationContext()
        self.prompt_generator = PromptGenerator(self.context_manager)
        
        # Personality management for witty conversations
        try:
            from personality_manager import create_personality_manager
            self.personality_manager = create_personality_manager()
            logger.info("Personality manager initialized for witty conversations")
        except ImportError:
            self.personality_manager = None
            logger.warning("Personality manager not available")
        
        # Enhanced rate limiting for Grok-4
        self.last_request_time = 0
        self.min_request_interval = rate_limit  # Configurable rate limit
        self.request_times = []  # Track request times for per-minute limiting
        self.token_usage = []  # Track token usage for per-minute limiting
        
        # Grok-4 specific limits
        if "grok-4" in model.lower():
            self.max_requests_per_minute = 480  # Grok-4 allows 480 requests/minute
            self.max_requests_per_hour = 20000  # Increased for Grok-4
            self.max_tokens_per_minute = 2000000  # 2M tokens per minute
            self.max_context_length = 256000  # 256k context window
        else:
            # Fallback to Grok-2 limits
            self.max_requests_per_minute = 30
            self.max_requests_per_hour = 1000
            self.max_tokens_per_minute = 100000  # Conservative estimate
            self.max_context_length = 4000
        
    async def process_command(self, command: str, device_context: Dict[str, Any] = None) -> str:
        """Process a voice command through Grok"""
        try:
            # Rate limiting
            await self._rate_limit()
            
            # Generate prompt with context
            messages = self.prompt_generator.generate_prompt(command, device_context)
            
            # Call Grok API with Grok-4 optimized parameters
            if "grok-4" in self.model.lower():
                # Grok-4 needs more tokens to generate responses
                max_tokens = 300
            else:
                # Grok-2 works fine with fewer tokens
                max_tokens = 200
                
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                stream=False
            )
            
            # Extract response and token usage
            assistant_response = response.choices[0].message.content.strip()
            usage = response.usage
            
            # Track token usage for rate limiting
            if usage:
                total_tokens = usage.total_tokens or 0
                self.token_usage.append((time.time(), total_tokens))
                logger.debug(f"Token usage: {total_tokens} tokens (input: {usage.prompt_tokens}, output: {usage.completion_tokens})")
            
            # Add to conversation history
            self.context_manager.add_message("assistant", assistant_response)
            
            logger.info(f"Grok-4 response: {assistant_response}")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            # Fallback to basic response
            return f"I'm having trouble processing that right now. Could you try again?"
    
    async def _rate_limit(self):
        """Enhanced rate limiting with per-minute and per-hour limits for Grok-4"""
        current_time = time.time()
        
        # Clean old request times (older than 1 hour)
        self.request_times = [t for t in self.request_times if current_time - t < 3600]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if current_time - t < 60]
        
        # Check per-minute request limit
        recent_requests = [t for t in self.request_times if current_time - t < 60]
        if len(recent_requests) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - recent_requests[0])
            if wait_time > 0:
                logger.warning(f"Rate limit: Waiting {wait_time:.1f}s for per-minute request limit ({len(recent_requests)}/{self.max_requests_per_minute})")
                await asyncio.sleep(wait_time)
        
        # Check per-minute token limit (Grok-4 specific)
        recent_tokens = sum(tokens for t, tokens in self.token_usage if current_time - t < 60)
        if recent_tokens >= self.max_tokens_per_minute:
            wait_time = 60 - (current_time - self.token_usage[0][0])
            if wait_time > 0:
                logger.warning(f"Rate limit: Waiting {wait_time:.1f}s for per-minute token limit ({recent_tokens}/{self.max_tokens_per_minute})")
                await asyncio.sleep(wait_time)
        
        # Check per-hour request limit
        if len(self.request_times) >= self.max_requests_per_hour:
            wait_time = 3600 - (current_time - self.request_times[0])
            if wait_time > 0:
                logger.warning(f"Rate limit: Waiting {wait_time:.1f}s for per-hour request limit ({len(self.request_times)}/{self.max_requests_per_hour})")
                await asyncio.sleep(wait_time)
        
        # Check minimum interval between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limit: Waiting {wait_time:.1f}s between requests")
            await asyncio.sleep(wait_time)
        
        # Record this request
        self.last_request_time = time.time()
        self.request_times.append(self.last_request_time)
    
    def update_device_context(self, device_states: Dict[str, Any]):
        """Update device context from Home Assistant"""
        self.context_manager.device_context.update(device_states)
        logger.info(f"Updated device context: {device_states}")
    
    def clear_context(self):
        """Clear conversation context"""
        self.context_manager = ConversationContext()
        self.prompt_generator = PromptGenerator(self.context_manager)
        logger.info("Conversation context cleared")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get current context summary for debugging"""
        return {
            "session_id": self.context_manager.session_id,
            "message_count": len(self.context_manager.conversation_history),
            "device_context": self.context_manager.device_context,
            "session_duration": time.time() - self.context_manager.session_start
        }

# Factory function for easy integration
def create_grok_handler(api_key: str = None, model: str = "grok-4-0709", rate_limit: float = 1.0) -> GrokHandler:
    """Create a Grok handler instance"""
    if not api_key:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("XAI_API_KEY environment variable not set")
    
    return GrokHandler(api_key, model, rate_limit)
