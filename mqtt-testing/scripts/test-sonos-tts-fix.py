#!/usr/bin/env python3
"""
Test script to verify Sonos TTS functionality with correct entity names
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
        logger.info("Connected to MQTT broker")
        # Subscribe to TTS status topic
        client.subscribe("alicia/tts/status")
    else:
        logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        payload = json.loads(msg.payload.decode())
        logger.info(f"Received TTS status: {payload}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON message: {msg.payload}")

def test_tts_announcement(speaker_entity, message):
    """Test TTS announcement to a specific speaker"""
    logger.info(f"Testing TTS announcement to {speaker_entity}: '{message}'")
    
    # Create MQTT client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Send TTS command
        tts_payload = {
            "speaker": speaker_entity,
            "message": message,
            "language": "en"
        }
        
        topic = "alicia/tts/announce"
        client.publish(topic, json.dumps(tts_payload))
        logger.info(f"Published TTS command to {topic}: {tts_payload}")
        
        # Wait for response
        time.sleep(5)
        
    except Exception as e:
        logger.error(f"Error during TTS test: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

def main():
    """Main test function"""
    logger.info("🎵 SONOS TTS FIX TEST")
    logger.info("=" * 40)
    
    # Test with correct entity names
    speakers = [
        "media_player.kitchen",
        "media_player.bedroom"
    ]
    
    test_message = "Hello, this is a test of the Sonos TTS system. Can you hear me?"
    
    for speaker in speakers:
        logger.info(f"\n🔊 Testing {speaker}")
        test_tts_announcement(speaker, test_message)
        time.sleep(3)  # Wait between tests
    
    logger.info("\n✅ TTS tests completed!")
    logger.info("Check the Home Assistant logs for any errors.")

if __name__ == "__main__":
    main()
