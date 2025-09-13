"""
Alicia Bus Architecture - AI Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Bus-integrated AI service that handles natural language processing
using Grok API. Processes transcribed text and generates responses
for voice interaction and smart home control.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional, List

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from service_wrapper import BusServiceWrapper, BusServiceAPI


class AIService(BusServiceWrapper):
    """
    AI Service for the Alicia bus architecture.

    Handles natural language processing and response generation using:
    - xAI Grok API (primary)
    - OpenAI GPT (fallback)
    - Local models (future)

    Features:
    - Context-aware conversation
    - Smart home command understanding
    - Multi-turn dialogue support
    - Response quality optimization
    - Bus integration for seamless communication
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "localhost"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "ai_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_ai_2024")
        }

        super().__init__("ai_service", mqtt_config)

        # AI Configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "grok")  # grok, openai, local
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("AI_MODEL", "grok-beta")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

        # Conversation context
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_length = int(os.getenv("MAX_HISTORY_LENGTH", "10"))

        # AI clients
        self.grok_client = None
        self.openai_client = None

        # Setup AI provider
        self._setup_ai_provider()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_ai_endpoints()

        # Service capabilities
        self.capabilities = [
            "natural_language_processing",
            "conversation_management",
            "smart_home_commands",
            "context_awareness",
            "response_generation"
        ]

        self.version = "1.0.0"

        self.logger.info(f"AI Service initialized with {self.ai_provider} provider")

    def _setup_ai_provider(self):
        """Setup the selected AI provider."""
        try:
            if self.ai_provider == "grok":
                self._setup_grok()
            elif self.ai_provider == "openai":
                self._setup_openai()
            elif self.ai_provider == "local":
                self._setup_local()
            else:
                raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

            self.logger.info(f"AI provider {self.ai_provider} setup complete")

        except Exception as e:
            self.logger.error(f"Failed to setup AI provider: {e}")
            raise

    def _setup_grok(self):
        """Setup xAI Grok client."""
        if not self.grok_api_key:
            raise ValueError("GROK_API_KEY environment variable is required")

        try:
            # Import xAI SDK (assuming it's available)
            # For now, we'll use requests to call the API directly
            import requests
            self.grok_client = requests.Session()
            self.grok_client.headers.update({
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            })
            self.logger.info("Grok client initialized")
        except ImportError:
            self.logger.error("xAI SDK not available. Install with: pip install xai-sdk")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup Grok client: {e}")
            raise

    def _setup_openai(self):
        """Setup OpenAI client."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.logger.info("OpenAI client initialized")
        except ImportError:
            self.logger.error("OpenAI SDK not available. Install with: pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup OpenAI client: {e}")
            raise

    def _setup_local(self):
        """Setup local AI model (placeholder for future implementation)."""
        self.logger.warning("Local AI models not yet implemented")
        # Future: Setup local models like GPT-2, Llama, etc.

    def _setup_ai_endpoints(self):
        """Setup FastAPI endpoints for AI service."""

        @self.api.app.post("/process")
        async def process_text(request: Dict[str, Any]):
            """Process text and generate AI response."""
            try:
                text = request.get("text", "")
                context = request.get("context", {})
                session_id = request.get("session_id", str(uuid.uuid4()))

                if not text:
                    raise HTTPException(status_code=400, detail="Text is required")

                # Process with AI
                result = await self._generate_ai_response_async(text, session_id, context)

                return result

            except Exception as e:
                self.logger.error(f"AI processing error: {e}")
                raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

        @self.api.app.post("/conversation")
        async def continue_conversation(request: Dict[str, Any]):
            """Continue an existing conversation."""
            try:
                text = request.get("text", "")
                session_id = request.get("session_id", "")
                context = request.get("context", {})

                if not text or not session_id:
                    raise HTTPException(status_code=400, detail="Text and session_id are required")

                # Continue conversation
                result = await self._continue_conversation_async(text, session_id, context)

                return result

            except Exception as e:
                self.logger.error(f"Conversation error: {e}")
                raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")

        @self.api.app.get("/models")
        async def list_models():
            """List available AI models."""
            models = []
            if self.grok_client:
                models.append({"name": "grok", "provider": "xai", "status": "available"})
            if self.openai_client:
                models.append({"name": self.model_name, "provider": "openai", "status": "available"})

            return {"models": models, "active": self.ai_provider}

        @self.api.app.delete("/conversation/{session_id}")
        async def clear_conversation(session_id: str):
            """Clear conversation history for a session."""
            if session_id in self.conversation_history:
                del self.conversation_history[session_id]
                return {"status": "cleared", "session_id": session_id}
            else:
                raise HTTPException(status_code=404, detail="Conversation not found")

        @self.api.app.get("/health")
        async def health_check():
            """AI service health check."""
            return {
                "service": "ai_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "provider": self.ai_provider,
                "model": self.model_name,
                "active_conversations": len(self.conversation_history),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to AI-related MQTT topics."""
        topics = [
            "alicia/voice/ai/request",
            "alicia/voice/stt/response",
            "alicia/voice/command/route",
            "capability:natural_language_processing",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to AI topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/voice/ai/request":
                self._handle_ai_request(message)
            elif topic == "alicia/voice/stt/response":
                self._handle_stt_response(message)
            elif topic == "alicia/voice/command/route":
                self._handle_voice_command(message)
            elif topic == "capability:natural_language_processing":
                self._handle_nlp_request(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing AI message: {e}")
            self._send_error_response(message, str(e))

    def _handle_ai_request(self, message: Dict[str, Any]):
        """Handle AI processing request."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text", "")
            session_id = payload.get("session_id", str(uuid.uuid4()))
            context = payload.get("context", {})

            if not text:
                self._send_error_response(message, "No text provided")
                return

            # Process AI request asynchronously
            asyncio.create_task(self._process_ai_request_async(message, text, session_id, context))

        except Exception as e:
            self.logger.error(f"Error handling AI request: {e}")
            self._send_error_response(message, str(e))

    def _handle_stt_response(self, message: Dict[str, Any]):
        """Handle STT response and potentially trigger AI processing."""
        try:
            payload = message.get("payload", {})
            transcription = payload.get("transcription", {})
            session_id = payload.get("session_id", "")

            if transcription.get("success") and session_id:
                # STT was successful, trigger AI processing
                text = transcription.get("text", "")
                if text:
                    ai_request = {
                        "message_id": f"ai_from_stt_{uuid.uuid4().hex[:8]}",
                        "timestamp": time.time(),
                        "source": "ai_service",
                        "destination": "ai_service",
                        "message_type": "request",
                        "payload": {
                            "text": text,
                            "session_id": session_id,
                            "context": {"source": "voice_input"}
                        }
                    }
                    self._handle_ai_request(ai_request)

        except Exception as e:
            self.logger.error(f"Error handling STT response: {e}")

    def _handle_voice_command(self, message: Dict[str, Any]):
        """Handle voice command that may need AI processing."""
        payload = message.get("payload", {})
        text = payload.get("text", "")

        if text:
            # This is a text-based voice command, process with AI
            self._handle_ai_request(message)

    def _handle_nlp_request(self, message: Dict[str, Any]):
        """Handle general NLP capability request."""
        # Route to AI processing
        self._handle_ai_request(message)

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _process_ai_request_async(self, original_message: Dict[str, Any],
                                      text: str, session_id: str, context: Dict[str, Any]):
        """Process AI request asynchronously."""
        try:
            # Generate AI response
            result = await self._generate_ai_response_async(text, session_id, context)

            # Send response
            self._send_ai_response(original_message, result, session_id)

        except Exception as e:
            self.logger.error(f"Error processing AI request: {e}")
            self._send_error_response(original_message, str(e))

    async def _continue_conversation_async(self, text: str, session_id: str,
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Continue an existing conversation."""
        # Add user message to history
        self._add_to_conversation_history(session_id, "user", text)

        # Generate response with conversation context
        result = await self._generate_ai_response_async(text, session_id, context)

        # Add AI response to history
        if result.get("success"):
            self._add_to_conversation_history(session_id, "assistant", result["response"])

        return result

    async def _generate_ai_response_async(self, text: str, session_id: str,
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response asynchronously."""
        loop = asyncio.get_event_loop()

        # Run AI generation in thread pool to avoid blocking
        result = await loop.run_in_executor(
            None,
            self._generate_ai_response_sync,
            text,
            session_id,
            context
        )

        return result

    def _generate_ai_response_sync(self, text: str, session_id: str,
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response synchronously."""
        start_time = time.time()

        try:
            # Prepare conversation context
            conversation_context = self._get_conversation_context(session_id)

            # Add current user message
            conversation_context.append({"role": "user", "content": text})

            # Generate system prompt based on context
            system_prompt = self._generate_system_prompt(context)

            # Generate response based on provider
            if self.ai_provider == "grok":
                response = self._generate_grok_response(system_prompt, conversation_context)
            elif self.ai_provider == "openai":
                response = self._generate_openai_response(system_prompt, conversation_context)
            elif self.ai_provider == "local":
                response = self._generate_local_response(system_prompt, conversation_context)
            else:
                raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

            # Add AI response to conversation history if successful
            if response.get("success", False) and "response" in response:
                self._add_to_conversation_history(session_id, "assistant", response["response"])

            # Add processing time
            response["processing_time"] = time.time() - start_time

            return response

        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def _generate_grok_response(self, system_prompt: str,
                              conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate response using xAI Grok."""
        try:
            # Prepare messages for Grok API
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_context[-self.max_history_length:])

            # Call Grok API
            response = self.grok_client.post(
                "https://api.x.ai/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "model": result.get("model", self.model_name),
                    "usage": result.get("usage", {}),
                    "provider": "grok"
                }
            else:
                return {
                    "success": False,
                    "error": f"Grok API error: {response.status_code}",
                    "provider": "grok"
                }

        except Exception as e:
            self.logger.error(f"Grok response generation failed: {e}")
            raise

    def _generate_openai_response(self, system_prompt: str,
                                conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            # Prepare messages for OpenAI API
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_context[-self.max_history_length:])

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "provider": "openai"
            }

        except Exception as e:
            self.logger.error(f"OpenAI response generation failed: {e}")
            raise

    def _generate_local_response(self, system_prompt: str,
                               conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate response using local model (placeholder)."""
        # Placeholder for local model implementation
        return {
            "success": False,
            "error": "Local models not yet implemented",
            "provider": "local"
        }

    def _generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt based on context."""
        base_prompt = """You are Alicia, an intelligent smart home assistant. You help users control their home, answer questions, and provide assistance.

Key capabilities:
- Control smart home devices (lights, thermostats, speakers, etc.)
- Answer questions and provide information
- Maintain context in conversations
- Be helpful, friendly, and efficient

Guidelines:
- Keep responses concise but informative
- Acknowledge user requests and confirm actions
- Ask for clarification when needed
- Use natural, conversational language
"""

        # Add context-specific instructions
        if context.get("source") == "voice_input":
            base_prompt += "\n- This interaction came from voice input, so responses should be spoken naturally"
        elif context.get("source") == "text_input":
            base_prompt += "\n- This is a text-based interaction"

        # Add device control context
        if context.get("devices"):
            base_prompt += f"\n- Available devices: {', '.join(context['devices'])}"

        return base_prompt

    def _get_conversation_context(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation context for a session."""
        return self.conversation_history.get(session_id, [])

    def _add_to_conversation_history(self, session_id: str, role: str, content: str):
        """Add message to conversation history."""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        self.conversation_history[session_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

        # Limit history length
        if len(self.conversation_history[session_id]) > self.max_history_length:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history_length:]

    def _send_ai_response(self, original_message: Dict[str, Any],
                        result: Dict[str, Any], session_id: str):
        """Send AI response via MQTT."""
        response = {
            "message_id": f"ai_response_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "response",
            "payload": {
                "session_id": session_id,
                "ai_response": result,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/ai/response", response)

    def _send_error_response(self, original_message: Dict[str, Any], error: str):
        """Send error response via MQTT."""
        response = {
            "message_id": f"ai_error_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "error",
            "payload": {
                "error": error,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/ai/error", response)


def main():
    """Main entry point for AI Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create AI service
    ai_service = AIService()

    # Start API server
    try:
        ai_service.api.run_api(host="0.0.0.0", port=8005)
    except KeyboardInterrupt:
        ai_service.shutdown()


if __name__ == "__main__":
    main()
