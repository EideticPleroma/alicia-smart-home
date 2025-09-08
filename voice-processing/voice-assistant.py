#!/usr/bin/env python3
"""
Alicia Voice Assistant - Phase 3 Integration
Handles voice command processing and MQTT integration
"""

import asyncio
import json
import logging
import paho.mqtt.client as mqtt
import requests
import time
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        self.mqtt_client = None
        self.whisper_url = "http://localhost:9000"
        self.piper_url = "http://localhost:10200"
        self.porcupine_url = "http://localhost:10400"
        self.mqtt_broker = "localhost"
        self.mqtt_port = 1883
        self.mqtt_username = "voice_assistant"
        self.mqtt_password = "alicia_ha_mqtt_2024"

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to voice-related topics
            client.subscribe("alicia/voice/command")
            client.subscribe("alicia/voice/status")
            client.subscribe("homeassistant/sensor/voice/#")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received MQTT message: {msg.topic} -> {payload}")

            if msg.topic == "alicia/voice/command":
                self.process_voice_command(payload)
            elif msg.topic.startswith("homeassistant/sensor/voice/"):
                self.handle_sensor_data(msg.topic, payload)

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def setup_mqtt(self):
        """Setup MQTT client"""
        self.mqtt_client = mqtt.Client("alicia_voice_assistant")
        self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info("MQTT client setup complete")
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")

    def check_service_health(self, service_name: str, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            if service_name == "whisper":
                response = requests.get(f"{url}/docs", timeout=5)
            else:
                response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def wait_for_services(self):
        """Wait for all voice services to be ready"""
        services = [
            ("Whisper STT", self.whisper_url),
            ("Piper TTS", self.piper_url),
            ("Porcupine Wake Word", self.porcupine_url)
        ]

        logger.info("Waiting for voice services to be ready...")
        for service_name, url in services:
            while not self.check_service_health(service_name, url):
                logger.info(f"Waiting for {service_name}...")
                time.sleep(10)
            logger.info(f"{service_name} is ready!")

    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Whisper"""
        try:
            files = {'file': ('audio.wav', audio_data, 'audio/wav')}
            response = requests.post(f"{self.whisper_url}/transcribe", files=files, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '').strip()
            else:
                logger.error(f"Whisper transcription failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """Synthesize speech using Piper"""
        try:
            response = requests.post(f"{self.piper_url}/synthesize", json={"text": text}, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Piper synthesis failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None

    def listen_for_wake_word(self) -> bool:
        """Listen for wake word using Porcupine"""
        try:
            response = requests.get(f"{self.porcupine_url}/listen", timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('wake_word_detected', False)
            else:
                logger.error(f"Porcupine wake word detection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error listening for wake word: {e}")
            return False

    def process_voice_command(self, command: str):
        """Process a voice command"""
        logger.info(f"Processing voice command: {command}")

        # Simple command processing logic
        command = command.lower()

        if "turn on" in command or "turn off" in command:
            self.handle_light_command(command)
        elif "temperature" in command or "temp" in command:
            self.handle_temperature_query(command)
        elif "status" in command:
            self.handle_status_query()
        else:
            self.handle_unknown_command(command)

    def handle_light_command(self, command: str):
        """Handle light control commands"""
        if "turn on" in command:
            device = self.extract_device_name(command)
            if device:
                self.publish_mqtt("alicia/commands", json.dumps({
                    "action": "turn_on",
                    "device": device,
                    "type": "light"
                }))
                self.speak_response(f"Turning on the {device}")
        elif "turn off" in command:
            device = self.extract_device_name(command)
            if device:
                self.publish_mqtt("alicia/commands", json.dumps({
                    "action": "turn_off",
                    "device": device,
                    "type": "light"
                }))
                self.speak_response(f"Turning off the {device}")

    def handle_temperature_query(self, command: str):
        """Handle temperature queries"""
        self.publish_mqtt("alicia/commands", json.dumps({
            "action": "get_temperature",
            "type": "sensor"
        }))

    def handle_status_query(self):
        """Handle status queries"""
        self.publish_mqtt("alicia/commands", json.dumps({
            "action": "get_status",
            "type": "system"
        }))

    def handle_unknown_command(self, command: str):
        """Handle unknown commands"""
        self.speak_response(f"I'm sorry, I didn't understand: {command}")

    def extract_device_name(self, command: str) -> Optional[str]:
        """Extract device name from command"""
        # Simple device name extraction
        devices = ["light", "lamp", "fan", "heater", "ac"]
        for device in devices:
            if device in command:
                return device
        return None

    def speak_response(self, text: str):
        """Speak a response using TTS"""
        audio_data = self.synthesize_speech(text)
        if audio_data:
            # In a real implementation, this would play the audio
            logger.info(f"Speaking: {text}")
            # For now, just publish to MQTT for other systems to handle
            self.publish_mqtt("alicia/voice/response", json.dumps({
                "text": text,
                "audio_available": True
            }))

    def publish_mqtt(self, topic: str, payload: str):
        """Publish message to MQTT"""
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload)
            logger.info(f"Published to MQTT: {topic} -> {payload}")

    def handle_sensor_data(self, topic: str, payload: str):
        """Handle sensor data from MQTT"""
        try:
            data = json.loads(payload)
            logger.info(f"Received sensor data: {topic} -> {data}")

            # Process sensor data and respond if needed
            if "temperature" in topic:
                temp = data.get("value")
                if temp:
                    self.speak_response(f"The current temperature is {temp} degrees")

        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")

    async def run(self):
        """Main run loop"""
        logger.info("Starting Alicia Voice Assistant...")

        # Wait for services to be ready
        self.wait_for_services()

        # Setup MQTT
        self.setup_mqtt()

        logger.info("Voice Assistant is ready!")

        # Main loop
        try:
            while True:
                # Check for wake word
                if self.listen_for_wake_word():
                    logger.info("Wake word detected!")
                    self.speak_response("Yes, I'm listening")

                    # In a real implementation, you would:
                    # 1. Start recording audio
                    # 2. Send to Whisper for transcription
                    # 3. Process the command
                    # 4. Respond via TTS

                    # For now, just wait
                    await asyncio.sleep(1)

                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())
