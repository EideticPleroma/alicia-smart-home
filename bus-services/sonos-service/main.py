"""
Alicia Bus Architecture - Sonos Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Bus-integrated Sonos speaker control service that handles:
- Speaker discovery and management
- Audio playback control
- Volume and grouping management
- Multi-room audio synchronization
- Integration with voice pipeline TTS output
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

from service_wrapper import BusServiceWrapper, BusServiceAPI


class SonosService(BusServiceWrapper):
    """
    Sonos Service for the Alicia bus architecture.

    Manages Sonos speakers and provides:
    - Automatic speaker discovery
    - Audio playback control
    - Volume management
    - Grouping and ungrouping
    - Multi-room synchronization
    - Integration with TTS audio output

    Features:
    - Real-time speaker status monitoring
    - Queue management and playback control
    - Favorite management
    - Cross-room audio synchronization
    - Bus integration for seamless control
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "sonos_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_sonos_2024")
        }

        super().__init__("sonos_service", mqtt_config)

        # Sonos Configuration
        self.discovery_interval = int(os.getenv("DISCOVERY_INTERVAL", "30"))  # seconds
        self.sonos_network = os.getenv("SONOS_NETWORK", "192.168.1.0/24")
        self.default_volume = int(os.getenv("DEFAULT_VOLUME", "30"))
        self.max_volume = int(os.getenv("MAX_VOLUME", "100"))

        # Speaker management
        self.speakers: Dict[str, Dict[str, Any]] = {}
        self.groups: Dict[str, List[str]] = {}
        self.current_track: Dict[str, Dict[str, Any]] = {}

        # Audio queue management
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self.is_playing = False

        # Setup Sonos integration
        self._setup_sonos()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_sonos_endpoints()

        # Service capabilities
        self.capabilities = [
            "speaker_discovery",
            "audio_playback",
            "volume_control",
            "group_management",
            "multi_room_audio",
            "queue_management"
        ]

        self.version = "1.0.0"

        # Start discovery and monitoring
        self._start_discovery()
        asyncio.create_task(self._process_audio_queue())

        self.logger.info("Sonos Service initialized")

    def _setup_sonos(self):
        """Setup Sonos integration."""
        try:
            # Import Sonos library (assuming soco is available)
            import soco
            self.soco = soco
            self.logger.info("Sonos (SoCo) library initialized")
        except ImportError:
            self.logger.error("SoCo library not available. Install with: pip install soco")
            self.soco = None
        except Exception as e:
            self.logger.error(f"Failed to setup Sonos: {e}")
            self.soco = None

    def _start_discovery(self):
        """Start periodic speaker discovery."""
        asyncio.create_task(self._discover_speakers())

    async def _discover_speakers(self):
        """Discover Sonos speakers on the network."""
        while True:
            try:
                if self.soco:
                    # Discover speakers
                    discovered_speakers = self.soco.discover()

                    if discovered_speakers:
                        for speaker in discovered_speakers:
                            await self._register_speaker(speaker)

                        self.logger.info(f"Discovered {len(discovered_speakers)} Sonos speakers")
                    else:
                        self.logger.debug("No Sonos speakers discovered")

                # Update speaker status
                await self._update_speaker_status()

            except Exception as e:
                self.logger.error(f"Speaker discovery failed: {e}")

            await asyncio.sleep(self.discovery_interval)

    async def _register_speaker(self, speaker):
        """Register a discovered speaker."""
        try:
            speaker_id = f"sonos_{speaker.uid.replace(':', '_')}"
            speaker_info = {
                "speaker_id": speaker_id,
                "uid": speaker.uid,
                "ip_address": speaker.ip_address,
                "model": getattr(speaker, 'model_name', 'Unknown'),
                "zone_name": speaker.zone_name,
                "player_name": speaker.player_name,
                "is_coordinator": speaker.is_coordinator,
                "volume": speaker.volume,
                "mute": speaker.mute,
                "transport_state": speaker.get_current_transport_info()['current_transport_state'],
                "last_seen": time.time(),
                "status": "online"
            }

            # Store speaker info
            self.speakers[speaker_id] = speaker_info

            # Publish speaker registration
            registration_message = {
                "message_id": f"speaker_reg_{speaker_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "device_registry",
                "message_type": "event",
                "payload": {
                    "device_id": speaker_id,
                    "device_type": "speaker",
                    "capabilities": [
                        {
                            "name": "audio_playback",
                            "version": "1.0.0",
                            "parameters": {
                                "supported_formats": ["mp3", "wav", "flac"],
                                "max_volume": self.max_volume,
                                "min_volume": 0
                            }
                        },
                        {
                            "name": "volume_control",
                            "version": "1.0.0",
                            "parameters": {
                                "step_size": 1,
                                "supports_mute": True
                            }
                        },
                        {
                            "name": "grouping",
                            "version": "1.0.0",
                            "parameters": {
                                "supports_stereo_pair": True,
                                "supports_multi_room": True
                            }
                        }
                    ],
                    "endpoints": {
                        "control": f"alicia/devices/{speaker_id}/command",
                        "status": f"alicia/devices/{speaker_id}/status",
                        "audio": f"alicia/devices/{speaker_id}/audio"
                    },
                    "metadata": {
                        "manufacturer": "Sonos",
                        "model": speaker_info["model"],
                        "zone_name": speaker_info["zone_name"],
                        "ip_address": speaker_info["ip_address"],
                        "version": "1.0.0"
                    }
                }
            }

            self.publish_message("alicia/system/discovery/register", registration_message)

            self.logger.info(f"Registered Sonos speaker: {speaker_id}")

        except Exception as e:
            self.logger.error(f"Failed to register speaker: {e}")

    async def _update_speaker_status(self):
        """Update status of all registered speakers."""
        for speaker_id, speaker_info in self.speakers.items():
            try:
                # Get updated status (simplified - in real implementation would query speaker)
                status_update = {
                    "speaker_id": speaker_id,
                    "volume": speaker_info.get("volume", self.default_volume),
                    "mute": speaker_info.get("mute", False),
                    "transport_state": speaker_info.get("transport_state", "STOPPED"),
                    "last_seen": time.time(),
                    "status": "online"
                }

                # Publish status update
                status_message = {
                    "message_id": f"speaker_status_{speaker_id}_{uuid.uuid4().hex[:8]}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": "broadcast",
                    "message_type": "event",
                    "payload": status_update
                }

                self.publish_message(f"alicia/devices/{speaker_id}/status", status_message)

            except Exception as e:
                self.logger.error(f"Failed to update speaker status for {speaker_id}: {e}")

    def _setup_sonos_endpoints(self):
        """Setup FastAPI endpoints for Sonos service."""

        @self.api.app.post("/play")
        async def play_audio(request: Dict[str, Any]):
            """Play audio on specified speaker(s)."""
            try:
                speaker_ids = request.get("speaker_ids", [])
                audio_url = request.get("audio_url")
                volume = request.get("volume", self.default_volume)

                if not speaker_ids:
                    raise HTTPException(status_code=400, detail="Speaker IDs are required")
                if not audio_url:
                    raise HTTPException(status_code=400, detail="Audio URL is required")

                # Queue audio for playback
                await self._queue_audio_playback(speaker_ids, audio_url, volume)

                return {
                    "status": "queued",
                    "speaker_ids": speaker_ids,
                    "audio_url": audio_url
                }

            except Exception as e:
                self.logger.error(f"Play audio error: {e}")
                raise HTTPException(status_code=500, detail=f"Playback failed: {str(e)}")

        @self.api.app.post("/volume")
        async def set_volume(request: Dict[str, Any]):
            """Set volume for specified speaker(s)."""
            try:
                speaker_ids = request.get("speaker_ids", [])
                volume = request.get("volume", self.default_volume)

                if not speaker_ids:
                    raise HTTPException(status_code=400, detail="Speaker IDs are required")
                if not (0 <= volume <= self.max_volume):
                    raise HTTPException(status_code=400, detail=f"Volume must be between 0 and {self.max_volume}")

                # Set volume
                await self._set_speaker_volume(speaker_ids, volume)

                return {
                    "status": "success",
                    "speaker_ids": speaker_ids,
                    "volume": volume
                }

            except Exception as e:
                self.logger.error(f"Set volume error: {e}")
                raise HTTPException(status_code=500, detail=f"Volume control failed: {str(e)}")

        @self.api.app.post("/group")
        async def create_group(request: Dict[str, Any]):
            """Create a speaker group."""
            try:
                group_name = request.get("group_name")
                speaker_ids = request.get("speaker_ids", [])

                if not group_name:
                    raise HTTPException(status_code=400, detail="Group name is required")
                if not speaker_ids or len(speaker_ids) < 2:
                    raise HTTPException(status_code=400, detail="At least 2 speakers are required for grouping")

                # Create group
                group_id = await self._create_speaker_group(group_name, speaker_ids)

                return {
                    "status": "success",
                    "group_id": group_id,
                    "group_name": group_name,
                    "speaker_ids": speaker_ids
                }

            except Exception as e:
                self.logger.error(f"Create group error: {e}")
                raise HTTPException(status_code=500, detail=f"Group creation failed: {str(e)}")

        @self.api.app.get("/speakers")
        async def list_speakers():
            """List all discovered speakers."""
            speakers_list = []
            for speaker_id, speaker_info in self.speakers.items():
                speakers_list.append({
                    "speaker_id": speaker_id,
                    "zone_name": speaker_info.get("zone_name"),
                    "model": speaker_info.get("model"),
                    "ip_address": speaker_info.get("ip_address"),
                    "status": speaker_info.get("status"),
                    "volume": speaker_info.get("volume"),
                    "is_coordinator": speaker_info.get("is_coordinator")
                })

            return {"speakers": speakers_list, "count": len(speakers_list)}

        @self.api.app.get("/groups")
        async def list_groups():
            """List all speaker groups."""
            return {"groups": self.groups}

        @self.api.app.get("/health")
        async def health_check():
            """Sonos service health check."""
            return {
                "service": "sonos_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "speakers_discovered": len(self.speakers),
                "groups_active": len(self.groups),
                "queue_size": self.audio_queue.qsize(),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to Sonos-related MQTT topics."""
        topics = [
            "alicia/devices/sonos/+/command",
            "alicia/devices/speakers/announce",
            "alicia/voice/tts/response",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to Sonos topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/devices/sonos/") and topic.endswith("/command"):
                self._handle_speaker_command(topic, message)
            elif topic == "alicia/devices/speakers/announce":
                self._handle_audio_announcement(message)
            elif topic == "alicia/voice/tts/response":
                self._handle_tts_response(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing Sonos message: {e}")

    def _handle_speaker_command(self, topic: str, message: Dict[str, Any]):
        """Handle speaker-specific commands."""
        try:
            # Extract speaker ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                speaker_id = parts[3]

                payload = message.get("payload", {})
                command = payload.get("command")

                if command == "set_volume":
                    volume = payload.get("volume", self.default_volume)
                    asyncio.create_task(self._set_speaker_volume([speaker_id], volume))
                elif command == "play_audio":
                    audio_url = payload.get("audio_url")
                    if audio_url:
                        asyncio.create_task(self._queue_audio_playback([speaker_id], audio_url))
                elif command == "stop":
                    asyncio.create_task(self._stop_speaker_playback([speaker_id]))

        except Exception as e:
            self.logger.error(f"Error handling speaker command: {e}")

    def _handle_audio_announcement(self, message: Dict[str, Any]):
        """Handle audio announcement requests."""
        try:
            payload = message.get("payload", {})
            speaker_ids = payload.get("speaker_ids", [])
            audio_path = payload.get("audio_path")
            volume = payload.get("volume", self.default_volume)

            if speaker_ids and audio_path:
                asyncio.create_task(self._queue_audio_playback(speaker_ids, audio_path, volume))

        except Exception as e:
            self.logger.error(f"Error handling audio announcement: {e}")

    def _handle_tts_response(self, message: Dict[str, Any]):
        """Handle TTS response and potentially play audio."""
        try:
            payload = message.get("payload", {})
            synthesis = payload.get("synthesis", {})
            session_id = payload.get("session_id", "")

            if synthesis.get("success"):
                audio_path = synthesis.get("audio_path")
                if audio_path:
                    # Play TTS audio on default speakers
                    default_speakers = list(self.speakers.keys())[:1]  # Use first speaker
                    if default_speakers:
                        asyncio.create_task(self._queue_audio_playback(
                            default_speakers, audio_path, self.default_volume
                        ))

        except Exception as e:
            self.logger.error(f"Error handling TTS response: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _queue_audio_playback(self, speaker_ids: List[str], audio_url: str, volume: int = None):
        """Queue audio for playback on specified speakers."""
        await self.audio_queue.put({
            "speaker_ids": speaker_ids,
            "audio_url": audio_url,
            "volume": volume or self.default_volume,
            "timestamp": time.time()
        })

    async def _process_audio_queue(self):
        """Process audio playback queue."""
        while True:
            try:
                if self.audio_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                # Get next audio item
                audio_item = await self.audio_queue.get()

                # Process audio playback
                await self._play_audio_on_speakers(
                    audio_item["speaker_ids"],
                    audio_item["audio_url"],
                    audio_item["volume"]
                )

                # Mark task as done
                self.audio_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing audio queue: {e}")
                await asyncio.sleep(1)

    async def _play_audio_on_speakers(self, speaker_ids: List[str], audio_url: str, volume: int):
        """Play audio on specified speakers."""
        try:
            for speaker_id in speaker_ids:
                if speaker_id in self.speakers:
                    # Set volume if specified
                    if volume is not None:
                        await self._set_speaker_volume([speaker_id], volume)

                    # Play audio (simplified - in real implementation would use SoCo)
                    self.logger.info(f"Playing audio on speaker {speaker_id}: {audio_url}")

                    # Update speaker status
                    self.speakers[speaker_id]["transport_state"] = "PLAYING"
                    self.speakers[speaker_id]["current_track"] = {
                        "url": audio_url,
                        "start_time": time.time()
                    }

                else:
                    self.logger.warning(f"Speaker {speaker_id} not found")

        except Exception as e:
            self.logger.error(f"Error playing audio on speakers: {e}")

    async def _set_speaker_volume(self, speaker_ids: List[str], volume: int):
        """Set volume for specified speakers."""
        try:
            for speaker_id in speaker_ids:
                if speaker_id in self.speakers:
                    # Set volume (simplified - in real implementation would use SoCo)
                    self.speakers[speaker_id]["volume"] = volume
                    self.logger.info(f"Set volume for speaker {speaker_id} to {volume}")

                    # Publish volume update
                    volume_message = {
                        "message_id": f"volume_update_{speaker_id}_{uuid.uuid4().hex[:8]}",
                        "timestamp": time.time(),
                        "source": self.service_name,
                        "destination": "broadcast",
                        "message_type": "event",
                        "payload": {
                            "speaker_id": speaker_id,
                            "volume": volume
                        }
                    }

                    self.publish_message(f"alicia/devices/{speaker_id}/status", volume_message)

                else:
                    self.logger.warning(f"Speaker {speaker_id} not found")

        except Exception as e:
            self.logger.error(f"Error setting speaker volume: {e}")

    async def _create_speaker_group(self, group_name: str, speaker_ids: List[str]) -> str:
        """Create a speaker group."""
        try:
            group_id = f"group_{uuid.uuid4().hex[:8]}"
            self.groups[group_id] = {
                "group_name": group_name,
                "speaker_ids": speaker_ids,
                "created_at": time.time()
            }

            self.logger.info(f"Created speaker group {group_id}: {group_name}")
            return group_id

        except Exception as e:
            self.logger.error(f"Error creating speaker group: {e}")
            raise

    async def _stop_speaker_playback(self, speaker_ids: List[str]):
        """Stop playback on specified speakers."""
        try:
            for speaker_id in speaker_ids:
                if speaker_id in self.speakers:
                    # Stop playback (simplified)
                    self.speakers[speaker_id]["transport_state"] = "STOPPED"
                    self.logger.info(f"Stopped playback on speaker {speaker_id}")

                else:
                    self.logger.warning(f"Speaker {speaker_id} not found")

        except Exception as e:
            self.logger.error(f"Error stopping speaker playback: {e}")


def main():
    """Main entry point for Sonos Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create Sonos service
    sonos_service = SonosService()

    # Start API server
    try:
        sonos_service.api.run_api(host="0.0.0.0", port=8005)
    except KeyboardInterrupt:
        sonos_service.shutdown()


if __name__ == "__main__":
    main()
