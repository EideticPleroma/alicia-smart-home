# Migration Guide: From Monolithic to Bus Architecture

## Overview

This guide helps you migrate from the old monolithic Alicia implementation to the new bus architecture with 23 microservices.

## What Changed

### Old Architecture (Monolithic)
- Single Docker Compose file with all services
- Direct service-to-service communication
- Limited scalability
- Basic security
- Single point of failure

### New Architecture (Bus-Based)
- 23 microservices with MQTT communication
- Centralized message bus
- Horizontal scaling support
- Enterprise-grade security
- Fault-tolerant design

## Migration Steps

### 1. **Stop Old Services**

```bash
# Stop old monolithic services
docker-compose down

# Remove old containers and volumes (optional)
docker-compose down -v
docker system prune -f
```

### 2. **Update Configuration**

```bash
# Create new environment file
cp .env.example .env

# Edit with your API keys and configuration
nano .env
```

**Required Environment Variables:**
```bash
# API Keys
XAI_API_KEY=your_grok_api_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# MQTT Bus Configuration
MQTT_BROKER=alicia_bus_core
MQTT_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=alicia_admin_2024
```

### 3. **Start New Bus Architecture**

```bash
# Start all 23 microservices
docker-compose -f docker-compose.bus.yml up -d

# Check service health
docker-compose -f docker-compose.bus.yml ps
```

### 4. **Verify Migration**

```bash
# Test MQTT broker
curl http://localhost:1883/health

# Test voice services
curl http://localhost:8001/health  # STT Service
curl http://localhost:8002/health  # AI Service
curl http://localhost:8003/health  # TTS Service

# Test device services
curl http://localhost:8006/health  # Device Manager
curl http://localhost:8007/health  # HA Bridge

# Test advanced features
curl http://localhost:8009/health  # Grok Integration
curl http://localhost:8010/health  # Personality System
```

## Service Mapping

### Old Services → New Services

| Old Service | New Service | Port | Purpose |
|-------------|-------------|------|---------|
| `alicia_whisper` | `alicia-stt-service` | 8001 | Speech-to-text |
| `alicia_piper` | `alicia-tts-service` | 8003 | Text-to-speech |
| `alicia_assistant` | `alicia-voice-router` | 8004 | Voice pipeline orchestration |
| `alicia_mqtt` | `alicia-bus-core` | 1883 | MQTT broker |
| `alicia_sonos` | `alicia-sonos-service` | 8005 | Speaker control |
| N/A | `alicia-ai-service` | 8002 | AI processing |
| N/A | `alicia-grok-integration` | 8009 | Grok-4 integration |
| N/A | `alicia-personality-system` | 8010 | Character profiles |
| N/A | `alicia-multi-language` | 8011 | Translation services |
| N/A | `alicia-advanced-voice` | 8012 | Voice enhancement |

## Configuration Changes

### Old Configuration Files
- `home-assistant/config/configuration.yaml` → **Deprecated**
- `mqtt/config/mosquitto.conf` → `bus-config/mosquitto.conf`
- `voice-processing/config/assistant_config.yaml` → **Deprecated**

### New Configuration Files
- `bus-config/mosquitto.conf` - MQTT broker configuration
- `bus-config/passwords` - Service authentication
- `bus-config/acl` - Access control lists
- `bus-services/*/config.yaml` - Individual service configuration

## API Changes

### Old API Endpoints
```bash
# Old endpoints (deprecated)
curl http://localhost:9000/transcribe
curl http://localhost:10200/synthesize
curl http://localhost:8000/health
```

### New API Endpoints
```bash
# New endpoints
curl http://localhost:8001/transcribe  # STT Service
curl http://localhost:8003/synthesize  # TTS Service
curl http://localhost:8004/health      # Voice Router
curl http://localhost:8002/process     # AI Service
```

## MQTT Topic Changes

### Old Topics
```
alicia/voice/command
alicia/voice/response
alicia/tts/kitchen
```

### New Topics
```
alicia/voice/command
alicia/voice/response
alicia/tts/kitchen
alicia/ai/process
alicia/personality/response
alicia/translation/request
alicia/device/command
alicia/device/status
```

## Data Migration

### Old Data Locations
- `mqtt/data/` → `bus-data/`
- `mqtt/log/` → `bus-logs/`
- `home-assistant/logs/` → `bus-logs/`

### New Data Locations
- `bus-data/` - MQTT broker data
- `bus-logs/` - All service logs
- `bus-services/*/data/` - Service-specific data

## Troubleshooting

### Common Issues

1. **Services Not Starting**
   ```bash
   # Check Docker logs
   docker-compose -f docker-compose.bus.yml logs [service_name]
   
   # Check service health
   curl http://localhost:[port]/health
   ```

2. **MQTT Connection Issues**
   ```bash
   # Test MQTT connectivity
   mosquitto_pub -h localhost -t "alicia/test" -m "Hello Bus"
   
   # Check MQTT broker logs
   docker-compose -f docker-compose.bus.yml logs alicia-bus-core
   ```

3. **Voice Services Not Working**
   ```bash
   # Test STT service
   curl -X POST http://localhost:8001/transcribe -F "file=@test.wav"
   
   # Test TTS service
   curl -X POST http://localhost:8003/synthesize -H "Content-Type: application/json" -d '{"text": "Hello"}'
   ```

### Rollback Plan

If you need to rollback to the old architecture:

```bash
# Stop bus services
docker-compose -f docker-compose.bus.yml down

# Start old services
docker-compose up -d

# Verify old services are running
docker-compose ps
```

## Benefits of New Architecture

### Scalability
- **Horizontal Scaling**: Add more instances of any service
- **Load Balancing**: Automatic distribution across service instances
- **Resource Optimization**: Scale only the services you need

### Reliability
- **Fault Tolerance**: If one service fails, others continue working
- **Health Monitoring**: Automatic health checks and recovery
- **Service Discovery**: Automatic service registration and discovery

### Security
- **TLS Encryption**: All communications encrypted
- **JWT Authentication**: Token-based API access
- **ACL Authorization**: Granular topic-based access control
- **Audit Logging**: Comprehensive security event logging

### Maintainability
- **Microservices**: Independent development and deployment
- **Clear Separation**: Each service has a single responsibility
- **Easy Updates**: Update individual services without affecting others

## Support

If you encounter issues during migration:

1. **Check Logs**: `docker-compose -f docker-compose.bus.yml logs [service_name]`
2. **Verify Health**: `curl http://localhost:[port]/health`
3. **Test MQTT**: `mosquitto_pub -h localhost -t "alicia/test" -m "Hello"`
4. **Review Documentation**: [Complete Bus Architecture Report](ALICIA_BUS_ARCHITECTURE_COMPLETE_REPORT.md)

## Next Steps

After successful migration:

1. **Test All Features**: Verify voice commands, device control, and AI responses
2. **Configure Monitoring**: Set up health monitoring and alerting
3. **Optimize Performance**: Tune service configurations for your environment
4. **Scale as Needed**: Add more service instances based on usage

---

**Migration completed successfully!** 🎉

Your Alicia Smart Home AI Assistant is now running on the new bus architecture with 23 microservices, enterprise-grade security, and horizontal scaling capabilities.
