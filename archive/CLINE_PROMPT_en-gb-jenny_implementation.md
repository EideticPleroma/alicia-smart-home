# Cline Prompt: Implement en-gb-jenny as Primary Voice for Alicia TTS System

## Project Context
You are working on the Alicia Smart Home AI Assistant project, specifically enhancing the Piper TTS (Text-to-Speech) system to use `en-gb-jenny` as the primary voice. The current system uses medium-quality voices and needs to be upgraded to provide more realistic, natural-sounding speech output.

## Current System Architecture
- **TTS Engine**: Piper neural TTS running in Docker containers
- **Current Primary Voice**: `en_US-lessac-medium`
- **Voice Processing**: Wyoming protocol with MQTT integration
- **Audio Output**: Sonos speakers via HTTP audio server
- **Configuration**: YAML-based with Docker Compose orchestration

## Implementation Objective
Replace the current primary voice with `en-gb-jenny` (British English, high-quality) and ensure seamless integration across all TTS components.

---

## PHASE 1: PLANNING & ANALYSIS

### 1.1 Current System Assessment
**Task**: Analyze the existing voice configuration and identify all components that need modification.

**Actions**:
1. Examine `voice-processing/start-piper.sh` to understand current voice model downloads
2. Review `voice-processing/unified-tts-service.py` for voice selection logic
3. Check `voice-processing/config/assistant_config.yaml` for voice configuration
4. Analyze `docker-compose.yml` for voice model volume mounts
5. Review documentation in `docs/12-Phase-3-Piper-TTS-Integration.md`

**Deliverables**:
- List of all files that reference voice configuration
- Current voice model inventory
- Voice selection logic flow diagram

### 1.2 Voice Model Research
**Task**: Research and verify en-gb-jenny model availability and specifications.

**Actions**:
1. Verify model exists in Piper voices repository
2. Check for high-quality versions (high, x_large if available)
3. Confirm download URLs and file sizes
4. Validate model compatibility with current Piper version (v1.2.0)

**Expected Model Details**:
- Model Name: `en_GB-jenny_dioco-medium` (or high if available)
- Sample Rate: 22,050Hz
- Quality: Medium/High
- File Size: ~50-100MB
- Download URL: `https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium/`

---

## PHASE 2: VERIFICATION & PREPARATION

### 2.1 System Compatibility Check
**Task**: Verify system can support the new voice model.

**Actions**:
1. Check available disk space in Docker volumes
2. Verify Piper executable supports the model format
3. Test current voice switching mechanism
4. Validate MQTT voice parameter handling

**Validation Commands**:
```bash
# Check disk space
docker exec alicia_unified_tts df -h /usr/local/bin/piper/models/

# Test current Piper functionality
docker exec alicia_unified_tts /usr/local/bin/piper/piper --help

# Verify model directory permissions
docker exec alicia_unified_tts ls -la /usr/local/bin/piper/models/
```

### 2.2 Backup Current Configuration
**Task**: Create backups before making changes.

**Actions**:
1. Backup current voice models
2. Create git branch for voice upgrade
3. Document current voice selection logic
4. Export current TTS configuration

**Backup Commands**:
```bash
# Create backup branch
git checkout -b feature/en-gb-jenny-voice-upgrade

# Backup current models
docker exec alicia_unified_tts tar -czf /tmp/current_models_backup.tar.gz /usr/local/bin/piper/models/

# Copy backup to host
docker cp alicia_unified_tts:/tmp/current_models_backup.tar.gz ./backup_models_$(date +%Y%m%d).tar.gz
```

---

## PHASE 3: IMPLEMENTATION

### 3.1 Update Voice Model Downloads
**Task**: Modify the startup script to download en-gb-jenny model.

**File**: `voice-processing/start-piper.sh`

**Changes Required**:
1. Add en-gb-jenny model download section
2. Prioritize en-gb-jenny as primary English voice
3. Keep existing models for fallback
4. Add model validation after download

**Implementation**:
```bash
# Add after line 13 (English section)
# British English - Primary Voice
wget -O en_GB-jenny_dioco-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx
wget -O en_GB-jenny_dioco-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx.json

# Verify download success
if [ ! -f "en_GB-jenny_dioco-medium.onnx" ]; then
    echo "ERROR: Failed to download en_GB-jenny model"
    exit 1
fi
```

### 3.2 Update Voice Selection Logic
**Task**: Modify the unified TTS service to use en-gb-jenny as default.

**File**: `voice-processing/unified-tts-service.py`

**Changes Required**:
1. Update `_get_piper_model_path()` method
2. Set en-gb-jenny as default voice
3. Add voice discovery functionality
4. Implement voice fallback hierarchy

**Implementation**:
```python
def _get_piper_model_path(self, voice: str) -> Optional[str]:
    """Get Piper model path for voice with en-gb-jenny as default"""
    # Voice mapping with en-gb-jenny as primary English voice
    voice_mapping = {
        "en": "en_GB-jenny_dioco-medium.onnx",  # Primary English voice
        "en_gb": "en_GB-jenny_dioco-medium.onnx",
        "en_us": "en_US-lessac-medium.onnx",    # Fallback
        "es": "es_ES-mls_10246-medium.onnx",
        "fr": "fr_FR-upmc-medium.onnx",
        "de": "de_DE-thorsten-medium.onnx",
        "it": "it_IT-riccardo-xw.onnx"
    }
    
    # Default to en-gb-jenny for any English variant
    if voice.startswith("en") and voice not in voice_mapping:
        model_name = "en_GB-jenny_dioco-medium.onnx"
    else:
        model_name = voice_mapping.get(voice, "en_GB-jenny_dioco-medium.onnx")
    
    model_path = f"/usr/local/bin/piper/models/{model_name}"
    return model_path if os.path.exists(model_path) else None
```

### 3.3 Update Configuration Files
**Task**: Update configuration to reflect new primary voice.

**Files to Update**:
1. `voice-processing/config/assistant_config.yaml`
2. `docs/12-Phase-3-Piper-TTS-Integration.md`

**Configuration Changes**:
```yaml
# assistant_config.yaml
wyoming:
  piper:
    url: "tcp://wyoming-piper:10200"
    voice: "en_GB-jenny_dioco-medium"  # Updated primary voice
    quality: "medium"
    language: "en_GB"  # British English
```

### 3.4 Update Docker Configuration
**Task**: Ensure Docker setup supports the new voice model.

**File**: `docker-compose.yml`

**Verification**:
1. Confirm volume mount includes new model
2. Check model directory permissions
3. Validate model loading in container startup

---

## PHASE 4: TESTING & VALIDATION

### 4.1 Unit Testing
**Task**: Test individual components with new voice.

**Test Cases**:
1. **Model Download Test**
   ```bash
   # Test model download in container
   docker exec alicia_unified_tts ls -la /usr/local/bin/piper/models/en_GB-jenny_dioco-medium.*
   ```

2. **Voice Selection Test**
   ```bash
   # Test voice selection logic
   docker exec alicia_unified_tts python3 -c "
   from unified_tts_service import UnifiedTTSService
   service = UnifiedTTSService()
   print('Default voice path:', service._get_piper_model_path('en'))
   print('GB voice path:', service._get_piper_model_path('en_gb'))
   "
   ```

3. **Piper TTS Test**
   ```bash
   # Test direct Piper synthesis
   echo "Hello, this is Alicia speaking with the new British voice." | \
   docker exec -i alicia_unified_tts /usr/local/bin/piper/piper \
   --model /usr/local/bin/piper/models/en_GB-jenny_dioco-medium.onnx \
   --output_file /tmp/test_jenny.wav
   ```

### 4.2 Integration Testing
**Task**: Test complete TTS pipeline with new voice.

**Test Scenarios**:
1. **MQTT TTS Request**
   ```bash
   # Send TTS request via MQTT
   mosquitto_pub -h localhost -t "alicia/tts/kitchen" -m '{
     "speaker": "kitchen",
     "message": "Good morning! This is Alicia with my new British accent.",
     "language": "en_gb",
     "volume": 30
   }'
   ```

2. **Wyoming Protocol Test**
   ```bash
   # Test Wyoming protocol with new voice
   curl -X POST http://localhost:10200/synthesize \
     -H "Content-Type: application/json" \
     -d '{"text": "Testing the new British voice", "voice": "en_GB-jenny_dioco-medium"}'
   ```

3. **Sonos Integration Test**
   ```bash
   # Test complete pipeline to Sonos
   python3 test_kitchen_tts.py --voice en_gb --message "Testing British voice on Sonos"
   ```

### 4.3 Quality Assessment
**Task**: Evaluate voice quality and naturalness.

**Assessment Criteria**:
1. **Clarity**: Is the speech clear and intelligible?
2. **Naturalness**: Does it sound natural and human-like?
3. **Accent**: Is the British accent appropriate and consistent?
4. **Performance**: Is synthesis time acceptable?
5. **Compatibility**: Does it work with all existing features?

**Quality Test Script**:
```python
# Create test_voice_quality.py
import requests
import time
import os

def test_voice_quality():
    test_phrases = [
        "Hello, this is Alicia, your smart home assistant.",
        "The weather today is sunny with a chance of rain.",
        "I've detected motion in the kitchen area.",
        "Would you like me to turn on the living room lights?",
        "Good evening! How can I help you today?"
    ]
    
    for phrase in test_phrases:
        start_time = time.time()
        response = requests.post('http://localhost:10200/synthesize', 
                               json={'text': phrase, 'voice': 'en_GB-jenny_dioco-medium'})
        synthesis_time = time.time() - start_time
        
        print(f"Phrase: {phrase}")
        print(f"Synthesis time: {synthesis_time:.2f}s")
        print(f"Status: {response.status_code}")
        print("---")
```

### 4.4 Performance Monitoring
**Task**: Monitor system performance with new voice.

**Metrics to Track**:
1. **Synthesis Time**: Average time to generate audio
2. **Memory Usage**: RAM consumption during synthesis
3. **CPU Usage**: Processing load during TTS
4. **Audio Quality**: File size and bitrate
5. **Error Rate**: Failed synthesis attempts

**Monitoring Commands**:
```bash
# Monitor resource usage
docker stats alicia_unified_tts

# Check audio file quality
docker exec alicia_unified_tts file /tmp/audio/*.wav

# Monitor logs for errors
docker logs alicia_unified_tts --tail 50
```

---

## PHASE 5: DEPLOYMENT & DOCUMENTATION

### 5.1 Production Deployment
**Task**: Deploy changes to production environment.

**Deployment Steps**:
1. Stop current TTS services
2. Deploy updated containers
3. Verify all services start correctly
4. Run smoke tests
5. Monitor for issues

**Deployment Commands**:
```bash
# Stop services
docker-compose stop unified-tts-service

# Rebuild with new voice
docker-compose build unified-tts-service

# Start services
docker-compose up -d unified-tts-service

# Verify deployment
docker-compose logs unified-tts-service
```

### 5.2 Documentation Updates
**Task**: Update all relevant documentation.

**Files to Update**:
1. `docs/12-Phase-3-Piper-TTS-Integration.md`
2. `docs/00-Table-of-Contents.md`
3. `README.md`
4. `voice-processing/README.md`

**Documentation Sections**:
- Voice model inventory
- Voice selection logic
- Configuration options
- Troubleshooting guide
- Performance metrics

### 5.3 User Communication
**Task**: Inform users about voice changes.

**Communication Points**:
1. Voice change announcement
2. New voice characteristics
3. Configuration options
4. Troubleshooting information

---

## SUCCESS CRITERIA

### Functional Requirements
- [ ] en-gb-jenny voice is set as primary English voice
- [ ] All existing TTS functionality works with new voice
- [ ] Voice selection logic supports en-gb-jenny
- [ ] Fallback to other voices works correctly
- [ ] MQTT integration functions properly
- [ ] Sonos audio output works correctly

### Quality Requirements
- [ ] Voice sounds natural and clear
- [ ] British accent is appropriate and consistent
- [ ] Synthesis time is acceptable (< 5 seconds)
- [ ] Audio quality meets standards
- [ ] No degradation in system performance

### Technical Requirements
- [ ] All tests pass
- [ ] No breaking changes to existing functionality
- [ ] Documentation is updated
- [ ] Configuration is properly managed
- [ ] Error handling works correctly

---

## ROLLBACK PLAN

If issues arise, rollback to previous voice:

1. **Immediate Rollback**:
   ```bash
   # Revert to previous voice in code
   git checkout HEAD~1 -- voice-processing/unified-tts-service.py
   
   # Restart services
   docker-compose restart unified-tts-service
   ```

2. **Model Rollback**:
   ```bash
   # Restore previous models
   docker exec alicia_unified_tts tar -xzf /tmp/current_models_backup.tar.gz -C /
   
   # Restart services
   docker-compose restart unified-tts-service
   ```

---

## ADDITIONAL CONSIDERATIONS

### Future Enhancements
1. **Voice Switching**: Implement runtime voice switching via MQTT
2. **Voice Quality Levels**: Support multiple quality levels (medium, high, x_large)
3. **Custom Voices**: Add support for custom voice models
4. **Voice Analytics**: Track voice usage and performance metrics

### Maintenance
1. **Model Updates**: Regular updates to voice models
2. **Performance Monitoring**: Ongoing performance tracking
3. **User Feedback**: Collect and act on user feedback
4. **Documentation**: Keep documentation current

---

**Expected Timeline**: 2-3 days for complete implementation and testing
**Risk Level**: Low (non-breaking changes with fallback support)
**Dependencies**: Docker, MQTT broker, Sonos speakers
