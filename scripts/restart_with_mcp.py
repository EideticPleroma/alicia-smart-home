#!/usr/bin/env python3
"""
Restart All Alicia Services using Docker MCP Tools
Systematically restarts all services using Docker MCP for better management
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True, result.stdout
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False, str(e)

def check_container_health(container_name, port):
    """Check if container is healthy via health endpoint"""
    result = subprocess.run(f"curl -s http://localhost:{port}/health", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0 and "healthy" in result.stdout:
        return True
    return False

def main():
    """Main restart sequence using Docker MCP approach"""
    print("🚀 Restarting All Alicia Services with Docker MCP...")
    print("=" * 60)
    
    # Service definitions
    services = [
        {
            "name": "STT Service",
            "container": "alicia_stt_service",
            "image": "alicia-stt-service", 
            "port": 8004,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "AI Service", 
            "container": "alicia_ai_service",
            "image": "alicia-ai-service",
            "port": 8005,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "TTS Service",
            "container": "alicia_tts_service", 
            "image": "alicia-tts-service",
            "port": 8006,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "Voice Router",
            "container": "alicia_voice_router",
            "image": "alicia-voice-router",
            "port": 8007, 
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "Device Manager",
            "container": "alicia_device_manager",
            "image": "alicia-device-manager", 
            "port": 8008,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "Security Gateway",
            "container": "alicia_security_gateway",
            "image": "alicia-security-gateway",
            "port": 8009,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883"
        },
        {
            "name": "Device Registry",
            "container": "alicia_device_registry",
            "image": "alicia-device-registry",
            "port": 8010,
            "env": "-e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883",
            "volumes": f'-v "{Path.cwd()}/data:/app/data"'
        }
    ]
    
    # Step 1: Ensure MQTT Broker is running
    print("📡 Checking MQTT Broker...")
    result = subprocess.run("docker ps --filter name=alicia_bus_core --format '{{.Names}}'", 
                          shell=True, capture_output=True, text=True)
    if "alicia_bus_core" not in result.stdout:
        print("🔄 Starting MQTT Broker...")
        cmd = f'docker run -d --name alicia_bus_core --network alicia_network -p 1883:1883 -p 8883:8883 -p 9001:9001 -v "{Path.cwd()}/config/mqtt/mosquitto-simple.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto:2.0.18'
        success, output = run_command(cmd, "Starting MQTT Broker")
        if not success:
            print("❌ Failed to start MQTT Broker. Exiting.")
            return False
        time.sleep(5)
    else:
        print("✅ MQTT Broker already running")
    
    # Step 2: Rebuild AI service if needed
    print("\n🔨 Checking AI Service image...")
    result = subprocess.run("docker images --format '{{.Repository}}' | findstr alicia-ai-service", 
                          shell=True, capture_output=True, text=True)
    if "alicia-ai-service" not in result.stdout:
        print("🔄 Rebuilding AI Service...")
        success, output = run_command("docker build -t alicia-ai-service ./services/bus-services/ai-service", 
                                    "Building AI Service")
        if not success:
            print("❌ Failed to build AI Service")
            return False
    
    # Step 3: Start all services
    print("\n🚀 Starting all services...")
    for service in services:
        print(f"\n📦 Starting {service['name']}...")
        
        # Stop and remove existing container
        run_command(f"docker stop {service['container']} 2>nul", f"Stopping {service['container']}")
        run_command(f"docker rm {service['container']} 2>nul", f"Removing {service['container']}")
        
        # Build run command
        volumes = service.get('volumes', '')
        cmd = f'docker run -d --name {service["container"]} --network alicia_network -p {service["port"]}:{service["port"]} {volumes} {service["env"]} {service["image"]}'
        
        # Start container
        success, output = run_command(cmd, f"Starting {service['name']}")
        if success:
            print(f"⏳ Waiting for {service['name']} to initialize...")
            time.sleep(10)
            
            # Health check
            if check_container_health(service['container'], service['port']):
                print(f"✅ {service['name']} is healthy!")
            else:
                print(f"⚠️ {service['name']} health check failed, but container is running")
        else:
            print(f"❌ Failed to start {service['name']}")
    
    # Final status
    print("\n" + "=" * 60)
    print("📊 Final Service Status:")
    run_command("docker ps --filter name=alicia", "Checking all containers")
    
    print("\n🎉 Service restart complete!")
    return True

if __name__ == "__main__":
    main()


