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
import os
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "sonos_speaker")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")
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
        
        # Configure MQTT client for better stability
        self.client.keepalive = 60
        self.client.clean_session = True
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        self.sonos_speakers = {}
        self.discover_speakers()

    def discover_speakers(self):
        """Discover Sonos speakers on the network"""
        logger.info("Discovering Sonos speakers...")

        # First try automatic discovery
        try:
            speakers = discover()
            if speakers:
                for speaker in speakers:
                    speaker_name = speaker.player_name.lower().replace(" ", "_")
                    self.sonos_speakers[speaker_name] = speaker
                    logger.info(f"Found Sonos speaker: {speaker.player_name} at {speaker.ip_address}")
                return
        except Exception as e:
            logger.error(f"Error in automatic discovery: {e}")

        # Fallback: Manual speaker configuration
        logger.info("Automatic discovery failed, trying manual configuration...")
        manual_speakers = {
            "kitchen": "192.168.1.101",
            "bedroom": "192.168.1.102"
        }

        for name, ip in manual_speakers.items():
            try:
                speaker = SoCo(ip)
                speaker_name = speaker.player_name.lower().replace(" ", "_")
                self.sonos_speakers[speaker_name] = speaker
                logger.info(f"Manually configured Sonos speaker: {speaker.player_name} at {ip}")
            except Exception as e:
                logger.warning(f"Failed to connect to {name} at {ip}: {e}")

        if not self.sonos_speakers:
            logger.error("No Sonos speakers found via automatic or manual discovery")

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            # Subscribe to command topics
            for speaker_name in self.sonos_speakers.keys():
                client.subscribe(TOPIC_COMMAND.format(speaker_name))
                logger.info(f"Subscribed to command topic: {TOPIC_COMMAND.format(speaker_name)}")
            client.subscribe(TOPIC_TTS)
            client.subscribe(TOPIC_GROUP)
            client.subscribe(TOPIC_VOLUME)
            client.subscribe(TOPIC_PLAYBACK)
            logger.info("All MQTT topics subscribed successfully")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            # Log specific error messages
            if rc == 1:
                logger.error("MQTT Connection refused - incorrect protocol version")
            elif rc == 2:
                logger.error("MQTT Connection refused - invalid client identifier")
            elif rc == 3:
                logger.error("MQTT Connection refused - server unavailable")
            elif rc == 4:
                logger.error("MQTT Connection refused - bad username or password")
            elif rc == 5:
                logger.error("MQTT Connection refused - not authorised")
            else:
                logger.error(f"MQTT Connection refused - unknown error code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")
            # Attempt to reconnect
            try:
                client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
        else:
            logger.info("Disconnected from MQTT broker normally")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            logger.info(f"Received MQTT message on topic: {msg.topic}")
            logger.info(f"Message payload: {msg.payload.decode()}")

            payload = json.loads(msg.payload.decode())
            logger.info(f"Parsed payload: {payload}")

            if msg.topic.startswith("alicia/tts/"):
                logger.info(f"TTS message detected for topic: {msg.topic}")
                self.handle_tts_command(payload)
            elif msg.topic == TOPIC_GROUP:
                logger.info(f"Group command detected: {msg.topic}")
                self.handle_group_command(payload)
            elif msg.topic == TOPIC_VOLUME:
                logger.info(f"Volume command detected: {msg.topic}")
                self.handle_volume_command(payload)
            elif msg.topic == TOPIC_PLAYBACK:
                logger.info(f"Playback command detected: {msg.topic}")
                self.handle_playback_command(payload)
            elif "commands/sonos/" in msg.topic:
                speaker_name = msg.topic.split("/")[-1]
                logger.info(f"Speaker command detected for {speaker_name}: {msg.topic}")
                self.handle_speaker_command(speaker_name, payload)
            else:
                logger.warning(f"Unrecognized topic: {msg.topic}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {msg.payload} - Error: {e}")
        except Exception as e:
            logger.error(f"Error processing message on topic {msg.topic}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")

    def handle_tts_command(self, payload):
        """Handle TTS announcement requests with Piper TTS integration"""
        try:
            speaker_name = payload.get("speaker", "").replace("media_player.", "")
            message = payload.get("message", "")
            language = payload.get("language", "en")

            if not message:
                logger.warning("TTS command received with empty message")
                return

            if speaker_name not in self.sonos_speakers:
                logger.error(f"Speaker {speaker_name} not found")
                return

            speaker = self.sonos_speakers[speaker_name]

            # Save current state
            was_playing = speaker.get_current_transport_info()['current_transport_state'] == 'PLAYING'
            current_volume = speaker.volume

            # Set volume for TTS
            tts_volume = payload.get("volume", 30)
            speaker.volume = tts_volume

            logger.info(f"Playing TTS on {speaker_name}: {message}")

            # Try Google TTS first (more reliable), fallback to Piper TTS
            tts_success = self._play_tts_with_google(speaker, message, language)

            if not tts_success:
                logger.info("Google TTS failed, trying Piper TTS fallback")
                tts_success = self._play_tts_with_piper(speaker, message, language)

            if not tts_success:
                logger.error("All TTS methods failed")
                # Publish failure status
                status_topic = "alicia/tts/status"
                status_payload = {
                    "status": "failed",
                    "speaker": speaker_name,
                    "error": "TTS playback failed",
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish(status_topic, json.dumps(status_payload))
                return

            # Wait for TTS to complete properly
            self._wait_for_tts_completion(speaker, message)

            # Restore previous state
            speaker.volume = current_volume
            if was_playing:
                speaker.play()

            # Publish completion status
            status_topic = "alicia/tts/status"
            status_payload = {
                "status": "completed",
                "speaker": speaker_name,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            self.client.publish(status_topic, json.dumps(status_payload))
            logger.info(f"TTS completed on {speaker_name}")

        except Exception as e:
            logger.error(f"Error handling TTS command: {e}")
            # Publish error status
            try:
                status_topic = "alicia/tts/status"
                status_payload = {
                    "status": "error",
                    "speaker": speaker_name if 'speaker_name' in locals() else "unknown",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.client.publish(status_topic, json.dumps(status_payload))
            except:
                pass

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

    def _play_tts_with_piper(self, speaker, message, language="en"):
        """Play TTS using Piper (local TTS engine) with HTTP audio server"""
        import subprocess
        import tempfile
        import os
        import threading
        import shutil

        temp_file_path = None

        try:
            # Check if Piper is installed (try multiple possible locations)
            piper_paths = [
                "/usr/local/bin/piper/piper",  # Docker installation path
                "/usr/local/bin/piper",       # Symlink path
                shutil.which("piper")         # PATH search
            ]

            piper_executable = None
            for path in piper_paths:
                if path and os.path.exists(path) and os.access(path, os.X_OK):
                    piper_executable = path
                    break

            if not piper_executable:
                logger.error("Piper TTS executable not found in any expected location")
                return False

            logger.info(f"Using Piper executable: {piper_executable}")

            # Use shared audio directory that HTTP server can access
            # The HTTP server runs on Windows host, so we need to use the Windows path
            shared_audio_dir = "/tmp/audio"  # This gets mounted to C:\temp\audio on host

            os.makedirs(shared_audio_dir, exist_ok=True)

            # Create unique filename for this TTS request
            import uuid
            audio_filename = f"tts_{uuid.uuid4().hex}.wav"
            temp_file_path = os.path.join(shared_audio_dir, audio_filename)

            logger.info(f"Generating TTS audio file: {temp_file_path}")

            # Piper TTS command with proper model selection
            model_name = self._get_piper_model_for_language(language)
            piper_cmd = [
                piper_executable,
                "--model", f"/usr/local/bin/piper/models/{model_name}.onnx",
                "--output_file", temp_file_path
            ]

            # Run Piper TTS
            process = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send message to Piper
            stdout, stderr = process.communicate(input=message)

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {stderr}")
                return False

            # Validate audio file
            if not self._validate_audio_file(temp_file_path):
                logger.error("Generated audio file is invalid")
                return False

            # Convert to MP3 if needed for better Sonos compatibility
            mp3_path = temp_file_path.replace('.wav', '.mp3')
            if self._convert_to_mp3(temp_file_path, mp3_path):
                # Use MP3 file instead
                os.remove(temp_file_path)
                temp_file_path = mp3_path
                audio_filename = audio_filename.replace('.wav', '.mp3')

            # Generate HTTP URL for the audio file
            host_ip = self._get_local_ip()
            audio_url = f"http://{host_ip}:8080/{audio_filename}"

            logger.info(f"Serving audio at: {audio_url}")

            # Ensure speaker is not in a group before playing
            try:
                if speaker.group and speaker.group.coordinator != speaker:
                    logger.info(f"Ungrouping {speaker.player_name} before TTS playback")
                    speaker.unjoin()
                    time.sleep(1)  # Give time for ungrouping
            except Exception as e:
                logger.warning(f"Could not ungroup speaker: {e}")

            # Play the audio on Sonos
            speaker.play_uri(audio_url)

            # Wait for playback to start and monitor
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                transport_info = speaker.get_current_transport_info()
                if transport_info.get('current_transport_state') == 'PLAYING':
                    logger.info("Piper TTS playback started successfully")
                    return True

            logger.warning("Piper TTS playback did not start within timeout")
            return False

        except Exception as e:
            logger.error(f"Piper TTS error: {e}")
            return False
        finally:
            # Cleanup in separate thread to avoid blocking
            if temp_file_path and os.path.exists(temp_file_path):
                threading.Thread(target=self._cleanup_temp_file, args=(temp_file_path,), daemon=True).start()

    def _play_tts_with_google(self, speaker, message, language="en"):
        """Play TTS using Google Translate (fallback) with HTTPS"""
        try:
            # Ensure speaker is not in a group before playing
            try:
                if speaker.group and speaker.group.coordinator != speaker:
                    logger.info(f"Ungrouping {speaker.player_name} before Google TTS playback")
                    speaker.unjoin()
                    time.sleep(1)  # Give time for ungrouping
            except Exception as e:
                logger.warning(f"Could not ungroup speaker: {e}")

            # Use Google Translate TTS with HTTPS to avoid firewall issues
            from urllib.parse import quote
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={language}&client=tw-ob&q={quote(message)}"

            # Add User-Agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # Test URL accessibility before playing
            import requests
            response = requests.head(tts_url, headers=headers, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Google TTS URL not accessible: {response.status_code}")
                return False

            speaker.play_uri(tts_url)

            # Wait for playback to start and verify
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                try:
                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state')
                    if state == 'PLAYING':
                        logger.info("Google TTS playback started successfully")
                        return True
                    elif state in ['STOPPED', 'PAUSED_PLAYBACK']:
                        logger.warning("Google TTS playback stopped immediately")
                        return False
                except Exception as e:
                    logger.warning(f"Error checking playback state: {e}")
                    
            logger.warning("Google TTS playback did not start within timeout")
            return False

        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return False

    def _wait_for_tts_completion(self, speaker, message):
        """Wait for TTS playback to complete properly"""
        try:
            # Calculate minimum wait time based on message length
            min_wait_time = max(len(message) * 0.05, 2)  # At least 2 seconds, 50ms per character
            logger.info(f"Waiting for TTS completion (min {min_wait_time:.1f}s)")
            
            # Wait for minimum time
            time.sleep(min_wait_time)
            
            # Monitor playback state until it stops
            max_wait = 30  # Maximum 30 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state', 'UNKNOWN')
                    
                    if state in ['STOPPED', 'PAUSED_PLAYBACK']:
                        logger.info(f"TTS playback completed (state: {state})")
                        break
                    elif state == 'PLAYING':
                        # Still playing, continue monitoring
                        time.sleep(1)
                    else:
                        # Unknown state, wait a bit more
                        time.sleep(0.5)
                        
                except Exception as e:
                    logger.warning(f"Error monitoring playback state: {e}")
                    time.sleep(1)
            else:
                logger.warning("TTS playback monitoring timed out")
                
        except Exception as e:
            logger.error(f"Error in TTS completion monitoring: {e}")

    def _get_local_ip(self):
        """Get local IP address that Sonos speakers can reach"""
        # Since we know the host IP is 192.168.1.100 and Sonos speakers are on 192.168.1.x
        # We'll use the host IP directly for better reliability
        host_ip = "192.168.1.100"
        logger.info(f"Using host IP for Sonos access: {host_ip}")
        return host_ip

    def _get_piper_model_for_language(self, language):
        """Get appropriate Piper model for language"""
        # Default models for common languages
        models = {
            "en": "en_US-lessac-medium",
            "en-us": "en_US-lessac-medium",
            "en-gb": "en_GB-alan-medium",
            "es": "es_bES-davefx-medium",
            "fr": "fr_FR-siwis-medium",
            "de": "de_DE-thorsten-medium",
            "it": "it_IT-riccardo-xwatts-medium",
            "pt": "pt_BR-faber-medium",
            "ru": "ru_RU-denis-medium",
            "ja": "ja_JP-takanobu-medium",
            "zh": "zh_CN-huayan-medium"
        }
        return models.get(language.lower(), "en_US-lessac-medium")

    def _validate_audio_file(self, file_path):
        """Validate audio file exists and has content"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Audio file does not exist: {file_path}")
                return False

            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # Less than 1KB is probably invalid
                logger.error(f"Audio file too small: {file_size} bytes")
                return False

            logger.info(f"Audio file validated: {file_path} ({file_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False

    def _convert_to_mp3(self, wav_path, mp3_path):
        """Convert WAV to MP3 for better Sonos compatibility"""
        try:
            from pydub import AudioSegment

            # Load WAV file
            audio = AudioSegment.from_wav(wav_path)

            # Export as MP3
            audio.export(mp3_path, format="mp3", bitrate="128k")

            logger.info(f"Converted {wav_path} to {mp3_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to convert to MP3: {e}")
            return False

    def _wait_for_playback_completion(self, speaker, temp_file_path, app):
        """Wait for playback to complete and cleanup"""
        try:
            import threading

            def monitor_playback():
                try:
                    # Wait for playback to complete
                    while True:
                        time.sleep(2)
                        transport_info = speaker.get_current_transport_info()
                        state = transport_info.get('current_transport_state')

                        if state in ['STOPPED', 'PAUSED_PLAYBACK']:
                            logger.info("Playback completed, cleaning up")
                            break
                        elif state == 'PLAYING':
                            # Still playing, continue monitoring
                            continue
                        else:
                            # Unknown state, wait a bit more
                            time.sleep(1)

                    # Stop Flask app
                    if app:
                        # Flask apps don't have a direct stop method, but we can shutdown the server
                        try:
                            # This is a bit of a hack, but works for our use case
                            import werkzeug.serving
                            werkzeug.serving.shutdown()
                        except:
                            pass

                    # Cleanup temp file
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        logger.info(f"Cleaned up temp file: {temp_file_path}")

                except Exception as e:
                    logger.error(f"Error in playback monitoring: {e}")

            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=monitor_playback, daemon=True)
            monitor_thread.start()

        except Exception as e:
            logger.error(f"Error setting up playback monitoring: {e}")

    def _cleanup_temp_file(self, file_path):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp file {file_path}: {e}")

    def publish_all_status(self):
        """Publish status for all discovered speakers"""
        for speaker_name in self.sonos_speakers.keys():
            self.publish_speaker_status(speaker_name)

    def run(self):
        """Main loop with connection retry logic"""
        max_retries = 5
        retry_delay = 5  # seconds
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} (attempt {retry_count + 1}/{max_retries})")
                self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
                self.client.loop_start()

                logger.info("Sonos MQTT Bridge started successfully")

                # Publish initial status
                time.sleep(3)  # Wait for connection to establish
                self.publish_all_status()

                # Reset retry count on successful connection
                retry_count = 0

                # Keep running
                while True:
                    time.sleep(30)  # Publish status every 30 seconds
                    self.publish_all_status()

            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Error in main loop (attempt {retry_count}/{max_retries}): {e}")

                if retry_count < max_retries:
                    logger.info(f"Retrying connection in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60s
                else:
                    logger.error("Maximum retry attempts reached. Giving up.")
                    break
            finally:
                try:
                    self.client.loop_stop()
                    self.client.disconnect()
                except:
                    pass

        logger.info("Sonos MQTT Bridge stopped")

if __name__ == "__main__":
    bridge = SonosMQTTBridge()
    bridge.run()
