"""
Alicia Bus Architecture - Home Assistant Bridge Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Home Assistant integration service that bridges HA entities
with the bus architecture. Handles bidirectional communication
between Home Assistant and bus services.
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


class HABridge(BusServiceWrapper):
    """
    Home Assistant Bridge service for the Alicia bus architecture.

    Provides bidirectional integration between Home Assistant and the bus:
    - Discovers and registers HA entities as bus devices
    - Translates HA state changes to bus messages
    - Routes bus commands to HA services
    - Maintains entity state synchronization

    Features:
    - Automatic HA entity discovery
    - Real-time state synchronization
    - Service call translation
    - Event-driven communication
    - Comprehensive entity support
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "ha_bridge"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_ha_2024")
        }

        super().__init__("ha_bridge", mqtt_config)

        # Home Assistant Configuration
        self.ha_url = os.getenv("HA_URL", "http://homeassistant:8123")
        self.ha_token = os.getenv("HA_TOKEN")
        self.discovery_interval = int(os.getenv("DISCOVERY_INTERVAL", "60"))  # seconds
        self.state_update_interval = int(os.getenv("STATE_UPDATE_INTERVAL", "30"))  # seconds

        # HA Integration
        self.ha_entities: Dict[str, Dict[str, Any]] = {}
        self.ha_services: Dict[str, Dict[str, Any]] = {}
        self.entity_states: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, Dict[str, Any]] = {}

        # HTTP client for HA API
        self.ha_session = None

        # Setup HA integration
        self._setup_ha_client()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_ha_endpoints()

        # Service capabilities
        self.capabilities = [
            "home_assistant_integration",
            "entity_discovery",
            "state_synchronization",
            "service_calls",
            "event_handling"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._discover_ha_entities())
        asyncio.create_task(self._sync_entity_states())

        self.logger.info("Home Assistant Bridge initialized")

    def _setup_ha_client(self):
        """Setup Home Assistant API client."""
        try:
            import requests
            self.ha_session = requests.Session()
            if self.ha_token:
                self.ha_session.headers.update({
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                })
            self.logger.info("Home Assistant API client initialized")
        except ImportError:
            self.logger.error("Requests library not available")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup HA client: {e}")
            raise

    def _setup_ha_endpoints(self):
        """Setup FastAPI endpoints for HA integration."""

        @self.api.app.post("/call-service")
        async def call_service(request: Dict[str, Any]):
            """Call Home Assistant service."""
            try:
                domain = request.get("domain")
                service = request.get("service")
                service_data = request.get("service_data", {})
                entity_id = request.get("entity_id")

                if not domain or not service:
                    raise HTTPException(status_code=400, detail="Domain and service are required")

                # Call HA service
                result = await self._call_ha_service(domain, service, service_data, entity_id)

                return result

            except Exception as e:
                self.logger.error(f"Service call error: {e}")
                raise HTTPException(status_code=500, detail=f"Service call failed: {str(e)}")

        @self.api.app.get("/entities")
        async def list_entities():
            """List all HA entities."""
            entities_list = []
            for entity_id, entity_info in self.ha_entities.items():
                entities_list.append({
                    "entity_id": entity_id,
                    "domain": entity_info.get("domain"),
                    "state": self.entity_states.get(entity_id, {}).get("state"),
                    "attributes": self.entity_states.get(entity_id, {}).get("attributes", {}),
                    "last_updated": self.entity_states.get(entity_id, {}).get("last_updated")
                })

            return {"entities": entities_list, "count": len(entities_list)}

        @self.api.app.get("/entities/{entity_id}")
        async def get_entity(entity_id: str):
            """Get detailed entity information."""
            if entity_id not in self.ha_entities:
                raise HTTPException(status_code=404, detail="Entity not found")

            entity_info = self.ha_entities[entity_id]
            state_info = self.entity_states.get(entity_id, {})

            return {
                "entity_id": entity_id,
                "domain": entity_info.get("domain"),
                "state": state_info.get("state"),
                "attributes": state_info.get("attributes", {}),
                "last_updated": state_info.get("last_updated"),
                "metadata": entity_info.get("metadata", {})
            }

        @self.api.app.get("/services")
        async def list_services():
            """List all HA services."""
            return {"services": self.ha_services}

        @self.api.app.get("/states")
        async def get_states():
            """Get all entity states."""
            return {"states": self.entity_states}

        @self.api.app.get("/health")
        async def health_check():
            """HA bridge health check."""
            ha_status = await self._check_ha_connectivity()

            return {
                "service": "ha_bridge",
                "status": "healthy" if self.is_connected else "unhealthy",
                "ha_connected": ha_status,
                "entities_discovered": len(self.ha_entities),
                "services_available": len(self.ha_services),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to HA-related MQTT topics."""
        topics = [
            "alicia/integration/ha/command",
            "alicia/integration/ha/service",
            "alicia/devices/+/command",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to HA bridge topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/integration/ha/command":
                self._handle_ha_command(message)
            elif topic == "alicia/integration/ha/service":
                self._handle_ha_service_call(message)
            elif topic.startswith("alicia/devices/") and topic.endswith("/command"):
                self._handle_device_command(topic, message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing HA message: {e}")

    def _handle_ha_command(self, message: Dict[str, Any]):
        """Handle HA command requests."""
        try:
            payload = message.get("payload", {})
            command = payload.get("command")
            entity_id = payload.get("entity_id")
            parameters = payload.get("parameters", {})

            if command == "get_state":
                # Get entity state
                asyncio.create_task(self._get_entity_state(entity_id))
            elif command == "set_state":
                # Set entity state
                asyncio.create_task(self._set_entity_state(entity_id, parameters))

        except Exception as e:
            self.logger.error(f"Error handling HA command: {e}")

    def _handle_ha_service_call(self, message: Dict[str, Any]):
        """Handle HA service call requests."""
        try:
            payload = message.get("payload", {})
            domain = payload.get("domain")
            service = payload.get("service")
            service_data = payload.get("service_data", {})

            # Call HA service
            asyncio.create_task(self._call_ha_service(domain, service, service_data))

        except Exception as e:
            self.logger.error(f"Error handling HA service call: {e}")

    def _handle_device_command(self, topic: str, message: Dict[str, Any]):
        """Handle device commands that may target HA entities."""
        try:
            # Extract device ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                device_id = parts[3]

                # Check if this is an HA entity
                if device_id in self.ha_entities:
                    payload = message.get("payload", {})
                    command = payload.get("command")
                    parameters = payload.get("parameters", {})

                    # Translate to HA service call
                    asyncio.create_task(self._translate_device_command(device_id, command, parameters))

        except Exception as e:
            self.logger.error(f"Error handling device command: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _discover_ha_entities(self):
        """Discover Home Assistant entities."""
        while True:
            try:
                if self.ha_session:
                    # Get all states
                    response = self.ha_session.get(f"{self.ha_url}/api/states")

                    if response.status_code == 200:
                        states = response.json()

                        for state in states:
                            entity_id = state["entity_id"]
                            domain = entity_id.split(".")[0]

                            # Store entity information
                            self.ha_entities[entity_id] = {
                                "entity_id": entity_id,
                                "domain": domain,
                                "metadata": {
                                    "friendly_name": state.get("attributes", {}).get("friendly_name", entity_id),
                                    "device_class": state.get("attributes", {}).get("device_class"),
                                    "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
                                },
                                "last_discovered": time.time()
                            }

                            # Update state
                            self.entity_states[entity_id] = {
                                "state": state["state"],
                                "attributes": state["attributes"],
                                "last_updated": state["last_updated"],
                                "last_changed": state["last_changed"]
                            }

                            # Register with device registry
                            await self._register_entity_with_bus(entity_id)

                        self.logger.info(f"Discovered {len(states)} HA entities")

                    # Get available services
                    services_response = self.ha_session.get(f"{self.ha_url}/api/services")
                    if services_response.status_code == 200:
                        services = services_response.json()
                        self.ha_services = {f"{s['domain']}.{s['services']}": s for s in services}

            except Exception as e:
                self.logger.error(f"Error discovering HA entities: {e}")

            await asyncio.sleep(self.discovery_interval)

    async def _register_entity_with_bus(self, entity_id: str):
        """Register HA entity with bus device registry."""
        try:
            entity_info = self.ha_entities[entity_id]
            domain = entity_info["domain"]

            # Determine capabilities based on domain
            capabilities = self._get_capabilities_for_domain(domain)

            # Create registration message
            registration_message = {
                "message_id": f"ha_entity_reg_{entity_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "device_registry",
                "message_type": "event",
                "payload": {
                    "device_id": f"ha_{entity_id}",
                    "device_type": domain,
                    "capabilities": capabilities,
                    "endpoints": {
                        "control": f"alicia/devices/ha_{entity_id}/command",
                        "status": f"alicia/devices/ha_{entity_id}/status"
                    },
                    "metadata": {
                        "manufacturer": "Home Assistant",
                        "model": domain,
                        "entity_id": entity_id,
                        "friendly_name": entity_info["metadata"]["friendly_name"],
                        "version": "1.0.0"
                    }
                }
            }

            self.publish_message("alicia/system/discovery/register", registration_message)

        except Exception as e:
            self.logger.error(f"Error registering entity {entity_id}: {e}")

    def _get_capabilities_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get capabilities for HA domain."""
        capabilities_map = {
            "light": [
                {
                    "name": "brightness_control",
                    "version": "1.0.0",
                    "parameters": {"min_value": 0, "max_value": 255}
                },
                {
                    "name": "color_control",
                    "version": "1.0.0",
                    "parameters": {"supports_rgb": True, "supports_temperature": True}
                }
            ],
            "switch": [
                {
                    "name": "power_control",
                    "version": "1.0.0",
                    "parameters": {"supports_toggle": True}
                }
            ],
            "climate": [
                {
                    "name": "temperature_control",
                    "version": "1.0.0",
                    "parameters": {"supports_target_temp": True, "supports_mode": True}
                }
            ],
            "sensor": [
                {
                    "name": "sensor_reading",
                    "version": "1.0.0",
                    "parameters": {"read_only": True}
                }
            ]
        }

        return capabilities_map.get(domain, [
            {
                "name": "generic_control",
                "version": "1.0.0",
                "parameters": {}
            }
        ])

    async def _sync_entity_states(self):
        """Synchronize entity states with HA."""
        while True:
            try:
                for entity_id in self.ha_entities.keys():
                    await self._get_entity_state(entity_id)

                await asyncio.sleep(self.state_update_interval)

            except Exception as e:
                self.logger.error(f"Error syncing entity states: {e}")
                await asyncio.sleep(self.state_update_interval)

    async def _get_entity_state(self, entity_id: str):
        """Get entity state from HA."""
        try:
            if self.ha_session and entity_id in self.ha_entities:
                response = self.ha_session.get(f"{self.ha_url}/api/states/{entity_id}")

                if response.status_code == 200:
                    state_data = response.json()

                    # Update local state
                    self.entity_states[entity_id] = {
                        "state": state_data["state"],
                        "attributes": state_data["attributes"],
                        "last_updated": state_data["last_updated"],
                        "last_changed": state_data["last_changed"]
                    }

                    # Publish state update
                    state_message = {
                        "message_id": f"ha_state_{entity_id}_{uuid.uuid4().hex[:8]}",
                        "timestamp": time.time(),
                        "source": self.service_name,
                        "destination": "broadcast",
                        "message_type": "event",
                        "payload": {
                            "entity_id": entity_id,
                            "state": state_data["state"],
                            "attributes": state_data["attributes"],
                            "last_updated": state_data["last_updated"]
                        }
                    }

                    self.publish_message(f"alicia/devices/ha_{entity_id}/status", state_message)

        except Exception as e:
            self.logger.error(f"Error getting entity state for {entity_id}: {e}")

    async def _set_entity_state(self, entity_id: str, parameters: Dict[str, Any]):
        """Set entity state in HA."""
        try:
            if self.ha_session and entity_id in self.ha_entities:
                # Determine service call based on parameters
                domain = self.ha_entities[entity_id]["domain"]

                if domain == "light":
                    if "brightness" in parameters:
                        service = "turn_on"
                        service_data = {"brightness": parameters["brightness"]}
                    else:
                        service = "turn_on" if parameters.get("state") == "on" else "turn_off"
                        service_data = {}
                elif domain == "switch":
                    service = "turn_on" if parameters.get("state") == "on" else "turn_off"
                    service_data = {}
                else:
                    # Generic service call
                    service = parameters.get("service", "turn_on")
                    service_data = parameters.get("service_data", {})

                await self._call_ha_service(domain, service, service_data, entity_id)

        except Exception as e:
            self.logger.error(f"Error setting entity state for {entity_id}: {e}")

    async def _call_ha_service(self, domain: str, service: str,
                              service_data: Dict[str, Any] = None,
                              entity_id: str = None) -> Dict[str, Any]:
        """Call Home Assistant service."""
        try:
            if not self.ha_session:
                raise Exception("HA session not available")

            # Prepare service data
            data = service_data or {}
            if entity_id:
                data["entity_id"] = entity_id

            # Call service
            response = self.ha_session.post(
                f"{self.ha_url}/api/services/{domain}/{service}",
                json=data
            )

            if response.status_code == 200:
                result = {
                    "success": True,
                    "domain": domain,
                    "service": service,
                    "entity_id": entity_id,
                    "response": response.json() if response.text else None
                }

                self.logger.info(f"Called HA service {domain}.{service} for {entity_id}")
                return result
            else:
                error_msg = f"HA service call failed: {response.status_code}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "domain": domain,
                    "service": service
                }

        except Exception as e:
            self.logger.error(f"Error calling HA service {domain}.{service}: {e}")
            return {
                "success": False,
                "error": str(e),
                "domain": domain,
                "service": service
            }

    async def _translate_device_command(self, device_id: str, command: str,
                                      parameters: Dict[str, Any]):
        """Translate device command to HA service call."""
        try:
            # Extract HA entity ID
            if device_id.startswith("ha_"):
                entity_id = device_id[3:]  # Remove "ha_" prefix
            else:
                entity_id = device_id

            if entity_id in self.ha_entities:
                entity_info = self.ha_entities[entity_id]
                domain = entity_info["domain"]

                # Translate command based on domain and command
                if domain == "light":
                    if command == "set_brightness":
                        await self._call_ha_service("light", "turn_on",
                                                  {"brightness": parameters.get("brightness", 255)},
                                                  entity_id)
                    elif command == "turn_on":
                        await self._call_ha_service("light", "turn_on", {}, entity_id)
                    elif command == "turn_off":
                        await self._call_ha_service("light", "turn_off", {}, entity_id)

                elif domain == "switch":
                    if command in ["turn_on", "turn_off"]:
                        await self._call_ha_service("switch", command, {}, entity_id)

                # Add more domain translations as needed

        except Exception as e:
            self.logger.error(f"Error translating device command: {e}")

    async def _check_ha_connectivity(self) -> bool:
        """Check Home Assistant connectivity."""
        try:
            if self.ha_session:
                response = self.ha_session.get(f"{self.ha_url}/api/")
                return response.status_code == 200
            return False
        except Exception:
            return False


def main():
    """Main entry point for Home Assistant Bridge service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create HA bridge
    ha_bridge = HABridge()

    # Start API server
    try:
        ha_bridge.api.run_api(host="0.0.0.0", port=8007)
    except KeyboardInterrupt:
        ha_bridge.shutdown()


if __name__ == "__main__":
    main()
