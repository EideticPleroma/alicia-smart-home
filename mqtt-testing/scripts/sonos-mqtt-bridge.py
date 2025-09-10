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
import threading
import http.server
import socketserver
import os
import uuid
import random

# Configuration
import os
MQTT_BROKER = os.getenv("MQTT_BROKER", "alicia_mqtt")  # Use container name instead of localhost
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "sonos_speaker")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")
# Generate unique client ID to prevent conflicts
CLIENT_ID = f"sonos_bridge_{uuid.uuid4().hex[:8]}"

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

# HTTP Server for audio files
class AudioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/tmp/audio", **kwargs)

    def end_headers(self):
        # Add CORS headers for Sonos compatibility
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_audio_server(port=8080):
    """Start the internal HTTP audio server"""
    try:
        os.makedirs("/tmp/audio", exist_ok=True)

        with socketserver.TCPServer(("", port), AudioHTTPRequestHandler) as httpd:
            logger.info(f"Audio server started on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start audio server: {e}")

class SonosMQTTBridge:
    def __init__(self):
        self.client = None
        self.sonos_speakers = {}
        self.connection_retry_count = 0
        self.max_retry_attempts = 5
        self.retry_delay = 1
        self.max_retry_delay = 60
        self.is_connected = False
        self.last_heartbeat = time.time()
        
        self.discover_speakers()

        # Start internal HTTP server in background thread
        self._start_internal_http_server()

        # Setup MQTT client with improved stability
        self.setup_mqtt()

    def setup_mqtt(self):
        """Setup MQTT client with improved stability and connection handling"""
        try:
            logger.info("Setting up MQTT client with improved stability...")

            # Create MQTT client with proper configuration
            self.client = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            self.client.on_connect_fail = self.on_connect_fail
            self.client.on_socket_open = self.on_socket_open
            self.client.on_socket_close = self.on_socket_close
            self.client.on_socket_register_write = self.on_socket_register_write
            self.client.on_socket_unregister_write = self.on_socket_unregister_write

            # Configure MQTT client for better stability
            self.client.keepalive = 120  # Increased keepalive
            self.client.clean_session = False  # Use persistent sessions
            self.client.max_inflight_messages_set(20)  # Limit concurrent messages
            self.client.max_queued_messages_set(100)  # Limit queued messages
            self.client.reconnect_delay_set(min_delay=1, max_delay=120)

            # Connect with retry logic
            self._connect_with_retry()

        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            raise

    def _connect_with_retry(self):
        """Connect to MQTT broker with exponential backoff retry logic"""
        for attempt in range(self.max_retry_attempts):
            try:
                logger.info(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} (attempt {attempt + 1}/{self.max_retry_attempts})")
                self.client.connect(MQTT_BROKER, MQTT_PORT, 120)
                self.client.loop_start()
                logger.info("MQTT client setup complete and connected")
                self.is_connected = True
                self.connection_retry_count = 0
                return
            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker (attempt {attempt + 1}): {e}")
                if attempt < self.max_retry_attempts - 1:
                    # Exponential backoff with jitter
                    delay = min(self.retry_delay * (2 ** attempt) + random.uniform(0, 1), self.max_retry_delay)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Failed to connect to MQTT broker after all attempts")
                    raise

    def _start_internal_http_server(self):
        """Start internal HTTP server in background thread"""
        def start_server():
            try:
                start_audio_server(8080)
            except Exception as e:
                logger.error(f"Failed to start internal HTTP server: {e}")

        # Start HTTP server thread
        http_thread = threading.Thread(target=start_server, daemon=True)
        http_thread.start()
        logger.info("Internal HTTP audio server started on port 8080")

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
            self.is_connected = True
            self.last_heartbeat = time.time()
            
            # Subscribe to command topics with QoS 1 for reliability
            for speaker_name in self.sonos_speakers.keys():
                client.subscribe(TOPIC_COMMAND.format(speaker_name), qos=1)
                logger.info(f"Subscribed to command topic: {TOPIC_COMMAND.format(speaker_name)}")
            # Subscribe to specific TTS command topics, not status topics
            client.subscribe("alicia/tts/kitchen", qos=1)
            client.subscribe("alicia/tts/bedroom", qos=1)
            logger.info(f"🎤 Subscribed to TTS command topics: alicia/tts/kitchen, alicia/tts/bedroom")
            client.subscribe(TOPIC_GROUP, qos=1)
            client.subscribe(TOPIC_VOLUME, qos=1)
            client.subscribe(TOPIC_PLAYBACK, qos=1)
            logger.info("All MQTT topics subscribed successfully")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.is_connected = False
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
        """MQTT disconnection callback with improved error handling"""
        self.is_connected = False
        
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")
            
            # Handle specific error codes
            if rc == 7:  # Connection lost
                logger.warning("Connection lost (code 7), implementing reconnection strategy...")
                self._handle_connection_lost()
            else:
                logger.error(f"Disconnection with error code: {rc}")
                # Attempt immediate reconnection for other errors
                try:
                    client.reconnect()
                except Exception as e:
                    logger.error(f"Failed to reconnect: {e}")
        else:
            logger.info("Disconnected from MQTT broker normally")

    def _handle_connection_lost(self):
        """Handle connection lost (code 7) with exponential backoff"""
        self.connection_retry_count += 1
        
        if self.connection_retry_count <= self.max_retry_attempts:
            # Calculate delay with exponential backoff
            delay = min(self.retry_delay * (2 ** (self.connection_retry_count - 1)) + random.uniform(0, 1), self.max_retry_delay)
            logger.info(f"Attempting reconnection {self.connection_retry_count}/{self.max_retry_attempts} in {delay:.1f} seconds...")
            
            # Schedule reconnection in a separate thread
            def delayed_reconnect():
                time.sleep(delay)
                try:
                    if not self.is_connected:
                        self.client.reconnect()
                except Exception as e:
                    logger.error(f"Reconnection attempt {self.connection_retry_count} failed: {e}")
                    if self.connection_retry_count < self.max_retry_attempts:
                        self._handle_connection_lost()
            
            threading.Thread(target=delayed_reconnect, daemon=True).start()
        else:
            logger.error("Max reconnection attempts reached. Manual intervention required.")

    def on_connect_fail(self, client, userdata):
        """MQTT connection failure callback"""
        logger.error("MQTT connection failed, will retry...")

    def on_socket_open(self, client, userdata, sock):
        """MQTT socket opened callback"""
        logger.debug("MQTT socket opened")

    def on_socket_close(self, client, userdata, sock):
        """MQTT socket closed callback"""
        logger.debug("MQTT socket closed")

    def on_socket_register_write(self, client, userdata, sock):
        """MQTT socket registered for write callback"""
        logger.debug("MQTT socket registered for write")

    def on_socket_unregister_write(self, client, userdata, sock):
        """MQTT socket unregistered for write callback"""
        logger.debug("MQTT socket unregistered for write")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages with improved error handling"""
        try:
            # Update heartbeat on message receipt
            self.last_heartbeat = time.time()
            
            logger.info(f"🔔 RECEIVED MQTT MESSAGE: {msg.topic}")
            logger.info(f"📦 Message payload: {msg.payload.decode()}")
            logger.info(f"📊 Payload length: {len(msg.payload)} bytes")

            payload = json.loads(msg.payload.decode())
            logger.info(f"📋 Parsed payload: {payload}")

            # Only process TTS command topics, not status topics
            if msg.topic in ["alicia/tts/kitchen", "alicia/tts/bedroom"]:
                logger.info(f"🎤 TTS command detected for topic: {msg.topic}")
                self.handle_tts_command(payload)
            elif msg.topic == "alicia/tts/status":
                logger.debug(f"📊 TTS status message received: {msg.topic}")
                # Ignore status messages to prevent feedback loop
            elif msg.topic == TOPIC_GROUP:
                logger.info(f"👥 Group command detected: {msg.topic}")
                self.handle_group_command(payload)
            elif msg.topic == TOPIC_VOLUME:
                logger.info(f"🔊 Volume command detected: {msg.topic}")
                self.handle_volume_command(payload)
            elif msg.topic == TOPIC_PLAYBACK:
                logger.info(f"▶️ Playback command detected: {msg.topic}")
                self.handle_playback_command(payload)
            elif msg.topic.startswith(TOPIC_COMMAND.format("")):
                speaker_name = msg.topic.split("/")[-1]
                logger.info(f"🎵 Speaker command detected for: {speaker_name}")
                self.handle_speaker_command(speaker_name, payload)
            else:
                logger.warning(f"❓ Unrecognized topic: {msg.topic}")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON payload: {msg.payload} - Error: {e}")
        except Exception as e:
            logger.error(f"❌ Error processing message on topic {msg.topic}: {e}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")

    def handle_tts_command(self, payload):
        """Handle TTS announcement requests with Wyoming protocol support"""
        try:
            speaker_name = payload.get("speaker", "").replace("media_player.", "")
            message = payload.get("message", "")
            language = payload.get("language", "en")
            use_wyoming = payload.get("use_wyoming", False)
            audio_url = payload.get("audio_url", "")

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

            tts_success = False

            # Check if this is a Wyoming protocol request with pre-generated audio
            if use_wyoming and audio_url:
                logger.info(f"Using Wyoming protocol with pre-generated audio: {audio_url}")
                tts_success = self._play_tts_with_wyoming_audio(speaker, audio_url, message)
            else:
                # Use Piper TTS first (local, private), fallback to Google TTS
                logger.info("Attempting Piper TTS (primary method)")
                tts_success = self._play_tts_with_piper(speaker, message, language)

                if not tts_success:
                    logger.info("Piper TTS failed, trying Google TTS fallback")
                    tts_success = self._play_tts_with_google(speaker, message, language)

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
                self._publish_with_qos(status_topic, json.dumps(status_payload), qos=1)
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
                "use_wyoming": use_wyoming,
                "timestamp": datetime.now().isoformat()
            }
            self._publish_with_qos(status_topic, json.dumps(status_payload), qos=1)
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
                self._publish_with_qos(status_topic, json.dumps(status_payload), qos=1)
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
                self._publish_with_qos("alicia/devices/sonos/group/status", json.dumps(status_payload), qos=1)

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
                self._publish_with_qos(status_topic, json.dumps(status_payload), qos=1)

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
                self._publish_with_qos(status_topic, json.dumps(status_payload), qos=1)

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
        """Publish current status of a speaker with QoS 1"""
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
                self._publish_with_qos(status_topic, json.dumps(status), qos=1)

                logger.info(f"Published status for {speaker_name}")

        except Exception as e:
            logger.error(f"Error publishing speaker status: {e}")

    def _publish_with_qos(self, topic, payload, qos=1, retain=False):
        """Publish message with QoS and error handling"""
        try:
            if not self.is_connected:
                logger.warning(f"Cannot publish to {topic}: not connected to MQTT broker")
                return False
            
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic} with QoS {qos}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False

    def _play_tts_with_piper(self, speaker, message, language="en"):
        """Play TTS using Piper (local TTS engine) with HTTP audio server and enhanced error handling"""
        import subprocess
        import tempfile
        import os
        import threading
        import shutil

        temp_file_path = None
        cleanup_files = []

        try:
            logger.info(f"🎵 Starting Piper TTS for message: '{message[:50]}...'")

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
                logger.error("❌ Piper TTS executable not found in any expected location")
                logger.error("Expected locations checked:")
                for path in piper_paths:
                    logger.error(f"  - {path}: {'EXISTS' if path and os.path.exists(path) else 'NOT FOUND'}")
                return False

            logger.info(f"✅ Using Piper executable: {piper_executable}")

            # Verify Piper models directory exists
            models_dir = "/usr/local/bin/piper/models"
            if not os.path.exists(models_dir):
                logger.error(f"❌ Piper models directory not found: {models_dir}")
                return False

            # Use shared audio directory that HTTP server can access
            shared_audio_dir = "/tmp/audio"
            os.makedirs(shared_audio_dir, exist_ok=True)

            # Create unique filename for this TTS request
            import uuid
            audio_filename = f"piper_tts_{uuid.uuid4().hex}.wav"
            temp_file_path = os.path.join(shared_audio_dir, audio_filename)
            cleanup_files.append(temp_file_path)

            logger.info(f"📁 Generating TTS audio file: {temp_file_path}")

            # Piper TTS command with proper model selection
            model_name = self._get_piper_model_for_language(language)
            model_path = f"{models_dir}/{model_name}.onnx"

            if not os.path.exists(model_path):
                logger.error(f"❌ Piper model not found: {model_path}")
                logger.error(f"Available models in {models_dir}:")
                try:
                    for file in os.listdir(models_dir):
                        if file.endswith('.onnx'):
                            logger.error(f"  - {file}")
                except Exception as e:
                    logger.error(f"Could not list models directory: {e}")
                return False

            piper_cmd = [
                piper_executable,
                "--model", model_path,
                "--output_file", temp_file_path
            ]

            logger.info(f"🚀 Running Piper command: {' '.join(piper_cmd)}")

            # Run Piper TTS with timeout
            try:
                process = subprocess.Popen(
                    piper_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Send message to Piper with timeout
                stdout, stderr = process.communicate(input=message, timeout=30)

                if process.returncode != 0:
                    logger.error(f"❌ Piper TTS process failed with return code: {process.returncode}")
                    logger.error(f"STDERR: {stderr}")
                    logger.error(f"STDOUT: {stdout}")
                    return False

            except subprocess.TimeoutExpired:
                logger.error("❌ Piper TTS timed out after 30 seconds")
                process.kill()
                return False
            except Exception as e:
                logger.error(f"❌ Error running Piper TTS process: {e}")
                return False

            # Validate audio file
            if not self._validate_audio_file(temp_file_path):
                logger.error("❌ Generated Piper audio file is invalid")
                return False

            logger.info("✅ Piper TTS audio generation successful")

            # Convert to MP3 if needed for better Sonos compatibility
            mp3_path = temp_file_path.replace('.wav', '.mp3')
            cleanup_files.append(mp3_path)

            if self._convert_to_mp3(temp_file_path, mp3_path):
                # Use MP3 file instead
                os.remove(temp_file_path)
                cleanup_files.remove(temp_file_path)
                temp_file_path = mp3_path
                audio_filename = audio_filename.replace('.wav', '.mp3')
                logger.info("✅ Converted WAV to MP3 for better Sonos compatibility")

            # Generate HTTP URL for the audio file
            host_ip = self._get_local_ip()
            audio_url = f"http://{host_ip}:8081/{audio_filename}"

            logger.info(f"🌐 Serving Piper audio at: {audio_url}")

            # Test URL accessibility before playing
            if not self._test_audio_url(audio_url):
                logger.error("❌ Generated audio URL is not accessible")
                return False

            # Ensure speaker is not in a group before playing
            try:
                if speaker.group and speaker.group.coordinator != speaker:
                    logger.info(f"🔄 Ungrouping {speaker.player_name} before Piper TTS playback")
                    speaker.unjoin()
                    time.sleep(1)  # Give time for ungrouping
            except Exception as e:
                logger.warning(f"⚠️ Could not ungroup speaker: {e}")

            # Play the audio on Sonos
            logger.info("▶️ Starting Piper TTS playback on Sonos")
            speaker.play_uri(audio_url)

            # Wait for playback to start and monitor
            max_wait = 15  # Increased timeout for Piper
            playback_started = False

            for i in range(max_wait):
                time.sleep(1)
                try:
                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state')

                    if state == 'PLAYING':
                        logger.info("✅ Piper TTS playback started successfully")
                        playback_started = True
                        break
                    elif state in ['STOPPED', 'PAUSED_PLAYBACK']:
                        logger.warning(f"⚠️ Piper TTS playback stopped immediately (state: {state})")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Error checking Piper playback state: {e}")

            if not playback_started:
                logger.error("❌ Piper TTS playback did not start within timeout")
                return False

            logger.info("🎉 Piper TTS completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Piper TTS error: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        finally:
            # Cleanup in separate thread to avoid blocking
            if cleanup_files:
                threading.Thread(target=self._cleanup_temp_files, args=(cleanup_files,), daemon=True).start()

    def _play_tts_with_wyoming_audio(self, speaker, audio_url, message):
        """Play TTS using pre-generated Wyoming protocol audio"""
        try:
            logger.info(f"Playing Wyoming TTS audio from: {audio_url}")

            # Ensure speaker is not in a group before playing
            try:
                if speaker.group and speaker.group.coordinator != speaker:
                    logger.info(f"Ungrouping {speaker.player_name} before Wyoming TTS playback")
                    speaker.unjoin()
                    time.sleep(1)  # Give time for ungrouping
            except Exception as e:
                logger.warning(f"Could not ungroup speaker: {e}")

            # Test URL accessibility before playing
            import requests
            try:
                response = requests.head(audio_url, timeout=5)
                if response.status_code != 200:
                    logger.warning(f"Wyoming audio URL not accessible: {response.status_code}")
                    return False
            except Exception as e:
                logger.warning(f"Could not access Wyoming audio URL: {e}")
                return False

            # Play the pre-generated audio on Sonos
            speaker.play_uri(audio_url)

            # Wait for playback to start and verify
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                try:
                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state')
                    if state == 'PLAYING':
                        logger.info("Wyoming TTS playback started successfully")
                        return True
                    elif state in ['STOPPED', 'PAUSED_PLAYBACK']:
                        logger.warning("Wyoming TTS playback stopped immediately")
                        return False
                except Exception as e:
                    logger.warning(f"Error checking Wyoming playback state: {e}")

            logger.warning("Wyoming TTS playback did not start within timeout")
            return False

        except Exception as e:
            logger.error(f"Wyoming TTS error: {e}")
            return False

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
        # Use the host machine's IP address that Sonos speakers can reach
        # This should be the actual network IP, not the container's internal IP
        host_ip = "192.168.1.100"  # Host machine IP address
        logger.info(f"Using host IP for HTTP server: {host_ip}:8081")
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

    def _cleanup_temp_files(self, file_paths):
        """Clean up multiple temporary audio files"""
        for file_path in file_paths:
            self._cleanup_temp_file(file_path)

    def _test_audio_url(self, audio_url):
        """Test if audio URL is accessible before playing"""
        try:
            import requests
            response = requests.head(audio_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Audio URL accessible: {audio_url}")
                return True
            else:
                logger.warning(f"⚠️ Audio URL returned status {response.status_code}: {audio_url}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Could not test audio URL {audio_url}: {e}")
            return False

    def publish_all_status(self):
        """Publish status for all discovered speakers"""
        for speaker_name in self.sonos_speakers.keys():
            self.publish_speaker_status(speaker_name)

    def run(self):
        """Main loop with improved connection monitoring and reduced status frequency"""
        try:
            logger.info("Sonos MQTT Bridge started successfully")

            # Publish initial status
            time.sleep(3)  # Wait for connection to establish
            self.publish_all_status()

            # Keep running with improved monitoring
            status_interval = 60  # Reduced from 30 to 60 seconds
            heartbeat_timeout = 300  # 5 minutes without activity
            
            while True:
                time.sleep(10)  # Check every 10 seconds
                
                # Check connection health
                if not self.is_connected:
                    logger.warning("Connection lost, attempting to reconnect...")
                    try:
                        self.client.reconnect()
                    except Exception as e:
                        logger.error(f"Reconnection failed: {e}")
                
                # Check for heartbeat timeout
                if time.time() - self.last_heartbeat > heartbeat_timeout:
                    logger.warning("No activity detected, checking connection...")
                    if not self.is_connected:
                        logger.warning("Connection appears to be lost")
                
                # Publish status updates less frequently
                if int(time.time()) % status_interval == 0:
                    self.publish_all_status()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
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
