# 🔧 Troubleshooting MOC

**Map of Content for Alicia System Troubleshooting and Problem Resolution**

## 🎯 **Overview**

This MOC provides a comprehensive troubleshooting guide for the Alicia microservices architecture. It covers common issues, diagnostic procedures, and resolution strategies for all 23 services and their interactions.

## 🚨 **Quick Diagnostic Checklist**

### **System Health Check**
```bash
# 1. Check all services are running
docker ps --filter "name=alicia"

# 2. Check service health endpoints
curl http://localhost:8009/health  # Security Gateway
curl http://localhost:8010/health  # Device Registry
curl http://localhost:8026/health  # Config Service

# 3. Check MQTT broker connectivity
docker exec alicia_mqtt_broker mosquitto_pub -h localhost -t "test" -m "hello"

# 4. Check network connectivity
docker network inspect alicia_network
```

### **Common Issue Categories**
- **🔴 Critical**: System-wide failures
- **🟡 Important**: Service-specific issues
- **🟢 Standard**: Minor issues or warnings

## 🔴 **Critical Issues**

### **1. MQTT Broker Failure**

#### **Symptoms**
- All services fail to start
- Services cannot communicate
- Authentication failures
- Message delivery failures

#### **Diagnosis**
```bash
# Check if MQTT broker is running
docker ps --filter "name=mqtt"

# Check MQTT broker logs
docker logs alicia_mqtt_broker

# Test MQTT connectivity
docker exec alicia_mqtt_broker mosquitto_pub -h localhost -t "test" -m "hello"
```

#### **Resolution**
```bash
# Restart MQTT broker
docker restart alicia_mqtt_broker

# If restart fails, recreate container
docker stop alicia_mqtt_broker
docker rm alicia_mqtt_broker
docker run -d --name alicia_mqtt_broker \
  --network alicia_network -p 1884:1883 \
  eclipse-mosquitto:2.0.18
```

### **2. Security Gateway Failure**

#### **Symptoms**
- Authentication failures
- Service registration failures
- JWT token validation errors
- Certificate validation failures

#### **Diagnosis**
```bash
# Check Security Gateway health
curl http://localhost:8009/health

# Check Security Gateway logs
docker logs alicia_security_gateway

# Check certificate files
docker exec alicia_security_gateway ls -la /app/certs/
```

#### **Resolution**
```bash
# Restart Security Gateway
docker restart alicia_security_gateway

# If restart fails, check certificates
docker exec alicia_security_gateway openssl x509 -in /app/certs/ca.crt -text -noout
```

### **3. Device Registry Failure**

#### **Symptoms**
- Service discovery failures
- Device registration failures
- Service lookup failures
- Database connection errors

#### **Diagnosis**
```bash
# Check Device Registry health
curl http://localhost:8010/health

# Check Device Registry logs
docker logs alicia_device_registry

# Check database file
docker exec alicia_device_registry ls -la /app/data/
```

#### **Resolution**
```bash
# Restart Device Registry
docker restart alicia_device_registry

# If restart fails, check database
docker exec alicia_device_registry sqlite3 /app/data/devices.db ".tables"
```

## 🟡 **Important Issues**

### **1. Voice Pipeline Issues**

#### **STT Service Problems**
```bash
# Check STT Service health
curl http://localhost:8001/health

# Check STT Service logs
docker logs alicia_stt_service

# Test STT functionality
curl -X POST http://localhost:8001/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@test_audio.wav"
```

#### **AI Service Problems**
```bash
# Check AI Service health
curl http://localhost:8002/health

# Check AI Service logs
docker logs alicia_ai_service

# Test AI functionality
curl -X POST http://localhost:8002/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'
```

#### **TTS Service Problems**
```bash
# Check TTS Service health
curl http://localhost:8003/health

# Check TTS Service logs
docker logs alicia_tts_service

# Test TTS functionality
curl -X POST http://localhost:8003/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'
```

### **2. Device Integration Issues**

#### **Sonos Service Problems**
```bash
# Check Sonos Service health
curl http://localhost:8017/health

# Check Sonos Service logs
docker logs alicia_sonos_service

# Test Sonos discovery
curl -X POST http://localhost:8017/discover

# Check discovered speakers
curl http://localhost:8017/speakers
```

#### **HA Bridge Problems**
```bash
# Check HA Bridge health
curl http://localhost:8016/health

# Check HA Bridge logs
docker logs alicia_ha_bridge

# Test HA Bridge connectivity
curl http://localhost:8016/entities
```

### **3. Configuration Issues**

#### **Config Service Problems**
```bash
# Check Config Service health
curl http://localhost:8026/health

# Check Config Service logs
docker logs alicia_config_service

# Test configuration retrieval
curl http://localhost:8026/config/security_gateway
```

## 🟢 **Standard Issues**

### **1. Performance Issues**

#### **High CPU Usage**
```bash
# Check CPU usage
docker stats

# Check specific service CPU usage
docker exec alicia_service_name top

# Check system CPU usage
htop
```

#### **High Memory Usage**
```bash
# Check memory usage
docker stats

# Check specific service memory usage
docker exec alicia_service_name free -h

# Check system memory usage
free -h
```

#### **High Disk Usage**
```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up Docker resources
docker system prune -a
```

### **2. Network Issues**

#### **Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8009

# Kill process using port
sudo kill -9 $(lsof -t -i:8009)

# Check Docker port mappings
docker port alicia_service_name
```

#### **Network Connectivity**
```bash
# Check network connectivity
ping alicia_mqtt_broker

# Check DNS resolution
nslookup alicia_mqtt_broker

# Check network configuration
docker network inspect alicia_network
```

### **3. Log Issues**

#### **Log File Size**
```bash
# Check log file sizes
docker exec alicia_service_name du -sh /app/logs/*

# Rotate logs
docker exec alicia_service_name logrotate /etc/logrotate.conf

# Clean old logs
docker exec alicia_service_name find /app/logs -name "*.log" -mtime +7 -delete
```

#### **Log Level Configuration**
```bash
# Check current log level
docker exec alicia_service_name env | grep LOG_LEVEL

# Set log level
docker exec alicia_service_name export LOG_LEVEL=DEBUG
```

## 🔍 **Diagnostic Tools**

### **1. Service Health Monitoring**
```bash
#!/bin/bash
# comprehensive_health_check.sh

echo "🔍 Alicia System Health Check"
echo "============================="

# Check all services
services=(
  "8009:Security Gateway"
  "8010:Device Registry"
  "8015:Configuration Manager"
  "8026:Config Service"
  "8012:Discovery Service"
  "8013:Health Monitor"
  "8014:Service Orchestrator"
  "8001:STT Service"
  "8002:AI Service"
  "8003:TTS Service"
  "8004:Voice Router"
  "8006:Device Manager"
  "8016:HA Bridge"
  "8017:Sonos Service"
  "8018:Device Control"
  "8019:Grok Integration"
  "8020:Advanced Voice"
  "8021:Personality System"
  "8022:Multi-Language"
  "8023:Load Balancer"
  "8024:Metrics Collector"
  "8025:Event Scheduler"
)

for service in "${services[@]}"; do
  port=$(echo $service | cut -d: -f1)
  name=$(echo $service | cut -d: -f2)
  
  if curl -s -f http://localhost:$port/health > /dev/null; then
    echo "✅ $name (Port $port) - Healthy"
  else
    echo "❌ $name (Port $port) - Unhealthy"
  fi
done
```

### **2. System Resource Monitoring**
```bash
#!/bin/bash
# system_monitoring.sh

echo "📊 System Resource Monitoring"
echo "============================="

# CPU Usage
echo "CPU Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Memory Usage
echo -e "\nMemory Usage:"
free -h

# Disk Usage
echo -e "\nDisk Usage:"
df -h

# Network Usage
echo -e "\nNetwork Usage:"
docker network ls
```

### **3. Log Analysis**
```bash
#!/bin/bash
# log_analysis.sh

echo "📋 Log Analysis"
echo "==============="

# Check for errors in all services
for container in $(docker ps --filter "name=alicia" --format "{{.Names}}"); do
  echo "Checking $container for errors..."
  docker logs $container 2>&1 | grep -i error | tail -5
done

# Check for warnings
for container in $(docker ps --filter "name=alicia" --format "{{.Names}}"); do
  echo "Checking $container for warnings..."
  docker logs $container 2>&1 | grep -i warning | tail -5
done
```

## 🛠️ **Resolution Procedures**

### **1. Service Restart Procedures**

#### **Single Service Restart**
```bash
# Stop service
docker stop alicia_service_name

# Remove container
docker rm alicia_service_name

# Rebuild and restart
docker build -t alicia-service-name ./services/bus-services/service-name
docker run -d --name alicia_service_name \
  --network alicia_network -p PORT:PORT \
  alicia-service-name
```

#### **Multiple Service Restart**
```bash
# Stop all services
docker stop $(docker ps -q --filter "name=alicia")

# Remove all containers
docker rm $(docker ps -aq --filter "name=alicia")

# Restart in dependency order
./scripts/restart_all_services_comprehensive.bat
```

### **2. Configuration Recovery**

#### **Reset to Default Configuration**
```bash
# Stop Config Service
docker stop alicia_config_service

# Remove configuration data
docker exec alicia_config_service rm -rf /app/data/*

# Restart Config Service
docker start alicia_config_service
```

#### **Restore from Backup**
```bash
# Stop services
docker stop alicia_config_service

# Restore configuration
docker cp backup/config/ alicia_config_service:/app/data/

# Restart services
docker start alicia_config_service
```

### **3. Database Recovery**

#### **Device Registry Database**
```bash
# Stop Device Registry
docker stop alicia_device_registry

# Backup current database
docker cp alicia_device_registry:/app/data/devices.db ./backup/

# Restore from backup
docker cp ./backup/devices.db alicia_device_registry:/app/data/

# Restart Device Registry
docker start alicia_device_registry
```

## 📊 **Monitoring and Alerting**

### **1. Health Check Monitoring**
```bash
#!/bin/bash
# health_monitor.sh

while true; do
  # Check critical services
  critical_services=("8009" "8010" "8026")
  
  for port in "${critical_services[@]}"; do
    if ! curl -s -f http://localhost:$port/health > /dev/null; then
      echo "ALERT: Service on port $port is down!"
      # Send alert notification
    fi
  done
  
  sleep 30
done
```

### **2. Performance Monitoring**
```bash
#!/bin/bash
# performance_monitor.sh

while true; do
  # Check CPU usage
  cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" alicia_service_name | sed 's/%//')
  
  if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    echo "ALERT: High CPU usage: $cpu_usage%"
  fi
  
  # Check memory usage
  memory_usage=$(docker stats --no-stream --format "{{.MemPerc}}" alicia_service_name | sed 's/%//')
  
  if (( $(echo "$memory_usage > 90" | bc -l) )); then
    echo "ALERT: High memory usage: $memory_usage%"
  fi
  
  sleep 60
done
```

## 🔗 **Related MOCs**

- **[[Service Dependencies MOC]]** - Understanding service relationships
- **[[Deployment Pipeline MOC]]** - Deployment and management procedures
- **[[Architecture MOC]]** - System architecture understanding
- **[[Monitoring MOC]]** - System monitoring and alerting

## 📚 **Additional Resources**

- **[[Common Error Messages]]** - Error message reference
- **[[Performance Tuning]]** - Performance optimization techniques
- **[[Security Troubleshooting]]** - Security-related issues
- **[[Network Troubleshooting]]** - Network connectivity issues

## 🎯 **Prevention Strategies**

### **1. Proactive Monitoring**
- **Health Checks**: Regular health check monitoring
- **Performance Metrics**: Continuous performance tracking
- **Log Monitoring**: Real-time log analysis
- **Resource Monitoring**: CPU, memory, and disk usage tracking

### **2. Regular Maintenance**
- **Log Rotation**: Regular log file rotation
- **Resource Cleanup**: Regular cleanup of unused resources
- **Configuration Backup**: Regular configuration backups
- **Service Updates**: Regular service updates and patches

### **3. Documentation Updates**
- **Issue Tracking**: Document all issues and resolutions
- **Knowledge Base**: Maintain troubleshooting knowledge base
- **Runbooks**: Create detailed runbooks for common procedures
- **Training**: Regular team training on troubleshooting procedures

---

**This MOC provides a comprehensive troubleshooting guide for the Alicia system. Use it to quickly diagnose and resolve issues, maintain system health, and prevent future problems.**
