"""
Alicia Bus Architecture - Device Manager Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Centralized device management service that handles:
- Generic device control and monitoring
- Device capability abstraction
- Command routing and execution
- Device status aggregation
- Integration with various device types
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


class DeviceManager(BusServiceWrapper):
    """
    Device Manager service for the Alicia bus architecture.

    Provides centralized device management and control:
    - Generic device command routing
    - Device capability abstraction
    - Status monitoring and aggregation
    - Device discovery coordination
    - Command execution and response handling

    Features:
    - Device-agnostic command interface
    - Capability-based command routing
    - Real-time device status monitoring
    - Command queuing and prioritization
    - Error handling and retry logic
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "device_manager"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_devices_2024")
        }

        super().__init__("device_manager", mqtt_config)

        # Device Manager Configuration
        self.command_timeout = int(os.getenv("COMMAND_TIMEOUT", "30"))  # seconds
        self.max_concurrent_commands = int(os.getenv("MAX_CONCURRENT_COMMANDS", "10"))
        self.status_update_interval = int(os.getenv("STATUS_UPDATE_INTERVAL", "60"))  # seconds

        # Device management
        self.managed_devices: Dict[str, Dict[str, Any]] = {}
        self.device_capabilities: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, Dict[str, Any]] = {}
        self.command_queue: asyncio.Queue = asyncio.Queue()

        # Command execution tracking
        self.active_commands: Dict[str, Dict[str, Any]] = {}
        self.command_history: List[Dict[str, Any]] = []

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_device_endpoints()

        # Service capabilities
        self.capabilities = [
            "device_management",
            "command_routing",
            "capability_abstraction",
            "status_monitoring",
            "device_discovery"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._process_command_queue())
        asyncio.create_task(self._monitor_device_status())

        self.logger.info("Device Manager initialized")

    def _setup_device_endpoints(self):
        """Setup FastAPI endpoints for device management."""

        @self.api.app.post("/command")
        async def send_command(request: Dict[str, Any]):
            """Send command to device(s)."""
            try:
                device_ids = request.get("device_ids", [])
                command = request.get("command")
                parameters = request.get("parameters", {})
                priority = request.get("priority", "normal")

                if not device_ids:
                    raise HTTPException(status_code=400, detail="Device IDs are required")
                if not command:
                    raise HTTPException(status_code=400, detail="Command is required")

                # Queue command for execution
                command_id = await self._queue_command(device_ids, command, parameters, priority)

                return {
                    "command_id": command_id,
                    "status": "queued",
                    "device_ids": device_ids,
                    "command": command
                }

            except Exception as e:
                self.logger.error(f"Send command error: {e}")
                raise HTTPException(status_code=500, detail=f"Command failed: {str(e)}")

        @self.api.app.get("/devices")
        async def list_devices():
            """List all managed devices."""
            devices_list = []
            for device_id, device_info in self.managed_devices.items():
                devices_list.append({
                    "device_id": device_id,
                    "device_type": device_info.get("device_type"),
                    "status": device_info.get("status"),
                    "capabilities": list(device_info.get("capabilities", {}).keys()),
                    "last_seen": device_info.get("last_seen"),
                    "metadata": device_info.get("metadata", {})
                })

            return {"devices": devices_list, "count": len(devices_list)}

        @self.api.app.get("/devices/{device_id}")
        async def get_device(device_id: str):
            """Get detailed device information."""
            if device_id not in self.managed_devices:
                raise HTTPException(status_code=404, detail="Device not found")

            device_info = self.managed_devices[device_id]
            return {
                "device_id": device_id,
                "device_type": device_info.get("device_type"),
                "status": device_info.get("status"),
                "capabilities": device_info.get("capabilities"),
                "endpoints": device_info.get("endpoints"),
                "metadata": device_info.get("metadata"),
                "last_seen": device_info.get("last_seen"),
                "last_status": device_info.get("last_status")
            }

        @self.api.app.get("/capabilities")
        async def list_capabilities():
            """List all device capabilities."""
            return {"capabilities": self.device_capabilities}

        @self.api.app.get("/commands/{command_id}")
        async def get_command_status(command_id: str):
            """Get command execution status."""
            if command_id in self.active_commands:
                return self.active_commands[command_id]
            elif command_id in self.pending_commands:
                return self.pending_commands[command_id]
            else:
                # Check command history
                for cmd in self.command_history[-100:]:  # Last 100 commands
                    if cmd.get("command_id") == command_id:
                        return cmd

                raise HTTPException(status_code=404, detail="Command not found")

        @self.api.app.get("/health")
        async def health_check():
            """Device manager health check."""
            return {
                "service": "device_manager",
                "status": "healthy" if self.is_connected else "unhealthy",
                "managed_devices": len(self.managed_devices),
                "active_commands": len(self.active_commands),
                "pending_commands": self.command_queue.qsize(),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to device-related MQTT topics."""
        topics = [
            "alicia/devices/+/command",
            "alicia/devices/+/status",
            "alicia/devices/+/response",
            "alicia/system/discovery/register",
            "alicia/system/discovery/unregister",
            "alicia/system/health/check",
            "capability:+"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to device manager topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/system/discovery/register":
                self._handle_device_registration(message)
            elif topic == "alicia/system/discovery/unregister":
                self._handle_device_unregistration(message)
            elif topic.startswith("alicia/devices/") and topic.endswith("/status"):
                self._handle_device_status(topic, message)
            elif topic.startswith("alicia/devices/") and topic.endswith("/response"):
                self._handle_device_response(topic, message)
            elif topic.startswith("capability:"):
                self._handle_capability_request(topic, message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing device message: {e}")

    def _handle_device_registration(self, message: Dict[str, Any]):
        """Handle device registration."""
        try:
            payload = message.get("payload", {})
            device_id = payload.get("device_id")
            device_type = payload.get("device_type")
            capabilities = payload.get("capabilities", [])
            endpoints = payload.get("endpoints", {})
            metadata = payload.get("metadata", {})

            if device_id:
                # Store device information
                self.managed_devices[device_id] = {
                    "device_id": device_id,
                    "device_type": device_type,
                    "capabilities": {cap["name"]: cap for cap in capabilities},
                    "endpoints": endpoints,
                    "metadata": metadata,
                    "status": "registered",
                    "last_seen": time.time(),
                    "registered_at": time.time()
                }

                # Update capability index
                for capability in capabilities:
                    cap_name = capability["name"]
                    if cap_name not in self.device_capabilities:
                        self.device_capabilities[cap_name] = {}
                    self.device_capabilities[cap_name][device_id] = capability

                self.logger.info(f"Registered device: {device_id} ({device_type})")

        except Exception as e:
            self.logger.error(f"Error handling device registration: {e}")

    def _handle_device_unregistration(self, message: Dict[str, Any]):
        """Handle device unregistration."""
        try:
            payload = message.get("payload", {})
            device_id = payload.get("device_id")

            if device_id and device_id in self.managed_devices:
                device_info = self.managed_devices[device_id]

                # Remove from capability index
                for cap_name in device_info.get("capabilities", {}):
                    if cap_name in self.device_capabilities and device_id in self.device_capabilities[cap_name]:
                        del self.device_capabilities[cap_name][device_id]

                # Remove device
                del self.managed_devices[device_id]

                self.logger.info(f"Unregistered device: {device_id}")

        except Exception as e:
            self.logger.error(f"Error handling device unregistration: {e}")

    def _handle_device_status(self, topic: str, message: Dict[str, Any]):
        """Handle device status updates."""
        try:
            # Extract device ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                device_id = parts[3]

                if device_id in self.managed_devices:
                    payload = message.get("payload", {})
                    self.managed_devices[device_id]["last_status"] = payload
                    self.managed_devices[device_id]["last_seen"] = time.time()
                    self.managed_devices[device_id]["status"] = payload.get("status", "unknown")

        except Exception as e:
            self.logger.error(f"Error handling device status: {e}")

    def _handle_device_response(self, topic: str, message: Dict[str, Any]):
        """Handle device command responses."""
        try:
            # Extract device ID from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                device_id = parts[3]

                payload = message.get("payload", {})
                command_id = payload.get("command_id")

                if command_id and command_id in self.active_commands:
                    # Update command status
                    command_info = self.active_commands[command_id]
                    command_info["status"] = payload.get("status", "completed")
                    command_info["response"] = payload
                    command_info["completed_at"] = time.time()

                    # Move to history
                    self.command_history.append(command_info)
                    del self.active_commands[command_id]

                    # Keep only last 1000 commands in history
                    if len(self.command_history) > 1000:
                        self.command_history = self.command_history[-1000:]

                    self.logger.info(f"Command {command_id} completed for device {device_id}")

        except Exception as e:
            self.logger.error(f"Error handling device response: {e}")

    def _handle_capability_request(self, topic: str, message: Dict[str, Any]):
        """Handle capability-based requests."""
        try:
            # Extract capability from topic
            capability = topic.split(":", 1)[1] if ":" in topic else ""

            if capability in self.device_capabilities:
                # Route to appropriate devices
                payload = message.get("payload", {})
                device_ids = list(self.device_capabilities[capability].keys())

                if device_ids:
                    asyncio.create_task(self._route_capability_command(
                        capability, device_ids, payload
                    ))

        except Exception as e:
            self.logger.error(f"Error handling capability request: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _queue_command(self, device_ids: List[str], command: str,
                           parameters: Dict[str, Any], priority: str) -> str:
        """Queue command for execution."""
        command_id = f"cmd_{uuid.uuid4().hex[:8]}"

        await self.command_queue.put({
            "command_id": command_id,
            "device_ids": device_ids,
            "command": command,
            "parameters": parameters,
            "priority": priority,
            "queued_at": time.time()
        })

        return command_id

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
                await self._execute_command(command_item)

                # Mark task as done
                self.command_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing command queue: {e}")
                await asyncio.sleep(1)

    async def _execute_command(self, command_item: Dict[str, Any]):
        """Execute command on specified devices."""
        try:
            command_id = command_item["command_id"]
            device_ids = command_item["device_ids"]
            command = command_item["command"]
            parameters = command_item["parameters"]

            # Track active command
            self.active_commands[command_id] = {
                "command_id": command_id,
                "device_ids": device_ids,
                "command": command,
                "parameters": parameters,
                "status": "executing",
                "started_at": time.time()
            }

            # Execute on each device
            for device_id in device_ids:
                if device_id in self.managed_devices:
                    await self._send_command_to_device(device_id, command_id, command, parameters)
                else:
                    self.logger.warning(f"Device {device_id} not found for command {command_id}")

            # Set timeout for command completion
            asyncio.create_task(self._set_command_timeout(command_id))

        except Exception as e:
            self.logger.error(f"Error executing command {command_item.get('command_id')}: {e}")

    async def _send_command_to_device(self, device_id: str, command_id: str,
                                    command: str, parameters: Dict[str, Any]):
        """Send command to specific device."""
        try:
            device_info = self.managed_devices[device_id]
            command_topic = device_info.get("endpoints", {}).get("control")

            if command_topic:
                # Send command via MQTT
                command_message = {
                    "message_id": f"{command_id}_{device_id}_{uuid.uuid4().hex[:8]}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": device_id,
                    "message_type": "command",
                    "payload": {
                        "command_id": command_id,
                        "command": command,
                        "parameters": parameters
                    }
                }

                self.publish_message(command_topic, command_message)
                self.logger.info(f"Sent command {command} to device {device_id}")

            else:
                self.logger.error(f"No command endpoint for device {device_id}")

        except Exception as e:
            self.logger.error(f"Error sending command to device {device_id}: {e}")

    async def _route_capability_command(self, capability: str, device_ids: List[str],
                                      payload: Dict[str, Any]):
        """Route capability-based command to devices."""
        try:
            command = payload.get("command", capability)
            parameters = payload.get("parameters", {})
            priority = payload.get("priority", "normal")

            # Queue command for capability
            command_id = await self._queue_command(device_ids, command, parameters, priority)

            self.logger.info(f"Routed capability command {command} to {len(device_ids)} devices")

        except Exception as e:
            self.logger.error(f"Error routing capability command: {e}")

    async def _set_command_timeout(self, command_id: str):
        """Set timeout for command completion."""
        await asyncio.sleep(self.command_timeout)

        if command_id in self.active_commands:
            # Command timed out
            command_info = self.active_commands[command_id]
            command_info["status"] = "timeout"
            command_info["error"] = "Command timeout"
            command_info["completed_at"] = time.time()

            # Move to history
            self.command_history.append(command_info)
            del self.active_commands[command_id]

            self.logger.warning(f"Command {command_id} timed out")

    async def _monitor_device_status(self):
        """Monitor device status periodically."""
        while True:
            try:
                current_time = time.time()

                # Check for offline devices
                for device_id, device_info in self.managed_devices.items():
                    last_seen = device_info.get("last_seen", 0)
                    if current_time - last_seen > 300:  # 5 minutes
                        device_info["status"] = "offline"

                await asyncio.sleep(self.status_update_interval)

            except Exception as e:
                self.logger.error(f"Error monitoring device status: {e}")
                await asyncio.sleep(self.status_update_interval)


def main():
    """Main entry point for Device Manager service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create device manager
    device_manager = DeviceManager()

    # Start API server
    try:
        device_manager.api.run_api(host="0.0.0.0", port=8006)
    except KeyboardInterrupt:
        device_manager.shutdown()


if __name__ == "__main__":
    main()
