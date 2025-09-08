---
tags: #phase-2 #step-3 #device-simulation #configuration-guide #esp32 #tplink #sonos #mqtt-topics #arduino-code #home-assistant-integration #alicia-project
---

# Phase 2 - Step 3: Device Simulation & Configuration Guide
**Date:** September 8, 2025
**Status:** 🔄 IN PROGRESS - Step 3.2 Device Simulations
**Duration:** Starting device simulation testing

## Executive Summary

Continuing device discovery and simulation testing with comprehensive device simulations and configuration guides for real-world device integration.

---

## Step 3.2: Advanced Device Simulations
**Status:** 🔄 IN PROGRESS
**Goal:** Test different device types and create configuration guides

### Device Types Tested:

#### 1. **ESP32 Temperature/Humidity Sensor**
**Simulation Results:**
```
✅ Device ID: esp32_living_room
✅ Temperature: 23°C
✅ Humidity: 45%
✅ Battery: 87%
✅ Topic: alicia/sensors/esp32_living_room
✅ JSON Format: Valid
```

**Real Device Configuration:**
```cpp
// ESP32 Arduino Code Template
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// MQTT Configuration
const char* mqtt_server = "192.168.1.100";  // Your PC's IP
const char* mqtt_user = "esp32_device";
const char* mqtt_password = "alicia_ha_mqtt_2024";
const char* client_id = "esp32_living_room";

// Sensor Configuration
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// MQTT Topics
const char* temp_topic = "alicia/sensors/esp32_living_room/temperature";
const char* humid_topic = "alicia/sensors/esp32_living_room/humidity";
const char* status_topic = "alicia/sensors/esp32_living_room/status";

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Connect to WiFi
  WiFi.begin("YourWiFiSSID", "YourWiFiPassword");

  // Connect to MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read sensors every 30 seconds
  static unsigned long lastReading = 0;
  if (millis() - lastReading > 30000) {
    float temp = dht.readTemperature();
    float humid = dht.readHumidity();

    // Publish sensor data
    char temp_str[8];
    dtostrf(temp, 1, 1, temp_str);
    client.publish(temp_topic, temp_str);

    char humid_str[8];
    dtostrf(humid, 1, 1, humid_str);
    client.publish(humid_topic, humid_str);

    lastReading = millis();
  }
}
```

#### 2. **TP-Link Smart Bulb (Kasa Series)**
**Simulation Results:**
```
✅ Device ID: tplink_bulb_001
✅ State: on
✅ Brightness: 75%
✅ Color: warm_white
✅ Power: 12.5W
✅ Topic: alicia/devices/tplink_bulb_001/status
```

**Home Assistant Configuration:**
```yaml
# Add to configuration.yaml
light:
  - platform: template
    lights:
      tplink_bulb:
        friendly_name: "Living Room Bulb"
        value_template: "{{ states('sensor.tplink_bulb_state') }}"
        level_template: "{{ states('sensor.tplink_bulb_brightness') }}"
        turn_on:
          service: mqtt.publish
          data:
            topic: "alicia/commands/tplink_bulb_001"
            payload: '{"command": "turn_on", "brightness": 255}'
        turn_off:
          service: mqtt.publish
          data:
            topic: "alicia/commands/tplink_bulb_001"
            payload: '{"command": "turn_off"}'
        set_level:
          service: mqtt.publish
          data:
            topic: "alicia/commands/tplink_bulb_001"
            payload: '{"command": "set_brightness", "brightness": {{ brightness }}}'
```

#### 3. **Sonos Speaker System**
**Simulation Results:**
```
✅ Device ID: sonos_living_room
✅ Playback State: playing
✅ Volume: 28%
✅ Current Track: Jazz Classics
✅ Group Members: living_room_sonos, kitchen_sonos
✅ WiFi Signal: 82%
✅ Topic: alicia/devices/sonos_living_room/status
```

**Sonos Integration Options:**

**Option A: MQTT Bridge (Recommended)**
```python
# Python script to bridge Sonos API to MQTT
import soco
import paho.mqtt.client as mqtt
import json
import time

# Sonos Configuration
speaker_ip = "192.168.1.150"  # Sonos speaker IP
speaker = soco.SoCo(speaker_ip)

# MQTT Configuration
mqtt_client = mqtt.Client("sonos_bridge")
mqtt_client.username_pw_set("voice_assistant", "alicia_ha_mqtt_2024")
mqtt_client.connect("localhost", 1883, 60)

def publish_sonos_status():
    status = {
        "device_id": "sonos_living_room",
        "playback_state": speaker.get_current_transport_info()['current_transport_state'],
        "volume": speaker.volume,
        "current_track": speaker.get_current_track_info()['title'],
        "artist": speaker.get_current_track_info()['artist']
    }

    mqtt_client.publish("alicia/devices/sonos_living_room/status",
                       json.dumps(status))

# Main loop
while True:
    publish_sonos_status()
    time.sleep(10)  # Update every 10 seconds
```

**Option B: Direct MQTT Control**
```yaml
# Home Assistant configuration for Sonos MQTT control
media_player:
  - platform: mqtt
    name: "Living Room Sonos"
    state_topic: "alicia/devices/sonos_living_room/status"
    command_topic: "alicia/commands/sonos_living_room"
    availability_topic: "alicia/devices/sonos_living_room/availability"

    # Volume control
    volume_state_topic: "alicia/devices/sonos_living_room/volume"
    volume_command_topic: "alicia/commands/sonos_living_room/volume"

    # Playback control
    supported_features:
      - PAUSE
      - PLAY
      - STOP
      - VOLUME_SET
      - VOLUME_MUTE
```

---

## Step 3.3: Device Configuration Guide
**Status:** 📝 DOCUMENTING
**Goal:** Create comprehensive setup guides for each device type

### **Network Setup Requirements**

#### **Local Network Testing (Current Setup)**
- **Devices connect to same WiFi** as your PC
- **Direct MQTT communication** via localhost:1883
- **No additional configuration** needed
- **Perfect for initial testing**

#### **Remote Device Access (Future Setup)**
- **Port forwarding** on your router (port 1883)
- **Dynamic DNS** for changing IP addresses
- **VPN setup** for secure remote access
- **Cloud MQTT broker** as backup option

### **Device-Specific Setup Instructions**

#### **ESP32 Development Setup**
1. **Hardware Requirements:**
   - ESP32 development board ($5-15)
   - DHT22 temperature/humidity sensor ($5)
   - Jumper wires and breadboard
   - USB cable for programming

2. **Software Setup:**
   ```bash
   # Install Arduino IDE
   # Add ESP32 board support
   # Install required libraries:
   # - WiFi
   # - PubSubClient (MQTT)
   # - DHT sensor library
   ```

3. **Configuration Steps:**
   - Update WiFi credentials
   - Set MQTT broker IP (your PC's IP)
   - Configure device ID and topics
   - Upload code to ESP32

#### **TP-Link Smart Device Setup**
1. **Hardware Requirements:**
   - TP-Link Kasa smart bulb/plug ($10-30)
   - TP-Link Kasa app installed

2. **Integration Options:**
   - **Direct MQTT**: Use custom firmware (advanced)
   - **API Bridge**: Python script to bridge TP-Link API to MQTT
   - **Home Assistant Integration**: Use HA's TP-Link integration

#### **Sonos Speaker Setup**
1. **Hardware Requirements:**
   - Sonos speaker ($200-400)
   - Sonos S1/S2 app installed

2. **Integration Options:**
   - **MQTT Bridge Script**: Python script monitoring Sonos API
   - **Home Assistant Integration**: Use HA's Sonos integration
   - **Direct MQTT Control**: Custom control scripts

---

## Step 3.4: Testing Results & Validation
**Status:** ✅ COMPLETED BASIC TESTING
**Goal:** Validate device simulation and communication patterns

### Test Results Summary:

#### **✅ MQTT Communication Tests**
- **Connection Authentication:** ✅ Working
- **Topic Publishing:** ✅ Working
- **Message Formatting:** ✅ JSON validation passed
- **Security:** ✅ Access control enforced

#### **✅ Device Simulation Tests**
- **ESP32 Sensor:** ✅ Realistic data generation
- **Smart Bulb:** ✅ State and control simulation
- **Sonos Speaker:** ✅ Playback and volume simulation
- **JSON Payloads:** ✅ Properly formatted

#### **✅ Configuration Validation**
- **Topic Structure:** ✅ Consistent naming
- **User Permissions:** ✅ ACL rules working
- **Network Connectivity:** ✅ All services communicating

---

## Current System Status:
- ✅ **MQTT Broker**: Running on localhost:1883
- ✅ **Authentication**: 4 users configured (alicia, esp32_device, voice_assistant, mobile_app)
- ✅ **Security**: ACL permissions active
- ✅ **Network**: Connected via alicia_network
- ✅ **Home Assistant**: Operational on localhost:18123
- ✅ **Device Simulations**: Working for ESP32, TP-Link, Sonos
- ✅ **Configuration Guides**: Created for all device types

## Next Steps:
1. **Complete Step 3.2** - Test additional device types
2. **Step 3.3** - Home Assistant discovery integration
3. **Step 3.4** - End-to-end communication testing
4. **Step 3.5** - Performance monitoring and optimization

---

*Report will be updated as each step is completed...*
