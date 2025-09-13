"""
Start All Services Script
Builds and starts all Alicia services using Docker Compose
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

class ServiceManager:
    """Manages building and starting all services"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services = {
            'mqtt-broker': {'port': 1883, 'health_endpoint': None},
            'ai-service': {'port': 8005, 'health_endpoint': '/health'},
            'stt-service': {'port': 8004, 'health_endpoint': '/health'},
            'tts-service': {'port': 8006, 'health_endpoint': '/health'},
            'voice-router': {'port': 8007, 'health_endpoint': '/health'},
            'device-manager': {'port': 8008, 'health_endpoint': '/health'},
            'health-monitor': {'port': 8009, 'health_endpoint': '/health'}
        }
        
    def cleanup_old_containers(self):
        """Clean up old containers"""
        logger.info("🧹 Cleaning up old containers...")
        try:
            # Stop and remove old containers
            subprocess.run(["docker-compose", "down", "--remove-orphans"], 
                          cwd=self.project_root, check=True)
            logger.info("✅ Old containers cleaned up")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")
    
    def build_services(self):
        """Build all services"""
        logger.info("🔨 Building all services...")
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.services.yml", "build"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✅ All services built successfully")
                return True
            else:
                logger.error(f"❌ Build failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Build error: {e}")
            return False
    
    def start_services(self):
        """Start all services"""
        logger.info("🚀 Starting all services...")
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.services.yml", "up", "-d"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✅ All services started")
                return True
            else:
                logger.error(f"❌ Start failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    def check_service_health(self, service_name: str, port: int, health_endpoint: str = None):
        """Check if a service is healthy"""
        if health_endpoint is None:
            # For MQTT broker, test connection
            try:
                from paho.mqtt import client as mqtt_client
                client = mqtt_client.Client()
                client.connect("localhost", port, 60)
                client.loop_start()
                time.sleep(1)
                client.loop_stop()
                client.disconnect()
                return True
            except Exception:
                return False
        else:
            # For HTTP services, test health endpoint
            try:
                response = requests.get(f"http://localhost:{port}{health_endpoint}", timeout=5)
                return response.status_code == 200
            except Exception:
                return False
    
    def wait_for_services(self, timeout: int = 60):
        """Wait for all services to be healthy"""
        logger.info("⏳ Waiting for services to be healthy...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_healthy = True
            for service_name, config in self.services.items():
                healthy = self.check_service_health(
                    service_name, 
                    config['port'], 
                    config['health_endpoint']
                )
                if not healthy:
                    all_healthy = False
                    logger.info(f"   Waiting for {service_name}...")
            
            if all_healthy:
                logger.info("✅ All services are healthy!")
                return True
            
            time.sleep(5)
        
        logger.warning("⚠️ Some services may not be fully ready")
        return False
    
    def test_services(self):
        """Test all services"""
        logger.info("🧪 Testing all services...")
        
        results = {}
        for service_name, config in self.services.items():
            healthy = self.check_service_health(
                service_name, 
                config['port'], 
                config['health_endpoint']
            )
            results[service_name] = healthy
            status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
            logger.info(f"   {service_name}: {status}")
        
        return results
    
    def generate_report(self, build_success: bool, start_success: bool, test_results: dict):
        """Generate comprehensive report"""
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        report = f"""
============================================================
ALICIA SERVICES DEPLOYMENT REPORT
============================================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

BUILD STATUS:
  Build Success: {'✅ SUCCESS' if build_success else '❌ FAILED'}
  Start Success: {'✅ SUCCESS' if start_success else '❌ FAILED'}

SERVICE HEALTH:
  Total Services: {total_tests}
  Healthy: {passed_tests}
  Unhealthy: {total_tests - passed_tests}
  Success Rate: {success_rate:.1f}%

DETAILED RESULTS:
"""
        
        for service_name, healthy in test_results.items():
            status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
            report += f"  {service_name}: {status}\n"
        
        overall_success = build_success and start_success and success_rate >= 80
        report += f"""
OVERALL STATUS: {'🎉 SUCCESS' if overall_success else '⚠️ PARTIAL SUCCESS'}

{'🎉 All services deployed and running successfully!' if overall_success else '⚠️ Some services may need attention.'}
============================================================
"""
        
        # Save report
        report_file = Path("tests/results/services_deployment_report.txt")
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        return overall_success
    
    def run_deployment(self):
        """Run complete deployment"""
        logger.info("🚀 Starting Alicia Services Deployment")
        
        # Step 1: Cleanup
        self.cleanup_old_containers()
        
        # Step 2: Build
        build_success = self.build_services()
        if not build_success:
            logger.error("❌ Build failed, stopping deployment")
            return False
        
        # Step 3: Start
        start_success = self.start_services()
        if not start_success:
            logger.error("❌ Start failed, stopping deployment")
            return False
        
        # Step 4: Wait for services
        self.wait_for_services()
        
        # Step 5: Test
        test_results = self.test_services()
        
        # Step 6: Generate report
        overall_success = self.generate_report(build_success, start_success, test_results)
        
        return overall_success

def main():
    """Main function"""
    service_manager = ServiceManager()
    
    try:
        success = service_manager.run_deployment()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())




