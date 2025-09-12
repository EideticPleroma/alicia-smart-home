# Configuration Schema Examples

## Service Configuration Schema

### Base Service Configuration
```json
{
  "service_name": "string",
  "service_type": "stt|tts|llm|device_control|voice_router|etc",
  "status": "healthy|unhealthy|unknown",
  "enabled": "boolean",
  "version": "string",
  "last_updated": "ISO 8601 timestamp",
  "config": {
    "api_key": "string (masked in UI)",
    "endpoints": [
      {
        "type": "string",
        "model": "string",
        "ip": "string",
        "port": "number",
        "protocol": "http|https|tcp|udp"
      }
    ],
    "settings": "object (service-specific)"
  }
}
```

### STT Service Configuration
```json
{
  "service_name": "whisper-service",
  "service_type": "stt",
  "status": "healthy",
  "enabled": true,
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "config": {
    "api_key": "sk-whisper-xxxx",
    "provider": "openai|local|azure",
    "model": "whisper-1",
    "language": "en|es|fr|de|etc",
    "sample_rate": 16000,
    "chunk_size": 1024,
    "endpoints": [
      {
        "type": "stt",
        "model": "whisper-1",
        "ip": "http://whisper:8001",
        "port": 8001,
        "protocol": "http"
      }
    ],
    "settings": {
      "temperature": 0.0,
      "max_tokens": 1000,
      "timeout": 30
    }
  }
}
```

### TTS Service Configuration
```json
{
  "service_name": "tts-service",
  "service_type": "tts",
  "status": "healthy",
  "enabled": true,
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "config": {
    "api_key": "sk-elevenlabs-xxxx",
    "provider": "elevenlabs|google|azure|piper",
    "voice": "ara-female-2",
    "voice_id": "pNInz6obpgDQGcFmaJgB",
    "language": "en-US",
    "sample_rate": 22050,
    "endpoints": [
      {
        "type": "tts",
        "provider": "elevenlabs",
        "ip": "http://tts:8002",
        "port": 8002,
        "protocol": "http"
      }
    ],
    "settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "style": 0.0,
      "use_speaker_boost": true
    }
  }
}
```

### LLM Service Configuration
```json
{
  "service_name": "grok-service",
  "service_type": "llm",
  "status": "healthy",
  "enabled": true,
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "config": {
    "api_key": "sk-grok-xxxx",
    "provider": "xai|openai|anthropic|local",
    "model": "grok-1.5",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "endpoints": [
      {
        "type": "llm",
        "model": "grok-1.5",
        "ip": "http://grok:8003",
        "port": 8003,
        "protocol": "http"
      }
    ],
    "settings": {
      "stream": true,
      "timeout": 60,
      "retry_attempts": 3,
      "conversation_memory": true
    }
  }
}
```

### Device Control Service Configuration
```json
{
  "service_name": "device-control-service",
  "service_type": "device_control",
  "status": "healthy",
  "enabled": true,
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "config": {
    "api_key": "ha-supervisor-token-xxxx",
    "provider": "homeassistant|openhab|domoticz",
    "base_url": "http://homeassistant:8123",
    "endpoints": [
      {
        "type": "device_control",
        "ip": "http://device-control:8004",
        "port": 8004,
        "protocol": "http"
      }
    ],
    "settings": {
      "polling_interval": 30,
      "device_timeout": 10,
      "max_retries": 3,
      "supported_devices": ["light", "switch", "sensor", "climate"]
    }
  }
}
```

## Device Configuration Schema

### Base Device Configuration
```json
{
  "device_id": "string (UUID)",
  "device_name": "string",
  "device_type": "external_api|local_service|hardware",
  "status": "online|offline|unknown",
  "last_seen": "ISO 8601 timestamp",
  "connection": {
    "host": "string",
    "port": "number",
    "protocol": "http|https|tcp|udp|mqtt",
    "authentication": {
      "type": "api_key|oauth|basic|certificate",
      "credentials": "object"
    }
  },
  "capabilities": ["string"],
  "metadata": "object"
}
```

### External API Device
```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "device_name": "GroqCloud",
  "device_type": "external_api",
  "status": "online",
  "last_seen": "2024-01-15T10:30:00Z",
  "connection": {
    "host": "api.groq.com",
    "port": 443,
    "protocol": "https",
    "authentication": {
      "type": "api_key",
      "credentials": {
        "api_key": "gsk_xxxx",
        "header_name": "Authorization",
        "header_format": "Bearer {api_key}"
      }
    }
  },
  "capabilities": ["llm", "text_generation", "chat_completion"],
  "metadata": {
    "provider": "groq",
    "region": "us-east-1",
    "rate_limit": "1000/hour",
    "models": ["llama-3-8b", "llama-3-70b", "mixtral-8x7b"]
  }
}
```

### Local Service Device
```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440001",
  "device_name": "LocalWhisper",
  "device_type": "local_service",
  "status": "online",
  "last_seen": "2024-01-15T10:30:00Z",
  "connection": {
    "host": "192.168.1.100",
    "port": 8001,
    "protocol": "http",
    "authentication": {
      "type": "api_key",
      "credentials": {
        "api_key": "local-whisper-key-xxxx",
        "header_name": "X-API-Key"
      }
    }
  },
  "capabilities": ["stt", "speech_recognition", "transcription"],
  "metadata": {
    "provider": "local",
    "model": "whisper-large-v3",
    "language": "en",
    "gpu_acceleration": true
  }
}
```

### Hardware Device
```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "device_name": "RaspberryPi-Sensor",
  "device_type": "hardware",
  "status": "online",
  "last_seen": "2024-01-15T10:30:00Z",
  "connection": {
    "host": "192.168.1.101",
    "port": 1883,
    "protocol": "mqtt",
    "authentication": {
      "type": "basic",
      "credentials": {
        "username": "sensor_user",
        "password": "sensor_pass_xxxx"
      }
    }
  },
  "capabilities": ["sensor_data", "temperature", "humidity", "motion"],
  "metadata": {
    "manufacturer": "Raspberry Pi",
    "model": "4B",
    "firmware_version": "1.2.3",
    "sensors": ["DHT22", "PIR", "BME280"]
  }
}
```

## MQTT Topic Schema

### Configuration Topics
```
alicia/config/update/{service_name}     # Update service configuration
alicia/config/reload                    # Reload all configurations
alicia/config/backup                    # Backup configurations
alicia/config/restore                   # Restore configurations
```

### Device Topics
```
alicia/device/register                  # Register new device
alicia/device/unregister/{device_id}    # Unregister device
alicia/device/status/{device_id}        # Device status update
alicia/device/ping/{device_id}          # Ping device
```

### Service Discovery Topics
```
alicia/system/discovery/register        # Service registration
alicia/system/discovery/unregister      # Service unregistration
alicia/system/health/{service_name}     # Service health status
alicia/system/health/check              # Health check request
```

## API Endpoint Schema

### Configuration Endpoints
```
GET    /api/config                      # Get all configurations
GET    /api/config/{service}            # Get service configuration
PATCH  /api/config/{service}            # Update service configuration
DELETE /api/config/{service}            # Delete service configuration
POST   /api/config/reload               # Reload configurations
POST   /api/config/backup               # Backup configurations
POST   /api/config/restore              # Restore configurations
```

### Device Endpoints
```
GET    /api/devices                     # Get all devices
GET    /api/devices/{id}                # Get device by ID
POST   /api/devices                     # Create new device
PATCH  /api/devices/{id}                # Update device
DELETE /api/devices/{id}                # Delete device
POST   /api/devices/{id}/ping           # Ping device
```

### System Endpoints
```
GET    /api/health                      # System health status
GET    /api/services                    # List all services
GET    /api/topology                    # Get service topology
POST   /api/reload                      # Reload system
```

## Validation Rules

### Service Configuration Validation
- `service_name`: Required, string, 3-50 characters, alphanumeric + hyphens
- `service_type`: Required, enum from allowed types
- `status`: Required, enum: healthy|unhealthy|unknown
- `enabled`: Required, boolean
- `version`: Required, semantic version string
- `api_key`: Optional, string, masked in UI
- `endpoints`: Required, array, at least one endpoint
- `settings`: Optional, object, service-specific

### Device Configuration Validation
- `device_id`: Required, UUID format
- `device_name`: Required, string, 3-50 characters
- `device_type`: Required, enum: external_api|local_service|hardware
- `status`: Required, enum: online|offline|unknown
- `connection.host`: Required, valid hostname or IP
- `connection.port`: Required, number, 1-65535
- `connection.protocol`: Required, enum: http|https|tcp|udp|mqtt
- `capabilities`: Required, array, at least one capability

### API Key Masking Rules
- Show only last 4 characters: `sk-xxxx`
- Mask middle characters: `sk-whisper-xxxx`
- Preserve prefix: `gsk_xxxx`
- Preserve suffix: `xxxx-token`

This schema provides a comprehensive structure for managing service and device configurations in the Alicia system, ensuring consistency, validation, and security across all components.

