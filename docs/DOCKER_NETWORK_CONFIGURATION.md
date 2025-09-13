# Docker Network Configuration for Alicia Services

## 🎯 **Network Architecture Overview**

Alicia uses a dedicated Docker network (`alicia_network`) for all service communication. This ensures proper isolation, security, and service discovery while maintaining the MQTT bus architecture.

## 🌐 **Network Configuration**

### **Docker Network Setup**
```yaml
networks:
  alicia_network:
    driver: bridge
    name: alicia_network
```

### **Service Communication**
- **MQTT Broker**: `alicia_bus_core` (container name)
- **Network**: `alicia_network` (bridge network)
- **Internal Communication**: Services communicate via container names
- **External Access**: Port mapping for external API access

## 🔧 **Service Network Configuration**

### **MQTT Broker (alicia_bus_core)**
```yaml
alicia-bus-core:
  container_name: alicia_bus_core
  networks:
    - alicia_network
  ports:
    - "1883:1883"    # MQTT
    - "8883:8883"    # MQTTS
    - "9001:9001"    # WebSocket
```

### **Service Configuration**
All services should connect to MQTT broker using:
- **Host**: `alicia_bus_core` (container name)
- **Port**: `1883` (internal MQTT port)
- **Network**: `alicia_network`

## 📋 **Service Deployment Order**

1. **Create Network**: `docker network create alicia_network`
2. **Start MQTT Broker**: `alicia_bus_core`
3. **Start Core Services**: Security Gateway, Device Registry
4. **Start Voice Services**: AI, STT, TTS, Voice Router
5. **Start Device Services**: Device Manager, HA Bridge
6. **Start Advanced Services**: Personality, Multi-Language, etc.

## 🚀 **Quick Start Commands**

### **Start Core Infrastructure**
```bash
# Create network
docker network create alicia_network

# Start MQTT broker
docker run -d --name alicia_bus_core \
  --network alicia_network \
  -p 1883:1883 -p 8883:8883 -p 9001:9001 \
  -v ./config/mqtt/mosquitto-simple.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto:2.0.18

# Start AI service
docker run -d --name alicia_ai_service \
  --network alicia_network \
  -e MQTT_BROKER=alicia_bus_core \
  -e MQTT_PORT=1883 \
  -e GROK_API_KEY=${GROK_API_KEY} \
  -p 8005:8005 \
  alicia-ai-service
```

### **Service Health Checks**
```bash
# Check MQTT broker
docker exec alicia_bus_core mosquitto_pub -h localhost -t "alicia/test" -m "test"

# Check AI service
curl http://localhost:8005/health

# Check all services
docker ps --filter "name=alicia"
```

## 🔍 **Debugging Network Issues**

### **Common Issues**
1. **Service can't connect to MQTT**: Check if services are on same network
2. **Port conflicts**: Ensure ports are properly mapped
3. **Service discovery**: Use container names, not localhost

### **Debug Commands**
```bash
# Check network
docker network ls
docker network inspect alicia_network

# Check service connectivity
docker exec alicia_ai_service ping alicia_bus_core
docker exec alicia_ai_service nslookup alicia_bus_core

# Check MQTT connectivity
docker exec alicia_ai_service python -c "
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect('alicia_bus_core', 1883, 60)
print('MQTT connection successful')
"
```

## 📝 **Service Environment Variables**

All services should use these environment variables:
```bash
MQTT_BROKER=alicia_bus_core
MQTT_PORT=1883
MQTT_USERNAME=<service_name>
MQTT_PASSWORD=<service_password>
```

## 🎯 **Best Practices**

1. **Always use container names** for internal communication
2. **Map ports** only for external API access
3. **Use the same network** for all services
4. **Test connectivity** before starting dependent services
5. **Monitor logs** for connection issues

---

*This configuration ensures proper service isolation while maintaining the MQTT bus architecture for seamless communication.*




