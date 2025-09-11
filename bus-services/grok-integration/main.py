"""
Alicia Bus Architecture - Grok Integration Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Advanced AI integration service that provides enhanced Grok capabilities
with context awareness, personality integration, and advanced conversation management.
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

from ..service_wrapper import BusServiceWrapper, BusServiceAPI


class GrokIntegration(BusServiceWrapper):
    """
    Grok Integration service for the Alicia bus architecture.

    Provides advanced AI capabilities with:
    - Enhanced Grok conversation management
    - Context-aware responses
    - Personality integration
    - Multi-modal conversation support
    - Advanced prompt engineering
    - Conversation memory and learning

    Features:
    - Real-time Grok API integration
    - Context preservation across sessions
    - Personality-driven responses
    - Multi-language conversation support
    - Advanced error handling and retry logic
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "grok_integration"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_grok_2024")
        }

        super().__init__("grok_integration", mqtt_config)

        # Grok Configuration
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.grok_base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
        self.grok_model = os.getenv("GROK_MODEL", "grok-beta")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.context_window = int(os.getenv("CONTEXT_WINDOW", "10"))

        # Conversation management
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.personality_profiles: Dict[str, Dict[str, Any]] = {}
        self.context_memory: Dict[str, Dict[str, Any]] = {}

        # Performance settings
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))

        # Setup HTTP client for Grok API
        self._setup_grok_client()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_grok_endpoints()

        # Service capabilities
        self.capabilities = [
            "advanced_ai_conversation",
            "context_awareness",
            "personality_integration",
            "multi_modal_support",
            "conversation_memory",
            "prompt_engineering"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._cleanup_expired_conversations())

        self.logger.info("Grok Integration initialized")

    def _setup_grok_client(self):
        """Setup Grok API client."""
        try:
            import requests
            self.grok_session = requests.Session()
            if self.grok_api_key:
                self.grok_session.headers.update({
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                })
            self.logger.info("Grok API client initialized")
        except ImportError:
            self.logger.error("Requests library not available")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup Grok client: {e}")
            raise

    def _setup_grok_endpoints(self):
        """Setup FastAPI endpoints for Grok integration."""

        @self.api.app.post("/conversation")
        async def start_conversation(request: Dict[str, Any]):
            """Start a new conversation with Grok."""
            try:
                user_id = request.get("user_id")
                personality = request.get("personality", "alicia")
                initial_message = request.get("message")
                language = request.get("language", "en")
                context = request.get("context", {})

                if not user_id or not initial_message:
                    raise HTTPException(status_code=400, detail="User ID and message are required")

                # Start conversation
                conversation_id = await self._start_conversation(
                    user_id, personality, initial_message, language, context
                )

                return {
                    "conversation_id": conversation_id,
                    "status": "started",
                    "personality": personality,
                    "language": language
                }

            except Exception as e:
                self.logger.error(f"Start conversation error: {e}")
                raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")

        @self.api.app.post("/message")
        async def send_message(request: Dict[str, Any]):
            """Send message to existing conversation."""
            try:
                conversation_id = request.get("conversation_id")
                message = request.get("message")
                context = request.get("context", {})

                if not conversation_id or not message:
                    raise HTTPException(status_code=400, detail="Conversation ID and message are required")

                # Send message
                response = await self._send_message(conversation_id, message, context)

                return {
                    "conversation_id": conversation_id,
                    "response": response,
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Send message error: {e}")
                raise HTTPException(status_code=500, detail=f"Message failed: {str(e)}")

        @self.api.app.post("/personality")
        async def set_personality(request: Dict[str, Any]):
            """Set or update personality profile."""
            try:
                personality_id = request.get("personality_id")
                profile_data = request.get("profile")

                if not personality_id or not profile_data:
                    raise HTTPException(status_code=400, detail="Personality ID and profile data are required")

                # Set personality
                await self._set_personality(personality_id, profile_data)

                return {
                    "personality_id": personality_id,
                    "status": "updated",
                    "profile": profile_data
                }

            except Exception as e:
                self.logger.error(f"Set personality error: {e}")
                raise HTTPException(status_code=500, detail=f"Personality update failed: {str(e)}")

        @self.api.app.get("/conversations/{conversation_id}")
        async def get_conversation(conversation_id: str):
            """Get conversation history."""
            if conversation_id not in self.conversations:
                raise HTTPException(status_code=404, detail="Conversation not found")

            conversation = self.conversations[conversation_id]
            return {
                "conversation_id": conversation_id,
                "messages": conversation,
                "count": len(conversation)
            }

        @self.api.app.get("/personalities")
        async def list_personalities():
            """List all personality profiles."""
            return {"personalities": self.personality_profiles}

        @self.api.app.get("/health")
        async def health_check():
            """Grok integration health check."""
            grok_status = await self._check_grok_connectivity()

            return {
                "service": "grok_integration",
                "status": "healthy" if self.is_connected else "unhealthy",
                "grok_connected": grok_status,
                "active_conversations": len(self.conversations),
                "personality_profiles": len(self.personality_profiles),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to Grok-related MQTT topics."""
        topics = [
            "alicia/ai/grok/command",
            "alicia/ai/grok/conversation",
            "alicia/personality/update",
            "alicia/voice/ai/request",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to Grok integration topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/ai/grok/command":
                self._handle_grok_command(message)
            elif topic == "alicia/ai/grok/conversation":
                self._handle_conversation_request(message)
            elif topic == "alicia/personality/update":
                self._handle_personality_update(message)
            elif topic == "alicia/voice/ai/request":
                self._handle_voice_ai_request(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing Grok message: {e}")

    def _handle_grok_command(self, message: Dict[str, Any]):
        """Handle Grok command requests."""
        try:
            payload = message.get("payload", {})
            command = payload.get("command")
            parameters = payload.get("parameters", {})

            if command == "analyze_text":
                # Analyze text with Grok
                asyncio.create_task(self._analyze_text_with_grok(parameters))
            elif command == "generate_response":
                # Generate contextual response
                asyncio.create_task(self._generate_contextual_response(parameters))

        except Exception as e:
            self.logger.error(f"Error handling Grok command: {e}")

    def _handle_conversation_request(self, message: Dict[str, Any]):
        """Handle conversation requests."""
        try:
            payload = message.get("payload", {})
            user_id = payload.get("user_id")
            message_text = payload.get("message")
            conversation_id = payload.get("conversation_id")

            if user_id and message_text:
                if conversation_id and conversation_id in self.conversations:
                    # Continue existing conversation
                    asyncio.create_task(self._send_message(conversation_id, message_text))
                else:
                    # Start new conversation
                    asyncio.create_task(self._start_conversation(user_id, "alicia", message_text))

        except Exception as e:
            self.logger.error(f"Error handling conversation request: {e}")

    def _handle_personality_update(self, message: Dict[str, Any]):
        """Handle personality updates."""
        try:
            payload = message.get("payload", {})
            personality_id = payload.get("personality_id")
            profile_data = payload.get("profile")

            if personality_id and profile_data:
                asyncio.create_task(self._set_personality(personality_id, profile_data))

        except Exception as e:
            self.logger.error(f"Error handling personality update: {e}")

    def _handle_voice_ai_request(self, message: Dict[str, Any]):
        """Handle voice AI requests."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            transcription = payload.get("transcription", "")
            context = payload.get("context", {})

            if transcription:
                # Process voice transcription with enhanced Grok
                asyncio.create_task(self._process_voice_transcription(session_id, transcription, context))

        except Exception as e:
            self.logger.error(f"Error handling voice AI request: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _start_conversation(self, user_id: str, personality: str,
                                initial_message: str, language: str = "en",
                                context: Dict[str, Any] = None) -> str:
        """Start a new conversation with Grok."""
        try:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

            # Initialize conversation
            self.conversations[conversation_id] = []

            # Get personality profile
            personality_profile = self.personality_profiles.get(personality, self._get_default_personality())

            # Create system prompt
            system_prompt = self._create_system_prompt(personality_profile, language, context)

            # Add initial message
            self.conversations[conversation_id].append({
                "role": "system",
                "content": system_prompt,
                "timestamp": time.time()
            })

            self.conversations[conversation_id].append({
                "role": "user",
                "content": initial_message,
                "timestamp": time.time()
            })

            # Get Grok response
            response = await self._call_grok_api(self.conversations[conversation_id])

            if response:
                self.conversations[conversation_id].append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": time.time()
                })

                # Publish conversation start
                conversation_message = {
                    "message_id": f"conv_start_{conversation_id}_{uuid.uuid4().hex[:8]}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": "broadcast",
                    "message_type": "event",
                    "payload": {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "personality": personality,
                        "language": language,
                        "initial_response": response
                    }
                }

                self.publish_message("alicia/ai/conversation/started", conversation_message)

            return conversation_id

        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            raise

    async def _send_message(self, conversation_id: str, message: str,
                          context: Dict[str, Any] = None) -> str:
        """Send message to existing conversation."""
        try:
            if conversation_id not in self.conversations:
                raise Exception(f"Conversation {conversation_id} not found")

            # Add user message
            self.conversations[conversation_id].append({
                "role": "user",
                "content": message,
                "timestamp": time.time()
            })

            # Get conversation history (limit to context window)
            conversation_history = self.conversations[conversation_id][-self.context_window:]

            # Add context if provided
            if context:
                context_message = f"Context: {json.dumps(context)}"
                conversation_history.append({
                    "role": "system",
                    "content": context_message,
                    "timestamp": time.time()
                })

            # Get Grok response
            response = await self._call_grok_api(conversation_history)

            if response:
                self.conversations[conversation_id].append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": time.time()
                })

                # Publish message response
                message_response = {
                    "message_id": f"msg_resp_{conversation_id}_{uuid.uuid4().hex[:8]}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": "broadcast",
                    "message_type": "event",
                    "payload": {
                        "conversation_id": conversation_id,
                        "user_message": message,
                        "ai_response": response,
                        "context": context
                    }
                }

                self.publish_message("alicia/ai/conversation/message", message_response)

            return response

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def _call_grok_api(self, messages: List[Dict[str, Any]]) -> str:
        """Call Grok API with conversation messages."""
        try:
            if not self.grok_session:
                raise Exception("Grok session not available")

            # Prepare request payload
            payload = {
                "model": self.grok_model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }

            # Make API call with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.grok_session.post(
                        f"{self.grok_base_url}/chat/completions",
                        json=payload,
                        timeout=self.request_timeout
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        self.logger.warning(f"Grok API error (attempt {attempt + 1}): {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))

                except Exception as e:
                    self.logger.warning(f"Grok API call failed (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))

            raise Exception("Grok API call failed after all retries")

        except Exception as e:
            self.logger.error(f"Error calling Grok API: {e}")
            return "I'm sorry, I'm having trouble connecting to my AI services right now. Please try again later."

    def _create_system_prompt(self, personality: Dict[str, Any], language: str,
                            context: Dict[str, Any] = None) -> str:
        """Create system prompt for Grok conversation."""
        try:
            base_prompt = personality.get("system_prompt", "")
            language_support = personality.get("language_support", {}).get(language, "")

            prompt_parts = [base_prompt]

            if language_support:
                prompt_parts.append(f"Language: {language_support}")

            if context:
                context_str = json.dumps(context, indent=2)
                prompt_parts.append(f"Current Context: {context_str}")

            # Add capabilities
            capabilities = personality.get("capabilities", [])
            if capabilities:
                prompt_parts.append(f"Capabilities: {', '.join(capabilities)}")

            return "\n\n".join(prompt_parts)

        except Exception as e:
            self.logger.error(f"Error creating system prompt: {e}")
            return "You are Alicia, a helpful AI assistant for smart home automation."

    def _get_default_personality(self) -> Dict[str, Any]:
        """Get default personality profile."""
        return {
            "name": "Alicia",
            "system_prompt": "You are Alicia, an advanced AI assistant for smart home automation. You are helpful, friendly, and knowledgeable about technology and home automation. You can control smart devices, provide information, and engage in natural conversation.",
            "capabilities": ["smart_home_control", "general_knowledge", "conversation"],
            "language_support": {
                "en": "Respond in English",
                "es": "Responde en español",
                "fr": "Réponds en français"
            }
        }

    async def _set_personality(self, personality_id: str, profile_data: Dict[str, Any]):
        """Set personality profile."""
        try:
            self.personality_profiles[personality_id] = profile_data

            # Publish personality update
            personality_message = {
                "message_id": f"personality_update_{personality_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "personality_id": personality_id,
                    "profile": profile_data
                }
            }

            self.publish_message("alicia/personality/updated", personality_message)

            self.logger.info(f"Updated personality profile: {personality_id}")

        except Exception as e:
            self.logger.error(f"Error setting personality: {e}")
            raise

    async def _analyze_text_with_grok(self, parameters: Dict[str, Any]):
        """Analyze text using Grok."""
        try:
            text = parameters.get("text", "")
            analysis_type = parameters.get("type", "sentiment")

            if not text:
                return

            # Create analysis prompt
            analysis_prompt = f"Analyze the following text for {analysis_type}: {text}"

            messages = [
                {"role": "system", "content": "You are an expert text analyzer."},
                {"role": "user", "content": analysis_prompt}
            ]

            analysis_result = await self._call_grok_api(messages)

            # Publish analysis result
            analysis_message = {
                "message_id": f"analysis_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "text": text,
                    "analysis_type": analysis_type,
                    "result": analysis_result
                }
            }

            self.publish_message("alicia/ai/analysis/complete", analysis_message)

        except Exception as e:
            self.logger.error(f"Error analyzing text: {e}")

    async def _generate_contextual_response(self, parameters: Dict[str, Any]):
        """Generate contextual response using Grok."""
        try:
            context = parameters.get("context", {})
            query = parameters.get("query", "")

            if not query:
                return

            # Create contextual prompt
            context_str = json.dumps(context, indent=2)
            contextual_prompt = f"Given this context: {context_str}\n\nRespond to: {query}"

            messages = [
                {"role": "system", "content": "You are an AI assistant that provides contextual responses."},
                {"role": "user", "content": contextual_prompt}
            ]

            response = await self._call_grok_api(messages)

            # Publish response
            response_message = {
                "message_id": f"contextual_resp_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "query": query,
                    "context": context,
                    "response": response
                }
            }

            self.publish_message("alicia/ai/contextual/response", response_message)

        except Exception as e:
            self.logger.error(f"Error generating contextual response: {e}")

    async def _process_voice_transcription(self, session_id: str, transcription: str,
                                        context: Dict[str, Any]):
        """Process voice transcription with enhanced Grok analysis."""
        try:
            # Analyze transcription for intent and context
            analysis_prompt = f"Analyze this voice transcription for intent, sentiment, and key information: {transcription}"

            messages = [
                {"role": "system", "content": "You are an expert at analyzing voice transcriptions for intent and context."},
                {"role": "user", "content": analysis_prompt}
            ]

            analysis = await self._call_grok_api(messages)

            # Generate enhanced response
            context_str = json.dumps(context, indent=2)
            response_prompt = f"Based on this transcription analysis: {analysis}\nAnd this context: {context_str}\n\nGenerate an appropriate response for the user."

            response_messages = [
                {"role": "system", "content": "You are Alicia, providing helpful responses to user voice commands."},
                {"role": "user", "content": response_prompt}
            ]

            enhanced_response = await self._call_grok_api(response_messages)

            # Publish enhanced voice response
            voice_response = {
                "message_id": f"voice_enhanced_{session_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "voice_router",
                "message_type": "response",
                "payload": {
                    "session_id": session_id,
                    "original_transcription": transcription,
                    "analysis": analysis,
                    "enhanced_response": enhanced_response,
                    "context": context
                }
            }

            self.publish_message("alicia/voice/ai/enhanced", voice_response)

        except Exception as e:
            self.logger.error(f"Error processing voice transcription: {e}")

    async def _cleanup_expired_conversations(self):
        """Cleanup expired conversations."""
        while True:
            try:
                current_time = time.time()
                conversation_timeout = 3600  # 1 hour

                # Find expired conversations
                expired_conversations = []
                for conv_id, messages in self.conversations.items():
                    if messages and current_time - messages[-1]["timestamp"] > conversation_timeout:
                        expired_conversations.append(conv_id)

                # Remove expired conversations
                for conv_id in expired_conversations:
                    self.logger.info(f"Cleaning up expired conversation: {conv_id}")
                    del self.conversations[conv_id]

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up conversations: {e}")
                await asyncio.sleep(300)

    async def _check_grok_connectivity(self) -> bool:
        """Check Grok API connectivity."""
        try:
            if self.grok_session:
                # Simple health check
                response = self.grok_session.get(f"{self.grok_base_url}/health", timeout=5)
                return response.status_code == 200
            return False
        except Exception:
            return False


def main():
    """Main entry point for Grok Integration service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create Grok integration
    grok_integration = GrokIntegration()

    # Start API server
    try:
        grok_integration.api.run_api(host="0.0.0.0", port=8009)
    except KeyboardInterrupt:
        grok_integration.shutdown()


if __name__ == "__main__":
    main()
