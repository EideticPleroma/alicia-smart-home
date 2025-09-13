# Parallel Service Build Plan

## 🚀 **Building 3 Services in Parallel**

**Date:** 2025-09-13  
**Status:** 🔄 **IN PROGRESS** - Building TTS, Voice Router, and Device Manager

## 📋 **Services Being Built**

### **1. TTS Service (Text-to-Speech)** 🔄
- **Image**: `alicia-tts-service`
- **Port**: 8006
- **Purpose**: Converts text to speech using Piper TTS
- **Dependencies**: Piper TTS models, audio processing libraries
- **Status**: Building in background

### **2. Voice Router** 🔄
- **Image**: `alicia-voice-router`
- **Port**: 8007
- **Purpose**: Orchestrates the complete voice pipeline
- **Dependencies**: MQTT communication, service coordination
- **Status**: Building in background

### **3. Device Manager** 🔄
- **Image**: `alicia-device-manager`
- **Port**: 8008
- **Purpose**: Manages and controls smart home devices
- **Dependencies**: Device protocols, MQTT communication
- **Status**: Building in background

## 🔧 **Configuration Updates Applied**

### **Port Assignments**
- **TTS Service**: 8006 (was 8003)
- **Voice Router**: 8007 (was 8004)
- **Device Manager**: 8008 (was 8006)

### **Dockerfile Updates**
- ✅ Added `service_wrapper.py` to all Dockerfiles
- ✅ Updated health check ports
- ✅ Updated exposed ports
- ✅ Fixed port conflicts

### **Service Code Updates**
- ✅ Updated main.py port configurations
- ✅ Ensured MQTT broker hostname is `alicia_bus_core`
- ✅ Added proper environment variable loading

## 🎯 **Deployment Plan**

### **Phase 1: Build Completion** (In Progress)
```bash
# TTS Service
docker build -t alicia-tts-service ./services/bus-services/tts-service

# Voice Router
docker build -t alicia-voice-router ./services/bus-services/voice-router

# Device Manager
docker build -t alicia-device-manager ./services/bus-services/device-manager
```

### **Phase 2: Service Deployment** (Next)
```bash
# TTS Service
docker run -d --name alicia_tts_service \
  --network alicia_network \
  -e MQTT_BROKER=alicia_bus_core \
  -e MQTT_PORT=1883 \
  -e OPENAI_API_KEY=mock_openai_key_for_testing \
  -p 8006:8006 \
  alicia-tts-service

# Voice Router
docker run -d --name alicia_voice_router \
  --network alicia_network \
  -e MQTT_BROKER=alicia_bus_core \
  -e MQTT_PORT=1883 \
  -p 8007:8007 \
  alicia-voice-router

# Device Manager
docker run -d --name alicia_device_manager \
  --network alicia_network \
  -e MQTT_BROKER=alicia_bus_core \
  -e MQTT_PORT=1883 \
  -p 8008:8008 \
  alicia-device-manager
```

### **Phase 3: Health Verification** (After Deployment)
```bash
# Check all services
docker ps

# Test health endpoints
curl http://localhost:8006/health  # TTS Service
curl http://localhost:8007/health  # Voice Router
curl http://localhost:8008/health  # Device Manager
```

## 📊 **Expected Service Architecture**

### **Complete Voice Pipeline**
```
User Voice Input → STT Service (8004) → AI Service (8005) → TTS Service (8006) → Audio Output
                                    ↓
                              Voice Router (8007) → Device Manager (8008)
```

### **Service Communication Flow**
1. **Voice Router** receives voice commands
2. **STT Service** processes audio to text
3. **AI Service** processes text and generates response
4. **TTS Service** converts response to speech
5. **Device Manager** executes device commands

## 🎯 **Success Criteria**

### **Build Success**
- ✅ All three images build without errors
- ✅ All Dockerfiles include service_wrapper.py
- ✅ Port configurations are correct
- ✅ Health checks are properly configured

### **Deployment Success**
- ✅ All services start successfully
- ✅ MQTT connections established
- ✅ Health endpoints responding
- ✅ Services can communicate via MQTT

### **Integration Success**
- ✅ Voice pipeline end-to-end working
- ✅ Device control commands working
- ✅ Service orchestration working
- ✅ Error handling and logging working

## 🚀 **Next Steps After Build**

1. **Deploy Services** - Start all three services
2. **Health Verification** - Test all health endpoints
3. **Integration Testing** - Test voice pipeline
4. **Device Testing** - Test device control
5. **Performance Testing** - Test under load

## 📝 **Build Progress Tracking**

- **TTS Service**: 🔄 Building (Piper TTS models)
- **Voice Router**: 🔄 Building (Service orchestration)
- **Device Manager**: 🔄 Building (Device protocols)

**Estimated Build Time**: 5-10 minutes per service
**Total Expected Time**: 10-15 minutes for all three

---

**🎯 GOAL**: Complete voice pipeline with 6 services running (MQTT + STT + AI + TTS + Voice Router + Device Manager)

**Status**: Building in parallel for maximum efficiency! 🚀




