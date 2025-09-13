"""
Debug All Services Script
Starts all services and provides debugging tools for each one
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import logging
import docker
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceDebugger:
    """Debug all services systematically"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.docker_client = docker.from_env()
        self.services = {
            'mqtt-broker': {
                'image': 'eclipse-mosquitto:2.0.18',
                'container_name': 'alicia-mqtt-broker',
                'ports': {'1883/tcp': 1883, '8883/tcp': 8883},
                'health_check': 'mqtt_connection'
            },
            'ai-service': {
                'build_path': './services/bus-services/ai-service',
                'container_name': 'alicia-ai-service',
                'ports': {'8005/tcp': 8005},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            },
            'stt-service': {
                'build_path': './services/bus-services/stt-service',
                'container_name': 'alicia-stt-service',
                'ports': {'8004/tcp': 8004},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            },
            'tts-service': {
                'build_path': './services/bus-services/tts-service',
                'container_name': 'alicia-tts-service',
                'ports': {'8006/tcp': 8006},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            },
            'voice-router': {
                'build_path': './services/bus-services/voice-router',
                'container_name': 'alicia-voice-router',
                'ports': {'8007/tcp': 8007},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            },
            'device-manager': {
                'build_path': './services/bus-services/device-manager',
                'container_name': 'alicia-device-manager',
                'ports': {'8008/tcp': 8008},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            },
            'health-monitor': {
                'build_path': './services/bus-services/health-monitor',
                'container_name': 'alicia-health-monitor',
                'ports': {'8009/tcp': 8009},
                'health_endpoint': '/health',
                'health_check': 'http_endpoint'
            }
        }
        self.network_name = 'alicia_debug_network'
        
    def cleanup_containers(self):
        """Clean up all containers"""
        logger.info("🧹 Cleaning up containers...")
        try:
            # Stop and remove all containers
            for service_name in self.services:
                container_name = self.services[service_name]['container_name']
                try:
                    container = self.docker_client.containers.get(container_name)
                    if container.status == 'running':
                        container.stop()
                    container.remove()
                    logger.info(f"   Removed {container_name}")
                except docker.errors.NotFound:
                    pass
                except Exception as e:
                    logger.warning(f"   Warning removing {container_name}: {e}")
            
            # Remove network
            try:
                network = self.docker_client.networks.get(self.network_name)
                network.remove()
                logger.info(f"   Removed network {self.network_name}")
            except docker.errors.NotFound:
                pass
                
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    def create_network(self):
        """Create Docker network"""
        logger.info("🌐 Creating Docker network...")
        try:
            self.docker_client.networks.create(
                self.network_name,
                driver='bridge'
            )
            logger.info(f"✅ Network {self.network_name} created")
            return True
        except Exception as e:
            logger.error(f"❌ Network creation failed: {e}")
            return False
    
    def start_mqtt_broker(self):
        """Start MQTT broker"""
        logger.info("🚀 Starting MQTT Broker...")
        try:
            container = self.docker_client.containers.run(
                self.services['mqtt-broker']['image'],
                name=self.services['mqtt-broker']['container_name'],
                ports=self.services['mqtt-broker']['ports'],
                volumes={
                    str(self.project_root / 'config/mqtt/mosquitto-simple.conf'): {
                        'bind': '/mosquitto/config/mosquitto.conf',
                        'mode': 'ro'
                    }
                },
                network=self.network_name,
                detach=True,
                restart_policy={'Name': 'unless-stopped'}
            )
            logger.info(f"✅ MQTT Broker started: {container.id[:12]}")
            time.sleep(3)  # Wait for broker to be ready
            return True
        except Exception as e:
            logger.error(f"❌ MQTT Broker failed: {e}")
            return False
    
    def test_mqtt_connection(self):
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
    
    def build_service(self, service_name: str):
        """Build a service"""
        logger.info(f"🔨 Building {service_name}...")
        try:
            build_path = self.project_root / self.services[service_name]['build_path']
            image_name = f"alicia-{service_name}"
            
            # Build the image
            image, build_logs = self.docker_client.images.build(
                path=str(build_path),
                tag=image_name,
                rm=True
            )
            
            logger.info(f"✅ {service_name} built successfully: {image.id[:12]}")
            return True
        except Exception as e:
            logger.error(f"❌ {service_name} build failed: {e}")
            return False
    
    def start_service(self, service_name: str):
        """Start a service"""
        logger.info(f"🚀 Starting {service_name}...")
        try:
            service_config = self.services[service_name]
            image_name = f"alicia-{service_name}"
            
            # Environment variables
            env_vars = {
                'MQTT_BROKER': 'mqtt-broker',
                'MQTT_PORT': '1883'
            }
            
            # Add service-specific environment variables
            if service_name == 'ai-service':
                env_vars['GROK_API_KEY'] = 'mock_grok_key_for_testing'
                env_vars['OPENAI_API_KEY'] = 'mock_openai_key_for_testing'
            elif service_name == 'stt-service':
                env_vars['STT_ENGINE'] = 'whisper'
            elif service_name == 'tts-service':
                env_vars['TTS_ENGINE'] = 'piper'
            
            container = self.docker_client.containers.run(
                image_name,
                name=service_config['container_name'],
                ports=service_config['ports'],
                environment=env_vars,
                network=self.network_name,
                detach=True,
                restart_policy={'Name': 'unless-stopped'}
            )
            
            logger.info(f"✅ {service_name} started: {container.id[:12]}")
            time.sleep(5)  # Wait for service to be ready
            return True
        except Exception as e:
            logger.error(f"❌ {service_name} start failed: {e}")
            return False
    
    def test_service_health(self, service_name: str):
        """Test service health"""
        logger.info(f"🧪 Testing {service_name} health...")
        try:
            service_config = self.services[service_name]
            
            if service_config['health_check'] == 'mqtt_connection':
                return self.test_mqtt_connection()
            elif service_config['health_check'] == 'http_endpoint':
                port = list(service_config['ports'].keys())[0].split('/')[0]
                response = requests.get(
                    f"http://localhost:{port}{service_config['health_endpoint']}", 
                    timeout=10
                )
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"✅ {service_name} healthy: {health_data.get('status', 'unknown')}")
                    return True
                else:
                    logger.warning(f"⚠️ {service_name} health check returned {response.status_code}")
                    return False
        except Exception as e:
            logger.warning(f"⚠️ {service_name} health check failed: {e}")
            return False
    
    def get_service_logs(self, service_name: str, lines: int = 50):
        """Get service logs"""
        logger.info(f"📋 Getting {service_name} logs...")
        try:
            container_name = self.services[service_name]['container_name']
            container = self.docker_client.containers.get(container_name)
            logs = container.logs(tail=lines).decode('utf-8')
            
            logger.info(f"📋 {service_name} logs (last {lines} lines):")
            logger.info("=" * 50)
            for line in logs.split('\n'):
                if line.strip():
                    logger.info(f"   {line}")
            logger.info("=" * 50)
            return logs
        except Exception as e:
            logger.error(f"❌ Failed to get {service_name} logs: {e}")
            return None
    
    def debug_service(self, service_name: str):
        """Debug a specific service"""
        logger.info(f"🔍 Debugging {service_name}...")
        
        # Build service
        if not self.build_service(service_name):
            return False
        
        # Start service
        if not self.start_service(service_name):
            return False
        
        # Test health
        health_ok = self.test_service_health(service_name)
        
        # Get logs
        self.get_service_logs(service_name)
        
        return health_ok
    
    def run_debug_session(self):
        """Run complete debug session"""
        logger.info("🚀 Starting Alicia Services Debug Session")
        
        # Step 1: Cleanup
        self.cleanup_containers()
        
        # Step 2: Create network
        if not self.create_network():
            return False
        
        # Step 3: Start MQTT Broker
        if not self.start_mqtt_broker():
            logger.error("❌ Failed to start MQTT Broker")
            return False
        
        # Step 4: Test MQTT
        if not self.test_mqtt_connection():
            logger.error("❌ MQTT connection test failed")
            return False
        
        # Step 5: Debug each service
        results = {}
        for service_name in ['ai-service', 'stt-service', 'tts-service', 'voice-router', 'device-manager', 'health-monitor']:
            logger.info(f"\n{'='*60}")
            logger.info(f"DEBUGGING {service_name.upper()}")
            logger.info(f"{'='*60}")
            
            results[service_name] = self.debug_service(service_name)
            
            if not results[service_name]:
                logger.warning(f"⚠️ {service_name} has issues - check logs above")
            else:
                logger.info(f"✅ {service_name} is working correctly")
        
        # Step 6: Generate summary
        self.generate_debug_summary(results)
        
        return True
    
    def generate_debug_summary(self, results: Dict[str, bool]):
        """Generate debug summary"""
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        summary = f"""
============================================================
ALICIA SERVICES DEBUG SUMMARY
============================================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

SERVICE STATUS:
  Total Services: {total}
  Working: {passed}
  Issues: {total - passed}
  Success Rate: {success_rate:.1f}%

DETAILED RESULTS:
"""
        
        for service_name, working in results.items():
            status = "✅ WORKING" if working else "❌ ISSUES"
            summary += f"  {service_name}: {status}\n"
        
        summary += f"""
NEXT STEPS:
  1. Check logs for services with issues
  2. Fix configuration problems
  3. Restart failed services
  4. Run integration tests

{'🎉 All services are working!' if success_rate == 100 else '⚠️ Some services need attention.'}
============================================================
"""
        
        print(summary)
        
        # Save summary
        summary_file = Path("tests/results/debug_summary.txt")
        summary_file.parent.mkdir(exist_ok=True)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

def main():
    """Main function"""
    debugger = ServiceDebugger()
    
    try:
        success = debugger.run_debug_session()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Debug session interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Debug session failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())




