# Alicia Bus Architecture - Introduction

## 🎯 **Project Overview**

Alicia is a production-ready, enterprise-grade smart home AI assistant built on a sophisticated 23-service message bus architecture.

## 🌟 **Key Features**

### **Voice Processing Pipeline**
- Speech-to-Text with OpenAI Whisper
- AI Processing with xAI Grok integration
- Text-to-Speech with Piper TTS
- Voice Router for orchestration

### **Smart Home Integration**
- Device Management and control
- Home Assistant Bridge
- Sonos Integration
- Device Discovery

### **Advanced AI Capabilities**
- Personality System
- Multi-language Support
- Context Awareness
- Emotion Detection

### **Enterprise Features**
- 23 Microservices with MQTT communication
- Load Balancing and scaling
- Health Monitoring
- Security Gateway
- Configuration Management

## 🏗️ **Architecture**

### **Microservices Design**
- 23 Independent Services
- MQTT-based communication
- Service Discovery
- Health Monitoring

### **Technology Stack**
- Python 3.11.7+, FastAPI 0.104.1+
- Eclipse Mosquitto 2.0.18+
- xAI Grok API, OpenAI Whisper, Piper TTS
- Docker, Docker Compose

## 🚀 **Quick Start**

```bash
# Deploy all services
docker-compose -f docker-compose.bus.yml up -d

# Verify deployment
docker-compose -f docker-compose.bus.yml ps
```

## 📊 **Service Overview**

- **Core Infrastructure**: 6 services
- **Voice Processing**: 4 services  
- **Device Integration**: 4 services
- **Advanced Features**: 4 services
- **Supporting Services**: 5 services

## 🔧 **Configuration**

### **Environment Variables**
```bash
GROK_API_KEY=your_grok_api_key
OPENAI_API_KEY=your_openai_api_key
HA_TOKEN=your_ha_token
```

### **Service Ports**
- Voice Router: 8004
- Health Monitor: 8083
- Load Balancer: 8085
- Metrics Collector: 8086

## 📚 **Next Steps**

1. [Installation](04-Installation.md)
2. [Configuration](05-Configuration.md)
3. [Service Details](07-Services/)
4. [Development](12-Development.md)