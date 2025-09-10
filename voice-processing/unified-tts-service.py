#!/usr/bin/env python3
"""
Unified TTS Service for Alicia
Bridges Wyoming protocol with Sonos audio output
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import threading
import time
import uuid
from typing import Optional, Dict, Any

import paho.mqtt.client as mqtt
from wyoming.client import AsyncTcpClient
from wyoming.event import Event
from wyoming.info import Info
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.server import AsyncEventHandler, AsyncServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedTTSService:
    """Unified TTS service that bridges Wyoming protocol with Sonos audio"""

    def __init__(self):
        # Configuration
        self.piper_executable = "/usr/local/bin/piper/piper"
        self.audio_dir = "/tmp/audio"
        self.http_server_url = "http://192.168.1.100:8080"
        self.mqtt_broker = os.getenv("MQTT_BROKER", "alicia_mqtt")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "tts_service")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")

        # MQTT client for Sonos communication
        self.mqtt_client = None

        # Ensure audio directory exists
        os.makedirs(self.audio_dir, exist_ok=True)

        # Setup MQTT
        self.setup_mqtt()

    def setup_mqtt(self):
        """Setup MQTT client for Sonos communication"""
        self.mqtt_client = mqtt.Client("unified_tts_service")
        self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info("MQTT client setup complete for TTS service")
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("TTS Service connected to MQTT broker")
            # Subscribe to TTS status updates
            client.subscribe("alicia/tts/status")
        else:
            logger.error(f"TTS Service failed to connect to MQTT broker: {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        """Handle MQTT messages"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"TTS Service received: {msg.topic} -> {payload}")

            if msg.topic == "alicia/tts/status":
                # Handle TTS completion status
                data = json.loads(payload)
                if data.get("status") == "completed":
                    logger.info(f"TTS completed for speaker: {data.get('speaker')}")
                elif data.get("status") == "failed":
                    logger.error(f"TTS failed: {data.get('error')}")

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    async def handle_wyoming_request(self, text: str, voice: str = "en_US-lessac-medium") -> Optional[str]:
        """Handle Wyoming TTS request and return HTTP URL for audio"""
        try:
            logger.info(f"Processing Wyoming TTS request: {text[:50]}...")

            # Generate unique filename
            audio_filename = f"wyoming_tts_{uuid.uuid4().hex}.wav"
            audio_path = os.path.join(self.audio_dir, audio_filename)

            # Generate audio using Piper
            success = await self._generate_audio_with_piper(text, voice, audio_path)

            if not success:
                logger.error("Failed to generate audio with Piper")
                return None

            # Generate HTTP URL for the audio file
            audio_url = f"{self.http_server_url}/{audio_filename}"

            # Send to Sonos via MQTT
            await self._send_to_sonos_via_mqtt(text, audio_url, voice)

            logger.info(f"TTS audio generated and sent to Sonos: {audio_url}")
            return audio_url

        except Exception as e:
            logger.error(f"Error handling Wyoming request: {e}")
            return None

    async def _generate_audio_with_piper(self, text: str, voice: str, output_path: str) -> bool:
        """Generate audio using Piper TTS"""
        try:
            # Check if Piper is available
            if not os.path.exists(self.piper_executable):
                logger.error(f"Piper executable not found: {self.piper_executable}")
                return False

            # Get model path for voice
            model_path = self._get_piper_model_path(voice)
            if not model_path or not os.path.exists(model_path):
                logger.error(f"Piper model not found: {model_path}")
                return False

            # Run Piper TTS
            cmd = [
                self.piper_executable,
                "--model", model_path,
                "--output_file", output_path
            ]

            logger.info(f"Running Piper command: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Send text to Piper
            stdout, stderr = await process.communicate(input=text.encode())

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {stderr.decode()}")
                return False

            # Validate output file
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                logger.error("Piper TTS generated invalid or empty audio file")
                return False

            logger.info(f"Audio generated successfully: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating audio with Piper: {e}")
            return False

    def _get_piper_model_path(self, voice: str) -> Optional[str]:
        """Get Piper model path for voice"""
        # Extract language from voice name
        if voice.startswith("en"):
            model_name = "en_US-lessac-medium.onnx"
        elif voice.startswith("es"):
            model_name = "es_ES-davefx-medium.onnx"
        elif voice.startswith("fr"):
            model_name = "fr_FR-siwis-medium.onnx"
        elif voice.startswith("de"):
            model_name = "de_DE-thorsten-medium.onnx"
        else:
            model_name = "en_US-lessac-medium.onnx"  # Default

        model_path = f"/usr/local/bin/piper/models/{model_name}"
        return model_path if os.path.exists(model_path) else None

    async def _send_to_sonos_via_mqtt(self, text: str, audio_url: str, voice: str):
        """Send TTS request to Sonos via MQTT"""
        try:
            # Extract language from voice
            language = voice.split("_")[0] if "_" in voice else "en"

            tts_payload = {
                "speaker": "kitchen",
                "message": text,
                "language": language,
                "volume": 30,
                "audio_url": audio_url,  # Direct audio URL for Sonos
                "use_wyoming": True
            }

            self.mqtt_client.publish("alicia/tts/kitchen", json.dumps(tts_payload))
            logger.info(f"Sent Wyoming TTS to Sonos: {text[:30]}...")

        except Exception as e:
            logger.error(f"Error sending to Sonos via MQTT: {e}")

    def cleanup_old_files(self):
        """Clean up old audio files"""
        try:
            import glob

            # Remove files older than 1 hour
            cutoff_time = time.time() - 3600

            for file_path in glob.glob(os.path.join(self.audio_dir, "wyoming_tts_*.wav")):
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old audio file: {file_path}")

        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

class WyomingTTSHandler(AsyncEventHandler):
    """Wyoming protocol handler for TTS requests"""

    def __init__(self, tts_service: UnifiedTTSService):
        self.tts_service = tts_service

    async def handle_event(self, event: Event) -> bool:
        """Handle Wyoming events"""
        try:
            if event.type == "synthesize":
                # Extract synthesis parameters
                text = event.data.get("text", "")
                voice = event.data.get("voice", {}).get("name", "en_US-lessac-medium")

                if not text:
                    logger.warning("Received synthesize event with empty text")
                    return True

                # Generate audio and get URL
                audio_url = await self.tts_service.handle_wyoming_request(text, voice)

                if audio_url:
                    # Send success response
                    response_event = Event(
                        type="audio-start",
                        data={"url": audio_url}
                    )
                    await self.write_event(response_event)

                    # Send audio-stop to complete the transaction
                    await self.write_event(Event(type="audio-stop"))
                else:
                    # Send error response
                    error_event = Event(
                        type="error",
                        data={"message": "TTS generation failed"}
                    )
                    await self.write_event(error_event)

                return True

            elif event.type == "describe":
                # Send service description
                info = Info(
                    name="Unified TTS Service",
                    description="Wyoming-compatible TTS service with Sonos integration",
                    version="1.0.0"
                )
                await self.write_event(info.event())
                return True

            return False

        except Exception as e:
            logger.error(f"Error handling Wyoming event: {e}")
            return False

async def main():
    """Main function to run the unified TTS service"""
    logger.info("Starting Unified TTS Service...")

    # Create TTS service
    tts_service = UnifiedTTSService()

    # Create Wyoming handler
    handler = WyomingTTSHandler(tts_service)

    # Start cleanup task
    async def cleanup_task():
        while True:
            await asyncio.sleep(1800)  # Clean up every 30 minutes
            tts_service.cleanup_old_files()

    # Start cleanup in background
    asyncio.create_task(cleanup_task())

    # Start Wyoming server
    server = AsyncServer(handler, port=10200)
    logger.info("Unified TTS Service listening on port 10200")

    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Unified TTS Service...")
    finally:
        if tts_service.mqtt_client:
            tts_service.mqtt_client.loop_stop()
            tts_service.mqtt_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
