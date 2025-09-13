#!/usr/bin/env python3
"""
Restart All Alicia Services
Quickly restarts all services in the correct order after system shutdown
"""

import subprocess
import time
import sys
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_container_running(container_name):
    """Check if a container is running"""
    result = subprocess.run(f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'", 
                          shell=True, capture_output=True, text=True)
    return container_name in result.stdout

def wait_for_health(container_name, port, max_wait=60):
    """Wait for container to be healthy"""
    print(f"⏳ Waiting for {container_name} to be healthy...")
    for i in range(max_wait):
        if check_container_running(container_name):
            # Check health endpoint
            result = subprocess.run(f"curl -s http://localhost:{port}/health", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0 and "healthy" in result.stdout:
                print(f"✅ {container_name} is healthy!")
                return True
        time.sleep(1)
    print(f"⚠️ {container_name} health check timeout")
    return False

def main():
    """Main restart sequence"""
    print("🚀 Restarting All Alicia Services...")
    print("=" * 50)
    
    # Service configuration
    services = [
        {
            "name": "MQTT Broker",
            "container": "alicia_bus_core",
            "image": "eclipse-mosquitto:2.0.18",
            "ports": "1883:1883 8883:8883 9001:9001",
            "volumes": f'"{Path.cwd()}/config/mqtt/mosquitto-simple.conf:/mosquitto/config/mosquitto.conf"',
            "health_port": None,
            "wait_time": 5
        },
        {
            "name": "STT Service",
            "container": "alicia_stt_service", 
            "image": "alicia-stt-service",
            "ports": "8004:8004",
            "volumes": None,
            "health_port": 8004,
            "wait_time": 10
        },
        {
            "name": "AI Service",
            "container": "alicia_ai_service",
            "image": "alicia-ai-service", 
            "ports": "8005:8005",
            "volumes": None,
            "health_port": 8005,
            "wait_time": 10
        },
        {
            "name": "TTS Service",
            "container": "alicia_tts_service",
            "image": "alicia-tts-service",
            "ports": "8006:8006", 
            "volumes": None,
            "health_port": 8006,
            "wait_time": 10
        },
        {
            "name": "Voice Router",
            "container": "alicia_voice_router",
            "image": "alicia-voice-router",
            "ports": "8007:8007",
            "volumes": None,
            "health_port": 8007,
            "wait_time": 10
        },
        {
            "name": "Device Manager", 
            "container": "alicia_device_manager",
            "image": "alicia-device-manager",
            "ports": "8008:8008",
            "volumes": None,
            "health_port": 8008,
            "wait_time": 10
        },
        {
            "name": "Security Gateway",
            "container": "alicia_security_gateway",
            "image": "alicia-security-gateway",
            "ports": "8009:8009",
            "volumes": None,
            "health_port": 8009,
            "wait_time": 10
        },
        {
            "name": "Device Registry",
            "container": "alicia_device_registry", 
            "image": "alicia-device-registry",
            "ports": "8010:8010",
            "volumes": f'"{Path.cwd()}/data:/app/data"',
            "health_port": 8010,
            "wait_time": 10
        }
    ]
    
    # Create network if it doesn't exist
    print("🌐 Creating Docker network...")
    run_command("docker network create alicia_network", "Creating alicia_network")
    
    # Start services in order
    for service in services:
        print(f"\n📦 Starting {service['name']}...")
        
        # Stop and remove existing container
        run_command(f"docker stop {service['container']} 2>nul", f"Stopping {service['container']}")
        run_command(f"docker rm {service['container']} 2>nul", f"Removing {service['container']}")
        
        # Build command
        if service['name'] == "MQTT Broker":
            cmd = f'docker run -d --name {service["container"]} --network alicia_network -p {service["ports"]} -v {service["volumes"]} {service["image"]}'
        else:
            env_vars = "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
            volumes = f'-v {service["volumes"]}' if service['volumes'] else ''
            cmd = f'docker run -d --name {service["container"]} --network alicia_network -p {service["ports"]} {volumes} {env_vars} {service["image"]}'
        
        # Start container
        if run_command(cmd, f"Starting {service['name']}"):
            print(f"⏳ Waiting {service['wait_time']}s for {service['name']} to initialize...")
            time.sleep(service['wait_time'])
            
            # Health check
            if service['health_port']:
                wait_for_health(service['container'], service['health_port'])
        else:
            print(f"❌ Failed to start {service['name']}")
            return False
    
    # Final status check
    print("\n" + "=" * 50)
    print("📊 Final Service Status:")
    run_command("docker ps --filter name=alicia", "Checking running containers")
    
    print("\n🎉 All services restarted successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


