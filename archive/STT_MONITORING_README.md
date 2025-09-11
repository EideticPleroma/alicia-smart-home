# STT Monitoring Tools for Alicia Voice Assistant

This collection of tools helps you monitor and debug the STT to TTS pipeline with Grok integration in your Alicia Voice Assistant system.

## 🛠️ Available Tools

### 1. `test_stt_mqtt_monitor.py` - Simple MQTT Monitor
**Purpose**: Monitor MQTT topics for STT inputs and voice pipeline activity in real-time.

**Usage**:
```bash
python test_stt_mqtt_monitor.py
```

**Features**:
- Monitors all voice-related MQTT topics
- Displays STT commands, voice responses, and TTS requests
- Shows real-time statistics
- Tracks message counts and errors

### 2. `test_send_stt_command.py` - STT Command Sender
**Purpose**: Send test STT commands to trigger the voice pipeline.

**Usage**:
```bash
# Send a test command
python test_send_stt_command.py "Hello Alicia, turn on the kitchen light"

# Specify a speaker
python test_send_stt_command.py "What's the temperature?" bedroom
```

**Features**:
- Sends STT commands to MQTT
- Triggers TTS requests
- Tests the complete pipeline flow

### 3. `test_voice_pipeline_debug.py` - Comprehensive Debugger
**Purpose**: Comprehensive debugging and testing of the entire voice pipeline.

**Usage**:
```bash
python test_voice_pipeline_debug.py
```

**Features**:
- Checks service connectivity
- Tests each pipeline stage individually
- Tests complete end-to-end pipeline
- Provides detailed diagnostic reports

### 4. `test_live_stt_monitor.py` - Advanced Live Monitor
**Purpose**: Advanced monitoring with audio recording and Grok integration testing.

**Usage**:
```bash
# Interactive mode
python test_live_stt_monitor.py interactive

# Live monitoring mode
python test_live_stt_monitor.py monitor

# Diagnostic mode
python test_live_stt_monitor.py diagnostics
```

**Features**:
- Real-time audio recording
- Whisper STT testing
- Grok integration monitoring
- Interactive testing mode
- Comprehensive diagnostics

## 🚀 Quick Start Guide

### Step 1: Start MQTT Monitoring
Open a terminal and start monitoring MQTT messages:
```bash
python test_stt_mqtt_monitor.py
```

### Step 2: Send Test Commands
In another terminal, send test STT commands:
```bash
python test_send_stt_command.py "Hello Alicia, test the voice pipeline"
```

### Step 3: Check Pipeline Status
Run the comprehensive debugger to check all services:
```bash
python test_voice_pipeline_debug.py
```

## 📊 What to Look For

### STT Commands
Look for messages like:
```
🎤 STT COMMAND DETECTED!
   Time: 14:30:25.123
   Command: 'Hello Alicia, turn on the kitchen light'
   Length: 45 characters
   Total STT commands: 1
```

### Voice Responses
Look for messages like:
```
🔊 VOICE RESPONSE DETECTED!
   Time: 14:30:26.456
   Response: 'I'll turn on the kitchen light for you'
   Total responses: 1
```

### TTS Requests
Look for messages like:
```
🗣️  TTS REQUEST DETECTED!
   Time: 14:30:26.789
   Topic: alicia/tts/kitchen
   Message: I'll turn on the kitchen light for you
   Speaker: kitchen
   Total TTS requests: 1
```

## 🔧 Troubleshooting

### No STT Commands Detected
1. Check if your voice input system is running
2. Verify MQTT broker is accessible
3. Check if the voice assistant is subscribed to the correct topics

### No Voice Responses
1. Check if Grok integration is working
2. Verify TTS service is running
3. Check MQTT message flow

### No TTS Requests
1. Check if TTS service is accessible
2. Verify Sonos bridge is running
3. Check MQTT topic subscriptions

### Service Connectivity Issues
Run the diagnostic tool to check all services:
```bash
python test_voice_pipeline_debug.py
```

## 📝 MQTT Topics Monitored

- `alicia/voice/command` - STT commands
- `alicia/voice/response` - Voice responses
- `alicia/voice/status` - Voice status messages
- `alicia/voice/wake` - Wake word detection
- `alicia/tts/+` - TTS requests
- `alicia/tts/status` - TTS status
- `homeassistant/sensor/voice/#` - Voice sensor data

## 🎯 Expected Pipeline Flow

1. **STT Command** → `alicia/voice/command`
2. **Grok Processing** → Internal processing
3. **Voice Response** → `alicia/voice/response`
4. **TTS Request** → `alicia/tts/kitchen`
5. **Audio Playback** → Sonos speakers

## 📈 Monitoring Statistics

The tools track:
- STT command count
- Voice response count
- TTS request count
- Error count
- Average response time
- Service connectivity status

## 🔍 Advanced Debugging

For advanced debugging, use the interactive mode:
```bash
python test_live_stt_monitor.py interactive
```

This provides:
- Real-time audio recording
- Manual STT testing
- TTS testing with custom text
- Live MQTT monitoring
- Comprehensive diagnostics

## 📋 Requirements

- Python 3.7+
- paho-mqtt
- requests
- pyaudio (for audio recording)
- Grok handler (optional, for full integration)

## 🚨 Common Issues

1. **MQTT Connection Failed**: Check broker settings and credentials
2. **Audio Recording Failed**: Check microphone permissions and PyAudio installation
3. **Service Not Accessible**: Check if Docker containers are running
4. **Grok Processing Failed**: Check API key and network connectivity

## 💡 Tips

- Run multiple monitoring tools simultaneously for comprehensive coverage
- Use the simple MQTT monitor for basic debugging
- Use the comprehensive debugger for detailed analysis
- Check Docker container logs if services are not responding
- Verify all required environment variables are set
