"""
Alicia Bus Architecture - TTS (Text-to-Speech) Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Bus-integrated TTS service that handles text-to-speech synthesis
using Piper or other TTS engines. Publishes audio results to the bus
for speaker playback and maintains compatibility with existing voice pipeline.
"""

import asyncio
import base64
import json
import logging
import os
import tempfile
import time
import uuid
from typing import Dict, Any, Optional, List

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn

from ..service_wrapper import BusServiceWrapper, BusServiceAPI


class TTSService(BusServiceWrapper):
    """
    TTS Service for the Alicia bus architecture.

    Handles text-to-speech synthesis with multiple engine support:
    - Piper TTS (primary)
    - Google Text-to-Speech (fallback)
    - Azure Speech Services (enterprise)

    Features:
    - High-quality voice synthesis
    - Multiple voice options
    - Real-time audio streaming
    - Load balancing across instances
    - Bus integration for seamless communication
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "tts_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_tts_2024")
        }

        super().__init__("tts_service", mqtt_config)

        # TTS Configuration
        self.tts_engine = os.getenv("TTS_ENGINE", "piper")  # piper, google, azure
        self.voice_model = os.getenv("VOICE_MODEL", "en_US-lessac-medium")
        self.speaker_id = int(os.getenv("SPEAKER_ID", "0"))
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "22050"))
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "1000"))

        # TTS clients
        self.piper_client = None
        self.google_client = None
        self.azure_client = None

        # Processing queue
        self.processing_queue = asyncio.Queue()
        self.is_processing = False

        # Setup TTS engine
        self._setup_tts_engine()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_tts_endpoints()

        # Service capabilities
        self.capabilities = [
            "text_to_speech",
            "voice_synthesis",
            "audio_generation",
            "multi_voice_support",
            "real_time_synthesis"
        ]

        self.version = "1.0.0"

        # Start processing loop
        asyncio.create_task(self._process_synthesis_queue())

        self.logger.info(f"TTS Service initialized with {self.tts_engine} engine")

    def _setup_tts_engine(self):
        """Setup the selected TTS engine."""
        try:
            if self.tts_engine == "piper":
                self._setup_piper()
            elif self.tts_engine == "google":
                self._setup_google()
            elif self.tts_engine == "azure":
                self._setup_azure()
            else:
                raise ValueError(f"Unsupported TTS engine: {self.tts_engine}")

            self.logger.info(f"TTS engine {self.tts_engine} setup complete")

        except Exception as e:
            self.logger.error(f"Failed to setup TTS engine: {e}")
            raise

    def _setup_piper(self):
        """Setup Piper TTS engine."""
        try:
            # Import Piper (assuming it's available)
            # For now, we'll use subprocess to call piper executable
            import subprocess
            self.piper_client = subprocess
            self.logger.info("Piper TTS client initialized")
        except ImportError:
            self.logger.error("Piper TTS not available. Install with: pip install piper-tts")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup Piper TTS: {e}")
            raise

    def _setup_google(self):
        """Setup Google Text-to-Speech client."""
        try:
            from google.cloud import texttospeech
            self.google_client = texttospeech.TextToSpeechClient()
            self.logger.info("Google TTS client initialized")
        except ImportError:
            self.logger.warning("Google Cloud TTS not available")
        except Exception as e:
            self.logger.error(f"Failed to setup Google TTS: {e}")

    def _setup_azure(self):
        """Setup Azure Speech Services client."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            speech_key = os.getenv("AZURE_SPEECH_KEY")
            service_region = os.getenv("AZURE_SPEECH_REGION", "eastus")

            if speech_key:
                speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
                self.azure_client = speech_config
                self.logger.info("Azure Speech client initialized")
            else:
                self.logger.warning("Azure Speech key not configured")
        except ImportError:
            self.logger.warning("Azure Speech SDK not available")
        except Exception as e:
            self.logger.error(f"Failed to setup Azure Speech: {e}")

    def _setup_tts_endpoints(self):
        """Setup FastAPI endpoints for TTS service."""

        @self.api.app.post("/synthesize")
        async def synthesize_text(request: Dict[str, Any]):
            """Synthesize text to speech."""
            try:
                text = request.get("text", "")
                voice = request.get("voice", self.voice_model)
                session_id = request.get("session_id", str(uuid.uuid4()))

                if not text:
                    raise HTTPException(status_code=400, detail="Text is required")

                # Process synthesis
                result = await self._synthesize_text_async(text, voice, session_id)

                return result

            except Exception as e:
                self.logger.error(f"TTS synthesis error: {e}")
                raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

        @self.api.app.post("/synthesize/base64")
        async def synthesize_base64(request: Dict[str, Any]):
            """Synthesize text and return base64 encoded audio."""
            try:
                text = request.get("text", "")
                voice = request.get("voice", self.voice_model)

                if not text:
                    raise HTTPException(status_code=400, detail="Text is required")

                # Process synthesis and encode
                result = await self._synthesize_text_async(text, voice)
                if result.get("success"):
                    # Read audio file and encode to base64
                    audio_path = result.get("audio_path")
                    if audio_path and os.path.exists(audio_path):
                        with open(audio_path, "rb") as f:
                            audio_data = f.read()
                        result["audio_base64"] = base64.b64encode(audio_data).decode()

                return result

            except Exception as e:
                self.logger.error(f"Base64 TTS synthesis error: {e}")
                raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

        @self.api.app.get("/voices")
        async def list_voices():
            """List available TTS voices."""
            voices = []
            if self.piper_client:
                voices.append({"name": self.voice_model, "engine": "piper", "status": "available"})
            if self.google_client:
                voices.append({"name": "en-US-Neural2-D", "engine": "google", "status": "available"})
            if self.azure_client:
                voices.append({"name": "en-US-AriaNeural", "engine": "azure", "status": "available"})

            return {"voices": voices, "active": self.voice_model}

        @self.api.app.get("/health")
        async def health_check():
            """TTS service health check."""
            return {
                "service": "tts_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "engine": self.tts_engine,
                "voice": self.voice_model,
                "queue_size": self.processing_queue.qsize(),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to TTS-related MQTT topics."""
        topics = [
            "alicia/voice/tts/request",
            "alicia/voice/ai/response",
            "alicia/voice/command/route",
            "capability:text_to_speech",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to TTS topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic in ["alicia/voice/tts/request", "capability:text_to_speech"]:
                self._handle_tts_request(message)
            elif topic == "alicia/voice/ai/response":
                self._handle_ai_response(message)
            elif topic == "alicia/voice/command/route":
                self._handle_voice_command(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing TTS message: {e}")
            self._send_error_response(message, str(e))

    def _handle_tts_request(self, message: Dict[str, Any]):
        """Handle TTS synthesis request."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text", "")
            voice = payload.get("voice", self.voice_model)
            session_id = payload.get("session_id", str(uuid.uuid4()))

            if not text:
                self._send_error_response(message, "No text provided")
                return

            # Add to processing queue
            asyncio.create_task(self._queue_synthesis(message, text, voice, session_id))

        except Exception as e:
            self.logger.error(f"Error handling TTS request: {e}")
            self._send_error_response(message, str(e))

    def _handle_ai_response(self, message: Dict[str, Any]):
        """Handle AI response and potentially trigger TTS synthesis."""
        try:
            payload = message.get("payload", {})
            ai_response = payload.get("ai_response", {})
            session_id = payload.get("session_id", "")

            if ai_response.get("success") and session_id:
                # AI was successful, trigger TTS synthesis
                text = ai_response.get("response", "")
                if text:
                    tts_request = {
                        "message_id": f"tts_from_ai_{uuid.uuid4().hex[:8]}",
                        "timestamp": time.time(),
                        "source": "tts_service",
                        "destination": "tts_service",
                        "message_type": "request",
                        "payload": {
                            "text": text,
                            "session_id": session_id,
                            "context": {"source": "ai_response"}
                        }
                    }
                    self._handle_tts_request(tts_request)

        except Exception as e:
            self.logger.error(f"Error handling AI response: {e}")

    def _handle_voice_command(self, message: Dict[str, Any]):
        """Handle voice command that may need TTS response."""
        payload = message.get("payload", {})
        response_text = payload.get("response_text", "")

        if response_text:
            # This is a voice command response, synthesize with TTS
            self._handle_tts_request(message)

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _queue_synthesis(self, original_message: Dict[str, Any], text: str,
                             voice: str, session_id: str):
        """Queue text for synthesis."""
        await self.processing_queue.put({
            "message": original_message,
            "text": text,
            "voice": voice,
            "session_id": session_id,
            "timestamp": time.time()
        })

    async def _process_synthesis_queue(self):
        """Process synthesis queue."""
        while True:
            try:
                if self.processing_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                # Get next item from queue
                item = await self.processing_queue.get()

                # Process synthesis
                result = await self._synthesize_text_async(
                    item["text"],
                    item["voice"],
                    item["session_id"]
                )

                # Send response
                self._send_synthesis_response(item["message"], result, item["session_id"])

                # Mark task as done
                self.processing_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing synthesis queue: {e}")
                await asyncio.sleep(1)

    async def _synthesize_text_async(self, text: str, voice: str = None,
                                   session_id: str = None) -> Dict[str, Any]:
        """Synthesize text to speech asynchronously."""
        loop = asyncio.get_event_loop()

        # Run synthesis in thread pool to avoid blocking
        result = await loop.run_in_executor(
            None,
            self._synthesize_text_sync,
            text,
            voice or self.voice_model,
            session_id
        )

        return result

    def _synthesize_text_sync(self, text: str, voice: str, session_id: str = None) -> Dict[str, Any]:
        """Synthesize text to speech synchronously."""
        start_time = time.time()

        try:
            # Limit text length
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length] + "..."

            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name

            # Synthesize based on engine
            if self.tts_engine == "piper":
                result = self._synthesize_piper(text, voice, output_path)
            elif self.tts_engine == "google":
                result = self._synthesize_google(text, voice, output_path)
            elif self.tts_engine == "azure":
                result = self._synthesize_azure(text, voice, output_path)
            else:
                raise ValueError(f"Unsupported TTS engine: {self.tts_engine}")

            # Add processing time
            result["processing_time"] = time.time() - start_time
            result["audio_path"] = output_path

            return result

        except Exception as e:
            self.logger.error(f"TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def _synthesize_piper(self, text: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Synthesize using Piper TTS."""
        try:
            # Use piper executable (assuming it's installed)
            import subprocess

            # Prepare piper command
            cmd = [
                "piper",
                "--model", f"/app/models/piper/{voice}.onnx",
                "--output_file", output_path
            ]

            # Run piper
            process = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=30
            )

            if process.returncode == 0:
                return {
                    "success": True,
                    "text": text,
                    "voice": voice,
                    "engine": "piper",
                    "sample_rate": self.sample_rate,
                    "audio_path": output_path
                }
            else:
                return {
                    "success": False,
                    "error": f"Piper failed: {process.stderr.decode()}",
                    "engine": "piper"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Piper synthesis timeout",
                "engine": "piper"
            }
        except Exception as e:
            self.logger.error(f"Piper synthesis failed: {e}")
            raise

    def _synthesize_google(self, text: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Synthesize using Google Text-to-Speech."""
        try:
            from google.cloud import texttospeech

            # Configure voice
            voice_config = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate
            )

            # Synthesize
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = self.google_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=audio_config
            )

            # Save audio
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            return {
                "success": True,
                "text": text,
                "voice": voice,
                "engine": "google",
                "sample_rate": self.sample_rate,
                "audio_path": output_path
            }

        except Exception as e:
            self.logger.error(f"Google TTS synthesis failed: {e}")
            raise

    def _synthesize_azure(self, text: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Synthesize using Azure Speech Services."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            # Configure voice
            self.azure_client.speech_synthesis_voice_name = voice

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_client,
                audio_config=None
            )

            # Synthesize
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Save audio
                with open(output_path, "wb") as out:
                    out.write(result.audio_data)

                return {
                    "success": True,
                    "text": text,
                    "voice": voice,
                    "engine": "azure",
                    "sample_rate": self.sample_rate,
                    "audio_path": output_path
                }
            else:
                return {
                    "success": False,
                    "error": f"Azure synthesis failed: {result.reason}",
                    "engine": "azure"
                }

        except Exception as e:
            self.logger.error(f"Azure TTS synthesis failed: {e}")
            raise

    def _send_synthesis_response(self, original_message: Dict[str, Any],
                               result: Dict[str, Any], session_id: str):
        """Send synthesis response via MQTT."""
        response = {
            "message_id": f"tts_response_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "response",
            "payload": {
                "session_id": session_id,
                "synthesis": result,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/tts/response", response)

    def _send_error_response(self, original_message: Dict[str, Any], error: str):
        """Send error response via MQTT."""
        response = {
            "message_id": f"tts_error_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "error",
            "payload": {
                "error": error,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/tts/error", response)


def main():
    """Main entry point for TTS Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create TTS service
    tts_service = TTSService()

    # Start API server
    try:
        tts_service.api.run_api(host="0.0.0.0", port=8003)
    except KeyboardInterrupt:
        tts_service.shutdown()


if __name__ == "__main__":
    main()
