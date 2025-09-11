"""
Alicia Bus Architecture - Voice Router Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Voice command router that orchestrates the complete voice pipeline:
STT → AI → TTS → Speaker. Handles voice command routing, session management,
and pipeline coordination for seamless voice interactions.
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


class VoiceRouter(BusServiceWrapper):
    """
    Voice Router service for the Alicia bus architecture.

    Orchestrates the complete voice pipeline:
    1. Receives voice commands
    2. Routes to STT service for transcription
    3. Routes transcription to AI service for processing
    4. Routes AI response to TTS service for synthesis
    5. Routes synthesized audio to speaker services

    Features:
    - Session management and tracking
    - Pipeline orchestration and coordination
    - Error handling and fallback mechanisms
    - Performance monitoring and optimization
    - Multi-modal voice command support
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "voice_router"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_router_2024")
        }

        super().__init__("voice_router", mqtt_config)

        # Voice Router Configuration
        self.max_sessions = int(os.getenv("MAX_SESSIONS", "10"))
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "300"))  # 5 minutes
        self.pipeline_timeout = int(os.getenv("PIPELINE_TIMEOUT", "30"))  # 30 seconds

        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_cleanup_task = None

        # Pipeline tracking
        self.pipeline_steps = {
            "stt": "alicia/voice/stt/request",
            "ai": "alicia/voice/ai/request",
            "tts": "alicia/voice/tts/request",
            "speaker": "alicia/devices/speakers/announce"
        }

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_router_endpoints()

        # Service capabilities
        self.capabilities = [
            "voice_command_routing",
            "pipeline_orchestration",
            "session_management",
            "voice_pipeline_coordination",
            "multi_modal_processing"
        ]

        self.version = "1.0.0"

        # Start session cleanup
        self._start_session_cleanup()

        self.logger.info("Voice Router initialized")

    def _start_session_cleanup(self):
        """Start periodic session cleanup task."""
        self.session_cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())

    async def _cleanup_expired_sessions(self):
        """Periodically clean up expired sessions."""
        while True:
            try:
                current_time = time.time()
                expired_sessions = []

                for session_id, session_data in self.active_sessions.items():
                    if current_time - session_data["created_at"] > self.session_timeout:
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    self.logger.info(f"Cleaning up expired session: {session_id}")
                    del self.active_sessions[session_id]

                await asyncio.sleep(60)  # Clean up every minute

            except Exception as e:
                self.logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)

    def _setup_router_endpoints(self):
        """Setup FastAPI endpoints for voice router."""

        @self.api.app.post("/process-voice")
        async def process_voice_command(request: Dict[str, Any]):
            """Process a voice command through the complete pipeline."""
            try:
                audio_data = request.get("audio_data")
                session_id = request.get("session_id", str(uuid.uuid4()))
                context = request.get("context", {})

                if not audio_data:
                    raise HTTPException(status_code=400, detail="Audio data is required")

                # Start voice processing pipeline
                result = await self._process_voice_pipeline(audio_data, session_id, context)

                return result

            except Exception as e:
                self.logger.error(f"Voice processing error: {e}")
                raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

        @self.api.app.post("/text-command")
        async def process_text_command(request: Dict[str, Any]):
            """Process a text command (bypassing STT)."""
            try:
                text = request.get("text", "")
                session_id = request.get("session_id", str(uuid.uuid4()))
                context = request.get("context", {})

                if not text:
                    raise HTTPException(status_code=400, detail="Text is required")

                # Start text processing pipeline (skip STT)
                result = await self._process_text_pipeline(text, session_id, context)

                return result

            except Exception as e:
                self.logger.error(f"Text command processing error: {e}")
                raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

        @self.api.app.get("/sessions")
        async def list_sessions():
            """List active voice sessions."""
            sessions = {}
            for session_id, session_data in self.active_sessions.items():
                sessions[session_id] = {
                    "created_at": session_data["created_at"],
                    "last_activity": session_data.get("last_activity", session_data["created_at"]),
                    "status": session_data.get("status", "active"),
                    "current_step": session_data.get("current_step", "unknown")
                }

            return {"sessions": sessions, "count": len(sessions)}

        @self.api.app.delete("/session/{session_id}")
        async def end_session(session_id: str):
            """End a voice session."""
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return {"status": "ended", "session_id": session_id}
            else:
                raise HTTPException(status_code=404, detail="Session not found")

        @self.api.app.get("/health")
        async def health_check():
            """Voice router health check."""
            return {
                "service": "voice_router",
                "status": "healthy" if self.is_connected else "unhealthy",
                "active_sessions": len(self.active_sessions),
                "max_sessions": self.max_sessions,
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to voice-related MQTT topics."""
        topics = [
            "alicia/voice/command/route",
            "alicia/voice/stt/response",
            "alicia/voice/stt/error",
            "alicia/voice/ai/response",
            "alicia/voice/ai/error",
            "alicia/voice/tts/response",
            "alicia/voice/tts/error",
            "alicia/devices/speakers/status",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to voice router topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/voice/command/route":
                self._handle_voice_command(message)
            elif topic == "alicia/voice/stt/response":
                self._handle_stt_response(message)
            elif topic == "alicia/voice/stt/error":
                self._handle_stt_error(message)
            elif topic == "alicia/voice/ai/response":
                self._handle_ai_response(message)
            elif topic == "alicia/voice/ai/error":
                self._handle_ai_error(message)
            elif topic == "alicia/voice/tts/response":
                self._handle_tts_response(message)
            elif topic == "alicia/voice/tts/error":
                self._handle_tts_error(message)
            elif topic == "alicia/devices/speakers/status":
                self._handle_speaker_status(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing voice router message: {e}")

    def _handle_voice_command(self, message: Dict[str, Any]):
        """Handle incoming voice command."""
        try:
            payload = message.get("payload", {})
            audio_data = payload.get("audio_data")
            session_id = payload.get("session_id", str(uuid.uuid4()))

            if not audio_data:
                self._send_error_response(message, "No audio data provided")
                return

            # Create new session
            self._create_session(session_id, "voice_command")

            # Start voice processing pipeline
            asyncio.create_task(self._process_voice_pipeline_async(message, audio_data, session_id))

        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            self._send_error_response(message, str(e))

    def _handle_stt_response(self, message: Dict[str, Any]):
        """Handle STT response and route to AI."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            transcription = payload.get("transcription", {})

            if not session_id or session_id not in self.active_sessions:
                self.logger.warning(f"Received STT response for unknown session: {session_id}")
                return

            # Update session
            self._update_session(session_id, "stt_complete", transcription)

            if transcription.get("success"):
                # STT successful, route to AI
                text = transcription.get("text", "")
                if text:
                    self._route_to_ai(session_id, text)
                else:
                    self._send_pipeline_error(session_id, "No transcription text received")
            else:
                # STT failed
                error = transcription.get("error", "STT processing failed")
                self._send_pipeline_error(session_id, f"STT Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling STT response: {e}")

    def _handle_stt_error(self, message: Dict[str, Any]):
        """Handle STT error."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            error = payload.get("error", "Unknown STT error")

            if session_id and session_id in self.active_sessions:
                self._send_pipeline_error(session_id, f"STT Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling STT error: {e}")

    def _handle_ai_response(self, message: Dict[str, Any]):
        """Handle AI response and route to TTS."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            ai_response = payload.get("ai_response", {})

            if not session_id or session_id not in self.active_sessions:
                self.logger.warning(f"Received AI response for unknown session: {session_id}")
                return

            # Update session
            self._update_session(session_id, "ai_complete", ai_response)

            if ai_response.get("success"):
                # AI successful, route to TTS
                response_text = ai_response.get("response", "")
                if response_text:
                    self._route_to_tts(session_id, response_text)
                else:
                    self._send_pipeline_error(session_id, "No AI response text received")
            else:
                # AI failed
                error = ai_response.get("error", "AI processing failed")
                self._send_pipeline_error(session_id, f"AI Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling AI response: {e}")

    def _handle_ai_error(self, message: Dict[str, Any]):
        """Handle AI error."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            error = payload.get("error", "Unknown AI error")

            if session_id and session_id in self.active_sessions:
                self._send_pipeline_error(session_id, f"AI Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling AI error: {e}")

    def _handle_tts_response(self, message: Dict[str, Any]):
        """Handle TTS response and route to speakers."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            synthesis = payload.get("synthesis", {})

            if not session_id or session_id not in self.active_sessions:
                self.logger.warning(f"Received TTS response for unknown session: {session_id}")
                return

            # Update session
            self._update_session(session_id, "tts_complete", synthesis)

            if synthesis.get("success"):
                # TTS successful, route to speakers
                audio_path = synthesis.get("audio_path")
                if audio_path:
                    self._route_to_speakers(session_id, audio_path)
                    # Mark pipeline as complete
                    self._complete_pipeline(session_id)
                else:
                    self._send_pipeline_error(session_id, "No audio path in TTS response")
            else:
                # TTS failed
                error = synthesis.get("error", "TTS synthesis failed")
                self._send_pipeline_error(session_id, f"TTS Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling TTS response: {e}")

    def _handle_tts_error(self, message: Dict[str, Any]):
        """Handle TTS error."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            error = payload.get("error", "Unknown TTS error")

            if session_id and session_id in self.active_sessions:
                self._send_pipeline_error(session_id, f"TTS Error: {error}")

        except Exception as e:
            self.logger.error(f"Error handling TTS error: {e}")

    def _handle_speaker_status(self, message: Dict[str, Any]):
        """Handle speaker status updates."""
        # Could be used for speaker availability tracking
        pass

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    def _create_session(self, session_id: str, source: str):
        """Create a new voice session."""
        self.active_sessions[session_id] = {
            "session_id": session_id,
            "created_at": time.time(),
            "last_activity": time.time(),
            "status": "active",
            "source": source,
            "current_step": "initialized",
            "pipeline_data": {}
        }

        self.logger.info(f"Created voice session: {session_id}")

    def _update_session(self, session_id: str, step: str, data: Dict[str, Any]):
        """Update session with new step data."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["current_step"] = step
            self.active_sessions[session_id]["last_activity"] = time.time()
            self.active_sessions[session_id]["pipeline_data"][step] = data

    def _complete_pipeline(self, session_id: str):
        """Mark pipeline as completed."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["completed_at"] = time.time()

            # Log completion
            session_data = self.active_sessions[session_id]
            duration = session_data["completed_at"] - session_data["created_at"]
            self.logger.info(f"Voice pipeline completed for session {session_id} in {duration:.2f}s")

    async def _process_voice_pipeline_async(self, original_message: Dict[str, Any],
                                          audio_data: str, session_id: str):
        """Process voice pipeline asynchronously."""
        try:
            # Route to STT service
            self._route_to_stt(session_id, audio_data)

        except Exception as e:
            self.logger.error(f"Error in voice pipeline: {e}")
            self._send_error_response(original_message, str(e))

    async def _process_text_pipeline(self, text: str, session_id: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Process text command pipeline (skip STT)."""
        try:
            # Create session
            self._create_session(session_id, "text_command")

            # Update session
            self._update_session(session_id, "text_received", {"text": text})

            # Route directly to AI
            self._route_to_ai(session_id, text)

            return {
                "session_id": session_id,
                "status": "processing",
                "message": "Text command sent to AI processing"
            }

        except Exception as e:
            self.logger.error(f"Error in text pipeline: {e}")
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }

    def _route_to_stt(self, session_id: str, audio_data: str):
        """Route audio to STT service."""
        stt_request = {
            "message_id": f"stt_request_{session_id}_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "stt_service",
            "message_type": "request",
            "payload": {
                "audio_data": audio_data,
                "session_id": session_id,
                "language": "en-US"
            }
        }

        self.publish_message("alicia/voice/stt/request", stt_request)
        self._update_session(session_id, "routed_to_stt", {})

    def _route_to_ai(self, session_id: str, text: str):
        """Route transcription to AI service."""
        ai_request = {
            "message_id": f"ai_request_{session_id}_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "ai_service",
            "message_type": "request",
            "payload": {
                "text": text,
                "session_id": session_id,
                "context": {"source": "voice_input"}
            }
        }

        self.publish_message("alicia/voice/ai/request", ai_request)
        self._update_session(session_id, "routed_to_ai", {})

    def _route_to_tts(self, session_id: str, text: str):
        """Route AI response to TTS service."""
        tts_request = {
            "message_id": f"tts_request_{session_id}_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "tts_service",
            "message_type": "request",
            "payload": {
                "text": text,
                "session_id": session_id,
                "voice": "en_US-lessac-medium"
            }
        }

        self.publish_message("alicia/voice/tts/request", tts_request)
        self._update_session(session_id, "routed_to_tts", {})

    def _route_to_speakers(self, session_id: str, audio_path: str):
        """Route synthesized audio to speakers."""
        speaker_request = {
            "message_id": f"speaker_request_{session_id}_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "capability:speaker",
            "message_type": "command",
            "payload": {
                "audio_path": audio_path,
                "session_id": session_id,
                "volume": 75
            }
        }

        self.publish_message("alicia/devices/speakers/announce", speaker_request)
        self._update_session(session_id, "routed_to_speakers", {})

    def _send_pipeline_error(self, session_id: str, error: str):
        """Send pipeline error for session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "error"
            self.active_sessions[session_id]["error"] = error
            self.active_sessions[session_id]["error_at"] = time.time()

        self.logger.error(f"Pipeline error for session {session_id}: {error}")

        # Publish error message
        error_message = {
            "message_id": f"pipeline_error_{session_id}_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "broadcast",
            "message_type": "error",
            "payload": {
                "session_id": session_id,
                "error": error,
                "pipeline_status": self.active_sessions.get(session_id, {})
            }
        }

        self.publish_message("alicia/voice/pipeline/error", error_message)

    def _send_error_response(self, original_message: Dict[str, Any], error: str):
        """Send error response via MQTT."""
        response = {
            "message_id": f"router_error_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "error",
            "payload": {
                "error": error,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/router/error", response)


def main():
    """Main entry point for Voice Router service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create voice router
    voice_router = VoiceRouter()

    # Start API server
    try:
        voice_router.api.run_api(host="0.0.0.0", port=8004)
    except KeyboardInterrupt:
        voice_router.shutdown()


if __name__ == "__main__":
    main()
