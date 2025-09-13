"""
Start and Test Services Script
Starts services individually and tests their functionality
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import logging
import signal
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages starting and testing services"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.running_services = {}
        self.mqtt_broker_running = False
        
    def start_mqtt_broker(self):
        """Start MQTT broker"""
        logger.info("Starting MQTT broker...")
        try:
            result = subprocess.run(
                ["docker-compose", "up", "-d", "mqtt-broker"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("MQTT broker started successfully")
                self.mqtt_broker_running = True
                return True
            else:
                logger.error(f"Failed to start MQTT broker: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to start MQTT broker: {e}")
            return False
    
    def start_service(self, service_name: str, port: int):
        """Start a service"""
        logger.info(f"Starting {service_name}...")
        
        service_path = self.project_root / f"services/bus-services/{service_name}"
        if not service_path.exists():
            logger.error(f"Service path not found: {service_path}")
            return False
        
        try:
            # Start service in background
            process = subprocess.Popen(
                ["python", "main.py"],
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_services[service_name] = {
                'process': process,
                'port': port,
                'start_time': time.time()
            }
            
            # Wait for service to start
            time.sleep(5)
            
            # Check if service is healthy
            if self.check_service_health(service_name, port):
                logger.info(f"✅ {service_name} started successfully on port {port}")
                return True
            else:
                logger.warning(f"⚠️ {service_name} started but health check failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    def check_service_health(self, service_name: str, port: int) -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get('status') == 'healthy'
        except Exception as e:
            logger.debug(f"Health check failed for {service_name}: {e}")
        return False
    
    def test_service_api(self, service_name: str, port: int):
        """Test service API endpoints"""
        logger.info(f"Testing {service_name} API...")
        
        try:
            # Test health endpoint
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {service_name} health endpoint working")
                health_data = response.json()
                logger.info(f"   Status: {health_data.get('status', 'unknown')}")
                logger.info(f"   Uptime: {health_data.get('uptime', 'unknown')}")
            else:
                logger.warning(f"⚠️ {service_name} health endpoint returned {response.status_code}")
            
            # Test other endpoints based on service type
            if service_name == "ai-service":
                self.test_ai_service_endpoints(port)
            elif service_name == "stt-service":
                self.test_stt_service_endpoints(port)
            elif service_name == "tts-service":
                self.test_tts_service_endpoints(port)
            elif service_name == "voice-router":
                self.test_voice_router_endpoints(port)
                
        except Exception as e:
            logger.error(f"Failed to test {service_name} API: {e}")
    
    def test_ai_service_endpoints(self, port: int):
        """Test AI service specific endpoints"""
        try:
            # Test process endpoint
            response = requests.post(
                f"http://localhost:{port}/process",
                json={"text": "Hello, how are you?", "context": "test"},
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ AI service process endpoint working")
            else:
                logger.warning(f"⚠️ AI service process endpoint returned {response.status_code}")
        except Exception as e:
            logger.warning(f"AI service process test failed: {e}")
    
    def test_stt_service_endpoints(self, port: int):
        """Test STT service specific endpoints"""
        try:
            # Test status endpoint
            response = requests.get(f"http://localhost:{port}/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ STT service status endpoint working")
            else:
                logger.warning(f"⚠️ STT service status endpoint returned {response.status_code}")
        except Exception as e:
            logger.warning(f"STT service status test failed: {e}")
    
    def test_tts_service_endpoints(self, port: int):
        """Test TTS service specific endpoints"""
        try:
            # Test status endpoint
            response = requests.get(f"http://localhost:{port}/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ TTS service status endpoint working")
            else:
                logger.warning(f"⚠️ TTS service status endpoint returned {response.status_code}")
        except Exception as e:
            logger.warning(f"TTS service status test failed: {e}")
    
    def test_voice_router_endpoints(self, port: int):
        """Test Voice Router specific endpoints"""
        try:
            # Test status endpoint
            response = requests.get(f"http://localhost:{port}/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Voice Router status endpoint working")
            else:
                logger.warning(f"⚠️ Voice Router status endpoint returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Voice Router status test failed: {e}")
    
    def stop_service(self, service_name: str):
        """Stop a service"""
        if service_name in self.running_services:
            logger.info(f"Stopping {service_name}...")
            process = self.running_services[service_name]['process']
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.running_services[service_name]
            logger.info(f"✅ {service_name} stopped")
    
    def stop_all_services(self):
        """Stop all running services"""
        logger.info("Stopping all services...")
        for service_name in list(self.running_services.keys()):
            self.stop_service(service_name)
    
    def run_live_testing(self):
        """Run live service testing"""
        logger.info("🚀 Starting Live Service Testing")
        
        # Start MQTT broker
        if not self.start_mqtt_broker():
            logger.error("Failed to start MQTT broker")
            return False
        
        # Wait for MQTT broker to be ready
        time.sleep(3)
        
        # Define services to test
        services_to_test = [
            {"name": "ai-service", "port": 8005},
            {"name": "stt-service", "port": 8004},
            {"name": "tts-service", "port": 8006},
            {"name": "voice-router", "port": 8007}
        ]
        
        successful_services = []
        failed_services = []
        
        # Start and test each service
        for service in services_to_test:
            service_name = service["name"]
            port = service["port"]
            
            if self.start_service(service_name, port):
                successful_services.append(service_name)
                self.test_service_api(service_name, port)
            else:
                failed_services.append(service_name)
        
        # Generate report
        self.generate_test_report(successful_services, failed_services)
        
        return len(failed_services) == 0
    
    def generate_test_report(self, successful_services, failed_services):
        """Generate test report"""
        report = f"""
============================================================
LIVE SERVICE TESTING REPORT
============================================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
  Total Services: {len(successful_services) + len(failed_services)}
  Successful: {len(successful_services)}
  Failed: {len(failed_services)}
  Success Rate: {(len(successful_services) / (len(successful_services) + len(failed_services)) * 100):.1f}%

SUCCESSFUL SERVICES:
"""
        
        for service in successful_services:
            report += f"  ✅ {service}\n"
        
        if failed_services:
            report += "\nFAILED SERVICES:\n"
            for service in failed_services:
                report += f"  ❌ {service}\n"
        
        report += f"""
MQTT BROKER: {'✅ RUNNING' if self.mqtt_broker_running else '❌ NOT RUNNING'}

{'🎉 Live testing completed successfully!' if len(failed_services) == 0 else '⚠️ Live testing completed with issues.'}
============================================================
"""
        
        # Save report
        report_file = Path("tests/results/live_testing_report.txt")
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_all_services()

def main():
    """Main function"""
    service_manager = ServiceManager()
    
    try:
        success = service_manager.run_live_testing()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Testing interrupted by user")
        return 1
    finally:
        service_manager.cleanup()

if __name__ == "__main__":
    sys.exit(main())




