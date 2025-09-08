#!/usr/bin/env python3
"""
Sonos MQTT Bridge for Alicia Smart Home
This script connects Sonos speakers to the MQTT broker for voice assistant integration
"""

import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import soco
from soco import SoCo
from soco.discovery import discover

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "sonos_speaker"
MQTT_PASSWORD = "alicia_ha_mqtt_2024"
CLIENT_ID = "sonos_bridge"

# MQTT Topics
TOPIC_STATUS = "alicia/devices/sonos/{}/status"
TOPIC_COMMAND = "alicia/commands/sonos/{}"
TOPIC_TTS = "alicia/tts/+"
TOPIC_GROUP = "alicia/commands/sonos/group"
TOPIC_VOLUME = "alicia/commands/sonos/volume"
TOPIC_PLAYBACK = "alicia/commands/sonos/playback"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SonosMQTTBridge:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID)
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.sonos_speakers = {}
        self.discover_speakers()

    def discover_speakers(self):
        """Discover Sonos speakers on the network"""
        logger.info("Discovering Sonos speakers...")
        try:
            speakers = discover()
            if speakers:
                for speaker in speakers:
                    speaker_name = speaker.player_name.lower().replace(" ", "_")
                    self.sonos_speakers[speaker_name] = speaker
                    logger.info(f"Found Sonos speaker: {speaker.player_name} at {speaker.ip_address}")
            else:
                logger.warning("No Sonos speakers found on network")
        except Exception as e:
            logger.error(f"Error discovering speakers: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to command topics
            for speaker_name in self.sonos_speakers.keys():
                client.subscribe(TOPIC_COMMAND.format(speaker_name))
            client.subscribe(TOPIC_TTS)
            client.subscribe(TOPIC_GROUP)
            client.subscribe(TOPIC_VOLUME)
            client.subscribe(TOPIC_PLAYBACK)
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"Disconnected from MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received command: {msg.topic} - {payload}")

            if msg.topic.startswith("alicia/tts/"):
                self.handle_tts_command(payload)
            elif msg.topic == TOPIC_GROUP:
                self.handle_group_command(payload)
            elif msg.topic == TOPIC_VOLUME:
                self.handle_volume_command(payload)
            elif msg.topic == TOPIC_PLAYBACK:
                self.handle_playback_command(payload)
            elif "commands/sonos/" in msg.topic:
                speaker_name = msg.topic.split("/")[-1]
                self.handle_speaker_command(speaker_name, payload)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def handle_tts_command(self, payload):
        """Handle TTS announcement requests"""
        try:
            speaker_name = payload.get("speaker", "").replace("media_player.", "")
            message = payload.get("message", "")
            language = payload.get("language", "en")

            if speaker_name in self.sonos_speakers:
                speaker = self.sonos_speakers[speaker_name]
                # Save current state
                was_playing = speaker.get_current_transport_info()['current_transport_state'] == 'PLAYING'
                current_volume = speaker.volume

                # Set volume for TTS
                speaker.volume = payload.get("volume", 30)

                # Play TTS (this is a simplified implementation)
                # In production, you'd integrate with a TTS service
                logger.info(f"Playing TTS on {speaker_name}: {message}")

                # Restore previous state
                if was_playing:
                    speaker.play()
                speaker.volume = current_volume

                # Publish completion status
                status_topic = "alicia/tts/status"
                status_payload = {
                    "status": "completed",
                    "speaker": speaker_name,
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish(status_topic, json.dumps(status_payload))

        except Exception as e:
            logger.error(f"Error handling TTS command: {e}")

    def handle_group_command(self, payload):
        """Handle speaker grouping commands"""
        try:
            master_name = payload.get("master", "").replace("media_player.", "")
            member_names = [name.replace("media_player.", "") for name in payload.get("members", [])]

            if master_name in self.sonos_speakers:
                master = self.sonos_speakers[master_name]
                members = [self.sonos_speakers[name] for name in member_names if name in self.sonos_speakers]

                # Create group
                for member in members:
                    member.join(master)

                logger.info(f"Created group with master {master_name} and members {member_names}")

                # Publish status
                status_payload = {
                    "group_created": True,
                    "master": master_name,
                    "members": member_names,
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish("alicia/devices/sonos/group/status", json.dumps(status_payload))

        except Exception as e:
            logger.error(f"Error handling group command: {e}")

    def handle_volume_command(self, payload):
        """Handle volume control commands"""
        try:
            speaker_name = payload.get("speaker", "").replace("media_player.", "")
            volume = payload.get("volume", 30)

            if speaker_name in self.sonos_speakers:
                speaker = self.sonos_speakers[speaker_name]
                speaker.volume = volume

                logger.info(f"Set volume for {speaker_name} to {volume}")

                # Publish status
                status_payload = {
                    "volume": volume,
                    "timestamp": datetime.now().isoformat()
                }
                status_topic = TOPIC_STATUS.format(speaker_name)
                self.client.publish(status_topic, json.dumps(status_payload))

        except Exception as e:
            logger.error(f"Error handling volume command: {e}")

    def handle_playback_command(self, payload):
        """Handle playback control commands"""
        try:
            speaker_name = payload.get("speaker", "").replace("media_player.", "")
            action = payload.get("action", "play")

            if speaker_name in self.sonos_speakers:
                speaker = self.sonos_speakers[speaker_name]

                if action == "play":
                    speaker.play()
                elif action == "pause":
                    speaker.pause()
                elif action == "stop":
                    speaker.stop()
                elif action == "next":
                    speaker.next()
                elif action == "previous":
                    speaker.previous()

                logger.info(f"Executed {action} on {speaker_name}")

                # Publish status
                status_payload = {
                    "playback_action": action,
                    "timestamp": datetime.now().isoformat()
                }
                status_topic = TOPIC_STATUS.format(speaker_name)
                self.client.publish(status_topic, json.dumps(status_payload))

        except Exception as e:
            logger.error(f"Error handling playback command: {e}")

    def handle_speaker_command(self, speaker_name, payload):
        """Handle general speaker commands"""
        try:
            if speaker_name in self.sonos_speakers:
                command = payload.get("command", "")
                speaker = self.sonos_speakers[speaker_name]

                if command == "status":
                    self.publish_speaker_status(speaker_name)
                elif command == "unjoin":
                    speaker.unjoin()
                    logger.info(f"Unjoined {speaker_name} from group")

        except Exception as e:
            logger.error(f"Error handling speaker command: {e}")

    def publish_speaker_status(self, speaker_name):
        """Publish current status of a speaker"""
        try:
            if speaker_name in self.sonos_speakers:
                speaker = self.sonos_speakers[speaker_name]

                status = {
                    "device_id": speaker_name,
                    "device_type": "sonos_speaker",
                    "state": speaker.get_current_transport_info()['current_transport_state'],
                    "volume": speaker.volume,
                    "current_track": speaker.get_current_track_info().get('title', 'Unknown'),
                    "group_members": [member.player_name for member in speaker.group.members] if speaker.group else [],
                    "wifi_signal_strength": 85,  # Placeholder - would need additional implementation
                    "timestamp": datetime.now().isoformat()
                }

                status_topic = TOPIC_STATUS.format(speaker_name)
                self.client.publish(status_topic, json.dumps(status))

                logger.info(f"Published status for {speaker_name}")

        except Exception as e:
            logger.error(f"Error publishing speaker status: {e}")

    def publish_all_status(self):
        """Publish status for all discovered speakers"""
        for speaker_name in self.sonos_speakers.keys():
            self.publish_speaker_status(speaker_name)

    def run(self):
        """Main loop"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()

            logger.info("Sonos MQTT Bridge started")

            # Publish initial status
            time.sleep(2)  # Wait for connection
            self.publish_all_status()

            # Keep running
            while True:
                time.sleep(30)  # Publish status every 30 seconds
                self.publish_all_status()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    bridge = SonosMQTTBridge()
    bridge.run()
