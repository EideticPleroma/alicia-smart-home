"""
Alicia Bus Architecture - Configuration Manager Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service provides centralized configuration management for all bus services,
including configuration storage, validation, updates, and distribution.
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import hashlib
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
import yaml
from dotenv import load_dotenv

from service_wrapper import BusServiceWrapper, BusServiceAPI

# Load environment variables
load_dotenv()


class ConfigFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    TOML = "toml"


class ConfigScope(Enum):
    GLOBAL = "global"
    SERVICE = "service"
    INSTANCE = "instance"
    ENVIRONMENT = "environment"


@dataclass
class Configuration:
    """Configuration entry."""
    config_id: str
    name: str
    description: str
    scope: ConfigScope
    service_name: Optional[str]
    instance_id: Optional[str]
    environment: str
    format: ConfigFormat
    content: Dict[str, Any]
    version: int = 1
    checksum: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class ConfigChange:
    """Configuration change record."""
    change_id: str
    config_id: str
    previous_version: int
    new_version: int
    changes: Dict[str, Any]
    changed_by: str
    timestamp: float
    approved: bool = False
    approved_by: Optional[str] = None
    rollback_available: bool = True


@dataclass
class ServiceConfig:
    """Service configuration mapping."""
    service_name: str
    instance_id: Optional[str]
    config_ids: List[str] = field(default_factory=list)
    last_updated: float = 0.0
    config_hash: str = ""


@dataclass
class ConfigValidation:
    """Configuration validation result."""
    config_id: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_at: float = field(default_factory=time.time)


class ConfigurationManagerService(BusServiceWrapper):
    """
    Configuration Manager Service for the Alicia Bus Architecture.

    Provides centralized configuration management for all bus services,
    including storage, validation, updates, and distribution.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": "configuration_manager",
            "password": "alicia_config_2024"
        }

        super().__init__("configuration_manager", mqtt_config)

        # Configuration storage
        self.configurations: Dict[str, Configuration] = {}
        self.config_changes: Dict[str, List[ConfigChange]] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.config_validations: Dict[str, ConfigValidation] = {}

        # Configuration files
        self.config_dir = Path("/app/config")
        self.config_dir.mkdir(exist_ok=True)

        # Configuration settings
        self.auto_backup = True
        self.backup_interval = 3600  # 1 hour
        self.max_versions_per_config = 10
        self.validation_enabled = True

        # FastAPI setup
        self.app = FastAPI(title="Alicia Configuration Manager", version="1.0.0")
        self._setup_api_endpoints()

        # Background threads
        self.backup_thread = threading.Thread(target=self._backup_loop)
        self.backup_thread.daemon = True

        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "configuration_management",
            "config_validation",
            "config_distribution",
            "version_control",
            "backup_restore"
        ]

        self.version = "1.0.0"

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the configuration manager."""

        @self.app.get("/health")
        async def get_health():
            """Get configuration manager service health."""
            return self.get_health_status()

        @self.app.get("/configs")
        async def get_configs(
            scope: Optional[str] = None,
            service_name: Optional[str] = None,
            environment: Optional[str] = None,
            active_only: bool = True
        ):
            """Get all configurations with optional filtering."""
            configs = []

            for config in self.configurations.values():
                if active_only and not config.is_active:
                    continue

                if scope and config.scope.value != scope:
                    continue

                if service_name and config.service_name != service_name:
                    continue

                if environment and config.environment != environment:
                    continue

                configs.append(asdict(config))

            configs.sort(key=lambda x: x["updated_at"], reverse=True)
            return {"configs": configs}

        @self.app.post("/configs")
        async def create_config(config_data: Dict[str, Any]):
            """Create a new configuration."""
            try:
                config_id = str(uuid.uuid4())

                # Create configuration
                config = Configuration(
                    config_id=config_id,
                    name=config_data["name"],
                    description=config_data.get("description", ""),
                    scope=ConfigScope(config_data["scope"]),
                    service_name=config_data.get("service_name"),
                    instance_id=config_data.get("instance_id"),
                    environment=config_data.get("environment", "development"),
                    format=ConfigFormat(config_data.get("format", "json")),
                    content=config_data["content"],
                    created_by=config_data.get("created_by", "api"),
                    tags=config_data.get("tags", [])
                )

                # Calculate checksum
                config.checksum = self._calculate_checksum(config.content)

                # Store configuration
                self.configurations[config_id] = config

                # Save to file
                self._save_config_to_file(config)

                self.logger.info(f"Created configuration: {config.name} ({config_id})")

                return {"config_id": config_id, "config": asdict(config)}

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

        @self.app.get("/configs/{config_id}")
        async def get_config(config_id: str):
            """Get a specific configuration."""
            if config_id not in self.configurations:
                raise HTTPException(status_code=404, detail="Configuration not found")

            return {"config": asdict(self.configurations[config_id])}

        @self.app.put("/configs/{config_id}")
        async def update_config(config_id: str, config_data: Dict[str, Any]):
            """Update a configuration."""
            if config_id not in self.configurations:
                raise HTTPException(status_code=404, detail="Configuration not found")

            config = self.configurations[config_id]
            old_content = config.content.copy()

            # Update fields
            for key, value in config_data.items():
                if hasattr(config, key) and key not in ["config_id", "created_at", "version"]:
                    if key == "scope":
                        setattr(config, key, ConfigScope(value))
                    elif key == "format":
                        setattr(config, key, ConfigFormat(value))
                    else:
                        setattr(config, key, value)

            # Update version and checksum
            config.version += 1
            config.updated_at = time.time()
            config.checksum = self._calculate_checksum(config.content)

            # Record change
            change = ConfigChange(
                change_id=str(uuid.uuid4()),
                config_id=config_id,
                previous_version=config.version - 1,
                new_version=config.version,
                changes=self._calculate_changes(old_content, config.content),
                changed_by=config_data.get("changed_by", "api"),
                timestamp=time.time()
            )

            if config_id not in self.config_changes:
                self.config_changes[config_id] = []
            self.config_changes[config_id].append(change)

            # Save to file
            self._save_config_to_file(config)

            # Notify services of configuration change
            self._notify_config_change(config)

            return {"config": asdict(config), "change": asdict(change)}

        @self.app.delete("/configs/{config_id}")
        async def delete_config(config_id: str):
            """Delete a configuration."""
            if config_id not in self.configurations:
                raise HTTPException(status_code=404, detail="Configuration not found")

            config = self.configurations[config_id]
            config.is_active = False
            config.updated_at = time.time()

            # Save updated config
            self._save_config_to_file(config)

            return {"message": "Configuration marked as inactive"}

        @self.app.get("/configs/{config_id}/history")
        async def get_config_history(config_id: str, limit: int = Query(10, description="Number of changes to return")):
            """Get configuration change history."""
            if config_id not in self.config_changes:
                return {"changes": []}

            changes = self.config_changes[config_id]
            changes.sort(key=lambda x: x.timestamp, reverse=True)

            return {"changes": [asdict(change) for change in changes[:limit]]}

        @self.app.post("/configs/{config_id}/rollback/{version}")
        async def rollback_config(config_id: str, version: int):
            """Rollback configuration to a specific version."""
            if config_id not in self.config_changes:
                raise HTTPException(status_code=404, detail="No change history found")

            # Find the change that resulted in the target version
            target_change = None
            for change in self.config_changes[config_id]:
                if change.new_version == version:
                    target_change = change
                    break

            if not target_change:
                raise HTTPException(status_code=404, detail="Version not found")

            # This is a simplified rollback - in production, you'd reconstruct the config
            raise HTTPException(status_code=501, detail="Rollback functionality not yet implemented")

        @self.app.get("/services/{service_name}/config")
        async def get_service_config(service_name: str, instance_id: Optional[str] = None):
            """Get merged configuration for a service."""
            merged_config = self._get_merged_config(service_name, instance_id)
            return {"service_name": service_name, "config": merged_config}

        @self.app.post("/validate/{config_id}")
        async def validate_config(config_id: str):
            """Validate a configuration."""
            if config_id not in self.configurations:
                raise HTTPException(status_code=404, detail="Configuration not found")

            config = self.configurations[config_id]
            validation = self._validate_config(config)

            self.config_validations[config_id] = validation

            return asdict(validation)

        @self.app.get("/backup")
        async def create_backup():
            """Create a backup of all configurations."""
            backup_file = self._create_backup()
            return {"backup_file": backup_file, "timestamp": time.time()}

        @self.app.post("/restore")
        async def restore_backup(backup_file: UploadFile = File(...)):
            """Restore configurations from backup."""
            try:
                content = await backup_file.read()
                backup_data = json.loads(content)

                restored_count = 0
                for config_data in backup_data.get("configurations", []):
                    config_id = config_data["config_id"]
                    if config_id not in self.configurations:
                        config = Configuration(**config_data)
                        self.configurations[config_id] = config
                        restored_count += 1

                return {"message": f"Restored {restored_count} configurations"}

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Restore failed: {str(e)}")

    def subscribe_to_topics(self):
        """Subscribe to configuration management topics."""
        self.mqtt_client.subscribe("alicia/config/+")
        self.mqtt_client.subscribe("alicia/services/+/config")
        self.logger.info("Subscribed to configuration topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/config/"):
                self._process_config_message(topic, message)
            elif topic.startswith("alicia/services/") and topic.endswith("/config"):
                self._process_service_config_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_config_message(self, topic: str, message: Dict[str, Any]):
        """Process configuration messages."""
        try:
            command = message.get("command")

            if command == "get_config":
                service_name = message.get("service_name")
                instance_id = message.get("instance_id")
                reply_topic = message.get("reply_topic")

                if service_name and reply_topic:
                    merged_config = self._get_merged_config(service_name, instance_id)
                    self.publish_message(reply_topic, {
                        "service_name": service_name,
                        "instance_id": instance_id,
                        "config": merged_config,
                        "timestamp": time.time()
                    })

            elif command == "update_config":
                config_id = message.get("config_id")
                new_content = message.get("content")
                changed_by = message.get("changed_by", "mqtt")

                if config_id and config_id in self.configurations:
                    config = self.configurations[config_id]
                    old_content = config.content.copy()

                    config.content.update(new_content)
                    config.version += 1
                    config.updated_at = time.time()
                    config.checksum = self._calculate_checksum(config.content)

                    # Record change
                    change = ConfigChange(
                        change_id=str(uuid.uuid4()),
                        config_id=config_id,
                        previous_version=config.version - 1,
                        new_version=config.version,
                        changes=self._calculate_changes(old_content, config.content),
                        changed_by=changed_by,
                        timestamp=time.time()
                    )

                    if config_id not in self.config_changes:
                        self.config_changes[config_id] = []
                    self.config_changes[config_id].append(change)

                    # Notify services
                    self._notify_config_change(config)

        except Exception as e:
            self.logger.error(f"Error processing config message: {e}")

    def _process_service_config_message(self, topic: str, message: Dict[str, Any]):
        """Process service configuration messages."""
        try:
            service_name = topic.split("/")[2]
            instance_id = message.get("instance_id")

            # Update service config mapping
            service_key = f"{service_name}:{instance_id}" if instance_id else service_name

            if service_key not in self.service_configs:
                self.service_configs[service_key] = ServiceConfig(
                    service_name=service_name,
                    instance_id=instance_id
                )

            service_config = self.service_configs[service_key]
            service_config.last_updated = time.time()

            # Calculate config hash for change detection
            merged_config = self._get_merged_config(service_name, instance_id)
            config_str = json.dumps(merged_config, sort_keys=True)
            service_config.config_hash = hashlib.md5(config_str.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error processing service config message: {e}")

    def _get_merged_config(self, service_name: str, instance_id: Optional[str] = None) -> Dict[str, Any]:
        """Get merged configuration for a service."""
        try:
            merged_config = {}

            # Get configurations in order of precedence (instance -> service -> global -> environment)
            config_candidates = []

            # Environment configs
            config_candidates.extend([
                config for config in self.configurations.values()
                if config.is_active and config.scope == ConfigScope.ENVIRONMENT
            ])

            # Global configs
            config_candidates.extend([
                config for config in self.configurations.values()
                if config.is_active and config.scope == ConfigScope.GLOBAL
            ])

            # Service configs
            config_candidates.extend([
                config for config in self.configurations.values()
                if config.is_active and config.scope == ConfigScope.SERVICE
                and config.service_name == service_name
            ])

            # Instance configs
            if instance_id:
                config_candidates.extend([
                    config for config in self.configurations.values()
                    if config.is_active and config.scope == ConfigScope.INSTANCE
                    and config.service_name == service_name and config.instance_id == instance_id
                ])

            # Merge configurations (later configs override earlier ones)
            for config in config_candidates:
                self._deep_merge(merged_config, config.content)

            return merged_config

        except Exception as e:
            self.logger.error(f"Error merging config for {service_name}: {e}")
            return {}

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _calculate_checksum(self, content: Dict[str, Any]) -> str:
        """Calculate checksum for configuration content."""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()

    def _calculate_changes(self, old_content: Dict[str, Any], new_content: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate changes between two configurations."""
        changes = {"added": {}, "modified": {}, "removed": []}

        # Find added and modified
        for key, value in new_content.items():
            if key not in old_content:
                changes["added"][key] = value
            elif old_content[key] != value:
                changes["modified"][key] = {"old": old_content[key], "new": value}

        # Find removed
        for key in old_content:
            if key not in new_content:
                changes["removed"].append(key)

        return changes

    def _validate_config(self, config: Configuration) -> ConfigValidation:
        """Validate a configuration."""
        validation = ConfigValidation(
            config_id=config.config_id,
            is_valid=True,
            errors=[],
            warnings=[]
        )

        try:
            # Basic validation rules
            if not config.name:
                validation.errors.append("Configuration name is required")
                validation.is_valid = False

            if not config.content:
                validation.errors.append("Configuration content cannot be empty")
                validation.is_valid = False

            # Service-specific validation
            if config.service_name:
                if config.service_name not in ["stt_service", "ai_service", "tts_service", "voice_router",
                                             "sonos_service", "device_manager", "ha_bridge", "device_control",
                                             "grok_integration", "personality_system", "multi_language", "advanced_voice"]:
                    validation.warnings.append(f"Unknown service name: {config.service_name}")

            # Content validation based on format
            if config.format == ConfigFormat.JSON:
                try:
                    json.dumps(config.content)
                except Exception as e:
                    validation.errors.append(f"Invalid JSON content: {str(e)}")
                    validation.is_valid = False

        except Exception as e:
            validation.errors.append(f"Validation error: {str(e)}")
            validation.is_valid = False

        return validation

    def _save_config_to_file(self, config: Configuration):
        """Save configuration to file."""
        try:
            filename = f"{config.config_id}.{config.format.value}"
            filepath = self.config_dir / filename

            if config.format == ConfigFormat.JSON:
                with open(filepath, 'w') as f:
                    json.dump(config.content, f, indent=2)
            elif config.format == ConfigFormat.YAML:
                with open(filepath, 'w') as f:
                    yaml.dump(config.content, f, default_flow_style=False)

        except Exception as e:
            self.logger.error(f"Error saving config to file: {e}")

    def _notify_config_change(self, config: Configuration):
        """Notify services of configuration change."""
        try:
            if config.scope == ConfigScope.GLOBAL:
                # Notify all services
                self.publish_message("alicia/config/global/updated", {
                    "config_id": config.config_id,
                    "service_name": config.service_name,
                    "timestamp": time.time()
                })
            elif config.scope == ConfigScope.SERVICE and config.service_name:
                # Notify specific service
                self.publish_message(f"alicia/config/service/{config.service_name}/updated", {
                    "config_id": config.config_id,
                    "service_name": config.service_name,
                    "instance_id": config.instance_id,
                    "timestamp": time.time()
                })

        except Exception as e:
            self.logger.error(f"Error notifying config change: {e}")

    def _create_backup(self) -> str:
        """Create a backup of all configurations."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"config_backup_{timestamp}.json"
            backup_path = self.config_dir / backup_file

            backup_data = {
                "timestamp": time.time(),
                "configurations": [asdict(config) for config in self.configurations.values()],
                "changes": {
                    config_id: [asdict(change) for change in changes]
                    for config_id, changes in self.config_changes.items()
                }
            }

            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            return str(backup_path)

        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return ""

    def _backup_loop(self):
        """Background backup loop."""
        while True:
            try:
                if self.auto_backup:
                    self._create_backup()
                time.sleep(self.backup_interval)

            except Exception as e:
                self.logger.error(f"Error in backup loop: {e}")
                time.sleep(60)

    def _sync_loop(self):
        """Background synchronization loop."""
        while True:
            try:
                # Check for configuration changes and notify services
                for service_config in self.service_configs.values():
                    merged_config = self._get_merged_config(
                        service_config.service_name,
                        service_config.instance_id
                    )
                    config_str = json.dumps(merged_config, sort_keys=True)
                    current_hash = hashlib.md5(config_str.encode()).hexdigest()

                    if current_hash != service_config.config_hash:
                        # Configuration changed, notify service
                        topic = f"alicia/services/{service_config.service_name}/config"
                        if service_config.instance_id:
                            topic += f"/{service_config.instance_id}"

                        self.publish_message(topic, {
                            "command": "reload_config",
                            "config": merged_config,
                            "timestamp": time.time()
                        })

                        service_config.config_hash = current_hash
                        service_config.last_updated = time.time()

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                time.sleep(60)

    def start_management(self):
        """Start the configuration management threads."""
        self.backup_thread.start()
        self.sync_thread.start()
        self.logger.info("Configuration management started")

    def shutdown(self):
        """Gracefully shutdown the configuration manager."""
        self.logger.info("Shutting down configuration manager...")

        super().shutdown()


async def main():
    """Main entry point for the Configuration Manager service."""
    service = ConfigurationManagerService()
    
    # Start the service management in background
    service.start_management()

    # Start FastAPI server
    api = BusServiceAPI(service)
    config = uvicorn.Config(api.app, host="0.0.0.0", port=8015)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
