# Alicia Bus Architecture Implementation Guide

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Message Bus Core Components](#message-bus-core-components)
3. [Message Format Standards](#message-format-standards)
4. [Security Architecture](#security-architecture)
5. [Device Discovery Protocol](#device-discovery-protocol)
6. [Service Integration Patterns](#service-integration-patterns)
7. [Configuration Management](#configuration-management)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Performance Specifications](#performance-specifications)
10. [Docker MCP Integration](#docker-mcp-integration)

## System Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    ALICIA MESSAGE BUS CORE                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   MQTT      │  │   Security  │  │  Discovery  │  │ Device  │ │
│  │  Broker     │  │   Gateway   │  │   Service   │  │Registry │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  Message    │  │  Monitoring │  │  Load       │  │  Config │ │
│  │  Router     │  │   Service   │  │  Balancer   │  │Manager  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ Voice Services │    │ Device Services │    │Integration Svc  │
│ ┌─────────────┐│    │ ┌─────────────┐│    │ ┌─────────────┐│
│ │ STT Service ││    │ │Speaker Mgmt ││    │ │HA Bridge    ││
│ │ AI Service  ││    │ │Sensor Data  ││    │ │API Gateway  ││
│ │ TTS Service ││    │ │Actuator Ctrl││    │ │Data Persist ││
│ └─────────────┘│    │ └─────────────┘│    │ └─────────────┘│
└────────────────┘    └────────────────┘    └────────────────┘
```

### Core Principles
1. **Single Communication Channel**: All services communicate through the bus
2. **No Direct Connections**: Services never communicate directly with each other
3. **Message-Based Architecture**: All interactions are message-based
4. **Self-Describing Messages**: Messages contain all necessary metadata
5. **Centralized Security**: All security handled at the bus level

## Message Bus Core Components

### 1. Enhanced MQTT Broker
**Container**: `alicia-bus-core`
**Image**: `eclipse-mosquitto:2.0.18` (latest stable 2.0.x)
**Ports**: 1883 (MQTT), 8883 (MQTTS), 9001 (WebSocket)

#### Configuration
```yaml
# docker-compose.yml
  alicia-bus-core:
    container_name: alicia_bus_core
    image: eclipse-mosquitto:2.0.18
  ports:
    - "1883:1883"
    - "8883:8883"
    - "9001:9001"
  volumes:
    - ./bus-config/mosquitto.conf:/mosquitto/config/mosquitto.conf
    - ./bus-config/passwords:/mosquitto/config/passwords
    - ./bus-config/acl:/mosquitto/config/acl
    - ./bus-data:/mosquitto/data
    - ./bus-logs:/mosquitto/log
  environment:
    - MQTT_BROKER_NAME=alicia-bus-core
    - MQTT_MAX_CONNECTIONS=1000
    - MQTT_MESSAGE_SIZE_LIMIT=268435456
  restart: unless-stopped
  networks:
    - alicia_bus_network
  healthcheck:
    test: ["CMD", "mosquitto_pub", "-h", "localhost", "-t", "test", "-m", "health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### Mosquitto Configuration
```conf
# bus-config/mosquitto.conf
# Basic Configuration
listener 1883
protocol mqtt
max_connections 1000
max_inflight_messages 100
max_queued_messages 1000
message_size_limit 268435456

# Secure Configuration
listener 8883
protocol mqtt
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key
require_certificate true
use_identity_as_username true

# WebSocket Configuration
listener 9001
protocol websockets
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key
require_certificate true
use_identity_as_username true

# Persistence
persistence true
persistence_location /mosquitto/data/
autosave_interval 60

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
log_type debug

# Security
allow_anonymous false
password_file /mosquitto/config/passwords
acl_file /mosquitto/config/acl

# Performance
sys_interval 10
```

### 2. Security Gateway
**Container**: `alicia-security-gateway`
**Image**: Custom Python FastAPI service (Python 3.11.7+, FastAPI 0.104.1+)
**Ports**: 8443 (HTTPS), 8080 (HTTP)

#### Security Gateway Service
```python
# bus-services/security-gateway/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt
import jwt
import ssl
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import json
import logging

app = FastAPI(title="Alicia Security Gateway", version="1.0.0")

class SecurityGateway:
    def __init__(self):
        self.mqtt_client = None
        self.device_certificates = {}
        self.message_encryption_key = None
        self.setup_mqtt()
        self.setup_encryption()
    
    def setup_mqtt(self):
        """Setup MQTT client for bus communication"""
        self.mqtt_client = mqtt.Client("security_gateway")
        self.mqtt_client.username_pw_set("security_gateway", "alicia_security_2024")
        self.mqtt_client.tls_set(ca_certs="certs/ca.crt")
        self.mqtt_client.connect("alicia_bus_core", 8883, 60)
        self.mqtt_client.loop_start()
    
    def setup_encryption(self):
        """Setup message encryption"""
        # Generate or load encryption key
        self.message_encryption_key = self.load_or_generate_key()
    
    def authenticate_device(self, device_certificate: str) -> bool:
        """Authenticate device using certificate"""
        try:
            cert = x509.load_pem_x509_certificate(device_certificate.encode())
            # Validate certificate
            return self.validate_certificate(cert)
        except Exception as e:
            logging.error(f"Device authentication failed: {e}")
            return False
    
    def encrypt_message(self, message: dict) -> str:
        """Encrypt message for secure transmission"""
        # Implementation for message encryption
        pass
    
    def decrypt_message(self, encrypted_message: str) -> dict:
        """Decrypt received message"""
        # Implementation for message decryption
        pass

security_gateway = SecurityGateway()

@app.post("/auth/device")
async def authenticate_device(certificate: str):
    """Authenticate device and issue access token"""
    if security_gateway.authenticate_device(certificate):
        token = jwt.encode({"device_id": "extracted_id"}, "secret", algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/encrypt")
async def encrypt_message(message: dict):
    """Encrypt message for bus transmission"""
    encrypted = security_gateway.encrypt_message(message)
    return {"encrypted_message": encrypted}

@app.post("/decrypt")
async def decrypt_message(encrypted_message: str):
    """Decrypt message from bus"""
    decrypted = security_gateway.decrypt_message(encrypted_message)
    return {"message": decrypted}
```

### 3. Device Registry
**Container**: `alicia-device-registry`
**Image**: Custom Python FastAPI service (Python 3.11.7+, FastAPI 0.104.1+)
**Ports**: 8081 (HTTP)

#### Device Registry Service
```python
# bus-services/device-registry/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import time
import logging

app = FastAPI(title="Alicia Device Registry", version="1.0.0")

class DeviceCapability(BaseModel):
    name: str
    version: str
    parameters: Dict
    endpoints: Dict[str, str]

class Device(BaseModel):
    device_id: str
    device_type: str
    capabilities: List[DeviceCapability]
    endpoints: Dict[str, str]
    metadata: Dict
    status: str = "online"
    last_seen: float = time.time()

class DeviceRegistry:
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.capability_index: Dict[str, List[str]] = {}
    
    def register_device(self, device: Device) -> bool:
        """Register a new device"""
        try:
            self.devices[device.device_id] = device
            self.update_capability_index(device)
            logging.info(f"Device registered: {device.device_id}")
            return True
        except Exception as e:
            logging.error(f"Device registration failed: {e}")
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister a device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            self.remove_from_capability_index(device)
            del self.devices[device_id]
            logging.info(f"Device unregistered: {device_id}")
            return True
        return False
    
    def update_capability_index(self, device: Device):
        """Update capability index for device discovery"""
        for capability in device.capabilities:
            if capability.name not in self.capability_index:
                self.capability_index[capability.name] = []
            if device.device_id not in self.capability_index[capability.name]:
                self.capability_index[capability.name].append(device.device_id)
    
    def find_devices_by_capability(self, capability: str) -> List[Device]:
        """Find devices with specific capability"""
        device_ids = self.capability_index.get(capability, [])
        return [self.devices[device_id] for device_id in device_ids if device_id in self.devices]
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def update_device_status(self, device_id: str, status: str):
        """Update device status"""
        if device_id in self.devices:
            self.devices[device_id].status = status
            self.devices[device_id].last_seen = time.time()

registry = DeviceRegistry()

@app.post("/devices/register")
async def register_device(device: Device):
    """Register a new device"""
    if registry.register_device(device):
        return {"status": "success", "message": "Device registered"}
    raise HTTPException(status_code=400, detail="Device registration failed")

@app.delete("/devices/{device_id}")
async def unregister_device(device_id: str):
    """Unregister a device"""
    if registry.unregister_device(device_id):
        return {"status": "success", "message": "Device unregistered"}
    raise HTTPException(status_code=404, detail="Device not found")

@app.get("/devices")
async def list_devices():
    """List all registered devices"""
    return {"devices": list(registry.devices.values())}

@app.get("/devices/capability/{capability}")
async def find_devices_by_capability(capability: str):
    """Find devices with specific capability"""
    devices = registry.find_devices_by_capability(capability)
    return {"devices": devices}

@app.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get specific device"""
    device = registry.get_device(device_id)
    if device:
        return device
    raise HTTPException(status_code=404, detail="Device not found")
```

### 4. Discovery Service
**Container**: `alicia-discovery-service`
**Image**: Custom Python service (Python 3.11.7+, Paho MQTT 1.6.1+)
**Ports**: 8082 (HTTP)

#### Discovery Service
```python
# bus-services/discovery-service/main.py
import asyncio
import json
import logging
import paho.mqtt.client as mqtt
from typing import Dict, List
import time

class DiscoveryService:
    def __init__(self):
        self.mqtt_client = None
        self.discovered_devices = {}
        self.setup_mqtt()
    
    def setup_mqtt(self):
        """Setup MQTT client for discovery"""
        self.mqtt_client = mqtt.Client("discovery_service")
        self.mqtt_client.username_pw_set("discovery_service", "alicia_discovery_2024")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("alicia_bus_core", 1883, 60)
        self.mqtt_client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logging.info("Discovery service connected to MQTT broker")
            # Subscribe to discovery topics
            client.subscribe("alicia/system/discovery/register")
            client.subscribe("alicia/system/discovery/unregister")
            client.subscribe("alicia/system/discovery/heartbeat")
        else:
            logging.error(f"Discovery service connection failed: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle discovery messages"""
        try:
            payload = json.loads(msg.payload.decode())
            
            if msg.topic == "alicia/system/discovery/register":
                self.handle_device_registration(payload)
            elif msg.topic == "alicia/system/discovery/unregister":
                self.handle_device_unregistration(payload)
            elif msg.topic == "alicia/system/discovery/heartbeat":
                self.handle_device_heartbeat(payload)
                
        except Exception as e:
            logging.error(f"Error processing discovery message: {e}")
    
    def handle_device_registration(self, payload):
        """Handle device registration"""
        device_id = payload.get("device_id")
        if device_id:
            self.discovered_devices[device_id] = {
                "payload": payload,
                "last_seen": time.time(),
                "status": "online"
            }
            logging.info(f"Device registered: {device_id}")
            
            # Notify device registry
            self.notify_device_registry(payload)
    
    def handle_device_unregistration(self, payload):
        """Handle device unregistration"""
        device_id = payload.get("device_id")
        if device_id and device_id in self.discovered_devices:
            del self.discovered_devices[device_id]
            logging.info(f"Device unregistered: {device_id}")
            
            # Notify device registry
            self.notify_device_registry_unregister(payload)
    
    def handle_device_heartbeat(self, payload):
        """Handle device heartbeat"""
        device_id = payload.get("device_id")
        if device_id and device_id in self.discovered_devices:
            self.discovered_devices[device_id]["last_seen"] = time.time()
            self.discovered_devices[device_id]["status"] = "online"
    
    def notify_device_registry(self, device_data):
        """Notify device registry of new device"""
        # Send to device registry service
        registry_payload = {
            "device_id": device_data["device_id"],
            "device_type": device_data["device_type"],
            "capabilities": device_data["capabilities"],
            "endpoints": device_data["endpoints"],
            "metadata": device_data["metadata"]
        }
        
        # Publish to device registry topic
        self.mqtt_client.publish(
            "alicia/system/registry/register",
            json.dumps(registry_payload)
        )
    
    def check_device_health(self):
        """Check device health and mark offline if needed"""
        current_time = time.time()
        for device_id, device_info in self.discovered_devices.items():
            if current_time - device_info["last_seen"] > 300:  # 5 minutes
                device_info["status"] = "offline"
                logging.warning(f"Device marked offline: {device_id}")

# Start discovery service
if __name__ == "__main__":
    discovery_service = DiscoveryService()
    
    # Run health check loop
    while True:
        discovery_service.check_device_health()
        time.sleep(60)  # Check every minute
```

## Message Format Standards

### Standard Message Format
```json
{
  "message_id": "uuid-v4",
  "timestamp": "2025-01-08T14:30:00.000Z",
  "source": "service_name",
  "destination": "service_name|broadcast|capability:capability_name",
  "message_type": "request|response|event|command|heartbeat",
  "priority": "low|normal|high|critical",
  "ttl": 300,
  "payload": {
    "data": "actual_message_content",
    "metadata": {
      "version": "1.0.0",
      "content_type": "application/json",
      "encoding": "utf-8"
    }
  },
  "security": {
    "signature": "message_signature",
    "encryption": "aes-256-gcm",
    "key_id": "encryption_key_id"
  },
  "routing": {
    "hops": 0,
    "max_hops": 10,
    "route": ["service1", "service2"]
  }
}
```

### Voice Processing Messages
```json
{
  "message_id": "voice-stt-001",
  "timestamp": "2025-01-08T14:30:00.000Z",
  "source": "voice_input",
  "destination": "capability:speech_to_text",
  "message_type": "request",
  "priority": "high",
  "payload": {
    "data": {
      "audio_data": "base64_encoded_audio",
      "audio_format": "wav",
      "sample_rate": 16000,
      "channels": 1,
      "language": "en-US",
      "confidence_threshold": 0.8
    },
    "metadata": {
      "session_id": "session-123",
      "user_id": "user-456",
      "device_id": "microphone-001"
    }
  }
}
```

### Device Control Messages
```json
{
  "message_id": "device-control-001",
  "timestamp": "2025-01-08T14:30:00.000Z",
  "source": "voice_processor",
  "destination": "device_id:sonos_kitchen_001",
  "message_type": "command",
  "priority": "normal",
  "payload": {
    "data": {
      "command": "play_audio",
      "parameters": {
        "audio_url": "http://192.168.1.100:8080/audio/sample.wav",
        "volume": 30,
        "fade_in": true
      }
    },
    "metadata": {
      "session_id": "session-123",
      "user_id": "user-456",
      "command_source": "voice_command"
    }
  }
}
```

## Security Architecture

### Certificate Management
```bash
# Generate CA certificate
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt -subj "/C=US/ST=State/L=City/O=Alicia/CN=Alicia-CA"

# Generate server certificate
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=State/L=City/O=Alicia/CN=alicia-bus-core"
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -out server.crt

# Generate device certificate
openssl genrsa -out device.key 4096
openssl req -new -key device.key -out device.csr -subj "/C=US/ST=State/L=City/O=Alicia/CN=device-001"
openssl x509 -req -days 365 -in device.csr -CA ca.crt -CAkey ca.key -out device.crt
```

### Access Control Lists (ACL)
```conf
# bus-config/acl
# System topics - only system services
user security_gateway
topic readwrite alicia/system/#
topic readwrite $SYS/#

user device_registry
topic readwrite alicia/system/registry/#
topic readwrite alicia/system/discovery/#

user discovery_service
topic readwrite alicia/system/discovery/#
topic readwrite alicia/system/registry/#

# Voice processing topics
user stt_service
topic readwrite alicia/voice/stt/#
topic read alicia/voice/command/#

user ai_service
topic readwrite alicia/voice/ai/#
topic read alicia/voice/stt/response

user tts_service
topic readwrite alicia/voice/tts/#
topic read alicia/voice/ai/response

# Device topics
user sonos_kitchen_001
topic readwrite alicia/devices/sonos_kitchen_001/#
topic read alicia/devices/speakers/announce

user esp32_sensor_001
topic readwrite alicia/devices/esp32_sensor_001/#
topic read alicia/devices/sensors/telemetry
```

## Device Discovery Protocol

### Device Registration Message
```json
{
  "message_id": "device-reg-001",
  "timestamp": "2025-01-08T14:30:00.000Z",
  "source": "sonos_kitchen_001",
  "destination": "alicia/system/discovery/register",
  "message_type": "event",
  "payload": {
    "data": {
      "device_id": "sonos_kitchen_001",
      "device_type": "speaker",
      "capabilities": [
        {
          "name": "audio_playback",
          "version": "1.0.0",
          "parameters": {
            "supported_formats": ["wav", "mp3", "flac"],
            "max_volume": 100,
            "min_volume": 0
          },
          "endpoints": {
            "input": "alicia/devices/sonos_kitchen_001/audio",
            "control": "alicia/devices/sonos_kitchen_001/command",
            "status": "alicia/devices/sonos_kitchen_001/status"
          }
        },
        {
          "name": "volume_control",
          "version": "1.0.0",
          "parameters": {
            "step_size": 1,
            "mute_support": true
          },
          "endpoints": {
            "input": "alicia/devices/sonos_kitchen_001/volume",
            "status": "alicia/devices/sonos_kitchen_001/volume_status"
          }
        }
      ],
      "endpoints": {
        "control": "alicia/devices/sonos_kitchen_001/command",
        "status": "alicia/devices/sonos_kitchen_001/status",
        "audio": "alicia/devices/sonos_kitchen_001/audio"
      },
      "metadata": {
        "manufacturer": "Sonos",
        "model": "One",
        "location": "kitchen",
        "version": "1.0.0",
        "ip_address": "192.168.1.101",
        "mac_address": "00:11:22:33:44:55"
      }
    }
  }
}
```

### Capability Discovery
```python
# bus-services/capability-discovery/main.py
class CapabilityDiscovery:
    def __init__(self):
        self.capabilities = {}
        self.device_capabilities = {}
    
    def register_capability(self, capability_name: str, device_id: str, capability_info: dict):
        """Register device capability"""
        if capability_name not in self.capabilities:
            self.capabilities[capability_name] = []
        
        capability_entry = {
            "device_id": device_id,
            "capability_info": capability_info,
            "registered_at": time.time()
        }
        
        self.capabilities[capability_name].append(capability_entry)
        self.device_capabilities[device_id] = capability_entry
    
    def find_capability_providers(self, capability_name: str) -> List[dict]:
        """Find devices that provide a specific capability"""
        return self.capabilities.get(capability_name, [])
    
    def get_device_capabilities(self, device_id: str) -> List[dict]:
        """Get all capabilities for a device"""
        return self.device_capabilities.get(device_id, [])
```

## Service Integration Patterns

### Service Wrapper Pattern
```python
# bus-services/service-wrapper/base.py
class BusServiceWrapper:
    def __init__(self, service_name: str, mqtt_config: dict):
        self.service_name = service_name
        self.mqtt_client = None
        self.setup_mqtt(mqtt_config)
    
    def setup_mqtt(self, config: dict):
        """Setup MQTT client for bus communication"""
        self.mqtt_client = mqtt.Client(self.service_name)
        self.mqtt_client.username_pw_set(config["username"], config["password"])
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(config["host"], config["port"], 60)
        self.mqtt_client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logging.info(f"{self.service_name} connected to bus")
            self.subscribe_to_topics()
        else:
            logging.error(f"{self.service_name} connection failed: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            message = json.loads(msg.payload.decode())
            self.process_message(msg.topic, message)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
    
    def publish_message(self, topic: str, message: dict):
        """Publish message to bus"""
        message["source"] = self.service_name
        message["timestamp"] = datetime.utcnow().isoformat()
        self.mqtt_client.publish(topic, json.dumps(message))
    
    def subscribe_to_topics(self):
        """Subscribe to relevant topics - override in subclasses"""
        pass
    
    def process_message(self, topic: str, message: dict):
        """Process incoming message - override in subclasses"""
        pass
```

### STT Service Integration
```python
# bus-services/stt-service/main.py
class STTService(BusServiceWrapper):
    def __init__(self):
        mqtt_config = {
            "host": "alicia_bus_core",
            "port": 1883,
            "username": "stt_service",
            "password": "alicia_stt_2024"
        }
        super().__init__("stt_service", mqtt_config)
        self.whisper_client = None
        self.setup_whisper()
    
    def setup_whisper(self):
        """Setup Whisper STT client"""
        # Initialize Whisper client
        pass
    
    def subscribe_to_topics(self):
        """Subscribe to STT request topics"""
        self.mqtt_client.subscribe("alicia/voice/stt/request")
        self.mqtt_client.subscribe("capability:speech_to_text")
    
    def process_message(self, topic: str, message: dict):
        """Process STT requests"""
        if topic in ["alicia/voice/stt/request", "capability:speech_to_text"]:
            self.process_stt_request(message)
    
    def process_stt_request(self, message: dict):
        """Process speech-to-text request"""
        try:
            audio_data = message["payload"]["data"]["audio_data"]
            language = message["payload"]["data"].get("language", "en-US")
            
            # Process with Whisper
            transcription = self.transcribe_audio(audio_data, language)
            
            # Send response
            response = {
                "message_id": f"stt-response-{uuid.uuid4().hex[:8]}",
                "destination": message["source"],
                "message_type": "response",
                "payload": {
                    "data": {
                        "transcription": transcription["text"],
                        "confidence": transcription["confidence"],
                        "language": transcription["language"]
                    },
                    "metadata": message["payload"]["metadata"]
                }
            }
            
            self.publish_message("alicia/voice/stt/response", response)
            
        except Exception as e:
            logging.error(f"STT processing failed: {e}")
            self.send_error_response(message, str(e))
    
    def transcribe_audio(self, audio_data: str, language: str) -> dict:
        """Transcribe audio using Whisper"""
        # Implementation for Whisper transcription
        pass
```

## Configuration Management

### Centralized Configuration Service
```python
# bus-services/config-service/main.py
class ConfigurationService:
    def __init__(self):
        self.configurations = {}
        self.environments = ["development", "staging", "production"]
        self.load_configurations()
    
    def load_configurations(self):
        """Load configurations from files"""
        for env in self.environments:
            config_file = f"config/{env}.yaml"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.configurations[env] = yaml.safe_load(f)
    
    def get_configuration(self, service: str, environment: str = "production") -> dict:
        """Get configuration for a service"""
        env_config = self.configurations.get(environment, {})
        return env_config.get(service, {})
    
    def update_configuration(self, service: str, config: dict, environment: str = "production"):
        """Update service configuration"""
        if environment not in self.configurations:
            self.configurations[environment] = {}
        
        self.configurations[environment][service] = config
        self.save_configuration(environment)
    
    def save_configuration(self, environment: str):
        """Save configuration to file"""
        config_file = f"config/{environment}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.configurations[environment], f)
```

### Environment-Specific Configurations
```yaml
# config/development.yaml
mqtt:
  broker: "localhost"
  port: 1883
  username: "dev_user"
  password: "dev_password"

stt_service:
  whisper:
    model: "base"
    language: "en"
  performance:
    max_audio_length: 30
    timeout: 10

tts_service:
  piper:
    voice: "en_US-lessac-medium"
    quality: "medium"
  performance:
    cache_size: 100
    timeout: 15

security:
  encryption: false
  certificate_validation: false
  rate_limiting: false
```

```yaml
# config/production.yaml
mqtt:
  broker: "alicia_bus_core"
  port: 8883
  username: "prod_user"
  password: "prod_password"
  tls: true

stt_service:
  whisper:
    model: "large"
    language: "en"
  performance:
    max_audio_length: 60
    timeout: 30

tts_service:
  piper:
    voice: "en_US-lessac-medium"
    quality: "high"
  performance:
    cache_size: 1000
    timeout: 30

security:
  encryption: true
  certificate_validation: true
  rate_limiting: true
  max_requests_per_minute: 100
```

## Monitoring and Observability

### Health Monitoring Service
```python
# bus-services/health-monitor/main.py
class HealthMonitor:
    def __init__(self):
        self.services = {}
        self.metrics = {}
        self.alerts = []
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Setup health monitoring"""
        self.start_health_checks()
        self.start_metrics_collection()
        self.start_alert_processing()
    
    def start_health_checks(self):
        """Start periodic health checks"""
        def health_check_loop():
            while True:
                self.check_all_services()
                time.sleep(30)  # Check every 30 seconds
        
        threading.Thread(target=health_check_loop, daemon=True).start()
    
    def check_all_services(self):
        """Check health of all services"""
        for service_name, service_info in self.services.items():
            health_status = self.check_service_health(service_name, service_info)
            self.update_service_status(service_name, health_status)
    
    def check_service_health(self, service_name: str, service_info: dict) -> dict:
        """Check health of a specific service"""
        try:
            # Check MQTT connectivity
            mqtt_health = self.check_mqtt_health(service_name)
            
            # Check service endpoint
            endpoint_health = self.check_endpoint_health(service_info.get("endpoint"))
            
            # Check resource usage
            resource_health = self.check_resource_usage(service_name)
            
            return {
                "status": "healthy" if all([mqtt_health, endpoint_health, resource_health]) else "unhealthy",
                "mqtt": mqtt_health,
                "endpoint": endpoint_health,
                "resources": resource_health,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def collect_metrics(self, service_name: str, metrics: dict):
        """Collect metrics from a service"""
        if service_name not in self.metrics:
            self.metrics[service_name] = []
        
        metrics["timestamp"] = time.time()
        self.metrics[service_name].append(metrics)
        
        # Keep only last 1000 metrics per service
        if len(self.metrics[service_name]) > 1000:
            self.metrics[service_name] = self.metrics[service_name][-1000:]
    
    def generate_alerts(self, service_name: str, health_status: dict):
        """Generate alerts based on health status"""
        if health_status["status"] == "unhealthy":
            alert = {
                "service": service_name,
                "severity": "critical",
                "message": f"Service {service_name} is unhealthy",
                "timestamp": time.time(),
                "details": health_status
            }
            self.alerts.append(alert)
            self.send_alert(alert)
```

### Metrics Collection
```python
# bus-services/metrics-collector/main.py
class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.start_collection()
    
    def start_collection(self):
        """Start metrics collection"""
        def collect_loop():
            while True:
                self.collect_system_metrics()
                self.collect_service_metrics()
                self.collect_message_metrics()
                time.sleep(10)  # Collect every 10 seconds
        
        threading.Thread(target=collect_loop, daemon=True).start()
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        import psutil
        
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "timestamp": time.time()
        }
        
        self.store_metrics("system", system_metrics)
    
    def collect_service_metrics(self):
        """Collect service-specific metrics"""
        # Collect metrics from each service
        for service_name in self.get_active_services():
            service_metrics = self.get_service_metrics(service_name)
            self.store_metrics(service_name, service_metrics)
    
    def collect_message_metrics(self):
        """Collect message bus metrics"""
        message_metrics = {
            "messages_per_second": self.calculate_message_rate(),
            "queue_depth": self.get_queue_depth(),
            "connection_count": self.get_connection_count(),
            "timestamp": time.time()
        }
        
        self.store_metrics("message_bus", message_metrics)
```

## Performance Specifications

### Latency Requirements
- **Voice Command Processing**: < 500ms end-to-end
- **Device Control Response**: < 100ms
- **Audio Delivery**: < 200ms
- **System Health Checks**: < 50ms
- **Message Routing**: < 10ms

### Throughput Requirements
- **Message Processing**: 1000+ messages per second
- **Concurrent Devices**: 100+ devices
- **Simultaneous Voice Sessions**: 10+ sessions
- **System Availability**: 99.9% uptime

### Resource Requirements
- **CPU**: 2+ cores per service
- **Memory**: 512MB+ per service
- **Storage**: 1GB+ for logs and data
- **Network**: 100Mbps+ bandwidth

## Docker MCP Integration

### Container Management
```python
# bus-services/docker-manager/main.py
class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Setup container monitoring"""
        self.start_container_monitoring()
        self.start_log_monitoring()
    
    def start_container_monitoring(self):
        """Monitor container health"""
        def monitor_loop():
            while True:
                self.check_container_health()
                time.sleep(30)
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def check_container_health(self):
        """Check health of all containers"""
        for container_name, container_info in self.containers.items():
            try:
                container = self.client.containers.get(container_name)
                health_status = self.get_container_health(container)
                self.update_container_status(container_name, health_status)
            except Exception as e:
                logging.error(f"Error checking container {container_name}: {e}")
    
    def get_container_health(self, container) -> dict:
        """Get container health status"""
        try:
            health = container.attrs.get("State", {}).get("Health", {})
            return {
                "status": health.get("Status", "unknown"),
                "started_at": container.attrs.get("State", {}).get("StartedAt"),
                "restart_count": container.attrs.get("RestartCount", 0),
                "memory_usage": container.attrs.get("MemoryStats", {}).get("Usage", 0),
                "cpu_usage": self.calculate_cpu_usage(container)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def start_log_monitoring(self):
        """Monitor container logs"""
        def log_monitor_loop():
            while True:
                self.collect_logs()
                time.sleep(60)  # Collect logs every minute
        
        threading.Thread(target=log_monitor_loop, daemon=True).start()
    
    def collect_logs(self):
        """Collect logs from all containers"""
        for container_name in self.containers:
            try:
                container = self.client.containers.get(container_name)
                logs = container.logs(tail=100, timestamps=True)
                self.process_logs(container_name, logs)
            except Exception as e:
                logging.error(f"Error collecting logs from {container_name}: {e}")
    
    def process_logs(self, container_name: str, logs: bytes):
        """Process container logs"""
        log_lines = logs.decode('utf-8').split('\n')
        for line in log_lines:
            if line.strip():
                self.analyze_log_line(container_name, line)
    
    def analyze_log_line(self, container_name: str, line: str):
        """Analyze log line for errors or important events"""
        if "ERROR" in line or "FATAL" in line:
            self.handle_error_log(container_name, line)
        elif "WARN" in line:
            self.handle_warning_log(container_name, line)
        elif "INFO" in line and "connected" in line.lower():
            self.handle_connection_log(container_name, line)
```

### Log Analysis and Alerting
```python
# bus-services/log-analyzer/main.py
class LogAnalyzer:
    def __init__(self):
        self.error_patterns = [
            r"ERROR.*connection.*failed",
            r"FATAL.*out of memory",
            r"ERROR.*authentication.*failed",
            r"ERROR.*mqtt.*disconnected"
        ]
        self.warning_patterns = [
            r"WARN.*timeout",
            r"WARN.*retry",
            r"WARN.*performance"
        ]
    
    def analyze_logs(self, container_name: str, logs: list):
        """Analyze logs for issues"""
        for log_line in logs:
            self.check_error_patterns(container_name, log_line)
            self.check_warning_patterns(container_name, log_line)
    
    def check_error_patterns(self, container_name: str, log_line: str):
        """Check for error patterns"""
        for pattern in self.error_patterns:
            if re.search(pattern, log_line, re.IGNORECASE):
                self.handle_error(container_name, log_line, pattern)
    
    def check_warning_patterns(self, container_name: str, log_line: str):
        """Check for warning patterns"""
        for pattern in self.warning_patterns:
            if re.search(pattern, log_line, re.IGNORECASE):
                self.handle_warning(container_name, log_line, pattern)
    
    def handle_error(self, container_name: str, log_line: str, pattern: str):
        """Handle error detection"""
        alert = {
            "type": "error",
            "container": container_name,
            "message": log_line,
            "pattern": pattern,
            "timestamp": time.time(),
            "severity": "critical"
        }
        self.send_alert(alert)
    
    def handle_warning(self, container_name: str, log_line: str, pattern: str):
        """Handle warning detection"""
        alert = {
            "type": "warning",
            "container": container_name,
            "message": log_line,
            "pattern": pattern,
            "timestamp": time.time(),
            "severity": "warning"
        }
        self.send_alert(alert)
```

This implementation guide provides the detailed technical specifications, code examples, and configuration details needed to implement the bus architecture migration. The guide includes comprehensive examples for all major components and demonstrates how to integrate with Docker MCP for monitoring and management.
