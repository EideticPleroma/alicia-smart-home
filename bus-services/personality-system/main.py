"""
Alicia Bus Architecture - Personality System Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Personality management service that handles character profiles,
conversation styles, and personality-driven AI responses.
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


class PersonalitySystem(BusServiceWrapper):
    """
    Personality System service for the Alicia bus architecture.

    Manages AI personality profiles and conversation styles:
    - Character profile management
    - Conversation style adaptation
    - Personality-driven response generation
    - Multi-character support
    - Dynamic personality switching

    Features:
    - Personality profile storage and retrieval
    - Conversation style analysis
    - Character role-playing capabilities
    - Personality blending and adaptation
    - Context-aware personality selection
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "personality_system"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_personality_2024")
        }

        super().__init__("personality_system", mqtt_config)

        # Personality Configuration
        self.personality_data_path = os.getenv("PERSONALITY_DATA_PATH", "/app/data/personalities")
        self.default_personality = os.getenv("DEFAULT_PERSONALITY", "alicia")
        self.max_personalities = int(os.getenv("MAX_PERSONALITIES", "50"))
        self.personality_cache_ttl = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

        # Personality management
        self.personalities: Dict[str, Dict[str, Any]] = {}
        self.active_personalities: Dict[str, str] = {}  # user_id -> personality_id
        self.personality_cache: Dict[str, Dict[str, Any]] = {}
        self.conversation_styles: Dict[str, Dict[str, Any]] = {}

        # Setup personality data directory
        os.makedirs(self.personality_data_path, exist_ok=True)

        # Load default personalities
        self._load_default_personalities()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_personality_endpoints()

        # Service capabilities
        self.capabilities = [
            "personality_management",
            "character_profiles",
            "conversation_styles",
            "personality_adaptation",
            "multi_character_support"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._cleanup_expired_cache())

        self.logger.info("Personality System initialized")

    def _load_default_personalities(self):
        """Load default personality profiles."""
        try:
            # Alicia - Default personality
            self.personalities["alicia"] = {
                "personality_id": "alicia",
                "name": "Alicia",
                "description": "A helpful and friendly AI assistant for smart home automation",
                "traits": ["helpful", "friendly", "knowledgeable", "efficient"],
                "communication_style": {
                    "formality": "casual",
                    "verbosity": "concise",
                    "humor": "light",
                    "empathy": "high"
                },
                "system_prompt": "You are Alicia, an advanced AI assistant for smart home automation. You are helpful, friendly, and knowledgeable about technology and home automation. You can control smart devices, provide information, and engage in natural conversation.",
                "capabilities": ["smart_home_control", "general_knowledge", "conversation"],
                "language_support": {
                    "en": "Respond in English",
                    "es": "Responde en español",
                    "fr": "Réponds en français",
                    "de": "Antworte auf Deutsch"
                },
                "created_at": time.time(),
                "updated_at": time.time()
            }

            # Professional - Business-focused personality
            self.personalities["professional"] = {
                "personality_id": "professional",
                "name": "Alex",
                "description": "A professional and efficient AI assistant for business environments",
                "traits": ["professional", "efficient", "precise", "reliable"],
                "communication_style": {
                    "formality": "formal",
                    "verbosity": "concise",
                    "humor": "minimal",
                    "empathy": "moderate"
                },
                "system_prompt": "You are Alex, a professional AI assistant focused on efficiency and precision. You provide clear, concise, and reliable assistance for business and technical tasks.",
                "capabilities": ["business_assistance", "technical_support", "data_analysis"],
                "language_support": {
                    "en": "Respond professionally in English",
                    "es": "Responde profesionalmente en español"
                },
                "created_at": time.time(),
                "updated_at": time.time()
            }

            # Creative - Artistic and imaginative personality
            self.personalities["creative"] = {
                "personality_id": "creative",
                "name": "Aria",
                "description": "A creative and imaginative AI assistant for artistic endeavors",
                "traits": ["creative", "imaginative", "artistic", "inspirational"],
                "communication_style": {
                    "formality": "casual",
                    "verbosity": "expressive",
                    "humor": "playful",
                    "empathy": "high"
                },
                "system_prompt": "You are Aria, a creative and imaginative AI assistant. You help with artistic projects, provide inspiration, and engage in creative conversations with enthusiasm and originality.",
                "capabilities": ["creative_writing", "art_design", "inspiration", "brainstorming"],
                "language_support": {
                    "en": "Respond creatively in English",
                    "es": "Responde creativamente en español",
                    "fr": "Réponds de manière créative en français"
                },
                "created_at": time.time(),
                "updated_at": time.time()
            }

            self.logger.info(f"Loaded {len(self.personalities)} default personalities")

        except Exception as e:
            self.logger.error(f"Error loading default personalities: {e}")

    def _setup_personality_endpoints(self):
        """Setup FastAPI endpoints for personality management."""

        @self.api.app.post("/personality")
        async def create_personality(request: Dict[str, Any]):
            """Create a new personality profile."""
            try:
                personality_data = request.get("personality")

                if not personality_data:
                    raise HTTPException(status_code=400, detail="Personality data is required")

                personality_id = personality_data.get("personality_id")
                if not personality_id:
                    personality_id = f"personality_{uuid.uuid4().hex[:8]}"
                    personality_data["personality_id"] = personality_id

                # Validate personality data
                await self._validate_personality_data(personality_data)

                # Create personality
                personality = await self._create_personality(personality_id, personality_data)

                return {
                    "personality_id": personality_id,
                    "status": "created",
                    "personality": personality
                }

            except Exception as e:
                self.logger.error(f"Create personality error: {e}")
                raise HTTPException(status_code=500, detail=f"Personality creation failed: {str(e)}")

        @self.api.app.put("/personality/{personality_id}")
        async def update_personality(personality_id: str, request: Dict[str, Any]):
            """Update an existing personality profile."""
            try:
                updates = request.get("updates", {})

                if not updates:
                    raise HTTPException(status_code=400, detail="Updates are required")

                # Update personality
                personality = await self._update_personality(personality_id, updates)

                return {
                    "personality_id": personality_id,
                    "status": "updated",
                    "personality": personality
                }

            except Exception as e:
                self.logger.error(f"Update personality error: {e}")
                raise HTTPException(status_code=500, detail=f"Personality update failed: {str(e)}")

        @self.api.app.get("/personality/{personality_id}")
        async def get_personality(personality_id: str):
            """Get personality profile."""
            if personality_id not in self.personalities:
                raise HTTPException(status_code=404, detail="Personality not found")

            return self.personalities[personality_id]

        @self.api.app.get("/personalities")
        async def list_personalities():
            """List all personality profiles."""
            personalities_list = []
            for personality_id, personality in self.personalities.items():
                personalities_list.append({
                    "personality_id": personality_id,
                    "name": personality.get("name"),
                    "description": personality.get("description"),
                    "traits": personality.get("traits", []),
                    "created_at": personality.get("created_at"),
                    "updated_at": personality.get("updated_at")
                })

            return {"personalities": personalities_list, "count": len(personalities_list)}

        @self.api.app.post("/activate")
        async def activate_personality(request: Dict[str, Any]):
            """Activate a personality for a user."""
            try:
                user_id = request.get("user_id")
                personality_id = request.get("personality_id")

                if not user_id or not personality_id:
                    raise HTTPException(status_code=400, detail="User ID and personality ID are required")

                if personality_id not in self.personalities:
                    raise HTTPException(status_code=404, detail="Personality not found")

                # Activate personality
                await self._activate_personality_for_user(user_id, personality_id)

                return {
                    "user_id": user_id,
                    "personality_id": personality_id,
                    "status": "activated"
                }

            except Exception as e:
                self.logger.error(f"Activate personality error: {e}")
                raise HTTPException(status_code=500, detail=f"Personality activation failed: {str(e)}")

        @self.api.app.get("/user/{user_id}/personality")
        async def get_user_personality(user_id: str):
            """Get active personality for a user."""
            personality_id = self.active_personalities.get(user_id)
            if not personality_id:
                # Return default personality
                personality_id = self.default_personality

            if personality_id not in self.personalities:
                raise HTTPException(status_code=404, detail="Personality not found")

            return self.personalities[personality_id]

        @self.api.app.post("/analyze-style")
        async def analyze_conversation_style(request: Dict[str, Any]):
            """Analyze conversation style and suggest personality."""
            try:
                conversation_history = request.get("conversation_history", [])
                user_id = request.get("user_id")

                if not conversation_history:
                    raise HTTPException(status_code=400, detail="Conversation history is required")

                # Analyze style
                style_analysis = await self._analyze_conversation_style(conversation_history)

                # Suggest personality
                suggested_personality = await self._suggest_personality_for_user(user_id, style_analysis)

                return {
                    "style_analysis": style_analysis,
                    "suggested_personality": suggested_personality,
                    "user_id": user_id
                }

            except Exception as e:
                self.logger.error(f"Analyze style error: {e}")
                raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")

        @self.api.app.get("/health")
        async def health_check():
            """Personality system health check."""
            return {
                "service": "personality_system",
                "status": "healthy" if self.is_connected else "unhealthy",
                "personalities_loaded": len(self.personalities),
                "active_users": len(self.active_personalities),
                "cache_size": len(self.personality_cache),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to personality-related MQTT topics."""
        topics = [
            "alicia/personality/create",
            "alicia/personality/update",
            "alicia/personality/activate",
            "alicia/personality/analyze",
            "alicia/conversation/style",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to personality topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/personality/create":
                self._handle_personality_create(message)
            elif topic == "alicia/personality/update":
                self._handle_personality_update(message)
            elif topic == "alicia/personality/activate":
                self._handle_personality_activate(message)
            elif topic == "alicia/personality/analyze":
                self._handle_style_analysis(message)
            elif topic == "alicia/conversation/style":
                self._handle_conversation_style(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing personality message: {e}")

    def _handle_personality_create(self, message: Dict[str, Any]):
        """Handle personality creation requests."""
        try:
            payload = message.get("payload", {})
            personality_data = payload.get("personality")

            if personality_data:
                asyncio.create_task(self._create_personality_from_message(personality_data))

        except Exception as e:
            self.logger.error(f"Error handling personality create: {e}")

    def _handle_personality_update(self, message: Dict[str, Any]):
        """Handle personality update requests."""
        try:
            payload = message.get("payload", {})
            personality_id = payload.get("personality_id")
            updates = payload.get("updates", {})

            if personality_id and updates:
                asyncio.create_task(self._update_personality(personality_id, updates))

        except Exception as e:
            self.logger.error(f"Error handling personality update: {e}")

    def _handle_personality_activate(self, message: Dict[str, Any]):
        """Handle personality activation requests."""
        try:
            payload = message.get("payload", {})
            user_id = payload.get("user_id")
            personality_id = payload.get("personality_id")

            if user_id and personality_id:
                asyncio.create_task(self._activate_personality_for_user(user_id, personality_id))

        except Exception as e:
            self.logger.error(f"Error handling personality activate: {e}")

    def _handle_style_analysis(self, message: Dict[str, Any]):
        """Handle style analysis requests."""
        try:
            payload = message.get("payload", {})
            conversation_history = payload.get("conversation_history", [])
            user_id = payload.get("user_id")

            if conversation_history:
                asyncio.create_task(self._analyze_conversation_style(conversation_history))

        except Exception as e:
            self.logger.error(f"Error handling style analysis: {e}")

    def _handle_conversation_style(self, message: Dict[str, Any]):
        """Handle conversation style updates."""
        try:
            payload = message.get("payload", {})
            user_id = payload.get("user_id")
            style_data = payload.get("style_data", {})

            if user_id and style_data:
                self.conversation_styles[user_id] = style_data

        except Exception as e:
            self.logger.error(f"Error handling conversation style: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _validate_personality_data(self, personality_data: Dict[str, Any]):
        """Validate personality data structure."""
        required_fields = ["name", "description", "traits", "communication_style", "system_prompt"]

        for field in required_fields:
            if field not in personality_data:
                raise Exception(f"Missing required field: {field}")

        # Validate communication style
        comm_style = personality_data.get("communication_style", {})
        required_style_fields = ["formality", "verbosity", "humor", "empathy"]

        for field in required_style_fields:
            if field not in comm_style:
                raise Exception(f"Missing communication style field: {field}")

    async def _create_personality(self, personality_id: str, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new personality profile."""
        try:
            # Check limits
            if len(self.personalities) >= self.max_personalities:
                raise Exception(f"Maximum number of personalities ({self.max_personalities}) reached")

            # Add metadata
            personality_data["personality_id"] = personality_id
            personality_data["created_at"] = time.time()
            personality_data["updated_at"] = time.time()

            # Store personality
            self.personalities[personality_id] = personality_data

            # Publish creation event
            creation_message = {
                "message_id": f"personality_created_{personality_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "personality_id": personality_id,
                    "personality": personality_data
                }
            }

            self.publish_message("alicia/personality/created", creation_message)

            self.logger.info(f"Created personality: {personality_id}")
            return personality_data

        except Exception as e:
            self.logger.error(f"Error creating personality: {e}")
            raise

    async def _create_personality_from_message(self, personality_data: Dict[str, Any]):
        """Create personality from MQTT message."""
        try:
            personality_id = personality_data.get("personality_id")
            if not personality_id:
                personality_id = f"personality_{uuid.uuid4().hex[:8]}"
                personality_data["personality_id"] = personality_id

            await self._create_personality(personality_id, personality_data)

        except Exception as e:
            self.logger.error(f"Error creating personality from message: {e}")

    async def _update_personality(self, personality_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing personality profile."""
        try:
            if personality_id not in self.personalities:
                raise Exception(f"Personality {personality_id} not found")

            # Update personality
            personality = self.personalities[personality_id]
            personality.update(updates)
            personality["updated_at"] = time.time()

            # Clear cache
            if personality_id in self.personality_cache:
                del self.personality_cache[personality_id]

            # Publish update event
            update_message = {
                "message_id": f"personality_updated_{personality_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "personality_id": personality_id,
                    "updates": updates,
                    "personality": personality
                }
            }

            self.publish_message("alicia/personality/updated", update_message)

            self.logger.info(f"Updated personality: {personality_id}")
            return personality

        except Exception as e:
            self.logger.error(f"Error updating personality: {e}")
            raise

    async def _activate_personality_for_user(self, user_id: str, personality_id: str):
        """Activate a personality for a specific user."""
        try:
            self.active_personalities[user_id] = personality_id

            # Publish activation event
            activation_message = {
                "message_id": f"personality_activated_{user_id}_{personality_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "user_id": user_id,
                    "personality_id": personality_id,
                    "personality": self.personalities.get(personality_id)
                }
            }

            self.publish_message("alicia/personality/activated", activation_message)

            self.logger.info(f"Activated personality {personality_id} for user {user_id}")

        except Exception as e:
            self.logger.error(f"Error activating personality: {e}")
            raise

    async def _analyze_conversation_style(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation style from history."""
        try:
            # Simple style analysis (could be enhanced with ML)
            total_messages = len(conversation_history)
            user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
            assistant_messages = [msg for msg in conversation_history if msg.get("role") == "assistant"]

            # Analyze formality
            formal_indicators = ["please", "thank you", "could you", "would you"]
            casual_indicators = ["hey", "yeah", "okay", "sure"]

            formality_score = 0
            for msg in user_messages[-10:]:  # Last 10 messages
                content = msg.get("content", "").lower()
                formality_score += sum(1 for indicator in formal_indicators if indicator in content)
                formality_score -= sum(1 for indicator in casual_indicators if indicator in content)

            # Analyze verbosity
            avg_length = sum(len(msg.get("content", "")) for msg in user_messages) / max(len(user_messages), 1)

            # Determine style
            style_analysis = {
                "formality": "formal" if formality_score > 0 else "casual",
                "verbosity": "verbose" if avg_length > 100 else "concise",
                "total_messages": total_messages,
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "avg_message_length": avg_length,
                "formality_score": formality_score
            }

            return style_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing conversation style: {e}")
            return {"error": str(e)}

    async def _suggest_personality_for_user(self, user_id: str, style_analysis: Dict[str, Any]) -> str:
        """Suggest a personality based on user's conversation style."""
        try:
            formality = style_analysis.get("formality", "casual")
            verbosity = style_analysis.get("verbosity", "concise")

            # Simple personality suggestion logic
            if formality == "formal" and verbosity == "concise":
                return "professional"
            elif formality == "casual" and verbosity == "verbose":
                return "creative"
            else:
                return "alicia"  # Default

        except Exception as e:
            self.logger.error(f"Error suggesting personality: {e}")
            return "alicia"

    async def _cleanup_expired_cache(self):
        """Cleanup expired personality cache."""
        while True:
            try:
                current_time = time.time()

                # Find expired cache entries
                expired_keys = []
                for key, cache_entry in self.personality_cache.items():
                    if current_time - cache_entry.get("cached_at", 0) > self.personality_cache_ttl:
                        expired_keys.append(key)

                # Remove expired entries
                for key in expired_keys:
                    del self.personality_cache[key]

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up cache: {e}")
                await asyncio.sleep(300)


def main():
    """Main entry point for Personality System service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create personality system
    personality_system = PersonalitySystem()

    # Start API server
    try:
        personality_system.api.run_api(host="0.0.0.0", port=8010)
    except KeyboardInterrupt:
        personality_system.shutdown()


if __name__ == "__main__":
    main()
