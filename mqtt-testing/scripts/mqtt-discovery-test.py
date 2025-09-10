#!/usr/bin/env python3
"""
MQTT Discovery Test Script for Alicia Project
This script simulates MQTT devices that publish discovery messages
to test the automatic device discovery functionality.
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import argparse

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "alicia"
MQTT_PASSWORD = "alicia_ha_mqtt_2024"

# Test Devices Configuration
TEST_DEVICES = [
    {
        "name": "living_room_temperature",
        "type": "sensor",
        "device_class": "temperature",
        "unit": "°C",
        "topic": "home/livingroom/temperature",
        "state_topic": "home/livingroom/temperature/state",
        "config_topic": "homeassistant/sensor/living_room_temperature/config"
    },
    {
        "name": "bedroom_light",
        "type": "light",
        "topic": "home/bedroom/light",
        "command_topic": "home/bedroom/light/set",
        "state_topic": "home/bedroom/light/state",
        "config_topic": "homeassistant/light/bedroom_light/config"
    },
    {
        "name": "kitchen_motion",
        "type": "binary_sensor",
        "device_class": "motion",
        "topic": "home/kitchen/motion",
        "state_topic": "home/kitchen/motion/state",
        "config_topic": "homeassistant/binary_sensor/kitchen_motion/config"
    },
    {
        "name": "office_humidity",
        "type": "sensor",
        "device_class": "humidity",
        "unit": "%",
        "topic": "home/office/humidity",
        "state_topic": "home/office/humidity/state",
        "config_topic": "homeassistant/sensor/office_humidity/config"
    }
]

class MQTTDeviceSimulator:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, username=MQTT_USERNAME, password=MQTT_PASSWORD):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            self.connected = True
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("📡 Disconnected from MQTT broker")
        self.connected = False

    def connect(self):
        """Connect to MQTT broker"""
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        try:
            print(f"🔌 Connecting to {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    def publish_discovery(self, device):
        """Publish MQTT discovery message for a device"""
        if not self.connected:
            print("❌ Not connected to MQTT broker")
            return False

        # Create discovery payload based on device type
        if device["type"] == "sensor":
            payload = {
                "name": device["name"].replace("_", " ").title(),
                "state_topic": device["state_topic"],
                "device_class": device["device_class"],
                "unit_of_measurement": device["unit"],
                "value_template": "{{ value_json.value }}",
                "unique_id": f"alicia_{device['name']}",
                "device": {
                    "identifiers": [f"alicia_device_{device['name']}"],
                    "name": "Alicia Smart Home",
                    "manufacturer": "Alicia Project",
                    "model": "MQTT Device Simulator"
                }
            }
        elif device["type"] == "light":
            payload = {
                "name": device["name"].replace("_", " ").title(),
                "command_topic": device["command_topic"],
                "state_topic": device["state_topic"],
                "payload_on": "ON",
                "payload_off": "OFF",
                "unique_id": f"alicia_{device['name']}",
                "device": {
                    "identifiers": [f"alicia_device_{device['name']}"],
                    "name": "Alicia Smart Home",
                    "manufacturer": "Alicia Project",
                    "model": "MQTT Device Simulator"
                }
            }
        elif device["type"] == "binary_sensor":
            payload = {
                "name": device["name"].replace("_", " ").title(),
                "state_topic": device["state_topic"],
                "device_class": device["device_class"],
                "payload_on": "ON",
                "payload_off": "OFF",
                "unique_id": f"alicia_{device['name']}",
                "device": {
                    "identifiers": [f"alicia_device_{device['name']}"],
                    "name": "Alicia Smart Home",
                    "manufacturer": "Alicia Project",
                    "model": "MQTT Device Simulator"
                }
            }

        try:
            result = self.client.publish(device["config_topic"], json.dumps(payload), retain=True)
            result.wait_for_publish()
            print(f"📡 Published discovery for {device['name']} to {device['config_topic']}")
            return True
        except Exception as e:
            print(f"❌ Failed to publish discovery for {device['name']}: {e}")
            return False

    def publish_state(self, device):
        """Publish state data for a device"""
        if not self.connected:
            print("❌ Not connected to MQTT broker")
            return False

        # Generate realistic state data based on device type
        if device["type"] == "sensor":
            if device["device_class"] == "temperature":
                value = round(random.uniform(18.0, 25.0), 1)
            elif device["device_class"] == "humidity":
                value = random.randint(30, 70)
            else:
                value = random.randint(0, 100)

            payload = {"value": value, "timestamp": int(time.time())}

        elif device["type"] == "light":
            state = random.choice(["ON", "OFF"])
            payload = {"state": state, "brightness": random.randint(0, 255) if state == "ON" else 0}

        elif device["type"] == "binary_sensor":
            state = random.choice(["ON", "OFF"])
            payload = {"state": state}

        try:
            result = self.client.publish(device["state_topic"], json.dumps(payload))
            result.wait_for_publish()
            print(f"📊 Published state for {device['name']}: {payload}")
            return True
        except Exception as e:
            print(f"❌ Failed to publish state for {device['name']}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="MQTT Discovery Test Script")
    parser.add_argument("--broker", default=MQTT_BROKER, help="MQTT broker host")
    parser.add_argument("--port", type=int, default=MQTT_PORT, help="MQTT broker port")
    parser.add_argument("--username", default=MQTT_USERNAME, help="MQTT username")
    parser.add_argument("--password", default=MQTT_PASSWORD, help="MQTT password")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=30, help="State update interval in seconds")

    args = parser.parse_args()

    print("🚀 Starting MQTT Discovery Test for Alicia Project")
    print(f"📡 Broker: {args.broker}:{args.port}")
    print(f"👤 User: {args.username}")
    print("=" * 50)

    simulator = MQTTDeviceSimulator(args.broker, args.port, args.username, args.password)

    if not simulator.connect():
        print("❌ Failed to connect to MQTT broker")
        return 1

    # Wait for connection
    time.sleep(2)

    if not simulator.connected:
        print("❌ Connection timeout")
        return 1

    try:
        # Publish discovery messages for all devices
        print("🔍 Publishing MQTT discovery messages...")
        for device in TEST_DEVICES:
            simulator.publish_discovery(device)
            time.sleep(0.5)  # Small delay between discoveries

        print("✅ All discovery messages published!")
        print("📝 Devices should now appear in Home Assistant automatically")
        print("=" * 50)

        if args.once:
            print("🏁 One-time run complete")
            return 0

        # Continuously publish state updates
        print(f"🔄 Publishing state updates every {args.interval} seconds...")
        print("Press Ctrl+C to stop")

        while True:
            for device in TEST_DEVICES:
                simulator.publish_state(device)
                time.sleep(1)  # Small delay between devices

            print(f"⏰ Waiting {args.interval} seconds until next update...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n🛑 Stopping MQTT device simulator...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        simulator.disconnect()

    return 0

if __name__ == "__main__":
    exit(main())
