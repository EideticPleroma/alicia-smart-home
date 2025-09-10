# Cline Correction Prompt: Fix en-gb-jenny Implementation Issues

## Current Status Assessment
You've made excellent progress implementing en-gb-jenny as the primary voice, but there are **critical inconsistencies** that need immediate fixing. The implementation is 85% complete but has one major issue preventing it from working correctly.

## 🚨 CRITICAL ISSUE TO FIX

### Problem: Inconsistent Voice Mapping
The `start-piper.sh` file has **two different voice mappings** that contradict each other:

1. **Lines 12-13**: Downloads en-gb-jenny as primary English voice ✅
2. **Lines 57-63**: The `piper_app.py` section still uses old mapping ❌

**Current (WRONG) mapping in piper_app.py:**
```python
model_map = {
    "en": "en_US-lessac-medium.onnx",  # ❌ This contradicts the download priority
    "es": "es_ES-mls_10246-medium.onnx",
    "fr": "fr_FR-upmc-medium.onnx",
    "de": "de_DE-thorsten-medium.onnx",
    "it": "it_IT-riccardo-xw.onnx"
}
```

**Should be (CORRECT) mapping:**
```python
model_map = {
    "en": "en_GB-jenny_dioco-medium.onnx",  # ✅ Primary English voice
    "en_gb": "en_GB-jenny_dioco-medium.onnx",
    "en_us": "en_US-lessac-medium.onnx",    # Fallback
    "es": "es_ES-mls_10246-medium.onnx",
    "fr": "fr_FR-upmc-medium.onnx",
    "de": "de_DE-thorsten-medium.onnx",
    "it": "it_IT-riccardo-xw.onnx"
}
```

## 🔧 IMMEDIATE ACTIONS REQUIRED

### 1. Fix the Voice Mapping Inconsistency
**File**: `voice-processing/start-piper.sh`
**Lines**: 57-63

**Action**: Update the `model_map` in the `piper_app.py` section to match the voice selection logic in `unified-tts-service.py`

### 2. Add Model Validation
**File**: `voice-processing/start-piper.sh`
**Location**: After line 33 (after all model downloads)

**Add this validation code:**
```bash
# Verify critical model downloads
echo "Validating model downloads..."

if [ ! -f "en_GB-jenny_dioco-medium.onnx" ]; then
    echo "❌ ERROR: Failed to download en_GB-jenny model"
    exit 1
fi

if [ ! -f "en_GB-jenny_dioco-medium.onnx.json" ]; then
    echo "❌ ERROR: Failed to download en_GB-jenny config"
    exit 1
fi

echo "✅ en_GB-jenny model validation passed"
```

### 3. Test the Implementation
**Action**: Run the test files to validate the fix works

**Commands to run:**
```bash
# Test voice selection logic
python3 test_voice_selection.py

# Test model download
python3 test_voice_model_download.py

# Test TTS synthesis (if services are running)
python3 test_tts_synthesis.py

# Test MQTT integration (if services are running)
python3 test_mqtt_tts.py
```

## 📋 VALIDATION CHECKLIST

Before considering the implementation complete, verify:

- [ ] `start-piper.sh` downloads en-gb-jenny first (✅ Already done)
- [ ] `start-piper.sh` piper_app.py uses en-gb-jenny for "en" language (❌ Needs fixing)
- [ ] `unified-tts-service.py` voice mapping uses en-gb-jenny for "en" (✅ Already done)
- [ ] `assistant_config.yaml` specifies en-gb-jenny as default (✅ Already done)
- [ ] Model validation prevents startup if en-gb-jenny missing (❌ Needs adding)
- [ ] All test files pass (❌ Needs testing)

## 🎯 EXPECTED OUTCOME

After these fixes:
1. **Consistent Voice Selection**: Both the startup script and service use en-gb-jenny as primary English voice
2. **Robust Validation**: System fails gracefully if en-gb-jenny model is missing
3. **Working Tests**: All test files should pass
4. **Functional TTS**: British accent should be heard when using "en" language

## 🚀 NEXT STEPS AFTER FIXING

1. **Fix the inconsistency** (priority #1)
2. **Add validation** (priority #2)
3. **Run tests** to verify everything works
4. **Test with actual TTS** to hear the British accent
5. **Update documentation** if needed

## 💡 WHY THIS MATTERS

Without this fix:
- The system downloads en-gb-jenny but doesn't use it
- Users will still hear the American accent despite the "upgrade"
- The implementation appears complete but doesn't work as intended
- All the excellent test work becomes meaningless

**This is a simple but critical fix that will make the implementation actually functional.**

---

**Priority**: 🔴 **CRITICAL** - Fix immediately before proceeding
**Estimated Time**: 5-10 minutes
**Complexity**: Low (simple text replacement)
**Impact**: High (makes the entire implementation work)
