#!/usr/bin/env python3
"""
Fix Docker Networking for Sonos Integration
Resolves IP mismatch and port forwarding issues
"""

import subprocess
import json
import time

def check_current_docker_setup():
    """Check current Docker networking configuration"""
    print("🐳 CURRENT DOCKER SETUP ANALYSIS")
    print("=" * 35)

    # Check Docker version and status
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"✅ Docker: {result.stdout.strip()}")
    except:
        print("❌ Docker not found or not accessible")
        return False

    # Check running containers
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        containers = result.stdout.strip().split('\n')
        print(f"📦 Running containers: {len(containers) - 1}")  # Subtract header

        alicia_containers = [c for c in containers if 'alicia' in c.lower()]
        if alicia_containers:
            print("✅ Alicia containers found:")
            for container in alicia_containers:
                print(f"   {container}")
        else:
            print("❌ No Alicia containers running")
    except:
        print("❌ Cannot check containers")

    # Check Docker networks
    try:
        result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True)
        networks = result.stdout.strip().split('\n')[1:]  # Skip header
        print(f"🌐 Docker networks: {len(networks)}")
        for network in networks:
            print(f"   {network}")
    except:
        print("❌ Cannot list networks")

    return True

def fix_docker_networking():
    """Fix Docker networking to use host networking"""
    print("\n🔧 FIXING DOCKER NETWORKING")
    print("-" * 30)

    # Stop any existing Alicia containers
    print("Stopping existing containers...")
    try:
        subprocess.run(['docker', 'stop', 'alicia-sonos'], capture_output=True)
        subprocess.run(['docker', 'rm', 'alicia-sonos'], capture_output=True)
        print("✅ Stopped and removed existing containers")
    except:
        print("ℹ️  No existing containers to stop")

    # Create proper docker-compose with host networking
    compose_content = """
version: '3.8'
services:
  sonos-bridge:
    build: ../
    container_name: alicia-sonos
    network_mode: host
    environment:
      - MQTT_BROKER=localhost
      - MQTT_PORT=1883
    volumes:
      - ../scripts:/app/scripts
    restart: unless-stopped
    command: python scripts/sonos-mqtt-bridge.py
"""

    with open('../docker-compose.fixed.yml', 'w') as f:
        f.write(compose_content)

    print("✅ Created docker-compose.fixed.yml with host networking")

    # Build and run with host networking
    print("Building and starting container...")
    try:
        # Build the image
        result = subprocess.run(['docker-compose', '-f', '../docker-compose.fixed.yml', 'build'],
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Image built successfully")
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False

        # Start the container
        result = subprocess.run(['docker-compose', '-f', '../docker-compose.fixed.yml', 'up', '-d'],
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Container started successfully")
        else:
            print(f"❌ Start failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Docker operation failed: {e}")
        return False

    # Wait for container to start
    time.sleep(3)

    # Verify container is running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'alicia-sonos' in result.stdout:
            print("✅ Alicia Sonos container is running")
            return True
        else:
            print("❌ Container not found in running processes")
            return False
    except:
        print("❌ Cannot verify container status")
        return False

def verify_network_connectivity():
    """Verify the container can access the network properly"""
    print("\n🔍 VERIFYING NETWORK CONNECTIVITY")
    print("-" * 35)

    # Check container IP
    try:
        result = subprocess.run(['docker', 'exec', 'alicia-sonos', 'hostname', '-I'],
                               capture_output=True, text=True)
        container_ip = result.stdout.strip()
        print(f"📡 Container IP: {container_ip}")

        # Check if container can reach speakers
        for speaker_ip in ['192.168.1.101', '192.168.1.102']:
            try:
                result = subprocess.run(['docker', 'exec', 'alicia-sonos',
                                       'ping', '-c', '1', '-W', '1', speaker_ip],
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Can reach speaker {speaker_ip}")
                else:
                    print(f"❌ Cannot reach speaker {speaker_ip}")
            except:
                print(f"❌ Error testing speaker {speaker_ip}")

    except:
        print("❌ Cannot check container networking")

def test_sonos_discovery():
    """Test if container can discover Sonos speakers"""
    print("\n🎵 TESTING SONOS DISCOVERY")
    print("-" * 28)

    # Run a quick discovery test in the container
    test_script = """
import sys
sys.path.append('/app')
from soco.discovery import discover
speakers = list(discover(timeout=5))
print(f"Found {len(speakers)} speakers")
for speaker in speakers:
    print(f"- {speaker.player_name} at {speaker.ip_address}")
"""

    try:
        with open('/tmp/sonos_test.py', 'w') as f:
            f.write(test_script)

        result = subprocess.run(['docker', 'exec', 'alicia-sonos',
                               'python', '/tmp/sonos_test.py'],
                               capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Sonos discovery test results:")
            print(result.stdout)
        else:
            print(f"❌ Discovery test failed: {result.stderr}")

    except Exception as e:
        print(f"❌ Cannot run discovery test: {e}")

def provide_final_instructions():
    """Provide final setup instructions"""
    print("\n📋 FINAL SETUP INSTRUCTIONS")
    print("-" * 30)

    print("1. 🔄 RESTART ROUTER AGAIN")
    print("   - The container IP change may require router restart")
    print("   - Go to router admin → System → Reboot")

    print("\n2. 🧪 TEST PORT FORWARDING")
    print("   cd mqtt-testing/scripts")
    print("   python quick-port-test.py")

    print("\n3. 🎵 TEST SONOS INTEGRATION")
    print("   python audio-test.py")

    print("\n4. 🔧 IF STILL ISSUES:")
    print("   - Check container logs: docker logs alicia-sonos")
    print("   - Verify container IP matches port forwarding rules")
    print("   - Test with: docker exec alicia-sonos python scripts/sonos-demo.py")

    print("\n5. 📊 MONITORING:")
    print("   - Container logs: docker logs -f alicia-sonos")
    print("   - Network: docker exec alicia-sonos ip addr show")

def main():
    print("🔧 DOCKER NETWORKING FIX FOR SONOS")
    print("=" * 40)

    # Check current setup
    if not check_current_docker_setup():
        print("❌ Docker setup issues detected")
        return

    # Fix networking
    if fix_docker_networking():
        print("✅ Docker networking fixed!")

        # Verify connectivity
        verify_network_connectivity()

        # Test Sonos discovery
        test_sonos_discovery()

        # Provide final instructions
        provide_final_instructions()

        print("\n🎉 DOCKER NETWORKING FIX COMPLETE!")
        print("   The container should now use the host's IP address")
        print("   Port forwarding should work correctly")

    else:
        print("❌ Docker networking fix failed")
        print("💡 Check Docker installation and permissions")

if __name__ == '__main__':
    main()
