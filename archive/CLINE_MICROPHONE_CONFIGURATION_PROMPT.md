# Cline Prompt: Alicia Microphone Configuration and Voice Testing

## Context
You are Cline, an AI coding assistant helping to configure microphone access and voice command testing for the Alicia Smart Home AI Assistant. The system uses Docker containers for voice processing (Whisper STT, Piper TTS) and needs to access the host computer's microphone for speech input.

## Current System Status
- ✅ TTS to Sonos implementation is COMPLETE
- ✅ Docker services are configured (Wyoming Whisper, Unified TTS, Sonos MQTT Bridge)
- ❌ Microphone access needs to be configured in Docker containers
- ❌ Voice command testing needs to be implemented

## Your Task
Configure microphone access for the Alicia voice assistant system and create comprehensive voice testing capabilities.

## Required Actions

### 1. Docker Configuration Updates
Update `docker-compose.yml` to enable microphone access:

**For `wyoming-whisper` service:**
```yaml
wyoming-whisper:
  # ... existing configuration ...
  devices:
    - /dev/snd:/dev/snd  # Audio device access for microphone
  privileged: true  # Required for audio device access
```

**For `alicia-assistant` service:**
```yaml
alicia-assistant:
  # ... existing configuration ...
  devices:
    - /dev/snd:/dev/snd  # Audio device access for microphone
  privileged: true  # Required for audio device access
```

### 2. Create Voice Testing Scripts

**Create `test_microphone_access.py`:**
- Test microphone connectivity and recording
- List available audio devices
- Verify PyAudio functionality
- Test recording and save test audio file
- Check Whisper STT service integration
- Provide troubleshooting tips for common issues

**Create `test_voice_commands.py`:**
- Interactive voice command testing
- Complete voice pipeline testing (mic → Whisper → TTS → Sonos)
- Audio recording with configurable duration
- MQTT integration for TTS commands
- Error handling and cleanup
- Support both single test and interactive modes

**Create `requirements_voice_test.txt`:**
- PyAudio for microphone access
- Requests for HTTP API calls
- Paho MQTT for MQTT communication

### 3. Voice Pipeline Integration
Ensure the complete voice pipeline works:
```
Microphone → Docker Container → Whisper STT → MQTT → TTS → Sonos
```

**Key Integration Points:**
- Microphone audio capture via PyAudio
- Docker device mapping for audio access
- Whisper STT service on port 10300
- MQTT broker for command routing
- Unified TTS service for audio generation
- Sonos MQTT bridge for speaker output

### 4. Error Handling and Troubleshooting
Implement comprehensive error handling for:
- Microphone access failures
- Audio device not found
- Docker container audio device mapping issues
- Whisper STT service connectivity
- MQTT broker connection problems
- Audio recording quality issues

### 5. Testing and Validation
Create test scenarios for:
- Microphone device detection
- Audio recording quality
- Speech-to-text accuracy
- Text-to-speech output
- Complete voice command pipeline
- Error recovery and fallback mechanisms

## Technical Requirements

### Audio Configuration
- **Sample Rate**: 16000 Hz (optimal for Whisper)
- **Channels**: Mono (1 channel)
- **Format**: 16-bit PCM
- **Chunk Size**: 1024 samples
- **Recording Duration**: 3-5 seconds for commands

### Docker Requirements
- **Device Mapping**: `/dev/snd:/dev/snd` for audio access
- **Privileged Mode**: Required for audio device access
- **Network Access**: Container-to-container communication
- **Volume Mounts**: Audio file sharing between services

### MQTT Topics
- **TTS Commands**: `alicia/tts/kitchen`
- **Voice Commands**: `alicia/voice/command`
- **Status Updates**: `alicia/voice/status`

## Expected Outputs

### 1. Updated Docker Configuration
- Modified `docker-compose.yml` with microphone access
- Proper device mapping and privileged mode
- Health checks for audio services

### 2. Voice Testing Suite
- `test_microphone_access.py` - Microphone connectivity testing
- `test_voice_commands.py` - Complete voice pipeline testing
- `requirements_voice_test.txt` - Python dependencies

### 3. Documentation
- Clear setup instructions
- Troubleshooting guide
- Testing procedures
- Common issues and solutions

## Success Criteria
- [ ] Microphone is accessible from Docker containers
- [ ] Audio recording works reliably
- [ ] Whisper STT processes audio correctly
- [ ] TTS commands reach Sonos speakers
- [ ] Complete voice pipeline functions end-to-end
- [ ] Error handling covers common failure modes
- [ ] Testing scripts provide clear feedback

## Platform Considerations
- **Windows**: Ensure microphone permissions for Python/Docker
- **Linux**: May require user to be in audio group
- **macOS**: Check microphone privacy settings
- **Docker**: Verify audio device access permissions

## Implementation Notes
- Use PyAudio for reliable microphone access
- Implement proper audio format conversion
- Add comprehensive logging for debugging
- Create user-friendly error messages
- Ensure proper cleanup of temporary files
- Test with various microphone types and qualities

## Validation Commands
After implementation, verify with:
```bash
# Test microphone access
python test_microphone_access.py

# Start services
docker-compose up -d

# Test complete pipeline
python test_voice_commands.py
```

## Expected User Experience
1. User runs microphone test script
2. System detects and tests microphone
3. User can record voice commands
4. Commands are transcribed by Whisper
5. Responses are spoken through Sonos speakers
6. Clear feedback provided at each step

This configuration will enable the Alicia voice assistant to use the host computer's microphone for speech input while maintaining the existing TTS-to-Sonos functionality.
