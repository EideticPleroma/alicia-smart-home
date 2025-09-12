"""
Alicia Bus Architecture - Device Registry Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Centralized device management and registration service for the Alicia bus architecture.
Provides device registration, capability tracking, status monitoring, and real-time
device discovery and updates across all services.
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
import uvicorn

from service_wrapper import BusServiceWrapper, BusServiceAPI


class DeviceRegistry(BusServiceWrapper):
    """
    Device Registry Service for the Alicia bus architecture.

    Provides centralized device management with the following features:
    - Device registration and deregistration
    - Device capability tracking and classification
    - Real-time device status monitoring
    - Device authentication and authorization
    - Device discovery and heartbeat monitoring
    - Device grouping and categorization
    - Device configuration management
    - Device health and performance tracking

    Features:
    - SQLite-based device database
    - Real-time device status updates
    - Device capability-based filtering
    - Automatic device cleanup
    - Device relationship mapping
    - Device configuration synchronization
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "device_registry"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_registry_2024")
        }

        super().__init__("device_registry", mqtt_config)

        # Database configuration
        self.db_path = Path(os.getenv("DATABASE_URL", "sqlite:///./devices.db")).path.replace("sqlite:///", "")
        self.registry_data_path = Path(os.getenv("REGISTRY_DATA_PATH", "/app/data"))

        # Device management
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.device_capabilities: Dict[str, Set[str]] = {}
        self.device_groups: Dict[str, Set[str]] = {}
        self.device_status: Dict[str, Dict[str, Any]] = {}
        self.device_history: List[Dict[str, Any]] = []

        # Configuration
        self.max_devices = int(os.getenv("MAX_DEVICES", "1000"))
        self.device_timeout = int(os.getenv("DEVICE_TIMEOUT", "300"))  # 5 minutes
        self.cleanup_interval = int(os.getenv("CLEANUP_INTERVAL", "60"))  # 1 minute
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))  # 30 seconds

        # Setup database and directories
        self._setup_database()
        self._setup_directories()
        self._load_devices_from_db()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_registry_endpoints()

        # Service capabilities
        self.capabilities = [
            "device_registration",
            "device_management",
            "capability_tracking",
            "status_monitoring",
            "device_discovery",
            "device_authentication",
            "device_grouping",
            "device_configuration"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._device_cleanup_task())
        asyncio.create_task(self._heartbeat_monitor_task())
        asyncio.create_task(self._status_update_task())

        self.logger.info("Device Registry Service initialized")

    def _setup_database(self):
        """Setup SQLite database for device storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create devices table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS devices (
                        device_id TEXT PRIMARY KEY,
                        device_type TEXT NOT NULL,
                        device_name TEXT,
                        capabilities TEXT,  -- JSON array
                        metadata TEXT,      -- JSON object
                        registered_at REAL,
                        last_seen REAL,
                        status TEXT DEFAULT 'offline',
                        ip_address TEXT,
                        mac_address TEXT,
                        firmware_version TEXT,
                        hardware_version TEXT
                    )
                ''')

                # Create device_groups table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS device_groups (
                        group_id TEXT PRIMARY KEY,
                        group_name TEXT,
                        group_type TEXT,
                        devices TEXT,  -- JSON array of device_ids
                        created_at REAL,
                        updated_at REAL
                    )
                ''')

                # Create device_history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS device_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT,
                        action TEXT,
                        details TEXT,  -- JSON object
                        timestamp REAL
                    )
                ''')

                conn.commit()

            self.logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            self.logger.error(f"Error setting up database: {e}")

    def _setup_directories(self):
        """Setup data directories."""
        try:
            self.registry_data_path.mkdir(parents=True, exist_ok=True)
            (self.registry_data_path / "backups").mkdir(exist_ok=True)
            (self.registry_data_path / "exports").mkdir(exist_ok=True)

            self.logger.info(f"Data directories created at {self.registry_data_path}")

        except Exception as e:
            self.logger.error(f"Error setting up directories: {e}")

    def _load_devices_from_db(self):
        """Load devices from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM devices")

                for row in cursor.fetchall():
                    device_id, device_type, device_name, capabilities_str, metadata_str, \
                    registered_at, last_seen, status, ip_address, mac_address, \
                    firmware_version, hardware_version = row

                    # Parse JSON fields
                    capabilities = json.loads(capabilities_str) if capabilities_str else []
                    metadata = json.loads(metadata_str) if metadata_str else {}

                    device_info = {
                        "device_id": device_id,
                        "device_type": device_type,
                        "device_name": device_name,
                        "capabilities": capabilities,
                        "metadata": metadata,
                        "registered_at": registered_at,
                        "last_seen": last_seen,
                        "status": status,
                        "ip_address": ip_address,
                        "mac_address": mac_address,
                        "firmware_version": firmware_version,
                        "hardware_version": hardware_version
                    }

                    self.devices[device_id] = device_info
                    self.device_capabilities[device_id] = set(capabilities)
                    self.device_status[device_id] = {
                        "status": status,
                        "last_seen": last_seen,
                        "ip_address": ip_address
                    }

            self.logger.info(f"Loaded {len(self.devices)} devices from database")

        except Exception as e:
            self.logger.error(f"Error loading devices from database: {e}")

    def _setup_registry_endpoints(self):
        """Setup FastAPI endpoints for device registry management."""

        @self.api.app.post("/devices/register")
        async def register_device(device_data: Dict[str, Any]):
            """Register a new device."""
            try:
                device_id = device_data.get("device_id")
                if not device_id:
                    raise HTTPException(status_code=400, detail="Device ID is required")

                if device_id in self.devices:
                    raise HTTPException(status_code=409, detail=f"Device '{device_id}' already registered")

                if len(self.devices) >= self.max_devices:
                    raise HTTPException(status_code=507, detail="Maximum number of devices reached")

                # Create device record
                device_info = {
                    "device_id": device_id,
                    "device_type": device_data.get("device_type", "unknown"),
                    "device_name": device_data.get("device_name", device_id),
                    "capabilities": device_data.get("capabilities", []),
                    "metadata": device_data.get("metadata", {}),
                    "registered_at": time.time(),
                    "last_seen": time.time(),
                    "status": "online",
                    "ip_address": device_data.get("ip_address"),
                    "mac_address": device_data.get("mac_address"),
                    "firmware_version": device_data.get("firmware_version"),
                    "hardware_version": device_data.get("hardware_version")
                }

                # Save to database
                self._save_device_to_db(device_info)

                # Update in-memory storage
                self.devices[device_id] = device_info
                self.device_capabilities[device_id] = set(device_info["capabilities"])
                self.device_status[device_id] = {
                    "status": "online",
                    "last_seen": time.time(),
                    "ip_address": device_info["ip_address"]
                }

                # Add to history
                self._add_to_history(device_id, "register", device_info)

                # Notify other services
                await self._notify_device_registered(device_id, device_info)

                return {
                    "device_id": device_id,
                    "status": "registered",
                    "registered_at": device_info["registered_at"]
                }

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error registering device: {e}")
                raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

        @self.api.app.post("/devices/{device_id}/heartbeat")
        async def device_heartbeat(device_id: str, heartbeat_data: Dict[str, Any]):
            """Update device heartbeat."""
            try:
                if device_id not in self.devices:
                    raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

                # Update device status
                current_time = time.time()
                self.devices[device_id]["last_seen"] = current_time
                self.devices[device_id]["status"] = "online"
                self.devices[device_id]["ip_address"] = heartbeat_data.get("ip_address")

                # Update status cache
                self.device_status[device_id] = {
                    "status": "online",
                    "last_seen": current_time,
                    "ip_address": heartbeat_data.get("ip_address")
                }

                # Update database
                self._update_device_status(device_id, "online", current_time)

                return {
                    "device_id": device_id,
                    "status": "heartbeat_received",
                    "timestamp": current_time
                }

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error processing heartbeat: {e}")
                raise HTTPException(status_code=500, detail=f"Heartbeat processing failed: {str(e)}")

        @self.api.app.get("/devices")
        async def list_devices(device_type: Optional[str] = None, status: Optional[str] = None):
            """List registered devices."""
            try:
                devices = []

                for device_id, device_info in self.devices.items():
                    # Apply filters
                    if device_type and device_info["device_type"] != device_type:
                        continue
                    if status and device_info["status"] != status:
                        continue

                    devices.append({
                        "device_id": device_id,
                        "device_type": device_info["device_type"],
                        "device_name": device_info["device_name"],
                        "status": device_info["status"],
                        "last_seen": device_info["last_seen"],
                        "capabilities": device_info["capabilities"],
                        "ip_address": device_info["ip_address"]
                    })

                return {
                    "devices": devices,
                    "count": len(devices),
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error listing devices: {e}")
                raise HTTPException(status_code=500, detail=f"Device listing failed: {str(e)}")

        @self.api.app.get("/devices/{device_id}")
        async def get_device(device_id: str):
            """Get device information."""
            try:
                if device_id not in self.devices:
                    raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

                device_info = self.devices[device_id]
                return {
                    "device": device_info,
                    "timestamp": time.time()
                }

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error getting device: {e}")
                raise HTTPException(status_code=500, detail=f"Device retrieval failed: {str(e)}")

        @self.api.app.delete("/devices/{device_id}")
        async def deregister_device(device_id: str):
            """Deregister a device."""
            try:
                if device_id not in self.devices:
                    raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

                # Remove from database
                self._remove_device_from_db(device_id)

                # Remove from memory
                device_info = self.devices.pop(device_id)
                self.device_capabilities.pop(device_id, None)
                self.device_status.pop(device_id, None)

                # Add to history
                self._add_to_history(device_id, "deregister", device_info)

                # Notify other services
                await self._notify_device_deregistered(device_id)

                return {
                    "device_id": device_id,
                    "status": "deregistered",
                    "timestamp": time.time()
                }

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Error deregistering device: {e}")
                raise HTTPException(status_code=500, detail=f"Deregistration failed: {str(e)}")

        @self.api.app.get("/capabilities")
        async def get_capabilities():
            """Get all device capabilities."""
            try:
                all_capabilities = set()
                for capabilities in self.device_capabilities.values():
                    all_capabilities.update(capabilities)

                return {
                    "capabilities": list(all_capabilities),
                    "count": len(all_capabilities),
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error getting capabilities: {e}")
                raise HTTPException(status_code=500, detail=f"Capabilities retrieval failed: {str(e)}")

        @self.api.app.get("/devices/search")
        async def search_devices(capability: Optional[str] = None, device_type: Optional[str] = None):
            """Search devices by capability or type."""
            try:
                matching_devices = []

                for device_id, device_info in self.devices.items():
                    # Check capability filter
                    if capability and capability not in self.device_capabilities.get(device_id, set()):
                        continue

                    # Check device type filter
                    if device_type and device_info["device_type"] != device_type:
                        continue

                    matching_devices.append({
                        "device_id": device_id,
                        "device_type": device_info["device_type"],
                        "device_name": device_info["device_name"],
                        "status": device_info["status"],
                        "capabilities": device_info["capabilities"]
                    })

                return {
                    "devices": matching_devices,
                    "count": len(matching_devices),
                    "filters": {
                        "capability": capability,
                        "device_type": device_type
                    },
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error searching devices: {e}")
                raise HTTPException(status_code=500, detail=f"Device search failed: {str(e)}")

        @self.api.app.get("/health")
        async def health_check():
            """Device registry health check."""
            return {
                "service": "device_registry",
                "status": "healthy" if self.is_connected else "unhealthy",
                "devices_registered": len(self.devices),
                "database_path": self.db_path,
                "uptime": time.time() - self.start_time
            }

    def _save_device_to_db(self, device_info: Dict[str, Any]):
        """Save device to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO devices (
                        device_id, device_type, device_name, capabilities, metadata,
                        registered_at, last_seen, status, ip_address, mac_address,
                        firmware_version, hardware_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_info["device_id"],
                    device_info["device_type"],
                    device_info["device_name"],
                    json.dumps(device_info["capabilities"]),
                    json.dumps(device_info["metadata"]),
                    device_info["registered_at"],
                    device_info["last_seen"],
                    device_info["status"],
                    device_info["ip_address"],
                    device_info["mac_address"],
                    device_info["firmware_version"],
                    device_info["hardware_version"]
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving device to database: {e}")

    def _update_device_status(self, device_id: str, status: str, last_seen: float):
        """Update device status in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE devices
                    SET status = ?, last_seen = ?
                    WHERE device_id = ?
                ''', (status, last_seen, device_id))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error updating device status: {e}")

    def _remove_device_from_db(self, device_id: str):
        """Remove device from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error removing device from database: {e}")

    def _add_to_history(self, device_id: str, action: str, details: Dict[str, Any]):
        """Add device action to history."""
        try:
            history_entry = {
                "device_id": device_id,
                "action": action,
                "details": details,
                "timestamp": time.time()
            }

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO device_history (device_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    device_id,
                    action,
                    json.dumps(details),
                    history_entry["timestamp"]
                ))
                conn.commit()

            # Keep history manageable
            self.device_history.append(history_entry)
            if len(self.device_history) > 1000:  # Keep last 1000 entries
                self.device_history = self.device_history[-1000:]

        except Exception as e:
            self.logger.error(f"Error adding to history: {e}")

    async def _notify_device_registered(self, device_id: str, device_info: Dict[str, Any]):
        """Notify services about device registration."""
        try:
            message = {
                "message_id": f"device_registered_{device_id}_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "all_services",
                "message_type": "device_registered",
                "payload": {
                    "device_id": device_id,
                    "device_info": device_info
                }
            }

            self.publish_message("alicia/devices/registered", message)
            self.logger.info(f"Device registration notification sent for {device_id}")

        except Exception as e:
            self.logger.error(f"Error notifying device registration: {e}")

    async def _notify_device_deregistered(self, device_id: str):
        """Notify services about device deregistration."""
        try:
            message = {
                "message_id": f"device_deregistered_{device_id}_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "all_services",
                "message_type": "device_deregistered",
                "payload": {
                    "device_id": device_id
                }
            }

            self.publish_message("alicia/devices/deregistered", message)
            self.logger.info(f"Device deregistration notification sent for {device_id}")

        except Exception as e:
            self.logger.error(f"Error notifying device deregistration: {e}")

    def _generate_id(self) -> str:
        """Generate a unique ID for messages."""
        import uuid
        return str(uuid.uuid4())[:8]

    async def _device_cleanup_task(self):
        """Clean up offline devices."""
        while True:
            try:
                current_time = time.time()
                offline_devices = []

                for device_id, device_info in self.devices.items():
                    if current_time - device_info["last_seen"] > self.device_timeout:
                        offline_devices.append(device_id)

                # Mark offline devices
                for device_id in offline_devices:
                    self.devices[device_id]["status"] = "offline"
                    self.device_status[device_id]["status"] = "offline"
                    self._update_device_status(device_id, "offline", self.devices[device_id]["last_seen"])

                if offline_devices:
                    self.logger.info(f"Marked {len(offline_devices)} devices as offline")

                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                self.logger.error(f"Error in device cleanup task: {e}")
                await asyncio.sleep(self.cleanup_interval)

    async def _heartbeat_monitor_task(self):
        """Monitor device heartbeats."""
        while True:
            try:
                # Check for devices that haven't sent heartbeat
                current_time = time.time()

                for device_id, status_info in self.device_status.items():
                    if status_info["status"] == "online":
                        if current_time - status_info["last_seen"] > self.heartbeat_interval * 2:
                            # Device missed heartbeat
                            self.logger.warning(f"Device {device_id} missed heartbeat")

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Error in heartbeat monitor task: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _status_update_task(self):
        """Send periodic status updates."""
        while True:
            try:
                # Send status update to monitoring service
                status_summary = {
                    "total_devices": len(self.devices),
                    "online_devices": len([d for d in self.devices.values() if d["status"] == "online"]),
                    "offline_devices": len([d for d in self.devices.values() if d["status"] == "offline"]),
                    "device_types": {}
                }

                # Count device types
                for device_info in self.devices.values():
                    device_type = device_info["device_type"]
                    status_summary["device_types"][device_type] = \
                        status_summary["device_types"].get(device_type, 0) + 1

                message = {
                    "message_id": f"registry_status_{int(time.time())}_{self._generate_id()}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": "health_monitor",
                    "message_type": "registry_status_update",
                    "payload": status_summary
                }

                self.publish_message("alicia/system/registry/status", message)

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                self.logger.error(f"Error in status update task: {e}")
                await asyncio.sleep(60)

    def subscribe_to_topics(self):
        """Subscribe to device-related MQTT topics."""
        topics = [
            "alicia/devices/register",
            "alicia/devices/deregister",
            "alicia/devices/heartbeat",
            "alicia/devices/discovery",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to device registry topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/devices/register":
                self._handle_device_registration(message)
            elif topic == "alicia/devices/deregister":
                self._handle_device_deregistration(message)
            elif topic == "alicia/devices/heartbeat":
                self._handle_device_heartbeat(message)
            elif topic == "alicia/devices/discovery":
                self._handle_device_discovery(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing registry message: {e}")

    def _handle_device_registration(self, message: Dict[str, Any]):
        """Handle device registration via MQTT."""
        try:
            payload = message.get("payload", {})
            device_id = payload.get("device_id")

            if device_id and device_id not in self.devices:
                # Register device
                device_info = {
                    "device_id": device_id,
                    "device_type": payload.get("device_type", "unknown"),
                    "device_name": payload.get("device_name", device_id),
                    "capabilities": payload.get("capabilities", []),
                    "metadata": payload.get("metadata", {}),
                    "registered_at": time.time(),
                    "last_seen": time.time(),
                    "status": "online",
                    "ip_address": payload.get("ip_address"),
                    "mac_address": payload.get("mac_address"),
                    "firmware_version": payload.get("firmware_version"),
                    "hardware_version": payload.get("hardware_version")
                }

                # Save to database and memory
                self._save_device_to_db(device_info)
                self.devices[device_id] = device_info
                self.device_capabilities[device_id] = set(device_info["capabilities"])
                self.device_status[device_id] = {
                    "status": "online",
                    "last_seen": time.time(),
                    "ip_address": device_info["ip_address"]
                }

                self.logger.info(f"Device registered via MQTT: {device_id}")

        except Exception as e:
            self.logger.error(f"Error handling device registration: {e}")

    def _handle_device_deregistration(self, message: Dict[str, Any]):
        """Handle device deregistration via MQTT."""
        try:
            payload = message.get("payload", {})
            device_id = payload.get("device_id")

            if device_id and device_id in self.devices:
                # Remove device
                self._remove_device_from_db(device_id)
                device_info = self.devices.pop(device_id)
                self.device_capabilities.pop(device_id, None)
                self.device_status.pop(device_id, None)

                self.logger.info(f"Device deregistered via MQTT: {device_id}")

        except Exception as e:
            self.logger.error(f"Error handling device deregistration: {e}")

    def _handle_device_heartbeat(self, message: Dict[str, Any]):
        """Handle device heartbeat via MQTT."""
        try:
            payload = message.get("payload", {})
            device_id = payload.get("device_id")

            if device_id and device_id in self.devices:
                current_time = time.time()
                self.devices[device_id]["last_seen"] = current_time
                self.devices[device_id]["status"] = "online"
                self.devices[device_id]["ip_address"] = payload.get("ip_address")

                self.device_status[device_id] = {
                    "status": "online",
                    "last_seen": current_time,
                    "ip_address": payload.get("ip_address")
                }

                self._update_device_status(device_id, "online", current_time)

        except Exception as e:
            self.logger.error(f"Error handling device heartbeat: {e}")

    def _handle_device_discovery(self, message: Dict[str, Any]):
        """Handle device discovery requests."""
        try:
            payload = message.get("payload", {})
            requester = payload.get("requester", "unknown")

            # Send list of all devices
            devices_list = []
            for device_id, device_info in self.devices.items():
                devices_list.append({
                    "device_id": device_id,
                    "device_type": device_info["device_type"],
                    "device_name": device_info["device_name"],
                    "status": device_info["status"],
                    "capabilities": device_info["capabilities"],
                    "ip_address": device_info["ip_address"]
                })

            response_message = {
                "message_id": f"device_discovery_response_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": requester,
                "message_type": "device_discovery_response",
                "payload": {
                    "devices": devices_list,
                    "count": len(devices_list)
                }
            }

            self.publish_message(f"alicia/devices/discovery/{requester}", response_message)

        except Exception as e:
            self.logger.error(f"Error handling device discovery: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()


def main():
    """Main entry point for Device Registry Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create device registry service
    registry_service = DeviceRegistry()

    # Start API server
    try:
        registry_service.api.run_api(host="0.0.0.0", port=8081)
    except KeyboardInterrupt:
        registry_service.shutdown()


if __name__ == "__main__":
    main()
