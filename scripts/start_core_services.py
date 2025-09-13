"""
Start Core Services Script
Builds and starts core services step by step
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_mqtt_broker():
    """Start MQTT broker"""
    logger.info("🚀 Starting MQTT Broker...")
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d", "mqtt-broker"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("✅ MQTT Broker started")
            time.sleep(3)  # Wait for broker to be ready
            return True
        else:
            logger.error(f"❌ MQTT Broker failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ MQTT Broker error: {e}")
        return False

def test_mqtt_connection():
    """Test MQTT connection"""
    logger.info("🧪 Testing MQTT connection...")
    try:
        from paho.mqtt import client as mqtt_client
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("✅ MQTT connection successful")
            else:
                logger.error(f"❌ MQTT connection failed: {rc}")
        
        client = mqtt_client.Client()
        client.on_connect = on_connect
        client.connect("localhost", 1883, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
        return True
    except Exception as e:
        logger.error(f"❌ MQTT test failed: {e}")
        return False

def build_ai_service():
    """Build AI service"""
    logger.info("🔨 Building AI Service...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "alicia-ai-service", "./services/bus-services/ai-service"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("✅ AI Service built successfully")
            return True
        else:
            logger.error(f"❌ AI Service build failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ AI Service build error: {e}")
        return False

def start_ai_service():
    """Start AI service"""
    logger.info("🚀 Starting AI Service...")
    try:
        result = subprocess.run([
            "docker", "run", "-d",
            "--name", "alicia-ai-service",
            "--network", "aliciav1_alicia_network",
            "-p", "8005:8005",
            "-e", "MQTT_BROKER=mqtt-broker",
            "-e", "MQTT_PORT=1883",
            "-e", f"GROK_API_KEY={subprocess.check_output(['echo', '%GROK_API_KEY%'], shell=True).decode().strip()}",
            "alicia-ai-service"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ AI Service started")
            time.sleep(5)  # Wait for service to be ready
            return True
        else:
            logger.error(f"❌ AI Service start failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ AI Service start error: {e}")
        return False

def test_ai_service():
    """Test AI service"""
    logger.info("🧪 Testing AI Service...")
    try:
        response = requests.get("http://localhost:8005/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ AI Service healthy: {health_data.get('status', 'unknown')}")
            return True
        else:
            logger.warning(f"⚠️ AI Service health check returned {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ AI Service health check failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting Core Services Deployment")
    
    # Step 1: Start MQTT Broker
    if not start_mqtt_broker():
        logger.error("❌ Failed to start MQTT Broker")
        return 1
    
    # Step 2: Test MQTT Connection
    if not test_mqtt_connection():
        logger.error("❌ MQTT connection test failed")
        return 1
    
    # Step 3: Build AI Service
    if not build_ai_service():
        logger.error("❌ Failed to build AI Service")
        return 1
    
    # Step 4: Start AI Service
    if not start_ai_service():
        logger.error("❌ Failed to start AI Service")
        return 1
    
    # Step 5: Test AI Service
    if not test_ai_service():
        logger.warning("⚠️ AI Service test failed, but service may still be starting")
    
    logger.info("🎉 Core services deployment completed!")
    return 0

if __name__ == "__main__":
    exit(main())




