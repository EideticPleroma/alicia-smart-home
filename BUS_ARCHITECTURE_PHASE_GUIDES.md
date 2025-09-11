# Alicia Bus Architecture - Phase-by-Phase Implementation Guide

## Phase 1: Bus Core Infrastructure (Weeks 1-2)

### Week 1: Foundation Setup

#### Day 1-2: Enhanced MQTT Broker
**Objective**: Deploy secure MQTT broker with authentication and encryption

**Tasks**:
1. **Create bus configuration directory**:
   ```bash
   mkdir -p bus-config bus-data bus-logs bus-services
   ```

2. **Deploy enhanced MQTT broker**:
   ```yaml
   # docker-compose.bus.yml
   version: '3.8'
   services:
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
       restart: unless-stopped
       networks:
         - alicia_bus_network
   ```

3. **Configure Mosquitto**:
   ```conf
   # bus-config/mosquitto.conf
   listener 1883
   protocol mqtt
   max_connections 1000
   allow_anonymous false
   password_file /mosquitto/config/passwords
   acl_file /mosquitto/config/acl
   ```

4. **Setup user authentication**:
   ```bash
   # Generate password file
   mosquitto_passwd -c bus-config/passwords security_gateway
   mosquitto_passwd -b bus-config/passwords device_registry alicia_registry_2024
   mosquitto_passwd -b bus-config/passwords discovery_service alicia_discovery_2024
   ```

**Docker MCP Commands**:
```bash
# Start the bus core
docker-compose -f docker-compose.bus.yml up -d alicia-bus-core

# Monitor logs
docker logs -f alicia_bus_core

# Check health
docker exec alicia_bus_core mosquitto_pub -h localhost -t test -m "health"
```

#### Day 3-4: Security Gateway
**Objective**: Implement centralized security and authentication

**Tasks**:
1. **Create security gateway service**:
   ```python
   # bus-services/security-gateway/main.py
   # Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+, PyJWT 2.8.0+
   from fastapi import FastAPI
   import paho.mqtt.client as mqtt
   import jwt
   import ssl
   
   app = FastAPI(title="Alicia Security Gateway")
   
   class SecurityGateway:
       def __init__(self):
           self.mqtt_client = None
           self.device_certificates = {}
           self.setup_mqtt()
       
       def setup_mqtt(self):
           self.mqtt_client = mqtt.Client("security_gateway")
           self.mqtt_client.username_pw_set("security_gateway", "alicia_security_2024")
           self.mqtt_client.connect("alicia_bus_core", 1883, 60)
           self.mqtt_client.loop_start()
   ```

2. **Deploy security gateway**:
   ```yaml
   # Add to docker-compose.bus.yml
   security-gateway:
     container_name: alicia_security_gateway
     build: ./bus-services/security-gateway
     ports:
       - "8443:8443"
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Build and start security gateway
docker-compose -f docker-compose.bus.yml up -d security-gateway

# Monitor security gateway logs
docker logs -f alicia_security_gateway

# Test authentication endpoint
curl -X POST http://localhost:8443/auth/device -d '{"certificate":"test_cert"}'
```

#### Day 5-7: Device Registry & Discovery
**Objective**: Implement device registration and discovery services

**Tasks**:
1. **Create device registry service**:
   ```python
   # bus-services/device-registry/main.py
   # Python 3.11.7+, FastAPI 0.104.1+, Pydantic 2.5.0+
   from fastapi import FastAPI
   from pydantic import BaseModel
   from typing import Dict, List
   
   app = FastAPI(title="Alicia Device Registry")
   
   class Device(BaseModel):
       device_id: str
       device_type: str
       capabilities: List[dict]
       endpoints: Dict[str, str]
       metadata: Dict
       status: str = "online"
   
   class DeviceRegistry:
       def __init__(self):
           self.devices: Dict[str, Device] = {}
           self.capability_index: Dict[str, List[str]] = {}
   ```

2. **Create discovery service**:
   ```python
   # bus-services/discovery-service/main.py
   # Python 3.11.7+, Paho MQTT 1.6.1+
   import paho.mqtt.client as mqtt
   import json
   
   class DiscoveryService:
       def __init__(self):
           self.mqtt_client = None
           self.discovered_devices = {}
           self.setup_mqtt()
       
       def setup_mqtt(self):
           self.mqtt_client = mqtt.Client("discovery_service")
           self.mqtt_client.username_pw_set("discovery_service", "alicia_discovery_2024")
           self.mqtt_client.on_connect = self.on_connect
           self.mqtt_client.on_message = self.on_message
           self.mqtt_client.connect("alicia_bus_core", 1883, 60)
           self.mqtt_client.loop_start()
   ```

**Docker MCP Commands**:
```bash
# Deploy registry and discovery services
docker-compose -f docker-compose.bus.yml up -d device-registry discovery-service

# Monitor service logs
docker logs -f alicia_device_registry
docker logs -f alicia_discovery_service

# Test device registration
mosquitto_pub -h localhost -t "alicia/system/discovery/register" \
  -m '{"device_id":"test_device","device_type":"sensor","capabilities":[]}'
```

### Week 2: Monitoring & Configuration

#### Day 8-10: Health Monitoring
**Objective**: Implement centralized health monitoring

**Tasks**:
1. **Create health monitoring service**:
   ```python
   # bus-services/health-monitor/main.py
   import threading
   import time
   import requests
   
   class HealthMonitor:
       def __init__(self):
           self.services = {}
           self.metrics = {}
           self.start_monitoring()
       
       def start_monitoring(self):
           def monitor_loop():
               while True:
                   self.check_all_services()
                   time.sleep(30)
           threading.Thread(target=monitor_loop, daemon=True).start()
   ```

2. **Deploy monitoring service**:
   ```yaml
   # Add to docker-compose.bus.yml
   health-monitor:
     container_name: alicia_health_monitor
     build: ./bus-services/health-monitor
     ports:
       - "8083:8083"
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy health monitor
docker-compose -f docker-compose.bus.yml up -d health-monitor

# Check health status
curl http://localhost:8083/health

# Monitor health logs
docker logs -f alicia_health_monitor
```

#### Day 11-14: Configuration Management
**Objective**: Implement centralized configuration service

**Tasks**:
1. **Create configuration service**:
   ```python
   # bus-services/config-service/main.py
   import yaml
   import os
   
   class ConfigurationService:
       def __init__(self):
           self.configurations = {}
           self.environments = ["development", "staging", "production"]
           self.load_configurations()
       
       def load_configurations(self):
           for env in self.environments:
               config_file = f"config/{env}.yaml"
               if os.path.exists(config_file):
                   with open(config_file, 'r') as f:
                       self.configurations[env] = yaml.safe_load(f)
   ```

2. **Create environment configurations**:
   ```yaml
   # config/development.yaml
   mqtt:
     broker: "alicia_bus_core"
     port: 1883
     username: "dev_user"
     password: "dev_password"
   
   security:
     encryption: false
     certificate_validation: false
   ```

**Docker MCP Commands**:
```bash
# Deploy config service
docker-compose -f docker-compose.bus.yml up -d config-service

# Test configuration retrieval
curl http://localhost:8084/config/stt_service/development

# Monitor config service logs
docker logs -f alicia_config_service
```

## Phase 2: Voice Pipeline Migration (Weeks 3-4)

### Week 3: STT Service Migration

#### Day 15-17: STT Service Wrapper
**Objective**: Migrate STT service to bus architecture

**Tasks**:
1. **Create STT service wrapper**:
   ```python
   # bus-services/stt-service/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   import whisper
   
   class STTService(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "stt_service",
               "password": "alicia_stt_2024"
           }
           super().__init__("stt_service", mqtt_config)
           self.whisper_model = whisper.load_model("base")
       
       def subscribe_to_topics(self):
           self.mqtt_client.subscribe("alicia/voice/stt/request")
           self.mqtt_client.subscribe("capability:speech_to_text")
       
       def process_message(self, topic: str, message: dict):
           if topic in ["alicia/voice/stt/request", "capability:speech_to_text"]:
               self.process_stt_request(message)
   ```

2. **Deploy STT service**:
   ```yaml
   # Add to docker-compose.bus.yml
   stt-service:
     container_name: alicia_stt_service
     build: ./bus-services/stt-service
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy STT service
docker-compose -f docker-compose.bus.yml up -d stt-service

# Test STT service
mosquitto_pub -h localhost -t "alicia/voice/stt/request" \
  -m '{"audio_data":"base64_audio","language":"en-US"}'

# Monitor STT logs
docker logs -f alicia_stt_service
```

#### Day 18-21: AI Service Migration
**Objective**: Migrate Grok AI service to bus architecture

**Tasks**:
1. **Create AI service wrapper**:
   ```python
   # bus-services/ai-service/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   from grok_handler import GrokHandler
   
   class AIService(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "ai_service",
               "password": "alicia_ai_2024"
           }
           super().__init__("ai_service", mqtt_config)
           self.grok_handler = GrokHandler()
       
       def subscribe_to_topics(self):
           self.mqtt_client.subscribe("alicia/voice/ai/request")
           self.mqtt_client.subscribe("alicia/voice/stt/response")
   ```

2. **Deploy AI service**:
   ```yaml
   # Add to docker-compose.bus.yml
   ai-service:
     container_name: alicia_ai_service
     build: ./bus-services/ai-service
     environment:
       - GROK_API_KEY=${GROK_API_KEY}
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy AI service
docker-compose -f docker-compose.bus.yml up -d ai-service

# Test AI service
mosquitto_pub -h localhost -t "alicia/voice/ai/request" \
  -m '{"text":"Hello Alicia","context":{}}'

# Monitor AI logs
docker logs -f alicia_ai_service
```

### Week 4: TTS Service Migration

#### Day 22-24: TTS Service Wrapper
**Objective**: Migrate TTS service to bus architecture

**Tasks**:
1. **Create TTS service wrapper**:
   ```python
   # bus-services/tts-service/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   import piper
   
   class TTSService(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "tts_service",
               "password": "alicia_tts_2024"
           }
           super().__init__("tts_service", mqtt_config)
           self.piper_model = piper.load_model("en_US-lessac-medium")
       
       def subscribe_to_topics(self):
           self.mqtt_client.subscribe("alicia/voice/tts/request")
           self.mqtt_client.subscribe("alicia/voice/ai/response")
   ```

2. **Deploy TTS service**:
   ```yaml
   # Add to docker-compose.bus.yml
   tts-service:
     container_name: alicia_tts_service
     build: ./bus-services/tts-service
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy TTS service
docker-compose -f docker-compose.bus.yml up -d tts-service

# Test TTS service
mosquitto_pub -h localhost -t "alicia/voice/tts/request" \
  -m '{"text":"Hello world","voice":"en_US-lessac-medium"}'

# Monitor TTS logs
docker logs -f alicia_tts_service
```

#### Day 25-28: Voice Router & Integration
**Objective**: Create voice command router and integrate all voice services

**Tasks**:
1. **Create voice router**:
   ```python
   # bus-services/voice-router/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   
   class VoiceRouter(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "voice_router",
               "password": "alicia_router_2024"
           }
           super().__init__("voice_router", mqtt_config)
       
       def subscribe_to_topics(self):
           self.mqtt_client.subscribe("alicia/voice/command/route")
           self.mqtt_client.subscribe("alicia/voice/tts/response")
   ```

2. **Deploy voice router**:
   ```yaml
   # Add to docker-compose.bus.yml
   voice-router:
     container_name: alicia_voice_router
     build: ./bus-services/voice-router
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy voice router
docker-compose -f docker-compose.bus.yml up -d voice-router

# Test complete voice pipeline
mosquitto_pub -h localhost -t "alicia/voice/command/route" \
  -m '{"audio_data":"base64_audio","session_id":"test123"}'

# Monitor all voice services
docker logs -f alicia_stt_service alicia_ai_service alicia_tts_service alicia_voice_router
```

## Phase 3: Device Integration (Weeks 5-6)

### Week 5: Speaker Services

#### Day 29-31: Sonos Integration
**Objective**: Migrate Sonos integration to bus architecture

**Tasks**:
1. **Create Sonos service**:
   ```python
   # bus-services/sonos-service/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   import soco
   
   class SonosService(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "sonos_service",
               "password": "alicia_sonos_2024"
           }
           super().__init__("sonos_service", mqtt_config)
           self.sonos_devices = self.discover_sonos_devices()
       
       def discover_sonos_devices(self):
           return soco.discover()
   ```

2. **Deploy Sonos service**:
   ```yaml
   # Add to docker-compose.bus.yml
   sonos-service:
     container_name: alicia_sonos_service
     build: ./bus-services/sonos-service
     network_mode: host
     depends_on:
       - alicia-bus-core
   ```

**Docker MCP Commands**:
```bash
# Deploy Sonos service
docker-compose -f docker-compose.bus.yml up -d sonos-service

# Test Sonos integration
mosquitto_pub -h localhost -t "alicia/devices/speakers/announce" \
  -m '{"device_id":"kitchen","audio_url":"http://192.168.1.100:8080/audio/test.wav"}'

# Monitor Sonos logs
docker logs -f alicia_sonos_service
```

#### Day 32-35: Device Management
**Objective**: Implement device management and control

**Tasks**:
1. **Create device manager**:
   ```python
   # bus-services/device-manager/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   
   class DeviceManager(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "device_manager",
               "password": "alicia_devices_2024"
           }
           super().__init__("device_manager", mqtt_config)
           self.devices = {}
       
       def subscribe_to_topics(self):
           self.mqtt_client.subscribe("alicia/devices/+/command")
           self.mqtt_client.subscribe("alicia/devices/+/status")
   ```

2. **Deploy device manager**:
   ```yaml
   # Add to docker-compose.bus.yml
   device-manager:
     container_name: alicia_device_manager
     build: ./bus-services/device-manager
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy device manager
docker-compose -f docker-compose.bus.yml up -d device-manager

# Test device management
mosquitto_pub -h localhost -t "alicia/devices/sonos_kitchen_001/command" \
  -m '{"command":"set_volume","parameters":{"volume":50}}'

# Monitor device manager logs
docker logs -f alicia_device_manager
```

### Week 6: Home Assistant Integration

#### Day 36-38: HA Bridge Service
**Objective**: Create Home Assistant bridge for bus communication

**Tasks**:
1. **Create HA bridge**:
   ```python
   # bus-services/ha-bridge/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   import requests
   
   class HABridge(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "ha_bridge",
               "password": "alicia_ha_2024"
           }
           super().__init__("ha_bridge", mqtt_config)
           self.ha_url = "http://homeassistant:8123"
           self.ha_token = os.getenv("HA_TOKEN")
   ```

2. **Deploy HA bridge**:
   ```yaml
   # Add to docker-compose.bus.yml
   ha-bridge:
     container_name: alicia_ha_bridge
     build: ./bus-services/ha-bridge
     environment:
       - HA_TOKEN=${HA_TOKEN}
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy HA bridge
docker-compose -f docker-compose.bus.yml up -d ha-bridge

# Test HA integration
mosquitto_pub -h localhost -t "alicia/integration/ha/command" \
  -m '{"entity_id":"light.kitchen","service":"turn_on"}'

# Monitor HA bridge logs
docker logs -f alicia_ha_bridge
```

#### Day 39-42: Complete Integration Testing
**Objective**: Test complete system integration

**Tasks**:
1. **Create integration tests**:
   ```python
   # tests/integration_test.py
   import pytest
   import paho.mqtt.client as mqtt
   import time
   
   class TestBusIntegration:
       def test_voice_pipeline(self):
           # Test complete voice pipeline
           pass
       
       def test_device_control(self):
           # Test device control through bus
           pass
       
       def test_ha_integration(self):
           # Test Home Assistant integration
           pass
   ```

2. **Run comprehensive tests**:
   ```bash
   # Run integration tests
   python -m pytest tests/integration_test.py -v
   
   # Test voice pipeline
   python tests/test_voice_pipeline.py
   
   # Test device control
   python tests/test_device_control.py
   ```

**Docker MCP Commands**:
```bash
# Run all tests
docker-compose -f docker-compose.bus.yml exec alicia_health_monitor python -m pytest

# Monitor all services
docker-compose -f docker-compose.bus.yml logs -f

# Check service health
curl http://localhost:8083/health/all
```

## Phase 4: Advanced Features (Weeks 7-8)

### Week 7: Analytics & Performance

#### Day 43-45: Analytics Service
**Objective**: Implement analytics and performance monitoring

**Tasks**:
1. **Create analytics service**:
   ```python
   # bus-services/analytics-service/main.py
   from bus_services.service_wrapper import BusServiceWrapper
   import time
   import json
   
   class AnalyticsService(BusServiceWrapper):
       def __init__(self):
           mqtt_config = {
               "host": "alicia_bus_core",
               "port": 1883,
               "username": "analytics_service",
               "password": "alicia_analytics_2024"
           }
           super().__init__("analytics_service", mqtt_config)
           self.metrics = {}
           self.start_analytics()
   ```

2. **Deploy analytics service**:
   ```yaml
   # Add to docker-compose.bus.yml
   analytics-service:
     container_name: alicia_analytics_service
     build: ./bus-services/analytics-service
     ports:
       - "8085:8085"
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy analytics service
docker-compose -f docker-compose.bus.yml up -d analytics-service

# View analytics dashboard
curl http://localhost:8085/analytics/dashboard

# Monitor analytics logs
docker logs -f alicia_analytics_service
```

#### Day 46-49: Performance Optimization
**Objective**: Optimize system performance and scalability

**Tasks**:
1. **Implement load balancing**:
   ```python
   # bus-services/load-balancer/main.py
   class LoadBalancer:
       def __init__(self):
           self.service_instances = {}
           self.load_balancing_strategy = "round_robin"
       
       def route_message(self, service_type: str, message: dict):
           instance = self.select_instance(service_type)
           return self.send_to_instance(instance, message)
   ```

2. **Deploy load balancer**:
   ```yaml
   # Add to docker-compose.bus.yml
   load-balancer:
     container_name: alicia_load_balancer
     build: ./bus-services/load-balancer
     depends_on:
       - alicia-bus-core
     networks:
       - alicia_bus_network
   ```

**Docker MCP Commands**:
```bash
# Deploy load balancer
docker-compose -f docker-compose.bus.yml up -d load-balancer

# Test load balancing
for i in {1..10}; do
  mosquitto_pub -h localhost -t "alicia/voice/stt/request" \
    -m "{\"test_id\":$i,\"audio_data\":\"test\"}"
done

# Monitor load balancer logs
docker logs -f alicia_load_balancer
```

### Week 8: Final Integration & Testing

#### Day 50-52: Complete System Testing
**Objective**: Comprehensive system testing and validation

**Tasks**:
1. **Create comprehensive test suite**:
   ```python
   # tests/complete_system_test.py
   class TestCompleteSystem:
       def test_end_to_end_voice_pipeline(self):
           # Test complete voice pipeline
           pass
       
       def test_device_discovery(self):
           # Test device discovery
           pass
       
       def test_security_validation(self):
           # Test security features
           pass
       
       def test_performance_benchmarks(self):
           # Test performance requirements
           pass
   ```

2. **Run performance benchmarks**:
   ```bash
   # Run performance tests
   python tests/performance_test.py
   
   # Run security tests
   python tests/security_test.py
   
   # Run integration tests
   python tests/integration_test.py
   ```

**Docker MCP Commands**:
```bash
# Run complete test suite
docker-compose -f docker-compose.bus.yml exec alicia_health_monitor python -m pytest tests/ -v

# Monitor all services during testing
docker-compose -f docker-compose.bus.yml logs -f

# Check system health
curl http://localhost:8083/health/all
```

#### Day 53-56: Documentation & Deployment
**Objective**: Finalize documentation and deploy to production

**Tasks**:
1. **Update documentation**:
   - Update architecture diagrams
   - Create deployment guides
   - Document new APIs
   - Create troubleshooting guides

2. **Deploy to production**:
   ```bash
   # Deploy production configuration
   docker-compose -f docker-compose.prod.yml up -d
   
   # Verify deployment
   curl http://localhost:8083/health/all
   
   # Monitor production logs
   docker-compose -f docker-compose.prod.yml logs -f
   ```

**Docker MCP Commands**:
```bash
# Deploy production system
docker-compose -f docker-compose.prod.yml up -d

# Monitor production deployment
docker-compose -f docker-compose.prod.yml logs -f

# Check production health
curl https://alicia-bus.example.com/health/all
```

## Docker MCP Integration Throughout

### Daily Monitoring Commands
```bash
# Check all container status
docker ps --filter "name=alicia"

# Monitor specific service logs
docker logs -f alicia_bus_core
docker logs -f alicia_stt_service
docker logs -f alicia_ai_service
docker logs -f alicia_tts_service

# Check container health
docker inspect alicia_bus_core | grep -A 10 "Health"

# Monitor resource usage
docker stats alicia_bus_core alicia_stt_service alicia_ai_service

# Check network connectivity
docker exec alicia_bus_core mosquitto_pub -h localhost -t test -m "connectivity"
```

### Troubleshooting Commands
```bash
# Check container logs for errors
docker logs alicia_bus_core 2>&1 | grep -i error

# Restart failed containers
docker-compose -f docker-compose.bus.yml restart alicia_bus_core

# Check container resource usage
docker exec alicia_bus_core top

# Test MQTT connectivity
docker exec alicia_bus_core mosquitto_pub -h localhost -t "test/topic" -m "test message"
```

This phase-by-phase guide provides detailed implementation steps with specific Docker MCP commands for monitoring and management throughout the migration process.
