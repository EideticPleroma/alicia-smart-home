"""
Configuration settings for Alicia Monitoring App
"""

import os
from typing import List, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "Alicia Monitoring App"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://alicia:alicia_password@localhost:5432/alicia_monitoring")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Alicia services configuration
    alicia_services: dict = {
        "whisper": {
            "host": os.getenv("WHISPER_HOST", "localhost"),
            "port": int(os.getenv("WHISPER_PORT", "10300")),
            "health_endpoint": "/health"
        },
        "piper": {
            "host": os.getenv("PIPER_HOST", "localhost"),
            "port": int(os.getenv("PIPER_PORT", "10200")),
            "health_endpoint": "/health"
        },
        "alicia_assistant": {
            "host": os.getenv("ALICIA_HOST", "localhost"),
            "port": int(os.getenv("ALICIA_PORT", "8000")),
            "health_endpoint": "/health"
        },
        "mqtt": {
            "host": os.getenv("MQTT_HOST", "localhost"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "voice_assistant"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")
        },
        "homeassistant": {
            "host": os.getenv("HA_HOST", "localhost"),
            "port": int(os.getenv("HA_PORT", "8123")),
            "health_endpoint": "/api/"
        }
    }
    
    # Monitoring settings
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # seconds
    metrics_retention_days: int = int(os.getenv("METRICS_RETENTION_DAYS", "30"))
    
    # WebSocket settings
    websocket_heartbeat_interval: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))  # seconds
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]
    
    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "alicia-monitoring-secret-key-change-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
