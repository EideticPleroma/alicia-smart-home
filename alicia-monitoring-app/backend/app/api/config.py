"""
Configuration management API endpoints
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ConfigUpdate(BaseModel):
    """Configuration update model"""
    service: str
    key: str
    value: Any
    environment: str = "production"

class ConfigGet(BaseModel):
    """Configuration get model"""
    service: str
    environment: str = "production"

class ConfigResponse(BaseModel):
    """Configuration response model"""
    service: str
    environment: str
    config: Dict[str, Any]
    last_updated: str

# Dependency injection
def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance"""
    from app.main import websocket_manager
    return websocket_manager

# In-memory configuration storage (in production, this would be in a database)
config_storage = {
    "production": {
        "whisper": {
            "host": "localhost",
            "port": 10300,
            "model": "medium",
            "language": "en"
        },
        "piper": {
            "host": "localhost",
            "port": 10200,
            "voice": "en_US-lessac-medium"
        },
        "alicia_assistant": {
            "host": "localhost",
            "port": 8000,
            "llm_enabled": False
        },
        "mqtt": {
            "host": "localhost",
            "port": 1883,
            "username": "voice_assistant",
            "password": "alicia_ha_mqtt_2024"
        },
        "homeassistant": {
            "host": "localhost",
            "port": 8123,
            "api_password": ""
        }
    },
    "development": {
        "whisper": {
            "host": "localhost",
            "port": 10300,
            "model": "base",
            "language": "en"
        },
        "piper": {
            "host": "localhost",
            "port": 10200,
            "voice": "en_US-lessac-medium"
        },
        "alicia_assistant": {
            "host": "localhost",
            "port": 8000,
            "llm_enabled": True
        },
        "mqtt": {
            "host": "localhost",
            "port": 1883,
            "username": "voice_assistant",
            "password": "alicia_ha_mqtt_2024"
        },
        "homeassistant": {
            "host": "localhost",
            "port": 8123,
            "api_password": ""
        }
    }
}

@router.get("/")
async def get_all_configs(
    environment: str = "production"
) -> Dict[str, Any]:
    """Get all configuration for an environment"""
    try:
        if environment not in config_storage:
            raise HTTPException(status_code=404, detail=f"Environment '{environment}' not found")
            
        return {
            "environment": environment,
            "configs": config_storage[environment],
            "timestamp": "2024-01-15T10:30:00Z"  # In production, this would be dynamic
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all configs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configurations")

@router.get("/{service}")
async def get_service_config(
    service: str,
    environment: str = "production"
) -> ConfigResponse:
    """Get configuration for a specific service"""
    try:
        if environment not in config_storage:
            raise HTTPException(status_code=404, detail=f"Environment '{environment}' not found")
            
        if service not in config_storage[environment]:
            raise HTTPException(status_code=404, detail=f"Service '{service}' not found in environment '{environment}'")
            
        return ConfigResponse(
            service=service,
            environment=environment,
            config=config_storage[environment][service],
            last_updated="2024-01-15T10:30:00Z"  # In production, this would be dynamic
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service config for {service}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service configuration")

@router.put("/{service}")
async def update_service_config(
    service: str,
    config_update: Dict[str, Any],
    environment: str = "production",
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
) -> Dict[str, Any]:
    """Update configuration for a specific service"""
    try:
        if environment not in config_storage:
            raise HTTPException(status_code=404, detail=f"Environment '{environment}' not found")
            
        if service not in config_storage[environment]:
            raise HTTPException(status_code=404, detail=f"Service '{service}' not found in environment '{environment}'")
            
        # Update configuration
        config_storage[environment][service].update(config_update)
        
        # Broadcast configuration update
        await websocket_manager.broadcast_config_update({
            "service": service,
            "environment": environment,
            "config": config_storage[environment][service]
        })
        
        return {
            "message": f"Configuration updated for {service}",
            "service": service,
            "environment": environment,
            "config": config_storage[environment][service]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service config for {service}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update service configuration")

@router.post("/{service}/test")
async def test_service_config(
    service: str,
    environment: str = "production"
) -> Dict[str, Any]:
    """Test configuration for a specific service"""
    try:
        if environment not in config_storage:
            raise HTTPException(status_code=404, detail=f"Environment '{environment}' not found")
            
        if service not in config_storage[environment]:
            raise HTTPException(status_code=404, detail=f"Service '{service}' not found in environment '{environment}'")
            
        config = config_storage[environment][service]
        
        # Test the service based on its type
        if service == "whisper":
            return await test_whisper_config(config)
        elif service == "piper":
            return await test_piper_config(config)
        elif service == "alicia_assistant":
            return await test_alicia_config(config)
        elif service == "mqtt":
            return await test_mqtt_config(config)
        elif service == "homeassistant":
            return await test_ha_config(config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown service type: {service}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing service config for {service}: {e}")
        raise HTTPException(status_code=500, detail="Failed to test service configuration")

async def test_whisper_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test Whisper configuration"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{config['host']}:{config['port']}/health") as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": "Whisper service is accessible",
                        "response_time_ms": 0  # Would calculate actual response time
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Whisper service returned status {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Whisper service: {str(e)}"
        }

async def test_piper_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test Piper configuration"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{config['host']}:{config['port']}/health") as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": "Piper service is accessible",
                        "response_time_ms": 0
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Piper service returned status {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Piper service: {str(e)}"
        }

async def test_alicia_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test Alicia Assistant configuration"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{config['host']}:{config['port']}/health") as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": "Alicia Assistant is accessible",
                        "response_time_ms": 0
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Alicia Assistant returned status {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Alicia Assistant: {str(e)}"
        }

async def test_mqtt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test MQTT configuration"""
    try:
        import paho.mqtt.client as mqtt
        import asyncio
        
        client = mqtt.Client()
        client.username_pw_set(config["username"], config["password"])
        
        connected = False
        error_message = None
        
        def on_connect(client, userdata, flags, rc):
            nonlocal connected, error_message
            if rc == 0:
                connected = True
            else:
                error_message = f"MQTT connection failed with code {rc}"
                
        client.on_connect = on_connect
        client.connect(config["host"], config["port"], 60)
        client.loop_start()
        
        await asyncio.sleep(2)
        client.loop_stop()
        client.disconnect()
        
        if connected:
            return {
                "status": "success",
                "message": "MQTT broker is accessible",
                "response_time_ms": 0
            }
        else:
            return {
                "status": "error",
                "message": error_message or "MQTT connection failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to MQTT broker: {str(e)}"
        }

async def test_ha_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test Home Assistant configuration"""
    import aiohttp
    
    try:
        headers = {}
        if config.get("api_password"):
            headers["Authorization"] = f"Bearer {config['api_password']}"
            
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{config['host']}:{config['port']}/api/", headers=headers) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": "Home Assistant is accessible",
                        "response_time_ms": 0
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Home Assistant returned status {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Home Assistant: {str(e)}"
        }

@router.get("/environments")
async def get_environments() -> List[str]:
    """Get available environments"""
    return list(config_storage.keys())

@router.post("/environments/{environment}")
async def create_environment(
    environment: str,
    base_environment: str = "production"
) -> Dict[str, Any]:
    """Create a new environment based on an existing one"""
    try:
        if environment in config_storage:
            raise HTTPException(status_code=400, detail=f"Environment '{environment}' already exists")
            
        if base_environment not in config_storage:
            raise HTTPException(status_code=404, detail=f"Base environment '{base_environment}' not found")
            
        # Copy base environment configuration
        config_storage[environment] = json.loads(json.dumps(config_storage[base_environment]))
        
        return {
            "message": f"Environment '{environment}' created based on '{base_environment}'",
            "environment": environment
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating environment {environment}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create environment")

