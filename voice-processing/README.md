# Alicia Enhanced Voice Assistant - Wyoming Protocol

A local voice assistant solution using Piper TTS and Whisper STT with Wyoming protocol compatibility, designed for seamless integration with Home Assistant and future LLM capabilities.

## Overview

This enhanced voice assistant framework bridges the gap between our current custom implementation and Home Assistant's approach, providing:

- **Wyoming Protocol Support**: Compatible with Home Assistant's voice ecosystem
- **Local Processing**: All voice processing happens locally, ensuring privacy
- **LLM Ready**: Prepared for future large language model integration
- **Multi-language Support**: Support for multiple languages through Piper voices
- **MQTT Integration**: Seamless communication with home automation systems
- **Docker-based**: Easy deployment and scaling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Home Assistant │    │   MQTT Broker   │    │   Alicia        │
│   (Optional)     │◄──►│   (Mosquitto)   │◄──►│   Assistant     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Wyoming Whisper │    │ Wyoming Piper   │    │   Device        │
│   (STT)         │    │   (TTS)         │    │   Control        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Differences from Home Assistant

| Feature | Our Current | Home Assistant | Our Enhanced Solution |
|---------|-------------|----------------|----------------------|
| **Protocol** | REST APIs | Wyoming Protocol | Wyoming Protocol ✅ |
| **Integration** | Manual | Seamless HA | HA Compatible ✅ |
| **Setup** | Complex | UI-based | Docker Compose ✅ |
| **Models** | Download at runtime | Pre-built | Optimized containers ✅ |
| **LLM Support** | None | Limited | Ready for integration ✅ |
| **Multi-language** | Basic | Good | Enhanced ✅ |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for testing)
- At least 4GB RAM
- Microphone and speakers (optional for testing)

### 1. Start the Services

```bash
# Navigate to voice-processing directory
cd voice-processing

# Start all services
docker-compose -f docker-compose.wyoming.yml up -d

# Check service status
docker-compose -f docker-compose.wyoming.yml ps
```

### 2. Verify Services

```bash
# Test Wyoming services
python test_wyoming_services.py
```

Expected output:
```
INFO - Starting Wyoming services tests...
INFO - Service connectivity: {
  "whisper_connected": true,
  "piper_connected": true
}
INFO - Whisper STT: PASS
INFO - Piper TTS: PASS
INFO - Overall: PASS
```

### 3. Test the Assistant

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test transcription (with audio file)
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: application/octet-stream" \
  --data-binary @test_audio.wav

# Test text-to-speech
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "language": "en"}' \
  --output speech.wav

# Test command processing
curl -X POST http://localhost:8000/process-command \
  -H "Content-Type: application/json" \
  -d '{"command": "turn on the living room light"}'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_URL` | `tcp://localhost:10300` | Wyoming Whisper service URL |
| `PIPER_URL` | `tcp://localhost:10200` | Wyoming Piper service URL |
| `MQTT_BROKER` | `localhost` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_USERNAME` | `voice_assistant` | MQTT username |
| `MQTT_PASSWORD` | `alicia_ha_mqtt_2024` | MQTT password |
| `LLM_ENABLED` | `false` | Enable LLM integration |
| `LLM_ENDPOINT` | `` | LLM API endpoint |

### Configuration File

Edit `config/assistant_config.yaml` to customize settings:

```yaml
assistant:
  name: "Alicia"
  language: "en"
  wake_word: "alicia"

llm:
  enabled: false
  endpoint: "http://localhost:11434/api/generate"
  model: "llama2"
```

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "whisper": true,
    "piper": true,
    "mqtt": true
  },
  "session_id": "uuid-string",
  "llm_enabled": false
}
```

### Transcribe Audio
```http
POST /transcribe
Content-Type: application/octet-stream

<audio_data>
```

Response:
```json
{
  "text": "Hello, how can I help you?",
  "language": "en",
  "session_id": "uuid-string"
}
```

### Synthesize Speech
```http
POST /synthesize
Content-Type: application/json

{
  "text": "Hello, world!",
  "language": "en"
}
```

Response: WAV audio file

### Process Command
```http
POST /process-command
Content-Type: application/json

{
  "command": "turn on the light"
}
```

Response:
```json
{
  "response": "Turning on the light.",
  "session_id": "uuid-string"
}
```

### Conversation History
```http
GET /conversation-history?limit=10
```

## MQTT Integration

The assistant publishes and subscribes to MQTT topics:

### Subscribed Topics
- `alicia/voice/command` - Voice commands
- `alicia/voice/wake` - Wake word detection
- `homeassistant/sensor/voice/#` - Sensor data

### Published Topics
- `alicia/voice/response` - Assistant responses
- `alicia/voice/status` - Assistant status
- `alicia/commands` - Device control commands

## Home Assistant Integration

### Option 1: Wyoming Integration (Recommended)

1. Install Wyoming integration in Home Assistant
2. Configure Whisper and Piper services
3. Add Assist pipeline using Wyoming services
4. Use the assistant through HA's voice interface

### Option 2: MQTT Bridge

1. Configure MQTT integration in Home Assistant
2. Use MQTT sensors to receive voice commands
3. Send responses back through MQTT

## LLM Integration (Future)

When ready to add LLM capabilities:

1. Set environment variable: `LLM_ENABLED=true`
2. Configure LLM endpoint in `config/assistant_config.yaml`
3. The assistant will automatically route complex queries to the LLM
4. Basic commands still processed locally for speed

## Multi-language Support

The system supports multiple languages through Piper voices:

- English: `en_US-lessac-medium`
- Spanish: `es_ES-mls_10246-medium`
- French: `fr_FR-upmc-medium`
- German: `de_DE-thorsten-medium`
- Italian: `it_IT-riccardo-xw`

## Troubleshooting

### Services Won't Start

```bash
# Check Docker logs
docker-compose -f docker-compose.wyoming.yml logs

# Check service health
docker-compose -f docker-compose.wyoming.yml ps

# Restart services
docker-compose -f docker-compose.wyoming.yml restart
```

### Wyoming Connection Issues

```bash
# Test individual services
python test_wyoming_services.py

# Check network connectivity
docker network ls
docker network inspect alicia_alicia_network
```

### Audio Issues

```bash
# Test audio devices (Linux)
arecord -l
aplay -l

# Test audio (Windows WSL)
# Ensure PulseAudio is configured
```

### MQTT Issues

```bash
# Test MQTT connection
mosquitto_sub -h localhost -t "alicia/#" -v

# Check MQTT logs
docker-compose -f docker-compose.wyoming.yml logs mosquitto
```

## Performance Optimization

### Hardware Requirements

- **Minimum**: 2GB RAM, single-core CPU
- **Recommended**: 4GB RAM, multi-core CPU
- **Optimal**: 8GB+ RAM, GPU acceleration

### Model Optimization

- Use smaller Whisper models for faster processing
- Choose appropriate Piper voice quality
- Enable model caching for faster startup

## Security Considerations

- All voice processing is local - no data sent to external servers
- MQTT communication can be encrypted with TLS
- API endpoints can be protected with authentication
- Audio data is processed in memory and not stored permanently

## Development

### Adding New Features

1. Extend the `AliciaAssistant` class in `alicia_assistant.py`
2. Add new API endpoints in the FastAPI app
3. Update configuration in `config/assistant_config.yaml`
4. Add tests in `test_wyoming_services.py`

### Custom Commands

Add new command handlers in the `process_basic_command` method:

```python
def process_basic_command(self, command: str) -> str:
    if "custom action" in command:
        return self.handle_custom_action(command)
    # ... existing handlers
```

## Migration from Current System

To migrate from the existing voice-processing setup:

1. Backup current configuration
2. Stop existing services
3. Deploy new Wyoming-based services
4. Update any integrations to use new endpoints
5. Test thoroughly before removing old services

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests with clear descriptions

## License

This project is part of the Alicia Smart Home AI Assistant framework.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Docker logs
3. Test individual components
4. Check MQTT connectivity

---

**Version**: 2.0.0
**Last Updated**: September 2025
**Compatibility**: Home Assistant 2025.9+, Docker Compose v2.0+
