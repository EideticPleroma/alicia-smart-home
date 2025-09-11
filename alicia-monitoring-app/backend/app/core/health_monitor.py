"""
Health monitoring service for Alicia components
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Health monitoring service for all Alicia components"""
    
    def __init__(self):
        self.services = settings.alicia_services
        self.health_status = {}
        self.metrics_history = []
        self.is_monitoring = False
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the health monitor"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        logger.info("Health monitor initialized")
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        self.is_monitoring = False
        logger.info("Health monitor cleaned up")
        
    async def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            
            # Build health check URL
            if service_name == "mqtt":
                # Special handling for MQTT
                health_status = await self.check_mqtt_health(service_config)
            else:
                # HTTP health check
                health_url = f"http://{service_config['host']}:{service_config['port']}{service_config.get('health_endpoint', '/health')}"
                
                async with self.session.get(health_url) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                    
                    if response.status == 200:
                        health_data = await response.json()
                        health_status = {
                            "status": "healthy",
                            "response_time_ms": response_time,
                            "last_check": datetime.now().isoformat(),
                            "details": health_data
                        }
                    else:
                        health_status = {
                            "status": "unhealthy",
                            "response_time_ms": response_time,
                            "last_check": datetime.now().isoformat(),
                            "error": f"HTTP {response.status}"
                        }
                        
        except asyncio.TimeoutError:
            health_status = {
                "status": "timeout",
                "response_time_ms": 10000,  # 10 second timeout
                "last_check": datetime.now().isoformat(),
                "error": "Connection timeout"
            }
        except Exception as e:
            health_status = {
                "status": "error",
                "response_time_ms": 0,
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
            
        return health_status
        
    async def check_mqtt_health(self, mqtt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Special health check for MQTT broker"""
        try:
            import paho.mqtt.client as mqtt
            import asyncio
            
            # Create MQTT client
            client = mqtt.Client()
            client.username_pw_set(mqtt_config["username"], mqtt_config["password"])
            
            # Set up connection tracking
            connected = False
            connection_error = None
            
            def on_connect(client, userdata, flags, rc):
                nonlocal connected, connection_error
                if rc == 0:
                    connected = True
                else:
                    connection_error = f"MQTT connection failed with code {rc}"
                    
            def on_disconnect(client, userdata, rc):
                nonlocal connected
                connected = False
                
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            
            # Attempt connection
            start_time = time.time()
            client.connect(mqtt_config["host"], mqtt_config["port"], 60)
            client.loop_start()
            
            # Wait for connection or timeout
            await asyncio.sleep(2)
            response_time = (time.time() - start_time) * 1000
            
            client.loop_stop()
            client.disconnect()
            
            if connected:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "last_check": datetime.now().isoformat(),
                    "details": {"mqtt_connected": True}
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "last_check": datetime.now().isoformat(),
                    "error": connection_error or "MQTT connection failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": 0,
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
            
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all services"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_status": "healthy",
            "summary": {
                "total_services": len(self.services),
                "healthy_services": 0,
                "unhealthy_services": 0,
                "error_services": 0
            }
        }
        
        # Check each service
        for service_name, service_config in self.services.items():
            service_health = await self.check_service_health(service_name, service_config)
            health_data["services"][service_name] = service_health
            
            # Update summary
            if service_health["status"] == "healthy":
                health_data["summary"]["healthy_services"] += 1
            elif service_health["status"] in ["unhealthy", "timeout"]:
                health_data["summary"]["unhealthy_services"] += 1
            else:
                health_data["summary"]["error_services"] += 1
                
        # Determine overall status
        if health_data["summary"]["unhealthy_services"] > 0 or health_data["summary"]["error_services"] > 0:
            health_data["overall_status"] = "degraded"
        if health_data["summary"]["healthy_services"] == 0:
            health_data["overall_status"] = "critical"
            
        # Store in history
        self.health_status = health_data
        self.metrics_history.append(health_data)
        
        # Keep only recent history (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics_history = [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]
        
        return health_data
        
    async def monitor_loop(self):
        """Background monitoring loop"""
        self.is_monitoring = True
        logger.info("Starting health monitoring loop")
        
        while self.is_monitoring:
            try:
                await self.get_health_status()
                await asyncio.sleep(settings.health_check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry
                
    async def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]
        
    async def get_service_metrics(self, service_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics for a specific service"""
        history = await self.get_metrics_history(hours)
        return [
            {
                "timestamp": metric["timestamp"],
                "status": metric["services"].get(service_name, {}).get("status", "unknown"),
                "response_time_ms": metric["services"].get(service_name, {}).get("response_time_ms", 0)
            }
            for metric in history
            if service_name in metric["services"]
        ]
