"""
Alicia Bus Architecture - STT (Speech-to-Text) Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Bus-integrated STT service that handles speech-to-text processing
using Whisper or other STT engines. Publishes results to the bus
for AI processing and maintains compatibility with existing voice pipeline.
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

import numpy as np
import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn

from service_wrapper import BusServiceWrapper, BusServiceAPI


class STTService(BusServiceWrapper):
    """
    STT Service for the Alicia bus architecture.

    Handles speech-to-text processing with multiple engine support:
    - OpenAI Whisper (primary)
    - Google Speech-to-Text (fallback)
    - Azure Speech Services (enterprise)

    Features:
    - Real-time audio processing
    - Multiple language support
    - Quality assessment and confidence scoring
    - Load balancing across multiple instances
    - Bus integration for seamless communication
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "stt_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_stt_2024")
        }

        super().__init__("stt_service", mqtt_config)

        # STT Configuration
        self.stt_engine = os.getenv("STT_ENGINE", "whisper")  # whisper, google, azure
        self.model_size = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
        self.language = os.getenv("STT_LANGUAGE", "en")  # auto for auto-detection
        self.max_audio_length = int(os.getenv("MAX_AUDIO_LENGTH", "30"))  # seconds
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

        # Engine instances
        self.whisper_model = None
        self.google_client = None
        self.azure_client = None

        # Processing queue
        self.processing_queue = asyncio.Queue()
        self.is_processing = False

        # Setup STT engine
        self._setup_stt_engine()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_stt_endpoints()

        # Service capabilities
        self.capabilities = [
            "speech_to_text",
            "audio_transcription",
            "real_time_processing",
            "multi_language_support",
            "confidence_scoring"
        ]

        self.version = "1.0.0"

        # Start processing loop
        asyncio.create_task(self._process_audio_queue())

        self.logger.info(f"STT Service initialized with {self.stt_engine} engine")

    def _setup_stt_engine(self):
        """Setup the selected STT engine."""
        try:
            if self.stt_engine == "whisper":
                self._setup_whisper()
            elif self.stt_engine == "google":
                self._setup_google()
            elif self.stt_engine == "azure":
                self._setup_azure()
            else:
                raise ValueError(f"Unsupported STT engine: {self.stt_engine}")

            self.logger.info(f"STT engine {self.stt_engine} setup complete")

        except Exception as e:
            self.logger.error(f"Failed to setup STT engine: {e}")
            raise

    def _setup_whisper(self):
        """Setup OpenAI Whisper model."""
        try:
            import whisper
            self.logger.info(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = whisper.load_model(self.model_size)
            self.logger.info("Whisper model loaded successfully")
        except ImportError:
            self.logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise

    def _setup_google(self):
        """Setup Google Speech-to-Text client."""
        try:
            from google.cloud import speech
            self.google_client = speech.SpeechClient()
            self.logger.info("Google Speech client initialized")
        except ImportError:
            self.logger.warning("Google Cloud Speech not available")
        except Exception as e:
            self.logger.error(f"Failed to setup Google Speech: {e}")

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

    def _setup_stt_endpoints(self):
        """Setup FastAPI endpoints for STT service."""

        @self.api.app.post("/transcribe")
        async def transcribe_audio(file: UploadFile = File(...), language: str = "auto"):
            """Transcribe uploaded audio file."""
            try:
                # Read audio data
                audio_data = await file.read()

                # Process transcription
                result = await self._transcribe_audio_async(audio_data, language)

                return result

            except Exception as e:
                self.logger.error(f"Transcription error: {e}")
                raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

        @self.api.app.post("/transcribe/base64")
        async def transcribe_base64(audio_data: str, language: str = "auto"):
            """Transcribe base64 encoded audio."""
            try:
                # Decode base64 audio
                audio_bytes = base64.b64decode(audio_data)

                # Process transcription
                result = await self._transcribe_audio_async(audio_bytes, language)

                return result

            except Exception as e:
                self.logger.error(f"Base64 transcription error: {e}")
                raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

        @self.api.app.get("/engines")
        async def list_engines():
            """List available STT engines."""
            engines = []
            if self.whisper_model:
                engines.append({"name": "whisper", "model": self.model_size, "status": "available"})
            if self.google_client:
                engines.append({"name": "google", "status": "available"})
            if self.azure_client:
                engines.append({"name": "azure", "status": "available"})

            return {"engines": engines, "active": self.stt_engine}

        @self.api.app.get("/health")
        async def health_check():
            """STT service health check."""
            return {
                "service": "stt_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "engine": self.stt_engine,
                "model": getattr(self, 'model_size', 'unknown'),
                "queue_size": self.processing_queue.qsize(),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to STT-related MQTT topics."""
        topics = [
            "alicia/voice/stt/request",
            "alicia/voice/command/route",
            "capability:speech_to_text",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to STT topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic in ["alicia/voice/stt/request", "capability:speech_to_text"]:
                self._handle_stt_request(message)
            elif topic == "alicia/voice/command/route":
                self._handle_voice_command(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing STT message: {e}")
            self._send_error_response(message, str(e))

    def _handle_stt_request(self, message: Dict[str, Any]):
        """Handle STT transcription request."""
        try:
            payload = message.get("payload", {})
            audio_data = payload.get("audio_data")
            language = payload.get("language", self.language)
            session_id = payload.get("session_id", str(uuid.uuid4()))

            if not audio_data:
                self._send_error_response(message, "No audio data provided")
                return

            # Decode base64 audio
            try:
                audio_bytes = base64.b64decode(audio_data)
            except Exception as e:
                self._send_error_response(message, f"Invalid audio data: {e}")
                return

            # Add to processing queue
            asyncio.create_task(self._queue_transcription(message, audio_bytes, language, session_id))

        except Exception as e:
            self.logger.error(f"Error handling STT request: {e}")
            self._send_error_response(message, str(e))

    def _handle_voice_command(self, message: Dict[str, Any]):
        """Handle voice command that may need STT processing."""
        # Check if this is a voice command that needs transcription
        payload = message.get("payload", {})
        if payload.get("audio_data"):
            self._handle_stt_request(message)

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _queue_transcription(self, original_message: Dict[str, Any], audio_bytes: bytes,
                                 language: str, session_id: str):
        """Queue audio for transcription."""
        await self.processing_queue.put({
            "message": original_message,
            "audio": audio_bytes,
            "language": language,
            "session_id": session_id,
            "timestamp": time.time()
        })

    async def _process_audio_queue(self):
        """Process audio transcription queue."""
        while True:
            try:
                if self.processing_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                # Get next item from queue
                item = await self.processing_queue.get()

                # Process transcription
                result = await self._transcribe_audio_async(
                    item["audio"],
                    item["language"]
                )

                # Send response
                self._send_transcription_response(item["message"], result, item["session_id"])

                # Mark task as done
                self.processing_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing audio queue: {e}")
                await asyncio.sleep(1)

    async def _transcribe_audio_async(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """Transcribe audio asynchronously."""
        loop = asyncio.get_event_loop()

        # Run transcription in thread pool to avoid blocking
        result = await loop.run_in_executor(
            None,
            self._transcribe_audio_sync,
            audio_bytes,
            language
        )

        return result

    def _transcribe_audio_sync(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """Transcribe audio synchronously."""
        start_time = time.time()

        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Transcribe based on engine
            if self.stt_engine == "whisper":
                result = self._transcribe_whisper(temp_path, language)
            elif self.stt_engine == "google":
                result = self._transcribe_google(audio_bytes, language)
            elif self.stt_engine == "azure":
                result = self._transcribe_azure(audio_bytes, language)
            else:
                raise ValueError(f"Unsupported STT engine: {self.stt_engine}")

            # Cleanup temp file
            os.unlink(temp_path)

            # Add processing time
            result["processing_time"] = time.time() - start_time

            return result

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def _transcribe_whisper(self, audio_path: str, language: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper."""
        try:
            result = self.whisper_model.transcribe(
                audio_path,
                language=language if language != "auto" else None,
                fp16=False  # Disable FP16 for compatibility
            )

            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "confidence": result.get("confidence", 0.0),
                "segments": result.get("segments", []),
                "engine": "whisper"
            }

        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            raise

    def _transcribe_google(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """Transcribe using Google Speech-to-Text."""
        try:
            from google.cloud import speech

            # Configure audio
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language if language != "auto" else "en-US"
            )

            # Transcribe
            response = self.google_client.recognize(config=config, audio=audio)

            if response.results:
                result = response.results[0]
                return {
                    "success": True,
                    "text": result.alternatives[0].transcript,
                    "language": language,
                    "confidence": result.alternatives[0].confidence,
                    "engine": "google"
                }
            else:
                return {
                    "success": False,
                    "error": "No transcription results",
                    "engine": "google"
                }

        except Exception as e:
            self.logger.error(f"Google transcription failed: {e}")
            raise

    def _transcribe_azure(self, audio_bytes: bytes, language: str) -> Dict[str, Any]:
        """Transcribe using Azure Speech Services."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            # Create audio stream
            stream = speechsdk.audio.AudioDataStream()
            stream.write(audio_bytes)

            # Configure speech recognition
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.azure_client,
                audio_config=speechsdk.audio.AudioConfig(stream=stream)
            )

            # Perform recognition
            result = speech_recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "success": True,
                    "text": result.text,
                    "language": language,
                    "confidence": 0.0,  # Azure doesn't provide confidence in simple API
                    "engine": "azure"
                }
            else:
                return {
                    "success": False,
                    "error": f"Recognition failed: {result.reason}",
                    "engine": "azure"
                }

        except Exception as e:
            self.logger.error(f"Azure transcription failed: {e}")
            raise

    def _send_transcription_response(self, original_message: Dict[str, Any],
                                   result: Dict[str, Any], session_id: str):
        """Send transcription response via MQTT."""
        response = {
            "message_id": f"stt_response_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "response",
            "payload": {
                "session_id": session_id,
                "transcription": result,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/stt/response", response)

    def _send_error_response(self, original_message: Dict[str, Any], error: str):
        """Send error response via MQTT."""
        response = {
            "message_id": f"stt_error_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": original_message.get("source"),
            "message_type": "error",
            "payload": {
                "error": error,
                "original_request": original_message.get("payload", {})
            }
        }

        self.publish_message("alicia/voice/stt/error", response)


def main():
    """Main entry point for STT Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create STT service
    stt_service = STTService()

    # Start API server
    try:
        stt_service.api.run_api(host="0.0.0.0", port=8001)
    except KeyboardInterrupt:
        stt_service.shutdown()


if __name__ == "__main__":
    main()
