"""
Alicia Bus Architecture - Device Control Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Generic device control service that handles various IoT devices
and provides unified control interfaces for smart home devices.
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


class DeviceControl(BusServiceWrapper):
    """
    Device Control service for the Alicia bus architecture.

    Provides unified control interfaces for various IoT devices:
    - Generic device command execution
    - Protocol abstraction (HTTP, MQTT, WebSocket, etc.)
    - Device-specific command translation
    - Control session management
    - Device capability validation

    Features:
    - Multi-protocol device communication
    - Device-agnostic command interface
    - Command queuing and prioritization
    - Real-time control feedback
    - Device capability discovery
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "device_control"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_control_2024")
        }

        super().__init__("device_control", mqtt_config)

        # Device Control Configuration
        self.command_timeout = int(os.getenv("COMMAND_TIMEOUT", "30"))  # seconds
        self.max_concurrent_commands = int(os.getenv("MAX_CONCURRENT_COMMANDS", "20"))
        self.control_session_timeout = int(os.getenv("SESSION_TIMEOUT", "300"))  # seconds

        # Device control management
        self.controlled_devices: Dict[str, Dict[str, Any]] = {}
        self.device_protocols: Dict[str, Dict[str, Any]] = {}
        self.control_sessions: Dict[str, Dict[str, Any]] = {}
        self.command_queue: asyncio.Queue = asyncio.Queue()

        # Protocol handlers
        self.protocol_handlers: Dict[str, Any] = {}

        # Setup protocol handlers
        self._setup_protocol_handlers()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_control_endpoints()

        # Service capabilities
        self.capabilities = [
            "device_control",
            "protocol_abstraction",
            "command_execution",
            "session_management",
            "capability_validation"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._process_command_queue())
        asyncio.create_task(self._cleanup_expired_sessions())

        self.logger.info("Device Control initialized")

    def _setup_protocol_handlers(self):
        """Setup protocol handlers for different device types."""
        try:
            # HTTP protocol handler
            import requests
            self.protocol_handlers["http"] = {
                "client": requests.Session(),
                "capabilities": ["get", "post", "put", "delete"]
            }

            # MQTT protocol handler (for device-specific MQTT)
            self.protocol_handlers["mqtt"] = {
                "client": None,  # Will be set up per device
                "capabilities": ["publish", "subscribe"]
            }

            # WebSocket protocol handler
            import websockets
            self.protocol_handlers["websocket"] = {
                "client": None,  # Will be set up per device
                "capabilities": ["send", "receive"]
            }

            self.logger.info("Protocol handlers initialized")

        except ImportError as e:
            self.logger.warning(f"Some protocol libraries not available: {e}")

    def _setup_control_endpoints(self):
        """Setup FastAPI endpoints for device control."""

        @self.api.app.post("/control")
        async def control_device(request: Dict[str, Any]):
            """Control a device."""
            try:
                device_id = request.get("device_id")
                command = request.get("command")
                parameters = request.get("parameters", {})
                protocol = request.get("protocol", "auto")
                priority = request.get("priority", "normal")

                if not device_id or not command:
                    raise HTTPException(status_code=400, detail="Device ID and command are required")

                # Queue control command
                session_id = await self._queue_control_command(
                    device_id, command, parameters, protocol, priority
                )

                return {
                    "session_id": session_id,
                    "status": "queued",
                    "device_id": device_id,
                    "command": command
                }

            except Exception as e:
                self.logger.error(f"Control device error: {e}")
                raise HTTPException(status_code=500, detail=f"Device control failed: {str(e)}")

        @self.api.app.post("/session")
        async def create_session(request: Dict[str, Any]):
            """Create a control session for a device."""
            try:
                device_id = request.get("device_id")
                session_type = request.get("session_type", "control")
                parameters = request.get("parameters", {})

                if not device_id:
                    raise HTTPException(status_code=400, detail="Device ID is required")

                # Create control session
                session_id = await self._create_control_session(device_id, session_type, parameters)

                return {
                    "session_id": session_id,
                    "status": "active",
                    "device_id": device_id,
                    "session_type": session_type
                }

            except Exception as e:
                self.logger.error(f"Create session error: {e}")
                raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

        @self.api.app.get("/devices")
        async def list_controlled_devices():
            """List all controlled devices."""
            devices_list = []
            for device_id, device_info in self.controlled_devices.items():
                devices_list.append({
                    "device_id": device_id,
                    "device_type": device_info.get("device_type"),
                    "protocol": device_info.get("protocol"),
                    "status": device_info.get("status"),
                    "capabilities": list(device_info.get("capabilities", {}).keys()),
                    "last_controlled": device_info.get("last_controlled")
                })

            return {"devices": devices_list, "count": len(devices_list)}

        @self.api.app.get("/sessions")
        async def list_sessions():
            """List all active control sessions."""
            sessions_list = []
            for session_id, session_info in self.control_sessions.items():
                sessions_list.append({
                    "session_id": session_id,
                    "device_id": session_info.get("device_id"),
                    "session_type": session_info.get("session_type"),
                    "status": session_info.get("status"),
                    "created_at": session_info.get("created_at"),
                    "last_activity": session_info.get("last_activity")
                })

            return {"sessions": sessions_list, "count": len(sessions_list)}

        @self.api.app.get("/protocols")
        async def list_protocols():
            """List supported protocols."""
            protocols_list = []
            for protocol_name, protocol_info in self.protocol_handlers.items():
                protocols_list.append({
                    "protocol": protocol_name,
                    "capabilities": protocol_info.get("capabilities", []),
                    "status": "available"
                })

            return {"protocols": protocols_list, "count": len(protocols_list)}

        @self.api.app.get("/health")
        async def health_check():
            """Device control health check."""
            return {
                "service": "device_control",
                "status": "healthy" if self.is_connected else "unhealthy",
                "controlled_devices": len(self.controlled_devices),
                "active_sessions": len(self.control_sessions),
                "queued_commands": self.command_queue.qsize(),
                "supported_protocols": list(self.protocol_handlers.keys()),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to device control MQTT topics."""
        topics = [
            "alicia/devices/+/control",
            "alicia/devices/+/command",
            "alicia/control/session/+",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to device control topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/devices/") and topic.endswith("/control"):
                self._handle_device_control(topic, message)
            elif topic.startswith("alicia/devices/") and topic.endswith("/command"):
                self._handle_device_command(topic, message)
            elif topic.startswith("alicia/control/session/"):
                self._handle_session_message(topic, message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing control message: {e}")

    def _handle_device_control(self, topic: str, message: Dict[str, Any]):
        """Handle device control requests."""
        try:
            # Extract device ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                device_id = parts[3]

                payload = message.get("payload", {})
                command = payload.get("command")
                parameters = payload.get("parameters", {})

                # Queue control command
                asyncio.create_task(self._queue_control_command(
                    device_id, command, parameters
                ))

        except Exception as e:
            self.logger.error(f"Error handling device control: {e}")

    def _handle_device_command(self, topic: str, message: Dict[str, Any]):
        """Handle device command requests."""
        try:
            # Extract device ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                device_id = parts[3]

                payload = message.get("payload", {})
                command = payload.get("command")
                parameters = payload.get("parameters", {})

                # Execute command directly
                asyncio.create_task(self._execute_device_command(
                    device_id, command, parameters
                ))

        except Exception as e:
            self.logger.error(f"Error handling device command: {e}")

    def _handle_session_message(self, topic: str, message: Dict[str, Any]):
        """Handle session-related messages."""
        try:
            # Extract session ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                session_id = parts[3]

                payload = message.get("payload", {})
                action = payload.get("action")

                if action == "close" and session_id in self.control_sessions:
                    # Close session
                    self.control_sessions[session_id]["status"] = "closed"
                    self.control_sessions[session_id]["closed_at"] = time.time()

        except Exception as e:
            self.logger.error(f"Error handling session message: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _queue_control_command(self, device_id: str, command: str,
                                   parameters: Dict[str, Any] = None,
                                   protocol: str = "auto", priority: str = "normal") -> str:
        """Queue control command for execution."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        await self.command_queue.put({
            "session_id": session_id,
            "device_id": device_id,
            "command": command,
            "parameters": parameters or {},
            "protocol": protocol,
            "priority": priority,
            "queued_at": time.time()
        })

        return session_id

    async def _process_command_queue(self):
        """Process command queue."""
        while True:
            try:
                if self.command_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                # Get next command
                command_item = await self.command_queue.get()

                # Execute command
                await self._execute_control_command(command_item)

                # Mark task as done
                self.command_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing command queue: {e}")
                await asyncio.sleep(1)

    async def _execute_control_command(self, command_item: Dict[str, Any]):
        """Execute control command."""
        try:
            session_id = command_item["session_id"]
            device_id = command_item["device_id"]
            command = command_item["command"]
            parameters = command_item["parameters"]
            protocol = command_item["protocol"]

            # Create control session
            self.control_sessions[session_id] = {
                "session_id": session_id,
                "device_id": device_id,
                "session_type": "control",
                "status": "active",
                "created_at": time.time(),
                "last_activity": time.time(),
                "commands_executed": []
            }

            # Execute device command
            await self._execute_device_command(device_id, command, parameters, protocol)

            # Update session
            self.control_sessions[session_id]["last_activity"] = time.time()
            self.control_sessions[session_id]["commands_executed"].append({
                "command": command,
                "parameters": parameters,
                "executed_at": time.time()
            })

        except Exception as e:
            self.logger.error(f"Error executing control command: {e}")

    async def _execute_device_command(self, device_id: str, command: str,
                                    parameters: Dict[str, Any] = None,
                                    protocol: str = "auto"):
        """Execute command on specific device."""
        try:
            parameters = parameters or {}

            # Get device information
            if device_id not in self.controlled_devices:
                # Try to discover device
                await self._discover_device(device_id)

            if device_id not in self.controlled_devices:
                self.logger.error(f"Device {device_id} not found")
                return

            device_info = self.controlled_devices[device_id]

            # Determine protocol
            if protocol == "auto":
                protocol = device_info.get("protocol", "http")

            # Execute command based on protocol
            if protocol == "http":
                await self._execute_http_command(device_id, command, parameters)
            elif protocol == "mqtt":
                await self._execute_mqtt_command(device_id, command, parameters)
            elif protocol == "websocket":
                await self._execute_websocket_command(device_id, command, parameters)
            else:
                self.logger.error(f"Unsupported protocol: {protocol}")

            # Update device last controlled time
            device_info["last_controlled"] = time.time()

        except Exception as e:
            self.logger.error(f"Error executing device command: {e}")

    async def _execute_http_command(self, device_id: str, command: str,
                                  parameters: Dict[str, Any]):
        """Execute HTTP-based command."""
        try:
            device_info = self.controlled_devices[device_id]
            device_config = device_info.get("config", {})

            # Build HTTP request
            method = device_config.get("method", "POST")
            url = device_config.get("base_url", "") + device_config.get("endpoints", {}).get(command, "")
            headers = device_config.get("headers", {})
            data = parameters

            # Execute HTTP request
            response = self.protocol_handlers["http"]["client"].request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )

            self.logger.info(f"HTTP command executed for {device_id}: {method} {url} - {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error executing HTTP command: {e}")

    async def _execute_mqtt_command(self, device_id: str, command: str,
                                  parameters: Dict[str, Any]):
        """Execute MQTT-based command."""
        try:
            device_info = self.controlled_devices[device_id]
            device_config = device_info.get("config", {})

            # Build MQTT message
            topic = device_config.get("topic_template", "").format(device_id=device_id, command=command)
            payload = json.dumps({
                "device_id": device_id,
                "command": command,
                "parameters": parameters,
                "timestamp": time.time()
            })

            # Publish MQTT message
            self.mqtt_client.publish(topic, payload)

            self.logger.info(f"MQTT command executed for {device_id}: {topic}")

        except Exception as e:
            self.logger.error(f"Error executing MQTT command: {e}")

    async def _execute_websocket_command(self, device_id: str, command: str,
                                       parameters: Dict[str, Any]):
        """Execute WebSocket-based command."""
        try:
            device_info = self.controlled_devices[device_id]
            device_config = device_info.get("config", {})

            # Build WebSocket message
            message = {
                "device_id": device_id,
                "command": command,
                "parameters": parameters,
                "timestamp": time.time()
            }

            # Send WebSocket message (simplified - would need actual WebSocket connection)
            self.logger.info(f"WebSocket command prepared for {device_id}: {message}")

        except Exception as e:
            self.logger.error(f"Error executing WebSocket command: {e}")

    async def _discover_device(self, device_id: str):
        """Discover and register a device."""
        try:
            # Query device registry for device information
            discovery_message = {
                "message_id": f"discover_{device_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "device_registry",
                "message_type": "query",
                "payload": {
                    "query_type": "device_info",
                    "device_id": device_id
                }
            }

            self.publish_message("alicia/system/discovery/query", discovery_message)

            # For now, create a basic device entry
            self.controlled_devices[device_id] = {
                "device_id": device_id,
                "device_type": "generic",
                "protocol": "http",
                "status": "discovered",
                "capabilities": {
                    "power_control": {"type": "boolean"},
                    "brightness_control": {"type": "range", "min": 0, "max": 100}
                },
                "config": {
                    "base_url": f"http://{device_id}.local:8080",
                    "endpoints": {
                        "turn_on": "/api/power/on",
                        "turn_off": "/api/power/off",
                        "set_brightness": "/api/brightness"
                    }
                },
                "last_controlled": time.time()
            }

            self.logger.info(f"Discovered device: {device_id}")

        except Exception as e:
            self.logger.error(f"Error discovering device {device_id}: {e}")

    async def _create_control_session(self, device_id: str, session_type: str,
                                    parameters: Dict[str, Any]) -> str:
        """Create a control session for a device."""
        try:
            session_id = f"session_{uuid.uuid4().hex[:8]}"

            self.control_sessions[session_id] = {
                "session_id": session_id,
                "device_id": device_id,
                "session_type": session_type,
                "status": "active",
                "created_at": time.time(),
                "last_activity": time.time(),
                "parameters": parameters,
                "commands_executed": []
            }

            self.logger.info(f"Created control session {session_id} for device {device_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Error creating control session: {e}")
            raise

    async def _cleanup_expired_sessions(self):
        """Cleanup expired control sessions."""
        while True:
            try:
                current_time = time.time()

                # Find expired sessions
                expired_sessions = []
                for session_id, session_info in self.control_sessions.items():
                    last_activity = session_info.get("last_activity", 0)
                    if current_time - last_activity > self.control_session_timeout:
                        expired_sessions.append(session_id)

                # Remove expired sessions
                for session_id in expired_sessions:
                    self.logger.info(f"Cleaning up expired session: {session_id}")
                    del self.control_sessions[session_id]

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error cleaning up sessions: {e}")
                await asyncio.sleep(60)


def main():
    """Main entry point for Device Control service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create device control
    device_control = DeviceControl()

    # Start API server
    try:
        device_control.api.run_api(host="0.0.0.0", port=8008)
    except KeyboardInterrupt:
        device_control.shutdown()


if __name__ == "__main__":
    main()
