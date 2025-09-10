#!/usr/bin/env python3
"""
Alicia Enhanced Voice Assistant - Wyoming Protocol + LLM Ready
Local voice assistant using Wyoming protocol for STT/TTS with LLM integration capability
"""

import asyncio
import json
import logging
import os
import time
from typing import Optional, Dict, Any
import uuid

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import uvicorn
import websockets
from wyoming.client import AsyncTcpClient
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Info
from wyoming.tts import Synthesize
from wyoming.asr import Transcribe
from wyoming.wake import Detect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AliciaAssistant:
    def __init__(self):
        self.app = FastAPI(title="Alicia Voice Assistant", version="2.0.0")

        # Configuration from environment
        self.whisper_url = os.getenv("WHISPER_URL", "tcp://alicia_wyoming_whisper:10300")
        self.piper_url = os.getenv("PIPER_URL", "tcp://alicia_wyoming_piper:10200")

        # Parse URLs for AsyncTcpClient (expects host, port separately)
        self.whisper_host, self.whisper_port = self._parse_wyoming_url(self.whisper_url)
        self.piper_host, self.piper_port = self._parse_wyoming_url(self.piper_url)
        self.mqtt_broker = os.getenv("MQTT_BROKER", "alicia_mqtt")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "voice_assistant")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")

        # Wyoming clients
        self.whisper_client = None
        self.piper_client = None

        # MQTT client
        self.mqtt_client = None

        # Assistant state
        self.is_listening = False
        self.conversation_history = []
        self.session_id = str(uuid.uuid4())

        # LLM integration placeholder
        self.llm_enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
        self.llm_endpoint = os.getenv("LLM_ENDPOINT", "")

        self.setup_routes()
        self.setup_mqtt()

    def _parse_wyoming_url(self, url: str) -> tuple[str, int]:
        """Parse Wyoming URL into host and port for AsyncTcpClient"""
        # Remove tcp:// prefix if present
        if url.startswith("tcp://"):
            url = url[6:]

        # Split host and port
        if ":" in url:
            host, port_str = url.rsplit(":", 1)
            port = int(port_str)
        else:
            # Default port if not specified
            host = url
            port = 10300 if "whisper" in url else 10200

        return host, port

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            services_status = await self.check_services_health()
            return {
                "status": "healthy" if all(services_status.values()) else "degraded",
                "services": services_status,
                "session_id": self.session_id,
                "llm_enabled": self.llm_enabled
            }

        @self.app.post("/transcribe")
        async def transcribe_audio(audio_data: bytes):
            """Transcribe audio using Wyoming Whisper"""
            try:
                text, language = await self.transcribe_with_whisper(audio_data)
                return {"text": text, "language": language, "session_id": self.session_id}
            except Exception as e:
                logger.error(f"Transcription error: {e}")
                raise HTTPException(status_code=500, detail="Transcription failed")

        @self.app.post("/synthesize")
        async def synthesize_text(text: str, language: str = "en"):
            """Synthesize speech using Wyoming Piper"""
            try:
                audio_data = await self.synthesize_with_piper(text, language)
                return StreamingResponse(
                    iter([audio_data]),
                    media_type="audio/wav",
                    headers={"Content-Disposition": "attachment; filename=speech.wav"}
                )
            except Exception as e:
                logger.error(f"Synthesis error: {e}")
                raise HTTPException(status_code=500, detail="Synthesis failed")

        @self.app.post("/process-command")
        async def process_command(command: str, background_tasks: BackgroundTasks):
            """Process voice command with optional LLM enhancement"""
            try:
                response = await self.process_voice_command(command)

                # Add to conversation history
                self.conversation_history.append({
                    "timestamp": time.time(),
                    "input": command,
                    "response": response
                })

                # Publish to MQTT
                self.publish_mqtt("alicia/voice/command/processed", json.dumps({
                    "command": command,
                    "response": response,
                    "session_id": self.session_id
                }))

                # Send TTS to Sonos speaker
                self.send_tts_to_sonos(response, "kitchen")

                # Synthesize response in background
                background_tasks.add_task(self.synthesize_and_publish, response)

                return {"response": response, "session_id": self.session_id}

            except Exception as e:
                logger.error(f"Command processing error: {e}")
                raise HTTPException(status_code=500, detail="Command processing failed")

        @self.app.get("/conversation-history")
        async def get_conversation_history(limit: int = 10):
            """Get recent conversation history"""
            return {
                "history": self.conversation_history[-limit:],
                "total": len(self.conversation_history)
            }

        @self.app.post("/clear-history")
        async def clear_conversation_history():
            """Clear conversation history"""
            self.conversation_history.clear()
            return {"message": "Conversation history cleared"}

    def setup_mqtt(self):
        """Setup MQTT client"""
        self.mqtt_client = mqtt.Client(f"alicia_assistant_{self.session_id}")
        self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info("MQTT client setup complete")
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe("alicia/voice/command")
            client.subscribe("alicia/voice/wake")
            client.subscribe("homeassistant/sensor/voice/#")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received MQTT message: {msg.topic} -> {payload}")

            if msg.topic == "alicia/voice/command":
                # Process command asynchronously
                asyncio.create_task(self.handle_mqtt_command(payload))
            elif msg.topic == "alicia/voice/wake":
                self.handle_wake_word()
            elif msg.topic.startswith("homeassistant/sensor/voice/"):
                self.handle_sensor_data(msg.topic, payload)

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    async def handle_mqtt_command(self, command: str):
        """Handle command from MQTT"""
        try:
            response = await self.process_voice_command(command)
            self.publish_mqtt("alicia/voice/response", json.dumps({
                "response": response,
                "session_id": self.session_id
            }))
        except Exception as e:
            logger.error(f"Error handling MQTT command: {e}")

    def handle_wake_word(self):
        """Handle wake word detection"""
        logger.info("Wake word detected!")
        self.is_listening = True
        self.publish_mqtt("alicia/voice/status", json.dumps({
            "status": "listening",
            "session_id": self.session_id
        }))

    def handle_sensor_data(self, topic: str, payload: str):
        """Handle sensor data from MQTT"""
        try:
            data = json.loads(payload)
            logger.info(f"Received sensor data: {topic} -> {data}")

            # Process sensor data and respond if needed
            if "temperature" in topic and self.is_listening:
                temp = data.get("value")
                if temp:
                    response = f"The current temperature is {temp} degrees"
                    asyncio.create_task(self.process_voice_command(response))

        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")

    async def check_services_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        health_status = {}

        # Check Wyoming services
        try:
            async with AsyncTcpClient(self.whisper_host, self.whisper_port) as client:
                health_status["whisper"] = True
        except:
            health_status["whisper"] = False

        try:
            async with AsyncTcpClient(self.piper_host, self.piper_port) as client:
                health_status["piper"] = True
        except:
            health_status["piper"] = False

        # Check MQTT
        health_status["mqtt"] = self.mqtt_client is not None and self.mqtt_client.is_connected()

        return health_status

    async def transcribe_with_whisper(self, audio_data: bytes) -> tuple[str, str]:
        """Transcribe audio using Wyoming Whisper"""
        try:
            async with AsyncTcpClient(self.whisper_host, self.whisper_port) as client:
                # Send transcription request
                await client.write_event(
                    Transcribe(name="alicia_transcription", language="en").event()
                )

                # Send audio data
                await client.write_event(AudioStart().event())
                await client.write_event(AudioChunk(audio_data).event())
                await client.write_event(AudioStop().event())

                # Read response
                while True:
                    event = await client.read_event()
                    if event.type == "transcription":
                        transcription = event.data.get("text", "")
                        language = event.data.get("language", "en")
                        return transcription, language

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise

    async def synthesize_with_piper(self, text: str, language: str = "en") -> bytes:
        """Synthesize speech using unified TTS service via MQTT to Sonos"""
        try:
            # Send TTS request to Sonos bridge via MQTT instead of Wyoming protocol
            tts_payload = {
                "speaker": "kitchen",  # Default speaker
                "message": text,
                "language": language,
                "volume": 30,
                "use_wyoming": True  # Flag for Wyoming protocol compatibility
            }
            self.publish_mqtt("alicia/tts/kitchen", json.dumps(tts_payload))

            # Return empty bytes since audio is handled by Sonos bridge
            # This maintains API compatibility while redirecting to MQTT
            logger.info(f"TTS request sent to Sonos bridge: {text}")
            return b""

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise

    async def process_voice_command(self, command: str) -> str:
        """Process voice command with optional LLM enhancement"""
        logger.info(f"Processing command: {command}")

        # If LLM is enabled, use it for enhanced processing
        if self.llm_enabled and self.llm_endpoint:
            return await self.process_with_llm(command)
        else:
            return self.process_basic_command(command)

    def process_basic_command(self, command: str) -> str:
        """Process command using basic logic"""
        command = command.lower()

        if "turn on" in command or "turn off" in command:
            return self.handle_light_command(command)
        elif "temperature" in command or "temp" in command:
            return "I'll check the current temperature for you."
        elif "status" in command:
            return "All systems are operating normally."
        elif "hello" in command or "hi" in command:
            return "Hello! How can I help you today?"
        elif "time" in command:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        else:
            return f"I heard: {command}. I'm still learning, but I'll help as best I can!"

    async def process_with_llm(self, command: str) -> str:
        """Process command using LLM (placeholder for future implementation)"""
        # This is where LLM integration would go
        logger.info("Processing with LLM (placeholder)")

        # For now, fall back to basic processing
        return self.process_basic_command(command)

    def handle_light_command(self, command: str) -> str:
        """Handle light control commands"""
        if "turn on" in command:
            device = self.extract_device_name(command)
            if device:
                self.publish_mqtt("alicia/commands", json.dumps({
                    "action": "turn_on",
                    "device": device,
                    "type": "light"
                }))
                return f"Turning on the {device}."
        elif "turn off" in command:
            device = self.extract_device_name(command)
            if device:
                self.publish_mqtt("alicia/commands", json.dumps({
                    "action": "turn_off",
                    "device": device,
                    "type": "light"
                }))
                return f"Turning off the {device}."

        return "I'm not sure which device you want to control."

    def extract_device_name(self, command: str) -> Optional[str]:
        """Extract device name from command"""
        devices = ["light", "lamp", "fan", "heater", "ac", "television", "tv"]
        for device in devices:
            if device in command:
                return device
        return None

    async def synthesize_and_publish(self, text: str):
        """Synthesize speech and publish to MQTT"""
        try:
            audio_data = await self.synthesize_with_piper(text)
            # In a real implementation, you might publish audio data or play it locally
            logger.info(f"Synthesized response: {text}")
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")

    def send_tts_to_sonos(self, text: str, speaker: str = "kitchen"):
        """Send TTS command to Sonos speaker"""
        tts_payload = {
            "speaker": speaker,
            "message": text,
            "language": "en",
            "volume": 30
        }
        self.publish_mqtt(f"alicia/tts/{speaker}", json.dumps(tts_payload))
        logger.info(f"Sent TTS to {speaker} speaker: {text}")

    def publish_mqtt(self, topic: str, payload: str):
        """Publish message to MQTT"""
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload)
            logger.info(f"Published to MQTT: {topic} -> {payload}")

    async def run(self):
        """Main run method"""
        logger.info("Starting Alicia Enhanced Voice Assistant...")

        # Wait for services to be ready
        await self.wait_for_services()

        logger.info("All services ready. Starting HTTP server...")

        # Start FastAPI server
        config = uvicorn.Config(self.app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def wait_for_services(self):
        """Wait for all services to be ready"""
        logger.info("Waiting for Wyoming services to be ready...")

        services = [
            ("Whisper STT", self.whisper_host, self.whisper_port),
            ("Piper TTS", self.piper_host, self.piper_port)
        ]

        for service_name, host, port in services:
            while True:
                try:
                    async with AsyncTcpClient(host, port) as client:
                        logger.info(f"{service_name} is ready!")
                        break
                except:
                    logger.info(f"Waiting for {service_name}...")
                    await asyncio.sleep(5)

def main():
    assistant = AliciaAssistant()
    asyncio.run(assistant.run())

if __name__ == "__main__":
    main()
