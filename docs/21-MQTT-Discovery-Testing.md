# MQTT Discovery Testing Guide

## Overview
This guide explains how to test the MQTT discovery functionality in the Alicia Smart Home project. The goal is to verify that devices can automatically register themselves with Home Assistant via MQTT discovery messages.

## Test Devices Created

The `mqtt-discovery-test.py` script simulates 4 different types of MQTT devices:

### 1. Living Room Temperature Sensor
- **Type**: Sensor (temperature)
- **Discovery Topic**: `homeassistant/sensor/living_room_temperature/config`
- **State Topic**: `home/livingroom/temperature/state`
- **Features**: Publishes temperature readings (18-25°C)

### 2. Bedroom Light
- **Type**: Light
- **Discovery Topic**: `homeassistant/light/bedroom_light/config`
- **Command Topic**: `home/bedroom/light/set`
- **State Topic**: `home/bedroom/light/state`
- **Features**: Supports ON/OFF commands, brightness control

### 3. Kitchen Motion Sensor
- **Type**: Binary Sensor (motion)
- **Discovery Topic**: `homeassistant/binary_sensor/kitchen_motion/config`
- **State Topic**: `home/kitchen/motion/state`
- **Features**: Detects motion (ON/OFF states)

### 4. Office Humidity Sensor
- **Type**: Sensor (humidity)
- **Discovery Topic**: `homeassistant/sensor/office_humidity/config`
- **State Topic**: `home/office/humidity/state`
- **Features**: Publishes humidity readings (30-70%)

## Prerequisites

1. **MQTT Setup Complete**: The HA MQTT setup script must have run successfully
2. **HA Connected to MQTT**: Home Assistant should be connected to the MQTT broker
3. **Discovery Enabled**: MQTT discovery should be enabled in HA configuration

## Running the Test

### Option 1: One-time Discovery Test
```bash
cd mqtt-testing/scripts
python3 mqtt-discovery-test.py --once
```

This will:
- Connect to the MQTT broker
- Publish discovery messages for all 4 devices
- Exit immediately

### Option 2: Continuous State Updates
```bash
cd mqtt-testing/scripts
python3 mqtt-discovery-test.py
```

This will:
- Connect to the MQTT broker
- Publish discovery messages for all devices
- Continuously publish state updates every 30 seconds
- Press Ctrl+C to stop

### Option 3: Custom Configuration
```bash
cd mqtt-testing/scripts
python3 mqtt-discovery-test.py \
  --broker localhost \
  --port 1883 \
  --username alicia \
  --password alicia_ha_mqtt_2024 \
  --interval 60 \
  --once
```

## Expected Results

### In Home Assistant UI
After running the discovery test, you should see:

1. **New Devices Section**: 4 new devices under "MQTT Device Simulator"
2. **New Entities**:
   - `sensor.living_room_temperature`
   - `light.bedroom_light`
   - `binary_sensor.kitchen_motion`
   - `sensor.office_humidity`

### In HA Logs
You should see discovery messages like:
```
INFO (MainThread) [homeassistant.components.mqtt.discovery] Found new component: sensor living_room_temperature
INFO (MainThread) [homeassistant.components.mqtt.discovery] Found new component: light bedroom_light
```

### In MQTT Test Script Output
```
✅ Connected to MQTT broker
🔍 Publishing MQTT discovery messages...
📡 Published discovery for living_room_temperature to homeassistant/sensor/living_room_temperature/config
📡 Published discovery for bedroom_light to homeassistant/light/bedroom_light/config
📡 Published discovery for kitchen_motion to homeassistant/binary_sensor/kitchen_motion/config
📡 Published discovery for office_humidity to homeassistant/sensor/office_humidity/config
✅ All discovery messages published!
📝 Devices should now appear in Home Assistant automatically
```

## Troubleshooting

### Devices Not Appearing
1. **Check MQTT Connection**: Ensure HA is connected to MQTT broker
2. **Verify Discovery**: Check that MQTT discovery is enabled in HA
3. **Check Logs**: Look for MQTT discovery errors in HA logs
4. **Test Broker**: Verify MQTT broker is running and accessible

### Authentication Issues
1. **Check Credentials**: Ensure correct username/password
2. **Verify ACL**: Check MQTT ACL permissions for the user
3. **Test Connection**: Try connecting with MQTT client manually

### Discovery Not Working
1. **Check Topics**: Verify discovery topics match HA configuration
2. **Validate Payload**: Ensure discovery payload format is correct
3. **Check Logs**: Look for MQTT discovery parsing errors

## Advanced Testing

### Test with Different MQTT Users
```bash
# Test with different user (if configured)
python3 mqtt-discovery-test.py --username esp32_device --password esp32_secure_2024
```

### Monitor MQTT Traffic
```bash
# Subscribe to all discovery topics
mosquitto_sub -h localhost -p 1883 -u alicia -P alicia_ha_mqtt_2024 -t "homeassistant/#" -v
```

### Debug Discovery Payloads
```bash
# Subscribe to specific discovery topic
mosquitto_sub -h localhost -p 1883 -u alicia -P alicia_ha_mqtt_2024 -t "homeassistant/sensor/living_room_temperature/config" -v
```

## Integration with Real Devices

Once testing is successful, real devices can use the same discovery format:

```python
# Example for ESP32 temperature sensor
import paho.mqtt.client as mqtt
import json

discovery_payload = {
    "name": "ESP32 Temperature",
    "state_topic": "home/esp32/temperature",
    "device_class": "temperature",
    "unit_of_measurement": "°C",
    "unique_id": "esp32_temp_001",
    "device": {
        "identifiers": ["esp32_001"],
        "name": "ESP32 Sensor Node",
        "manufacturer": "Espressif",
        "model": "ESP32-WROOM-32"
    }
}

client = mqtt.Client()
client.username_pw_set("esp32_device", "esp32_secure_2024")
client.connect("mqtt-broker", 1883)
client.publish("homeassistant/sensor/esp32_temperature/config", json.dumps(discovery_payload), retain=True)
```

## Next Steps

1. **Phase 5**: Full deployment testing
2. **Real Devices**: Implement discovery in actual IoT devices
3. **Automation**: Create automations based on discovered devices
4. **Monitoring**: Set up monitoring for device connectivity

---
**Test Status**: Ready for execution
**Last Updated**: 2025-01-09
**Version**: 1.0
