# Docker Configuration Fixes - Alicia Project

## Issue Summary
Docker containers were hanging during startup due to multiple configuration issues in Docker Compose files.

## Root Causes Identified

### 1. **Docker Daemon Not Running**
- **Issue**: Docker Desktop was not responding (500 Internal Server Error)
- **Impact**: All Docker commands failed
- **Solution**: Restart Docker Desktop manually

### 2. **Network Configuration Conflicts**
- **Issue**: Multiple files referenced different network names:
  - `home-assistant/docker-compose.yml` and `voice-processing/docker-compose.yml` referenced external network `postgres_alicia_network`
  - `postgres/docker-compose.yml` created its own `alicia_network`
  - External networks didn't exist, causing container startup failures
- **Impact**: Containers failed to start due to missing network dependencies
- **Solution**: Standardized all networks to use `alicia_network` with bridge driver

### 3. **Windows-Specific Networking Issues**
- **Issue**: Several files used `network_mode: host` which is problematic with Docker Desktop on Windows
- **Issue**: `docker-compose.sonos.yml` had macvlan configuration with `parent: eth0` (interface doesn't exist on Windows)
- **Impact**: Network connectivity failures on Windows systems
- **Solution**: Replaced `network_mode: host` with proper bridge networking

### 4. **Obsolete Docker Compose Syntax**
- **Issue**: All files used obsolete `version: '3.8'` field
- **Impact**: Warning messages and potential compatibility issues
- **Solution**: Removed version fields (obsolete in Docker Compose v2.0+)

### 5. **Missing Service Dependencies**
- **Issue**: Some services lacked proper dependency declarations
- **Impact**: Race conditions during startup
- **Solution**: Added `depends_on` declarations and health checks

### 6. **Inconsistent MQTT Broker References**
- **Issue**: Services referenced `localhost` for MQTT broker instead of container names
- **Impact**: Services couldn't communicate within Docker network
- **Solution**: Updated to use container names (`alicia_mqtt`, `alicia_mqtt_home`, etc.)

## Files Fixed

### docker-compose.host.yml
**Changes:**
- Removed obsolete `version: '3.8'`
- Replaced `network_mode: host` with bridge networking
- Added MQTT broker service (was commented out)
- Added health checks
- Updated MQTT broker reference from `localhost` to `alicia_mqtt`
- Added proper service dependencies

### docker-compose.sonos.yml
**Changes:**
- Removed obsolete `version: '3.8'`
- Replaced `network_mode: host` with bridge networking
- Removed problematic macvlan configuration
- Added health checks
- Updated MQTT broker reference
- Standardized network configuration

### home-assistant/docker-compose.yml
**Changes:**
- Replaced external network reference with local bridge network
- Removed `external: true` and `name: postgres_alicia_network`
- Added proper network driver configuration

### voice-processing/docker-compose.yml
**Changes:**
- Replaced external network reference with local bridge network
- Removed `external: true` and `name: postgres_alicia_network`
- Added proper network driver configuration

### mqtt-testing/docker-compose.fixed.yml
**Changes:**
- Removed obsolete `version: '3.8'`
- Replaced `network_mode: host` with bridge networking
- Added missing MQTT broker service
- Added health checks and dependencies
- Updated MQTT broker reference

## Network Architecture (After Fixes)

```
alicia_network (bridge driver)
├── alicia_postgres (postgres:5432)
├── alicia_mqtt (mosquitto:1883,9001)
├── homeassistant (:8123 → 18123)
├── alicia_whisper (:9000)
├── alicia_piper (:10200)
├── alicia_porcupine (:10400)
├── alicia_sonos_bridge
└── alicia_mqtt_home (additional MQTT instance)
```

## Testing Recommendations

1. **Start Docker Desktop** and ensure it's fully running
2. **Test individual services first:**
   ```bash
   cd postgres && docker-compose up -d
   cd ../home-assistant && docker-compose up -d
   cd ../voice-processing && docker-compose up -d
   ```
3. **Check container status:**
   ```bash
   docker ps -a
   docker-compose logs [service_name]
   ```
4. **Verify network connectivity:**
   ```bash
   docker network inspect alicia_network
   ```

## Prevention Measures

1. **Use consistent network naming** across all Docker Compose files
2. **Avoid `network_mode: host`** on Windows systems
3. **Always test Docker Compose files** with `docker-compose config` before deployment
4. **Use health checks** for proper service startup ordering
5. **Document network dependencies** clearly

## Next Steps

1. Restart Docker Desktop
2. Test the fixed configurations
3. Monitor container logs for any remaining issues
4. Consider implementing Docker Compose profiles for different deployment scenarios

## Files Modified
- `docker-compose.host.yml`
- `docker-compose.sonos.yml`
- `home-assistant/docker-compose.yml`
- `voice-processing/docker-compose.yml`
- `mqtt-testing/docker-compose.fixed.yml`

## Documentation Updates
- Created this troubleshooting guide
- Updated network architecture documentation
- Added testing procedures

---
*Document Version: 1.0*
*Date: 2025-01-09*
*Fixed By: Cline AI Assistant*
