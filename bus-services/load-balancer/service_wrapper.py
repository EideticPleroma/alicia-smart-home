"""
Alicia Bus Architecture - Base Service Wrapper
Python 3.11.7+, Paho MQTT 1.6.1+, FastAPI 0.104.1+

This module provides the base BusServiceWrapper class that all bus services
must extend. It handles MQTT communication, message routing, and common
service functionality.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt
from fastapi import FastAPI


class BusServiceWrapper(ABC):
    """
    Base wrapper class for all bus services.

    This class provides:
    - MQTT client setup and management
    - Message publishing and subscription
    - Health monitoring
    - Service discovery
    - Standardized message format handling
    """

    def __init__(self, service_name: str, mqtt_config: Dict[str, Any]):
        """
        Initialize the bus service wrapper.

        Args:
            service_name: Unique name for this service
            mqtt_config: MQTT configuration dictionary
        """
        self.service_name = service_name
        self.mqtt_config = mqtt_config
        self.mqtt_client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0

        # Setup logging
        self.logger = logging.getLogger(f"bus.{service_name}")
        self.logger.setLevel(logging.INFO)

        # Setup MQTT client
        self._setup_mqtt()

        # Setup FastAPI app if needed
        self.app: Optional[FastAPI] = None
        if hasattr(self, '_setup_api'):
            self._setup_api()

    def _setup_mqtt(self):
        """Setup MQTT client with proper configuration."""
        self.mqtt_client = mqtt.Client(
            client_id=f"{self.service_name}_{uuid.uuid4().hex[:8]}",
            clean_session=True,
            userdata=self
        )

        # Set credentials
        if 'username' in self.mqtt_config and 'password' in self.mqtt_config:
            self.mqtt_client.username_pw_set(
                self.mqtt_config['username'],
                self.mqtt_config['password']
            )

        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_publish = self._on_publish

        # Connect to broker
        broker = self.mqtt_config.get('host', 'alicia_bus_core')
        port = self.mqtt_config.get('port', 1883)

        try:
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            self.logger.info(f"Connected to MQTT broker at {broker}:{port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            self.is_connected = True
            self.logger.info("Connected to MQTT broker")
            self.subscribe_to_topics()
            self._publish_service_online()
        else:
            self.is_connected = False
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        self.is_connected = False
        self.logger.warning(f"Disconnected from MQTT broker: {rc}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            self.message_count += 1
            payload = json.loads(msg.payload.decode('utf-8'))
            self.logger.debug(f"Received message on {msg.topic}: {payload}")

            # Process the message
            self.process_message(msg.topic, payload)

        except json.JSONDecodeError as e:
            self.error_count += 1
            self.logger.error(f"Failed to parse message payload: {e}")
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error processing message: {e}")

    def _on_publish(self, client, userdata, mid):
        """Handle message publish confirmation."""
        self.logger.debug(f"Message published: {mid}")

    def publish_message(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """
        Publish a message to the bus.

        Args:
            topic: MQTT topic to publish to
            payload: Message payload dictionary
            qos: Quality of Service level (0, 1, or 2)
        """
        if not self.is_connected:
            self.logger.warning("Not connected to MQTT broker, cannot publish")
            return

        # Create standardized message format
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "source": self.service_name,
            "destination": "broadcast",  # Default to broadcast
            "message_type": "event",  # Default message type
            "priority": "normal",
            "ttl": 300,  # 5 minutes default TTL
            "payload": payload,
            "routing": {
                "hops": 0,
                "max_hops": 10
            }
        }

        try:
            json_payload = json.dumps(message)
            result = self.mqtt_client.publish(topic, json_payload, qos=qos)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish message: {result.rc}")
            else:
                self.logger.debug(f"Published message to {topic}")
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error publishing message: {e}")

    def subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics. Override in subclasses."""
        # Default subscription - override in subclasses
        self.mqtt_client.subscribe(f"alicia/{self.service_name}/command")
        self.mqtt_client.subscribe("alicia/system/health/check")

    @abstractmethod
    def process_message(self, topic: str, message: Dict[str, Any]):
        """
        Process incoming messages. Must be implemented by subclasses.

        Args:
            topic: MQTT topic the message was received on
            message: Parsed message payload
        """
        pass

    def _publish_service_online(self):
        """Publish service online status."""
        online_message = {
            "service_name": self.service_name,
            "status": "online",
            "timestamp": self.start_time,
            "capabilities": getattr(self, 'capabilities', []),
            "version": getattr(self, 'version', '1.0.0')
        }

        self.publish_message(
            "alicia/system/discovery/register",
            online_message
        )

    def publish_health_status(self):
        """Publish current health status."""
        health_status = {
            "service_name": self.service_name,
            "status": "healthy" if self.is_connected else "unhealthy",
            "uptime": time.time() - self.start_time,
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "timestamp": time.time()
        }

        self.publish_message(
            f"alicia/system/health/{self.service_name}",
            health_status
        )

    def shutdown(self):
        """Gracefully shutdown the service."""
        self.logger.info("Shutting down service...")

        # Publish offline status
        offline_message = {
            "service_name": self.service_name,
            "status": "offline",
            "timestamp": time.time()
        }

        self.publish_message(
            "alicia/system/discovery/unregister",
            offline_message
        )

        # Disconnect from MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        self.logger.info("Service shutdown complete")

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "service_name": self.service_name,
            "status": "healthy" if self.is_connected else "unhealthy",
            "uptime": time.time() - self.start_time,
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "mqtt_connected": self.is_connected,
            "timestamp": time.time()
        }


class BusServiceAPI:
    """
    FastAPI integration for bus services that need HTTP APIs.
    """

    def __init__(self, service_wrapper: BusServiceWrapper):
        self.service = service_wrapper
        self.app = FastAPI(
            title=f"Alicia {service_wrapper.service_name}",
            version="1.0.0"
        )

        # Add health endpoint
        @self.app.get("/health")
        async def health_check():
            return self.service.get_health_status()

        # Add status endpoint
        @self.app.get("/status")
        async def get_status():
            return {
                "service": self.service.service_name,
                "status": "running",
                "health": self.service.get_health_status()
            }

    def run_api(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
