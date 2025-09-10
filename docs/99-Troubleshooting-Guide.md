# Chapter 99: Comprehensive Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide covers common issues and their solutions for the Alicia Smart Home AI Assistant. The guide is organized by component and includes diagnostic procedures, error resolution, and preventive measures.

## Table of Contents

- [Docker & Container Issues](#docker--container-issues)
- [Database Problems](#database-problems)
- [MQTT Broker Issues](#mqtt-broker-issues)
- [Home Assistant Problems](#home-assistant-problems)
- [Voice Processing Issues](#voice-processing-issues)
- [Sonos Integration Problems](#sonos-integration-problems)
- [Network & Connectivity](#network--connectivity)
- [Performance Issues](#performance-issues)
- [Security & Authentication](#security--authentication)

---

## Docker & Container Issues

### Docker Daemon Not Responding

**Symptoms:**
- `docker: command not found` or `500 Internal Server Error`
- Commands fail with connection errors

**Solutions:**
```bash
# Restart Docker Desktop (Windows/macOS)
# Or restart Docker service (Linux)
sudo systemctl restart docker

# Check Docker status
docker info
docker version

# Verify Docker is running
docker ps
```

**Prevention:**
- Keep Docker Desktop updated
- Monitor system resources
- Use Docker Desktop's restart policy

### Container Startup Failures

**Symptoms:**
- Containers exit immediately after starting
- `docker-compose up` shows errors
- Health checks failing

**Common Causes & Solutions:**

#### Port Conflicts
```bash
# Check what's using the port
netstat -tulpn | grep :8123

# Find process using port
lsof -i :8123

# Kill conflicting process
sudo kill -9 <PID>

# Or change port mapping in docker-compose.yml
ports:
  - "8124:8123"
```

#### Missing Environment Variables
```bash
# Check environment file
cat home-assistant/.env

# Validate required variables
POSTGRES_DB=alicia_db
POSTGRES_USER=alicia_user
POSTGRES_PASSWORD=alicia_secure_2024
```

#### Volume Mount Issues
```bash
# Check directory permissions
ls -la /path/to/volume

# Fix permissions
sudo chown -R 1000:1000 /path/to/volume

# Verify Docker can access
docker run --rm -v /path/to/volume:/test alpine ls /test
```

### Container Health Check Failures

**Symptoms:**
- Containers show `unhealthy` status
- Services not responding to health checks

**Solutions:**
```bash
# Check container logs
docker logs alicia_homeassistant

# Test health check manually
docker exec alicia_homeassistant curl -f http://localhost:8123/api/

# Restart unhealthy containers
docker-compose restart homeassistant

# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Database Problems

### PostgreSQL Connection Refused

**Symptoms:**
- HA logs show database connection errors
- `psql: could not connect to server`

**Solutions:**
```bash
# Check database container status
docker ps | grep postgres

# Verify database is accepting connections
docker exec alicia_postgres pg_isready -U alicia_user -d alicia_db

# Check database logs
docker logs alicia_postgres

# Test connection from HA container
docker exec alicia_homeassistant nc -zv alicia_postgres 5432
```

### Database Schema Issues

**Symptoms:**
- Tables missing after container restart
- Migration errors in HA logs

**Solutions:**
```bash
# Run initialization scripts manually
docker exec alicia_postgres psql -U alicia_user -d alicia_db -f /docker-entrypoint-initdb.d/02-setup-extensions.sql
docker exec alicia_postgres psql -U alicia_user -d alicia_db -f /docker-entrypoint-initdb.d/03-create-schema.sql

# Verify tables exist
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "\dt alicia.*"

# Reset database if needed
docker-compose down
docker volume rm alicia_postgres_data
docker-compose up -d postgres
```

### pgvector Extension Issues

**Symptoms:**
- Vector operations failing
- AI model storage not working

**Solutions:**
```bash
# Check if extension is installed
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Install manually if missing
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify vector operations
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "SELECT '[1,2,3]'::vector(3) <=> '[1,2,4]'::vector(3);"
```

---

## MQTT Broker Issues

### Connection Refused

**Symptoms:**
- Clients cannot connect to MQTT broker
- `Connection refused` errors

**Solutions:**
```bash
# Check broker status
docker ps | grep mqtt

# Verify broker is listening
docker exec alicia_mqtt netstat -tlnp | grep 1883

# Check broker logs
docker logs alicia_mqtt

# Test connection
mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
```

### Authentication Failures

**Symptoms:**
- `Connection refused: bad username or password`
- MQTT clients failing to authenticate

**Solutions:**
```bash
# Check password file
docker exec alicia_mqtt cat /mosquitto/config/passwords

# Verify ACL permissions
docker exec alicia_mqtt cat /mosquitto/config/acl

# Test with correct credentials
mosquitto_pub -h localhost -p 1883 -u alicia -P alicia_ha_mqtt_2024 -t "test" -m "hello"

# Regenerate password file if corrupted
docker exec alicia_mqtt mosquitto_passwd -b /mosquitto/config/passwords alicia alicia_ha_mqtt_2024
```

### Topic Permission Issues

**Symptoms:**
- `ACL denied` errors in broker logs
- Messages not being published/received

**Solutions:**
```bash
# Check ACL configuration
docker exec alicia_mqtt cat /mosquitto/config/acl

# Test topic permissions
mosquitto_pub -h localhost -p 1883 -u voice_assistant -P alicia_ha_mqtt_2024 -t "alicia/tts/test" -m "test"

# Update ACL if needed
# Edit mqtt/config/acl file and restart broker
docker-compose restart mqtt
```

### High Latency or Message Loss

**Symptoms:**
- Slow message delivery
- Messages not reaching subscribers

**Solutions:**
```bash
# Check broker performance
docker stats alicia_mqtt

# Monitor active connections
docker exec alicia_mqtt netstat -t | grep 1883 | wc -l

# Check broker configuration
docker exec alicia_mqtt cat /mosquitto/config/mosquitto.conf

# Restart broker if needed
docker-compose restart mqtt
```

---

## Home Assistant Problems

### Configuration Errors

**Symptoms:**
- HA fails to start with config errors
- Deprecated option warnings

**Solutions:**
```yaml
# Fix deprecated options in configuration.yaml
# OLD (deprecated)
history:
  exclude:
    domains:
      - automation

# NEW (current)
history:
  exclude_domains:
    - automation
  exclude_entities:
    - sun.sun
```

### MQTT Integration Issues

**Symptoms:**
- Automations fail with MQTT subscription errors
- MQTT entities not appearing

**Solutions:**
1. Access HA web interface: `http://localhost:8123`
2. Go to **Settings > Devices & Services**
3. Click **Add Integration**
4. Search for and select **MQTT**
5. Configure with broker details:
   - **Broker**: `alicia_mqtt`
   - **Port**: `1883`
   - **Username**: `alicia`
   - **Password**: `alicia_ha_mqtt_2024`

### Database Connection Issues

**Symptoms:**
- HA shows database errors
- History and logbook not working

**Solutions:**
```yaml
# Update database configuration in configuration.yaml
recorder:
  db_url: postgresql://alicia_user:alicia_secure_2024@alicia_postgres:5432/alicia_db

history:
  db_url: postgresql://alicia_user:alicia_secure_2024@alicia_postgres:5432/alicia_db

logbook:
  db_url: postgresql://alicia_user:alicia_secure_2024@alicia_postgres:5432/alicia_db
```

### Add-on Installation Issues

**Symptoms:**
- Add-ons fail to install or start
- Supervisor errors

**Solutions:**
```bash
# Check HA supervisor status
docker exec alicia_homeassistant ha supervisor info

# Restart supervisor
docker exec alicia_homeassistant ha supervisor restart

# Check add-on logs
docker exec alicia_homeassistant ha logs
```

---

## Voice Processing Issues

### Wyoming Services Not Responding

**Symptoms:**
- TTS/STT services unavailable
- `Connection refused` to Wyoming ports

**Solutions:**
```bash
# Check service status
docker ps | grep wyoming

# Verify service logs
docker logs alicia_wyoming_whisper

# Test service connectivity
curl http://localhost:10300/info
curl http://localhost:10200/info
curl http://localhost:10400/info
```

### Model Download Failures

**Symptoms:**
- Services fail to start due to missing models
- Model download errors

**Solutions:**
```bash
# Download required models manually
cd voice-processing/models

# Whisper models
wget https://huggingface.co/rhasspy/wyoming-whisper/resolve/main/tiny-int8.tar.gz
tar -xzf tiny-int8.tar.gz

# Piper voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Porcupine keywords
wget https://github.com/Picovoice/porcupine/raw/master/resources/keyword_files/en/hey_alicia_en_windows_v2_1_0.ppn

# Restart services
docker-compose restart wyoming-whisper wyoming-piper wyoming-porcupine
```

### Audio Quality Issues

**Symptoms:**
- Poor TTS/STT quality
- Audio distortion or noise

**Solutions:**
```bash
# Check audio device configuration
arecord -l  # Linux
# Or check Windows audio devices

# Test audio pipeline
# Record test audio
arecord -d 5 -f cd test.wav

# Test Whisper STT
curl -X POST http://localhost:10300/transcribe \
  -F "file=@test.wav"

# Test Piper TTS
curl -X POST http://localhost:10200/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Test audio quality"}' \
  --output test_tts.wav

# Play test audio
aplay test_tts.wav
```

---

## Sonos Integration Problems

### Speaker Discovery Issues

**Symptoms:**
- Sonos speakers not found by bridge
- `No speakers discovered` in logs

**Solutions:**
```bash
# Check network connectivity
ping 192.168.1.101  # Kitchen speaker
ping 192.168.1.102  # Bedroom speaker

# Test from host machine
python -c "import soco; print(soco.discover())"

# Check firewall settings (Windows)
# Allow ports 80, 443, 554, 1400, 1900

# Restart Sonos bridge
docker-compose restart sonos-bridge
```

### Audio Playback Failures

**Symptoms:**
- TTS commands sent but no audio playback
- `UPnP Error 714` messages

**Solutions:**
```bash
# Check HTTP audio server
curl http://localhost:8080/

# Test audio file serving
curl -I http://localhost:8080/audio/test.mp3

# Verify volume mounts
docker exec sonos-bridge ls -la /tmp/audio

# Check speaker connectivity
docker exec sonos-bridge ping 192.168.1.101

# Restart audio server
.\start-audio-server.ps1
```

### Firewall Blocking Issues

**Symptoms:**
- Speakers can't access HTTP server
- Network connectivity issues

**Solutions (Windows):**
```powershell
# Add firewall rules
New-NetFirewallRule -DisplayName "Sonos HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Profile Any
New-NetFirewallRule -DisplayName "Sonos HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Profile Any
New-NetFirewallRule -DisplayName "Sonos RTSP" -Direction Inbound -Protocol TCP -LocalPort 554 -Profile Any
New-NetFirewallRule -DisplayName "Sonos Controller" -Direction Inbound -Protocol TCP -LocalPort 1400 -Profile Any
New-NetFirewallRule -DisplayName "Sonos Discovery" -Direction Inbound -Protocol UDP -LocalPort 1900 -Profile Any

# Enable UPnP
# Windows Services → UPnP Device Host → Start
```

### Volume Mount Issues

**Symptoms:**
- Audio files not accessible to speakers
- Docker volume mount failures

**Solutions:**
```bash
# Check volume mount syntax (Windows)
# In docker-compose.yml
volumes:
  - //c/temp/audio:/tmp/audio:rw

# Verify directory exists and has permissions
ls -la C:\temp\audio

# Test volume mount
docker run --rm -v //c/temp/audio:/test alpine ls /test
```

---

## Network & Connectivity

### Container Networking Issues

**Symptoms:**
- Services can't communicate with each other
- DNS resolution failures

**Solutions:**
```bash
# Check Docker network
docker network inspect alicia_network

# Verify container connectivity
docker exec alicia_homeassistant ping alicia_mqtt
docker exec alicia_homeassistant ping alicia_postgres

# Restart network
docker-compose down
docker-compose up -d

# Check DNS resolution
docker exec alicia_homeassistant nslookup alicia_mqtt
```

### Port Mapping Conflicts

**Symptoms:**
- Services not accessible on expected ports
- `Port already in use` errors

**Solutions:**
```bash
# Check port usage
netstat -tulpn | grep :8123

# Find conflicting process
lsof -i :8123

# Change port mapping
# Edit docker-compose.yml
ports:
  - "8124:8123"  # External 8124 → Internal 8123

# Restart services
docker-compose up -d
```

### DNS Resolution Problems

**Symptoms:**
- Container name resolution failures
- `Name resolution failure` errors

**Solutions:**
```bash
# Check Docker DNS
docker exec alicia_homeassistant cat /etc/resolv.conf

# Test DNS resolution
docker exec alicia_homeassistant nslookup alicia_mqtt

# Restart Docker daemon
sudo systemctl restart docker

# Recreate network
docker network rm alicia_network
docker-compose up -d
```

---

## Performance Issues

### High CPU Usage

**Symptoms:**
- Containers using excessive CPU
- System slowdown

**Solutions:**
```bash
# Monitor container resource usage
docker stats

# Check specific container
docker stats alicia_homeassistant

# Limit CPU usage in docker-compose.yml
services:
  homeassistant:
    deploy:
      resources:
        limits:
          cpus: '1.0'
        reservations:
          cpus: '0.5'
```

### High Memory Usage

**Symptoms:**
- Containers using excessive memory
- Out of memory errors

**Solutions:**
```bash
# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Set memory limits
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  homeassistant:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Slow Response Times

**Symptoms:**
- Slow TTS/STT processing
- Delayed MQTT message delivery

**Solutions:**
```bash
# Check system resources
top
free -h

# Monitor disk I/O
iotop

# Optimize database
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "VACUUM ANALYZE;"

# Check network latency
ping alicia_mqtt
```

---

## Security & Authentication

### MQTT Authentication Issues

**Symptoms:**
- Authentication failures
- Access denied errors

**Solutions:**
```bash
# Verify password file
docker exec alicia_mqtt cat /mosquitto/config/passwords

# Check password format
docker exec alicia_mqtt mosquitto_passwd -b /mosquitto/config/passwords test_user test_password

# Test authentication
mosquitto_pub -h localhost -p 1883 -u test_user -P test_password -t "test" -m "hello"
```

### File Permission Issues

**Symptoms:**
- Configuration files not readable
- Volume mount permission errors

**Solutions:**
```bash
# Check file permissions
ls -la home-assistant/config/configuration.yaml

# Fix permissions
sudo chown -R 1000:1000 home-assistant/config

# Check Docker volume permissions
docker run --rm -v $(pwd)/home-assistant/config:/test alpine ls -la /test
```

### SSL/TLS Configuration

**Symptoms:**
- HTTPS connection failures
- Certificate validation errors

**Solutions:**
```yaml
# Enable SSL in mosquitto.conf
listener 8883
protocol mqtt
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key

# Client SSL configuration
mosquitto_pub -h localhost -p 8883 \
  --cafile ca.crt \
  --cert client.crt \
  --key client.key \
  -t "test" -m "secure message"
```

---

## Diagnostic Tools

### System Health Check

```bash
#!/bin/bash
# comprehensive-health-check.sh

echo "=== Docker Services Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== Container Resource Usage ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\n=== Network Connectivity ==="
docker exec alicia_homeassistant ping -c 3 alicia_mqtt
docker exec alicia_homeassistant ping -c 3 alicia_postgres

echo -e "\n=== MQTT Broker Status ==="
docker exec alicia_mqtt netstat -tlnp | grep 1883

echo -e "\n=== Database Connectivity ==="
docker exec alicia_postgres pg_isready -U alicia_user -d alicia_db

echo -e "\n=== Voice Services Status ==="
curl -s http://localhost:10300/info | head -5
curl -s http://localhost:10200/info | head -5
```

### Log Analysis

```bash
# Monitor all logs
docker-compose logs -f

# Search for specific errors
docker-compose logs | grep -i error

# Analyze MQTT broker logs
docker logs alicia_mqtt | grep -i "connection\|auth\|acl"

# Check HA logs for issues
docker logs alicia_homeassistant | grep -i "error\|warning"
```

### Performance Monitoring

```bash
# Real-time monitoring
watch -n 2 'docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.NetIO}}"'

# MQTT message monitoring
mosquitto_sub -h localhost -p 1883 -u alicia -P alicia_ha_mqtt_2024 -t "#" -v

# Database performance
docker exec alicia_postgres psql -U alicia_user -d alicia_db -c "SELECT * FROM pg_stat_activity;"
```

---

## Preventive Maintenance

### Regular Tasks

1. **Update Docker Images**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

2. **Clean Up Resources**
   ```bash
   docker system prune -a
   docker volume prune
   ```

3. **Monitor Logs**
   ```bash
   # Set up log rotation
   docker-compose logs --tail=1000 > logs_$(date +%Y%m%d).txt
   ```

4. **Backup Configuration**
   ```bash
   # Backup HA config
   docker run --rm -v alicia_homeassistant_config:/config -v $(pwd)/backups:/backup alpine tar czf /backup/ha_config_$(date +%Y%m%d).tar.gz -C / config
   ```

### Monitoring Setup

1. **Health Checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8123/api/"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

2. **Log Rotation**
   ```bash
   # Configure log rotation in docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '1.0'
       reservations:
         memory: 512M
         cpus: '0.5'
   ```

---

## Emergency Recovery

### Complete System Reset

```bash
# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v
docker system prune -a

# Clean up networks
docker network prune

# Restart fresh
docker-compose up -d

# Restore configuration from backup
# (Restore HA config, MQTT passwords, etc.)
```

### Database Recovery

```bash
# Stop HA to prevent writes
docker-compose stop homeassistant

# Restore from backup
docker exec -i alicia_postgres psql -U alicia_user -d alicia_db < backup.sql

# Restart services
docker-compose up -d
```

### Configuration Recovery

```bash
# Restore HA configuration
docker run --rm -v alicia_homeassistant_config:/config -v $(pwd)/backups:/backup alpine tar xzf /backup/ha_config_latest.tar.gz -C /

# Restore MQTT configuration
cp backups/mqtt_config/* mqtt/config/

# Restart services
docker-compose restart
```

---

## Support Resources

### Documentation Links
- [Docker Troubleshooting](https://docs.docker.com/config/containers/troubleshooting/)
- [Home Assistant Troubleshooting](https://www.home-assistant.io/docs/troubleshooting/)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/troubleshooting.html)
- [MQTT Troubleshooting](https://mosquitto.org/man/mosquitto-8.html)

### Community Support
- [Home Assistant Community](https://community.home-assistant.io/)
- [Docker Forums](https://forums.docker.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/docker)

### Professional Support
- [Home Assistant Professional Services](https://www.home-assistant.io/support/)
- [Docker Enterprise Support](https://www.docker.com/support/)

---

**This troubleshooting guide covers the most common issues encountered with the Alicia Smart Home AI Assistant. For issues not covered here, please check the component-specific documentation or seek help from the community forums.**
