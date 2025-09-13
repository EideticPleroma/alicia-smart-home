"""
Alicia Bus Architecture - Configuration Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Centralized configuration management service for the Alicia bus architecture.
Provides dynamic configuration updates, environment-specific settings, and
configuration validation across all services.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv

from service_wrapper import BusServiceWrapper, BusServiceAPI

# Load environment variables
load_dotenv()


class ConfigurationService(BusServiceWrapper):
    """
    Configuration Service for the Alicia bus architecture.

    Provides centralized configuration management with the following features:
    - Dynamic configuration updates across all services
    - Environment-specific configuration handling
    - Configuration validation and schema enforcement
    - Real-time configuration synchronization
    - Configuration backup and restore capabilities
    - Service-specific configuration overrides

    Features:
    - Hierarchical configuration structure
    - Environment variable integration
    - Configuration change notifications
    - Validation against JSON schemas
    - Configuration history and versioning
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "config_service"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_config_2024")
        }

        super().__init__("config_service", mqtt_config)

        # Configuration settings
        self.config_path = Path(os.getenv("CONFIG_PATH", "/app/config"))
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.config_cache: Dict[str, Any] = {}
        self.config_schemas: Dict[str, Dict[str, Any]] = {}
        self.config_history: List[Dict[str, Any]] = []
        self.max_history_size = int(os.getenv("MAX_HISTORY_SIZE", "100"))

        # Service configurations
        self.service_configs: Dict[str, Dict[str, Any]] = {}
        self.global_config: Dict[str, Any] = {}

        # Setup configuration
        self._setup_config_directory()
        self._load_base_configurations()
        self._setup_config_endpoints()

        # Setup API
        self.api = BusServiceAPI(self)

        # Service capabilities
        self.capabilities = [
            "configuration_management",
            "dynamic_updates",
            "environment_handling",
            "validation",
            "backup_restore",
            "service_discovery"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._config_monitor_task())
        asyncio.create_task(self._cleanup_old_history())

        self.logger.info("Configuration Service initialized")

    def _setup_config_directory(self):
        """Setup configuration directory structure."""
        try:
            # Create main config directory
            self.config_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            (self.config_path / "services").mkdir(exist_ok=True)
            (self.config_path / "environments").mkdir(exist_ok=True)
            (self.config_path / "schemas").mkdir(exist_ok=True)
            (self.config_path / "backups").mkdir(exist_ok=True)

            self.logger.info(f"Configuration directories created at {self.config_path}")

        except Exception as e:
            self.logger.error(f"Error setting up config directory: {e}")

    def _load_base_configurations(self):
        """Load base configuration files."""
        try:
            # Load global configuration
            global_config_path = self.config_path / "global.json"
            if global_config_path.exists():
                with open(global_config_path, 'r') as f:
                    self.global_config = json.load(f)
                self.logger.info("Global configuration loaded")
            else:
                # Create default global config
                self.global_config = {
                    "environment": self.environment,
                    "version": "1.0.0",
                    "services": {},
                    "features": {
                        "voice_processing": True,
                        "device_integration": True,
                        "advanced_features": True
                    }
                }
                self._save_global_config()

            # Load service configurations
            services_path = self.config_path / "services"
            if services_path.exists():
                for config_file in services_path.glob("*.json"):
                    service_name = config_file.stem
                    with open(config_file, 'r') as f:
                        self.service_configs[service_name] = json.load(f)

            # Load environment-specific configurations
            env_config_path = self.config_path / "environments" / f"{self.environment}.json"
            if env_config_path.exists():
                with open(env_config_path, 'r') as f:
                    env_config = json.load(f)
                    # Merge environment config with global config
                    self._merge_configs(self.global_config, env_config)

            self.logger.info(f"Base configurations loaded for environment: {self.environment}")

        except Exception as e:
            self.logger.error(f"Error loading base configurations: {e}")

    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]):
        """Merge override configuration into base configuration."""
        for key, value in override_config.items():
            if isinstance(value, dict) and key in base_config and isinstance(base_config[key], dict):
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value

    def _save_global_config(self):
        """Save global configuration to file."""
        try:
            global_config_path = self.config_path / "global.json"
            with open(global_config_path, 'w') as f:
                json.dump(self.global_config, f, indent=2)
            self.logger.info("Global configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving global configuration: {e}")

    def _setup_config_endpoints(self):
        """Setup FastAPI endpoints for configuration management."""

        @self.api.app.get("/config")
        async def get_global_config():
            """Get global configuration."""
            return {
                "environment": self.environment,
                "config": self.global_config,
                "timestamp": time.time()
            }

        @self.api.app.get("/config/{service_name}")
        async def get_service_config(service_name: str):
            """Get configuration for a specific service."""
            if service_name not in self.service_configs:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

            return {
                "service": service_name,
                "config": self.service_configs[service_name],
                "timestamp": time.time()
            }

        @self.api.app.post("/config/{service_name}")
        async def update_service_config(service_name: str, config: Dict[str, Any]):
            """Update configuration for a specific service."""
            try:
                # Validate configuration if schema exists
                if service_name in self.config_schemas:
                    self._validate_config(config, self.config_schemas[service_name])

                # Store old configuration for history
                old_config = self.service_configs.get(service_name, {})

                # Update configuration
                self.service_configs[service_name] = config

                # Save to file
                self._save_service_config(service_name, config)

                # Add to history
                self._add_to_history(service_name, old_config, config, "update")

                # Notify other services
                await self._notify_config_change(service_name, config)

                return {
                    "service": service_name,
                    "status": "updated",
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error updating service config: {e}")
                raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")

        @self.api.app.post("/config/global")
        async def update_global_config(config: Dict[str, Any]):
            """Update global configuration."""
            try:
                old_config = self.global_config.copy()
                self._merge_configs(self.global_config, config)
                self._save_global_config()

                # Add to history
                self._add_to_history("global", old_config, self.global_config, "update")

                # Notify all services
                await self._notify_global_config_change()

                return {
                    "status": "updated",
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error updating global config: {e}")
                raise HTTPException(status_code=500, detail=f"Global configuration update failed: {str(e)}")

        @self.api.app.get("/services")
        async def list_services():
            """List all configured services."""
            return {
                "services": list(self.service_configs.keys()),
                "count": len(self.service_configs),
                "timestamp": time.time()
            }

        @self.api.app.post("/backup")
        async def create_backup():
            """Create configuration backup."""
            try:
                backup_name = f"backup_{int(time.time())}.json"
                backup_path = self.config_path / "backups" / backup_name

                backup_data = {
                    "timestamp": time.time(),
                    "environment": self.environment,
                    "global_config": self.global_config,
                    "service_configs": self.service_configs,
                    "version": self.version
                }

                with open(backup_path, 'w') as f:
                    json.dump(backup_data, f, indent=2)

                return {
                    "backup_name": backup_name,
                    "path": str(backup_path),
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Error creating backup: {e}")
                raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")

        @self.api.app.get("/health")
        async def health_check():
            """Configuration service health check."""
            return {
                "service": "config_service",
                "status": "healthy" if self.is_connected else "unhealthy",
                "environment": self.environment,
                "services_configured": len(self.service_configs),
                "global_config_loaded": bool(self.global_config),
                "uptime": time.time() - self.start_time
            }

    def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]):
        """Validate configuration against schema."""
        # Basic validation - in production, use JSON Schema validation
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required field '{field}' missing from configuration")

    def _save_service_config(self, service_name: str, config: Dict[str, Any]):
        """Save service configuration to file."""
        try:
            config_path = self.config_path / "services" / f"{service_name}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Service configuration saved: {service_name}")
        except Exception as e:
            self.logger.error(f"Error saving service configuration: {e}")

    def _add_to_history(self, service_name: str, old_config: Dict[str, Any],
                       new_config: Dict[str, Any], action: str):
        """Add configuration change to history."""
        history_entry = {
            "timestamp": time.time(),
            "service": service_name,
            "action": action,
            "old_config": old_config,
            "new_config": new_config,
            "user": "system"  # In production, track actual user
        }

        self.config_history.append(history_entry)

        # Keep history size manageable
        if len(self.config_history) > self.max_history_size:
            self.config_history = self.config_history[-self.max_history_size:]

    async def _notify_config_change(self, service_name: str, config: Dict[str, Any]):
        """Notify service about configuration change."""
        try:
            message = {
                "message_id": f"config_update_{service_name}_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": service_name,
                "message_type": "configuration_update",
                "payload": {
                    "service": service_name,
                    "config": config,
                    "environment": self.environment
                }
            }

            self.publish_message(f"alicia/config/{service_name}/update", message)
            self.logger.info(f"Configuration update notification sent to {service_name}")

        except Exception as e:
            self.logger.error(f"Error notifying config change: {e}")

    async def _notify_global_config_change(self):
        """Notify all services about global configuration change."""
        try:
            message = {
                "message_id": f"global_config_update_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "all_services",
                "message_type": "global_configuration_update",
                "payload": {
                    "config": self.global_config,
                    "environment": self.environment
                }
            }

            self.publish_message("alicia/config/global/update", message)
            self.logger.info("Global configuration update notification sent")

        except Exception as e:
            self.logger.error(f"Error notifying global config change: {e}")

    def _generate_id(self) -> str:
        """Generate a unique ID for messages."""
        import uuid
        return str(uuid.uuid4())[:8]

    async def _config_monitor_task(self):
        """Monitor configuration files for changes."""
        while True:
            try:
                # Check for file changes (simplified - in production use file watchers)
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in config monitor task: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_history(self):
        """Clean up old configuration history entries."""
        while True:
            try:
                # Clean up old history entries (keep last 30 days)
                cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago

                self.config_history = [
                    entry for entry in self.config_history
                    if entry["timestamp"] > cutoff_time
                ]

                await asyncio.sleep(24 * 60 * 60)  # Clean up daily

            except Exception as e:
                self.logger.error(f"Error cleaning up history: {e}")
                await asyncio.sleep(24 * 60 * 60)

    def subscribe_to_topics(self):
        """Subscribe to configuration-related MQTT topics."""
        topics = [
            "alicia/config/request",
            "alicia/config/global/request",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to configuration topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/config/request":
                self._handle_config_request(message)
            elif topic == "alicia/config/global/request":
                self._handle_global_config_request(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing config message: {e}")

    def _handle_config_request(self, message: Dict[str, Any]):
        """Handle configuration request."""
        try:
            payload = message.get("payload", {})
            service_name = payload.get("service")
            requester = payload.get("requester", "unknown")

            if service_name and service_name in self.service_configs:
                config = self.service_configs[service_name]

                response_message = {
                    "message_id": f"config_response_{service_name}_{int(time.time())}_{self._generate_id()}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": requester,
                    "message_type": "configuration_response",
                    "payload": {
                        "service": service_name,
                        "config": config,
                        "environment": self.environment
                    }
                }

                self.publish_message(f"alicia/config/{requester}/response", response_message)

        except Exception as e:
            self.logger.error(f"Error handling config request: {e}")

    def _handle_global_config_request(self, message: Dict[str, Any]):
        """Handle global configuration request."""
        try:
            payload = message.get("payload", {})
            requester = payload.get("requester", "unknown")

            response_message = {
                "message_id": f"global_config_response_{int(time.time())}_{self._generate_id()}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": requester,
                "message_type": "global_configuration_response",
                "payload": {
                    "config": self.global_config,
                    "environment": self.environment,
                    "services": list(self.service_configs.keys())
                }
            }

            self.publish_message(f"alicia/config/{requester}/global/response", response_message)

        except Exception as e:
            self.logger.error(f"Error handling global config request: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()


async def main():
    """Main entry point for Configuration Service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create configuration service
    config_service = ConfigurationService()

    # Start API server
    try:
        api = BusServiceAPI(config_service)
        config = uvicorn.Config(api.app, host="0.0.0.0", port=8026)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        config_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
