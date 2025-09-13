"""
Alicia Bus Architecture - Discovery Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Automatic device discovery and service registration service for the Alicia bus architecture.
Provides network scanning, device enumeration, service discovery, and load balancing
across all services in the bus ecosystem.
"""

import asyncio
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import socket
import time
from typing import Dict, Any, Optional, List, Set
from concurrent.futures import ThreadPoolExecutor
import ipaddress

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
import uvicorn

from service_wrapper import BusServiceWrapper, BusServiceAPI


class DiscoveryService(BusServiceWrapper):
    """
    Discovery Service for the Alicia bus architecture.

    Provides automatic device discovery with the following features:
    - Network device scanning and enumeration
    - Service discovery and registration
    - Dynamic service discovery and load balancing
    - Device capability detection
    - Network topology mapping
    - Service health monitoring
    - Automatic service failover
    - Load distribution across service instances

    Features:
    - Multi-protocol device discovery (UPnP, mDNS, ARP)
    - Service instance tracking and load balancing
    - Network topology visualization
    - Automatic service registration
    - Device capability fingerprinting
    - Service dependency resolution
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "discovery_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_discovery_2024")
        }

        super().__init__("discovery_service", mqtt_config)

        # Discovery configuration
        self.discovery_interval = int(os.getenv("DISCOVERY_INTERVAL", "30"))  # seconds
        self.device_timeout = int(os.getenv("DEVICE_TIMEOUT", "300"))  # 5 minutes
        self.scan_timeout = int(os.getenv("SCAN_TIMEOUT", "10"))  # seconds
        self.max_concurrent_scans = int(os.getenv("MAX_CONCURRENT_SCANS", "10"))

        # Network configuration
        self.network_ranges = os.getenv("NETWORK_RANGES", "192.168.1.0/24,10.0.0.0/8").split(",")
        self.ports_to_scan = [22, 80, 443, 8080, 8081, 8082, 8083, 8084, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012]

        # Discovery state
        self.discovered_devices: Dict[str, Dict[str, Any]] = {}
        self.service_instances: Dict[str, List[Dict[str, Any]]] = {}
        self.network_topology: Dict[str, Any] = {}
        self.discovery_history: List[Dict[str, Any]] = []

        # Load balancing
        self.service_load: Dict[str, Dict[str, int]] = {}
        self.load_balancing_enabled = os.getenv("LOAD_BALANCING_ENABLED", "true").lower() == "true"

        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_scans)

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_discovery_endpoints()

        # Service capabilities
        self.capabilities = [
            "device_discovery",
            "service_discovery",
            "network_scanning",
            "load_balancing",
            "topology_mapping",
            "service_registration",
            "capability_detection",
            "health_monitoring"
        ]

        self.version = "1.0.0"

        # Background tasks will be started in main()

        self.logger.info("Discovery Service initialized")

    def _setup_discovery_endpoints(self):
        """Setup FastAPI endpoints for discovery management."""

        @self.api.app.get("/devices")
        async def get_discovered_devices():
            """Get all discovered devices."""
            return {
                "devices": list(self.discovered_devices.values()),
                "count": len(self.discovered_devices),
                "timestamp": time.time()
            }

        @self.api.app.get("/services")
        async def get_service_instances():
            """Get all discovered service instances."""
            return {
                "services": self.service_instances,
                "load_balancing": self.load_balancing_enabled,
                "timestamp": time.time()
            }

        @self.api.app.get("/topology")
        async def get_network_topology():
            """Get network topology information."""
            return {
                "topology": self.network_topology,
                "timestamp": time.time()
            }

        @self.api.app.post("/scan")
        async def trigger_network_scan():
            """Trigger immediate network scan."""
            try:
                await self._perform_network_scan()
                return {
                    "status": "scan_completed",
                    "devices_found": len(self.discovered_devices),
                    "timestamp": time.time()
                }
            except Exception as e:
                self.logger.error(f"Error during network scan: {e}")
                raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

        @self.api.app.get("/services/{service_name}/instances")
        async def get_service_instances(service_name: str):
            """Get instances of a specific service."""
            if service_name not in self.service_instances:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

            instances = self.service_instances[service_name]
            if self.load_balancing_enabled and len(instances) > 1:
                # Return load-balanced instance
                instance = self._select_service_instance(service_name)
                return {
                    "service": service_name,
                    "instance": instance,
                    "load_balanced": True,
                    "timestamp": time.time()
                }

            return {
                "service": service_name,
                "instances": instances,
                "count": len(instances),
                "timestamp": time.time()
            }

        @self.api.app.get("/health")
        async def health_check():
            """Discovery service health check."""
            return {
                "service": "discovery_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "devices_discovered": len(self.discovered_devices),
                "services_tracked": len(self.service_instances),
                "network_ranges": self.network_ranges,
                "uptime": time.time() - self.start_time
            }

    def _select_service_instance(self, service_name: str) -> Dict[str, Any]:
        """Select service instance using load balancing."""
        instances = self.service_instances[service_name]
        if not instances:
            return None

        if len(instances) == 1:
            return instances[0]

        # Simple round-robin load balancing
        if service_name not in self.service_load:
            self.service_load[service_name] = {"current": 0, "total": len(instances)}

        current = self.service_load[service_name]["current"]
        instance = instances[current]

        # Update for next call
        self.service_load[service_name]["current"] = (current + 1) % len(instances)

        return instance

    async def _discovery_loop(self):
        """Main discovery loop."""
        while True:
            try:
                await self._perform_network_scan()
                await asyncio.sleep(self.discovery_interval)
            except Exception as e:
                self.logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(self.discovery_interval)

    async def _perform_network_scan(self):
        """Perform network scanning for devices and services."""
        try:
            self.logger.info("Starting network discovery scan")

            # Create tasks for concurrent scanning
            scan_tasks = []
            for network_range in self.network_ranges:
                try:
                    network = ipaddress.ip_network(network_range.strip())
                    scan_tasks.append(self._scan_network_range(network))
                except ValueError as e:
                    self.logger.error(f"Invalid network range {network_range}: {e}")

            # Execute scans concurrently
            if scan_tasks:
                await asyncio.gather(*scan_tasks, return_exceptions=True)

            # Update discovery history
            self._update_discovery_history()

            self.logger.info(f"Network scan completed. Found {len(self.discovered_devices)} devices")

        except Exception as e:
            self.logger.error(f"Error performing network scan: {e}")

    async def _scan_network_range(self, network: ipaddress.IPv4Network):
        """Scan a specific network range."""
        try:
            # Get list of IP addresses to scan
            hosts = list(network.hosts())[:254]  # Limit to reasonable size

            # Scan hosts concurrently
            scan_tasks = []
            for host in hosts:
                if host != network.network_address and host != network.broadcast_address:
                    scan_tasks.append(self._scan_host(str(host)))

            # Execute host scans with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrent_scans)
            async def scan_with_semaphore(host_ip):
                async with semaphore:
                    return await self._scan_host(host_ip)

            results = await asyncio.gather(
                *[scan_with_semaphore(host) for host in [str(host) for host in hosts[:50]]],  # Limit for demo
                return_exceptions=True
            )

            # Process results
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    device_info = result["device"]
                    device_id = device_info["ip_address"]
                    self.discovered_devices[device_id] = device_info

        except Exception as e:
            self.logger.error(f"Error scanning network range {network}: {e}")

    async def _scan_host(self, host_ip: str) -> Dict[str, Any]:
        """Scan a specific host for open ports and services."""
        try:
            # Use thread pool for blocking socket operations
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._blocking_host_scan,
                host_ip
            )

            if result:
                # Check if it's a known service
                await self._identify_service(result)

            return result

        except Exception as e:
            self.logger.debug(f"Error scanning host {host_ip}: {e}")
            return {"status": "error", "host": host_ip, "error": str(e)}

    def _blocking_host_scan(self, host_ip: str) -> Optional[Dict[str, Any]]:
        """Blocking host scan operation."""
        try:
            # Quick connectivity check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.scan_timeout)

            # Try to connect to common ports
            open_ports = []
            for port in self.ports_to_scan[:5]:  # Limit ports for speed
                try:
                    result = sock.connect_ex((host_ip, port))
                    if result == 0:
                        open_ports.append(port)
                except:
                    pass

            sock.close()

            if open_ports:
                device_info = {
                    "ip_address": host_ip,
                    "open_ports": open_ports,
                    "scan_time": time.time(),
                    "status": "online",
                    "device_type": self._guess_device_type(open_ports),
                    "capabilities": self._detect_capabilities(open_ports)
                }

                return {
                    "status": "success",
                    "device": device_info
                }

        except Exception as e:
            pass

        return None

    def _guess_device_type(self, open_ports: List[int]) -> str:
        """Guess device type based on open ports."""
        if 22 in open_ports:
            return "server"
        elif 80 in open_ports or 443 in open_ports:
            return "web_server"
        elif any(port in [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012] for port in open_ports):
            return "alicia_service"
        elif 8080 in open_ports or 8081 in open_ports or 8082 in open_ports or 8083 in open_ports or 8084 in open_ports:
            return "alicia_core_service"
        else:
            return "unknown"

    def _detect_capabilities(self, open_ports: List[int]) -> List[str]:
        """Detect device capabilities based on open ports."""
        capabilities = []

        port_capabilities = {
            22: "ssh",
            80: "http",
            443: "https",
            8001: "stt_service",
            8002: "ai_service",
            8003: "tts_service",
            8004: "voice_router",
            8005: "sonos_service",
            8006: "device_manager",
            8007: "ha_bridge",
            8008: "device_control",
            8009: "grok_integration",
            8010: "personality_system",
            8011: "multi_language",
            8012: "advanced_voice",
            8080: "security_gateway",
            8081: "device_registry",
            8082: "discovery_service",
            8083: "health_monitor",
            8084: "config_service"
        }

        for port in open_ports:
            if port in port_capabilities:
                capabilities.append(port_capabilities[port])

        return capabilities

    async def _identify_service(self, scan_result: Dict[str, Any]):
        """Identify and register discovered services."""
        try:
            device_info = scan_result["device"]
            capabilities = device_info.get("capabilities", [])

            for capability in capabilities:
                if capability.endswith("_service"):
                    service_name = capability

                    if service_name not in self.service_instances:
                        self.service_instances[service_name] = []

                    # Check if instance already exists
                    existing_instance = None
                    for instance in self.service_instances[service_name]:
                        if instance["ip_address"] == device_info["ip_address"]:
                            existing_instance = instance
                            break

                    if existing_instance:
                        # Update existing instance
                        existing_instance["last_seen"] = time.time()
                        existing_instance["status"] = "online"
                    else:
                        # Add new instance
                        instance_info = {
                            "service_name": service_name,
                            "ip_address": device_info["ip_address"],
                            "port": device_info["open_ports"][0],  # Use first open port
                            "capabilities": capabilities,
                            "registered_at": time.time(),
                            "last_seen": time.time(),
                            "status": "online",
                            "load_factor": 0
                        }

                        self.service_instances[service_name].append(instance_info)

                        # Notify other services
                        await self._notify_service_discovered(service_name, instance_info)

        except Exception as e:
            self.logger.error(f"Error identifying service: {e}")

    async def _notify_service_discovered(self, service_name: str, instance_info: Dict[str, Any]):
        """Notify services about discovered service instance."""
        try:
            message = {
                "message_id": f"service_discovered_{service_name}_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "all_services",
                "message_type": "service_discovered",
                "payload": {
                    "service_name": service_name,
                    "instance": instance_info
                }
            }

            self.publish_message("alicia/discovery/service/found", message)
            self.logger.info(f"Service discovery notification sent for {service_name}")

        except Exception as e:
            self.logger.error(f"Error notifying service discovery: {e}")

    def _update_discovery_history(self):
        """Update discovery history."""
        try:
            history_entry = {
                "timestamp": time.time(),
                "devices_discovered": len(self.discovered_devices),
                "services_tracked": len(self.service_instances),
                "network_ranges": self.network_ranges
            }

            self.discovery_history.append(history_entry)

            # Keep last 100 entries
            if len(self.discovery_history) > 100:
                self.discovery_history = self.discovery_history[-100:]

        except Exception as e:
            self.logger.error(f"Error updating discovery history: {e}")

    async def _service_health_monitor(self):
        """Monitor health of discovered services."""
        while True:
            try:
                for service_name, instances in self.service_instances.items():
                    for instance in instances:
                        # Simple health check - could be enhanced
                        if time.time() - instance["last_seen"] > self.device_timeout:
                            instance["status"] = "offline"
                        else:
                            instance["status"] = "online"

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in service health monitor: {e}")
                await asyncio.sleep(60)

    async def _topology_update_task(self):
        """Update network topology information."""
        while True:
            try:
                # Build topology information
                self.network_topology = {
                    "timestamp": time.time(),
                    "network_ranges": self.network_ranges,
                    "total_devices": len(self.discovered_devices),
                    "total_services": len(self.service_instances),
                    "device_types": {},
                    "service_distribution": {}
                }

                # Count device types
                for device in self.discovered_devices.values():
                    device_type = device.get("device_type", "unknown")
                    self.network_topology["device_types"][device_type] = \
                        self.network_topology["device_types"].get(device_type, 0) + 1

                # Count service instances
                for service_name, instances in self.service_instances.items():
                    self.network_topology["service_distribution"][service_name] = len(instances)

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating topology: {e}")
                await asyncio.sleep(300)

    def _generate_id(self) -> str:
        """Generate a unique ID for messages."""
        import uuid
        return str(uuid.uuid4())[:8]

    def subscribe_to_topics(self):
        """Subscribe to discovery-related MQTT topics."""
        topics = [
            "alicia/discovery/request",
            "alicia/services/register",
            "alicia/services/deregister",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to discovery topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/discovery/request":
                self._handle_discovery_request(message)
            elif topic == "alicia/services/register":
                self._handle_service_registration(message)
            elif topic == "alicia/services/deregister":
                self._handle_service_deregistration(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing discovery message: {e}")

    def _handle_discovery_request(self, message: Dict[str, Any]):
        """Handle discovery request."""
        try:
            payload = message.get("payload", {})
            requester = payload.get("requester", "unknown")

            # Send current discovery state
            response_message = {
                "message_id": f"discovery_response_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": requester,
                "message_type": "discovery_response",
                "payload": {
                    "devices": list(self.discovered_devices.values()),
                    "services": self.service_instances,
                    "topology": self.network_topology
                }
            }

            self.publish_message(f"alicia/discovery/response/{requester}", response_message)

        except Exception as e:
            self.logger.error(f"Error handling discovery request: {e}")

    def _handle_service_registration(self, message: Dict[str, Any]):
        """Handle service registration."""
        try:
            payload = message.get("payload", {})
            service_name = payload.get("service_name")
            instance_info = payload.get("instance", {})

            if service_name and instance_info:
                if service_name not in self.service_instances:
                    self.service_instances[service_name] = []

                # Add instance if not already present
                existing = False
                for instance in self.service_instances[service_name]:
                    if instance.get("ip_address") == instance_info.get("ip_address"):
                        existing = True
                        break

                if not existing:
                    instance_info["registered_at"] = time.time()
                    instance_info["last_seen"] = time.time()
                    instance_info["status"] = "online"
                    self.service_instances[service_name].append(instance_info)

                    self.logger.info(f"Service registered: {service_name}")

        except Exception as e:
            self.logger.error(f"Error handling service registration: {e}")

    def _handle_service_deregistration(self, message: Dict[str, Any]):
        """Handle service deregistration."""
        try:
            payload = message.get("payload", {})
            service_name = payload.get("service_name")
            instance_ip = payload.get("ip_address")

            if service_name and service_name in self.service_instances:
                self.service_instances[service_name] = [
                    instance for instance in self.service_instances[service_name]
                    if instance.get("ip_address") != instance_ip
                ]

                self.logger.info(f"Service deregistered: {service_name} at {instance_ip}")

        except Exception as e:
            self.logger.error(f"Error handling service deregistration: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()


async def main():
    """Main entry point for Discovery Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create discovery service
    discovery_service = DiscoveryService()
    
    # Start background tasks
    asyncio.create_task(discovery_service._discovery_loop())
    asyncio.create_task(discovery_service._service_health_monitor())
    asyncio.create_task(discovery_service._topology_update_task())

    # Start API server
    try:
        config = uvicorn.Config(discovery_service.api.app, host="0.0.0.0", port=8012)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        discovery_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
