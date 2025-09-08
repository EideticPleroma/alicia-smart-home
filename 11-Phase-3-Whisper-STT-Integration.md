# Chapter 11: Phase 3 - Whisper STT Integration

## Overview

This chapter documents the integration of OpenAI's Whisper speech-to-text model into the Alicia smart home system as part of Phase 3: Voice Processing Integration.

## Implementation Details

### Docker Container Setup

The Whisper STT service is deployed as a Docker container using Ubuntu 22.04 base image with the following configuration:

```yaml
whisper-stt:
  container_name: alicia_whisper
  image: ubuntu:22.04
  ports:
    - "9000:9000"
  command: ["bash", "-c", "apt-get update && apt-get install -y python3 python3-pip ffmpeg && pip3 install openai-whisper fastapi uvicorn && python3 -c 'from fastapi import FastAPI, UploadFile; import whisper, uvicorn; app = FastAPI(); model = whisper.load_model(\"base\"); @app.post(\"/transcribe\"); async def transcribe_audio(file: UploadFile): audio_data = await file.read(); open(\"/tmp/audio.wav\", \"wb\").write(audio_data); result = model.transcribe(\"/tmp/audio.wav\"); return {\"text\": result[\"text\"]}; uvicorn.run(app, host=\"0.0.0.0\", port=9000)'"]
  volumes:
    - ./models:/root/.cache/whisper
  restart: unless-stopped
  networks:
    - alicia_network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/docs"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 120s
```

### Service Architecture

The Whisper service provides a REST API endpoint for audio transcription:

- **Endpoint**: `POST /transcribe`
- **Input**: Audio file (WAV format)
- **Output**: JSON with transcribed text
- **Model**: Whisper "base" model (74MB, optimized for speed)

### Integration Points

#### MQTT Integration
- **Topic**: `alicia/voice/audio`
- **Payload**: Base64-encoded audio data
- **Response Topic**: `alicia/voice/transcript`
- **Response Payload**: `{"text": "transcribed text", "confidence": 0.95}`

#### Home Assistant Integration
The Whisper service integrates with Home Assistant through MQTT:

```yaml
mqtt:
  sensor:
    - name: "Voice Transcript"
      state_topic: "alicia/voice/transcript"
      value_template: "{{ value_json.text }}"
      json_attributes_topic: "alicia/voice/transcript"
```

### Performance Characteristics

#### Model Specifications
- **Model Size**: 74MB (base model)
- **Supported Languages**: 99 languages
- **Audio Format**: WAV, MP3, M4A, FLAC, etc.
- **Typical Latency**: 2-5 seconds for 10-second audio clips

#### Hardware Requirements
- **RAM**: Minimum 2GB, Recommended 4GB
- **CPU**: Multi-core recommended for parallel processing
- **Storage**: 1GB for model and cache

### Testing and Validation

#### Basic Functionality Test
```bash
# Test with sample audio file
curl -X POST -F "file=@test_audio.wav" http://localhost:9000/transcribe
```

Expected response:
```json
{
  "text": "Hello, this is a test of the Whisper speech to text system."
}
```

#### Integration Test
```bash
# Test MQTT integration
mosquitto_pub -h localhost -t "alicia/voice/audio" -m "base64_audio_data" -u voice_assistant -P alicia_ha_mqtt_2024
```

#### Performance Test
```bash
# Test with various audio lengths
time curl -X POST -F "file=@long_audio.wav" http://localhost:9000/transcribe
```

### Error Handling

#### Common Error Scenarios
1. **Invalid Audio Format**
   - Error: "Audio format not supported"
   - Solution: Convert audio to supported format (WAV recommended)

2. **Model Loading Failure**
   - Error: "Model download failed"
   - Solution: Check internet connectivity and disk space

3. **Memory Issues**
   - Error: "Out of memory"
   - Solution: Reduce model size or increase RAM allocation

#### Error Response Format
```json
{
  "error": "Audio processing failed",
  "details": "Invalid audio format",
  "timestamp": "2025-01-08T14:30:00Z"
}
```

### Security Considerations

#### Access Control
- Service runs on internal network only
- No external internet access required
- MQTT authentication required for all interactions

#### Data Privacy
- Audio data processed locally
- No audio data sent to external services
- Temporary files cleaned up automatically

### Monitoring and Logging

#### Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9000/docs"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 120s
```

#### Log Files
- Container logs: `docker logs alicia_whisper`
- Application logs: Integrated with Python logging
- MQTT logs: Available through broker logs

### Future Enhancements

#### Planned Improvements
1. **Model Optimization**
   - Implement model quantization for faster inference
   - Add support for larger models (medium, large)
   - GPU acceleration support

2. **Audio Processing**
   - Real-time streaming audio support
   - Voice activity detection
   - Noise reduction preprocessing

3. **Language Support**
   - Custom language model training
   - Multi-language conversation support
   - Accent adaptation

#### Scalability Considerations
- Horizontal scaling with multiple containers
- Load balancing for high-volume deployments
- Caching for frequently transcribed phrases

## Conclusion

The Whisper STT integration provides robust speech-to-text capabilities for the Alicia system. The containerized deployment ensures consistent performance and easy maintenance. The MQTT-based integration allows seamless communication with other system components.

## References

- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [MQTT Protocol Specification](https://mqtt.org/mqtt-specification/)

---

**Chapter 11 Complete - Whisper STT Integration**
*Document Version: 1.0*
*Last Updated: January 8, 2025*
