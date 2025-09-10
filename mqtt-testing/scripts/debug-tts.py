#!/usr/bin/env python3
"""
Debug TTS functionality step by step
"""

import json
import time
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "alicia"
MQTT_PASSWORD = "alicia_ha_mqtt_2024"

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
        # Subscribe to TTS status topic
        client.subscribe("alicia/tts/status")
        client.subscribe("alicia/commands/sonos/#")
    else:
        logger.error(f"❌ Failed to connect to MQTT broker. Return code: {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        payload = json.loads(msg.payload.decode())
        logger.info(f"📨 Received: {msg.topic} -> {payload}")
    except json.JSONDecodeError:
        logger.info(f"📨 Received: {msg.topic} -> {msg.payload.decode()}")

def test_single_tts():
    """Test a single TTS announcement with detailed logging"""
    logger.info("🔍 DEBUGGING TTS FUNCTIONALITY")
    logger.info("=" * 50)
    
    # Create MQTT client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to broker
        logger.info("🔌 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(3)
        
        # Send TTS command
        tts_payload = {
            "speaker": "media_player.kitchen",
            "message": "Debug test message",
            "language": "en"
        }
        
        topic = "alicia/tts/announce"
        logger.info(f"📤 Publishing TTS command to {topic}")
        logger.info(f"📤 Payload: {tts_payload}")
        
        client.publish(topic, json.dumps(tts_payload))
        
        # Wait for response
        logger.info("⏳ Waiting for response...")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"❌ Error during TTS test: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("🔌 Disconnected from MQTT broker")

if __name__ == "__main__":
    test_single_tts()
