# Sonos Integration Guide for Alicia Smart Home
**Date:** September 8, 2025
**Status:** ✅ CONFIGURED - Ready for Testing
**Integration Type:** MQTT Bridge + Home Assistant

## Overview

This guide provides complete instructions for integrating Sonos speakers into the Alicia Smart Home system. The integration uses a Python MQTT bridge to connect Sonos speakers with the existing MQTT infrastructure and Home Assistant.

---

## Architecture

```
Sonos Speakers (Network) ↔ Sonos MQTT Bridge (Python) ↔ MQTT Broker ↔ Home Assistant
                                      ↕
                                 Voice Assistant (TTS)
```

### Components:
- **Sonos Speakers**: Physical audio devices on the home network
- **MQTT Bridge**: Python service that translates MQTT commands to Sonos API calls
- **Home Assistant**: Provides web interface and automation engine
- **Voice Assistant**: Sends TTS announcements via MQTT

---

## Prerequisites

### Hardware Requirements
- ✅ Sonos speakers connected to home network
- ✅ Same network segment as Home Assistant and MQTT broker
- ✅ Static IP addresses recommended for speakers

### Software Requirements
- ✅ Python 3.8+
- ✅ Docker containers running (Home Assistant, MQTT)
- ✅ Network connectivity between all components

### Network Configuration
- **Home Assistant**: `localhost:8123`
- **MQTT Broker**: `localhost:1883`
- **Sonos Speakers**: `192.168.1.100-102` (example IPs)

---

## Configuration Steps

### Step 1: Environment Setup

1. **Update Home Assistant Environment Variables**
   ```bash
   # Copy and edit the .env file
   cp home-assistant/.env.example home-assistant/.env

   # Update with your actual Sonos speaker IPs
   SONOS_HOST_LIVING_ROOM=192.168.1.100
   SONOS_HOST_KITCHEN=192.168.1.101
   SONOS_HOST_BEDROOM=192.168.1.102
   ```

2. **Install Python Dependencies**
   ```bash
   cd mqtt-testing/scripts
   pip install -r requirements.txt
   ```

### Step 2: Home Assistant Configuration

The following files have been configured:

#### `configuration.yaml` - Sonos Integration
```yaml
# Sonos Integration
sonos:
  media_player:
    - host: !env_var SONOS_HOST_LIVING_ROOM
      name: "Living Room Sonos"
    - host: !env_var SONOS_HOST_KITCHEN
      name: "Kitchen Sonos"
    - host: !env_var SONOS_HOST_BEDROOM
      name: "Bedroom Sonos"

# Text-to-Speech Integration
tts:
  - platform: google_translate
    language: 'en'
    cache: true
    cache_dir: /tmp/tts
    time_memory: 300
```

#### `automations.yaml` - Sonos Automations
- **TTS Announcements**: Play voice messages through speakers
- **Volume Control**: Adjust speaker volume via MQTT
- **Playback Control**: Play/pause/stop music playback
- **Group Management**: Create multi-room audio groups
- **Status Monitoring**: Periodic status updates

### Step 3: MQTT Configuration

#### ACL Permissions Added
```acl
# Sonos Speaker User
user sonos_speaker
topic write alicia/devices/sonos/+/status
topic write alicia/audio/+/status
topic write homeassistant/media_player/#
topic read alicia/commands/sonos/+
topic read alicia/tts/+
topic read alicia/audio/+/command
```

#### Password File Updated
- Added `sonos_speaker` user with authentication credentials

### Step 4: Start Services

1. **Start MQTT Broker**
   ```bash
   docker-compose up -d mqtt
   ```

2. **Start Home Assistant**
   ```bash
   docker-compose up -d home-assistant
   ```

3. **Start Sonos MQTT Bridge**
   ```bash
   cd mqtt-testing/scripts
   python sonos-mqtt-bridge.py
   ```

---

## MQTT Topic Structure

### Command Topics (Subscribe)
```
alicia/commands/sonos/{speaker_name}     # Individual speaker commands
alicia/commands/sonos/group              # Multi-room group commands
alicia/commands/sonos/volume             # Volume control
alicia/commands/sonos/playback           # Playback control
alicia/tts/announce                      # TTS announcements
```

### Status Topics (Publish)
```
alicia/devices/sonos/{speaker_name}/status    # Speaker status updates
alicia/devices/sonos/group/status             # Group status updates
alicia/tts/status                             # TTS completion status
homeassistant/media_player/#                   # HA media player updates
```

---

## JSON Payload Formats

### TTS Announcement
```json
{
  "speaker": "media_player.living_room_sonos",
  "message": "Hello from Alicia Smart Home",
  "language": "en",
  "volume": 30
}
```

### Volume Control
```json
{
  "speaker": "media_player.living_room_sonos",
  "volume": 0.5
}
```

### Playback Control
```json
{
  "speaker": "media_player.living_room_sonos",
  "action": "play"
}
```

### Group Creation
```json
{
  "master": "media_player.living_room_sonos",
  "members": ["media_player.kitchen_sonos", "media_player.bedroom_sonos"]
}
```

### Status Response
```json
{
  "device_id": "living_room_sonos",
  "device_type": "sonos_speaker",
  "state": "PLAYING",
  "volume": 25,
  "current_track": "Jazz Classics",
  "group_members": ["living_room_sonos", "kitchen_sonos"],
  "wifi_signal_strength": 85,
  "timestamp": "2025-09-08T23:27:15.123456"
}
```

---

## Testing Procedures

### Automated Testing
```powershell
# Run the integration test script
.\mqtt-testing\scripts\test-sonos-integration.ps1 -SpeakerName "living_room_sonos"
```

### Manual Testing Steps

1. **Verify Speaker Discovery**
   ```bash
   # Check MQTT bridge logs for discovered speakers
   tail -f /dev/null  # Monitor bridge output
   ```

2. **Test MQTT Connection**
   ```bash
   # Use MQTT client to test connection
   mosquitto_pub -h localhost -p 1883 -u sonos_speaker -P alicia_ha_mqtt_2024 -t "alicia/commands/sonos/living_room_sonos" -m '{"command": "status"}'
   ```

3. **Test Home Assistant Integration**
   - Open HA web interface: `http://localhost:8123`
   - Check for Sonos media players in the UI
   - Test manual control of speakers

4. **Test TTS Announcements**
   ```bash
   # Send TTS command via MQTT
   mosquitto_pub -h localhost -p 1883 -u mobile_app -P alicia_ha_mqtt_2024 -t "alicia/tts/announce" -m '{"speaker": "media_player.living_room_sonos", "message": "Test announcement", "volume": 25}'
   ```

### Expected Test Results
- ✅ Speakers appear in Home Assistant dashboard
- ✅ MQTT messages are processed without errors
- ✅ Speaker status updates are published
- ✅ TTS announcements play through speakers
- ✅ Volume and playback controls work
- ✅ Multi-room grouping functions

---

## Usage Examples

### Voice Assistant Integration
```python
# Example: Send TTS announcement from voice assistant
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.username_pw_set("voice_assistant", "alicia_ha_mqtt_2024")
client.connect("localhost", 1883)

payload = {
    "speaker": "media_player.living_room_sonos",
    "message": "The front door is open",
    "volume": 30
}

client.publish("alicia/tts/announce", json.dumps(payload))
```

### Mobile App Control
```javascript
// Example: Control speaker volume from mobile app
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883', {
  username: 'mobile_app',
  password: 'alicia_ha_mqtt_2024'
});

const volumeCommand = {
  speaker: 'media_player.living_room_sonos',
  volume: 0.7
};

client.publish('alicia/commands/sonos/volume', JSON.stringify(volumeCommand));
```

### Home Assistant Automation
```yaml
# Example: Announce when someone arrives home
automation:
  - alias: "Welcome Home Announcement"
    trigger:
      platform: device
      device_id: !secret phone_device_id
      domain: device_tracker
      entity_id: device_tracker.phone
      from: 'not_home'
      to: 'home'
    action:
      - service: mqtt.publish
        data:
          topic: "alicia/tts/announce"
          payload_template: >
            {
              "speaker": "media_player.living_room_sonos",
              "message": "Welcome home!",
              "volume": 25
            }
```

---

## Troubleshooting

### Common Issues

#### 1. Speakers Not Found
**Symptoms:** Bridge logs show "No Sonos speakers found"
**Solutions:**
- Verify speakers are on the same network
- Check speaker IP addresses in Sonos app
- Ensure speakers are powered on
- Restart Sonos MQTT bridge

#### 2. MQTT Connection Failed
**Symptoms:** Bridge fails to connect to MQTT broker
**Solutions:**
- Verify broker is running: `docker ps`
- Check MQTT credentials in bridge script
- Confirm network connectivity to localhost:1883
- Check broker logs for authentication errors

#### 3. TTS Not Working
**Symptoms:** No audio from speakers during TTS
**Solutions:**
- Verify Google TTS service is accessible
- Check speaker volume levels
- Ensure speaker is not muted
- Test manual TTS through Home Assistant

#### 4. No Audio Playback
**Symptoms:** Speakers don't respond to playback commands
**Solutions:**
- Check if speakers have music sources configured
- Verify speaker grouping hasn't broken playback
- Test manual control through Sonos app
- Restart speakers if necessary

#### 5. Home Assistant Not Responding
**Symptoms:** HA web interface shows errors
**Solutions:**
- Check HA logs: `docker logs home-assistant`
- Verify configuration syntax
- Restart HA: `docker-compose restart home-assistant`
- Check MQTT integration status in HA

### Diagnostic Commands

```bash
# Check running containers
docker ps

# View MQTT broker logs
docker logs mqtt

# View Home Assistant logs
docker logs home-assistant

# Test MQTT connectivity
mosquitto_pub -h localhost -p 1883 -u sonos_speaker -P alicia_ha_mqtt_2024 -t "test" -m "hello"

# Check network connectivity to speakers
ping 192.168.1.100

# Monitor MQTT messages
mosquitto_sub -h localhost -p 1883 -u mobile_app -P alicia_ha_mqtt_2024 -t "alicia/devices/sonos/#"
```

---

## Security Considerations

### Authentication
- ✅ MQTT broker requires authentication
- ✅ Separate user credentials for each device type
- ✅ ACL permissions restrict topic access
- ✅ Passwords are hashed in password file

### Network Security
- ✅ Speakers should be on trusted home network
- ✅ Consider VLAN isolation for IoT devices
- ✅ Regular firmware updates for speakers
- ✅ Monitor for unauthorized network access

### Access Control
- ✅ MQTT topics are restricted by ACL
- ✅ Home Assistant requires authentication
- ✅ API endpoints protected
- ✅ Audit logs for MQTT messages

---

## Performance Optimization

### Bridge Configuration
- Status updates every 30 seconds (configurable)
- Automatic speaker rediscovery on failure
- Error handling with reconnection logic
- Minimal resource usage

### Network Considerations
- Use wired connections for best audio quality
- Avoid network congestion during audio streaming
- Consider QoS settings for MQTT messages
- Monitor network latency for real-time control

### Home Assistant Optimization
- Use automation triggers instead of polling
- Configure appropriate update intervals
- Monitor HA resource usage
- Consider separate HA instance for audio control

---

## Future Enhancements

### Planned Features
- **Advanced TTS**: Integration with Piper TTS for offline announcements
- **Audio Streaming**: Stream audio content from various sources
- **Voice Control**: Direct voice commands to speakers
- **Smart Scheduling**: Automated volume adjustments based on time/location
- **Energy Monitoring**: Track speaker power consumption
- **Multi-Zone Support**: Enhanced multi-room audio management

### Integration Possibilities
- **Spotify Connect**: Direct streaming from Spotify
- **AirPlay**: Apple device integration
- **Bluetooth**: Wireless audio source support
- **Voice Assistant**: Enhanced voice command processing
- **Mobile App**: Dedicated Sonos control interface

---

## Support and Maintenance

### Monitoring
- Monitor MQTT bridge logs for errors
- Check Home Assistant logs for integration issues
- Verify speaker connectivity regularly
- Monitor network performance

### Updates
- Keep Python dependencies updated
- Update Sonos firmware regularly
- Monitor for Home Assistant updates
- Backup configurations before changes

### Documentation Updates
- Update IP addresses when network changes
- Document new automation rules
- Maintain troubleshooting procedures
- Track integration changes

---

*This integration provides a solid foundation for voice-controlled smart home audio. The MQTT-based architecture ensures reliable communication and easy expansion for future features.*
