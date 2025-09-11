# Prompt for Cline: Bus Architecture Voice Processing Workflow for Alicia Project

You are Cline, handling voice pipeline tasks within the bus architecture. All voice services (STT, AI, TTS) must communicate through the message bus, following bus architecture principles and service discovery patterns.

### Core Bus Architecture Rules
1. **Service Wrapper Pattern**: All voice services MUST extend BusServiceWrapper and communicate via MQTT topics.
2. **Message Flow**: Voice pipeline follows STT → AI → TTS message flow through bus topics.
3. **Service Discovery**: Voice services MUST register with device registry and declare capabilities.
4. **Security Integration**: All voice messages MUST be encrypted and authenticated via security gateway.
5. **Health Monitoring**: Voice services MUST implement health checks and send periodic heartbeats.

### Voice Service Architecture
1. **STT Service**: Processes audio via alicia/voice/stt/request → alicia/voice/stt/response
2. **AI Service**: Processes text via alicia/voice/ai/request → alicia/voice/ai/response  
3. **TTS Service**: Generates audio via alicia/voice/tts/request → alicia/voice/tts/response
4. **Voice Router**: Routes voice commands and orchestrates the pipeline

### Enforcement Guidelines
- Sections: "Component Analysis", "Steps/Commands", "Integration Plan", "Testing/Security".
- Integration with Other Rules: gitFlow.md for changes; integrationTesting.md for full pipeline; documentationUpdate.md for docs.
- Request details: e.g., mic model.

### Voice Service Implementation Examples

#### STT Service Bus Integration
```python
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

#### Voice Pipeline Message Flow
```python
# Voice Router orchestrates the pipeline
def process_voice_command(self, audio_data):
    # Send to STT service
    self.publish_message("alicia/voice/stt/request", {
        "audio_data": audio_data,
        "session_id": self.session_id,
        "language": "en-US"
    })
    
    # Listen for STT response
    self.mqtt_client.subscribe("alicia/voice/stt/response")
```

### Examples
- User: "Debug STT service bus integration." → Analysis: STT service wrapper. Steps: Check MQTT connectivity, validate message format. Commands: docker logs -f alicia_stt_service; mosquitto_sub -h localhost -t "alicia/voice/stt/#" -v. Testing: Send test audio via MQTT topic.
- User: "Integrate voice services with bus." → Plan: Create service wrappers for STT, AI, TTS; implement message flow. Security: Encrypt audio data in messages, use service authentication.

### Bus Architecture Voice Processing Checklist
- [ ] **Service Wrappers**: All voice services extend BusServiceWrapper
- [ ] **Message Topics**: Proper topic hierarchy (alicia/voice/service/action)
- [ ] **Service Registration**: Services register with device registry
- [ ] **Security**: Message encryption and authentication
- [ ] **Health Monitoring**: Health check endpoints and heartbeats
- [ ] **Error Handling**: Proper error responses and retry logic

Confirm: "Following Bus Architecture Voice Processing Workflow v2.0."
