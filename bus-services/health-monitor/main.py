"""
Alicia Bus Architecture - Health Monitor Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service monitors the health and performance of all bus services,
collects metrics, and provides alerting capabilities.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..service_wrapper import BusServiceWrapper, BusServiceAPI


@dataclass
class ServiceHealth:
    """Service health status data structure."""
    service_name: str
    status: str  # 'healthy', 'unhealthy', 'unknown'
    last_seen: float
    uptime: float
    messages_processed: int
    errors: int
    cpu_percent: float
    memory_mb: float
    response_time_ms: float
    timestamp: float


@dataclass
class HealthAlert:
    """Health alert data structure."""
    alert_id: str
    service_name: str
    alert_type: str  # 'service_down', 'high_cpu', 'high_memory', 'high_errors'
    severity: str  # 'critical', 'warning', 'info'
    message: str
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None


class HealthMonitorService(BusServiceWrapper):
    """
    Health Monitor Service for the Alicia Bus Architecture.

    Monitors all services, collects performance metrics, and provides
    alerting capabilities for service failures and performance issues.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": "alicia_bus_core",
            "port": 1883,
            "username": "health_monitor",
            "password": "alicia_health_2024"
        }

        super().__init__("health_monitor", mqtt_config)

        # Service tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.service_dependencies: Dict[str, List[str]] = {}

        # Metrics storage
        self.db_path = "/app/data/health_monitor.db"
        self._init_database()

        # Monitoring configuration
        self.health_check_interval = 30  # seconds
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_mb": 500.0,
            "error_rate": 0.1,  # 10% error rate
            "response_time_ms": 5000.0,
            "max_offline_time": 300.0  # 5 minutes
        }

        # FastAPI setup
        self.app = FastAPI(title="Alicia Health Monitor", version="1.0.0")
        self._setup_api_endpoints()

        # Background monitoring
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "health_monitoring",
            "performance_metrics",
            "alert_system",
            "service_discovery",
            "dependency_tracking"
        ]

        self.version = "1.0.0"

    def _init_database(self):
        """Initialize SQLite database for metrics storage."""
        try:
            self.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS service_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    cpu_percent REAL,
                    memory_mb REAL,
                    messages_processed INTEGER,
                    errors INTEGER,
                    response_time_ms REAL,
                    status TEXT
                )
            """)

            self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    service_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at REAL
                )
            """)

            self.db_conn.commit()
            self.logger.info("Health monitor database initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the health monitor."""

        @self.app.get("/health")
        async def get_health():
            """Get health monitor service health."""
            return self.get_health_status()

        @self.app.get("/services")
        async def get_services():
            """Get all monitored services status."""
            return {
                "services": [asdict(health) for health in self.service_health.values()],
                "total_services": len(self.service_health),
                "healthy_services": len([h for h in self.service_health.values() if h.status == "healthy"]),
                "timestamp": time.time()
            }

        @self.app.get("/services/{service_name}")
        async def get_service(service_name: str):
            """Get specific service health details."""
            if service_name not in self.service_health:
                raise HTTPException(status_code=404, detail="Service not found")

            health = self.service_health[service_name]
            return asdict(health)

        @self.app.get("/metrics")
        async def get_metrics(hours: int = 24):
            """Get performance metrics for all services."""
            try:
                cutoff_time = time.time() - (hours * 3600)
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT service_name, timestamp, cpu_percent, memory_mb,
                           messages_processed, errors, response_time_ms, status
                    FROM service_metrics
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """, (cutoff_time,))

                metrics = []
                for row in cursor.fetchall():
                    metrics.append({
                        "service_name": row[0],
                        "timestamp": row[1],
                        "cpu_percent": row[2],
                        "memory_mb": row[3],
                        "messages_processed": row[4],
                        "errors": row[5],
                        "response_time_ms": row[6],
                        "status": row[7]
                    })

                return {"metrics": metrics, "hours": hours}
            except Exception as e:
                self.logger.error(f"Failed to retrieve metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/alerts")
        async def get_alerts(active_only: bool = True):
            """Get health alerts."""
            try:
                alerts = []
                for alert in self.active_alerts.values():
                    if not active_only or not alert.resolved:
                        alerts.append(asdict(alert))

                return {"alerts": alerts, "total": len(alerts)}
            except Exception as e:
                self.logger.error(f"Failed to retrieve alerts: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/restart/{service_name}")
        async def restart_service(service_name: str):
            """Attempt to restart a failed service."""
            if service_name not in self.service_health:
                raise HTTPException(status_code=404, detail="Service not found")

            try:
                # Publish restart command to the service
                restart_message = {
                    "command": "restart",
                    "reason": "health_monitor_triggered",
                    "timestamp": time.time()
                }

                self.publish_message(
                    f"alicia/{service_name}/command",
                    restart_message
                )

                return {"status": "restart_command_sent", "service": service_name}
            except Exception as e:
                self.logger.error(f"Failed to send restart command: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/dependencies")
        async def get_dependencies():
            """Get service dependency map."""
            return {"dependencies": self.service_dependencies}

    def subscribe_to_topics(self):
        """Subscribe to health monitoring topics."""
        self.mqtt_client.subscribe("alicia/system/health/+")
        self.mqtt_client.subscribe("alicia/system/discovery/+")
        self.logger.info("Subscribed to health monitoring topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/system/health/"):
                self._process_health_message(topic, message)
            elif topic.startswith("alicia/system/discovery/"):
                self._process_discovery_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_health_message(self, topic: str, message: Dict[str, Any]):
        """Process health status messages from services."""
        try:
            service_name = message.get("service_name", "unknown")

            # Update service health
            health = ServiceHealth(
                service_name=service_name,
                status=message.get("status", "unknown"),
                last_seen=time.time(),
                uptime=message.get("uptime", 0),
                messages_processed=message.get("messages_processed", 0),
                errors=message.get("errors", 0),
                cpu_percent=message.get("cpu_percent", 0),
                memory_mb=message.get("memory_mb", 0),
                response_time_ms=message.get("response_time_ms", 0),
                timestamp=time.time()
            )

            self.service_health[service_name] = health

            # Store metrics in database
            self._store_metrics(health)

            # Check for alerts
            self._check_alerts(health)

            self.logger.debug(f"Updated health for {service_name}: {health.status}")

        except Exception as e:
            self.logger.error(f"Error processing health message: {e}")

    def _process_discovery_message(self, topic: str, message: Dict[str, Any]):
        """Process service discovery messages."""
        try:
            if "register" in topic:
                service_name = message.get("service_name", message.get("device_id", "unknown"))
                capabilities = message.get("capabilities", [])
                dependencies = message.get("dependencies", [])

                self.service_dependencies[service_name] = dependencies

                # Initialize health tracking for new service
                if service_name not in self.service_health:
                    self.service_health[service_name] = ServiceHealth(
                        service_name=service_name,
                        status="unknown",
                        last_seen=0,
                        uptime=0,
                        messages_processed=0,
                        errors=0,
                        cpu_percent=0,
                        memory_mb=0,
                        response_time_ms=0,
                        timestamp=time.time()
                    )

                self.logger.info(f"Registered service: {service_name}")

            elif "unregister" in topic:
                service_name = message.get("service_name", "unknown")
                if service_name in self.service_health:
                    del self.service_health[service_name]
                if service_name in self.service_dependencies:
                    del self.service_dependencies[service_name]

                self.logger.info(f"Unregistered service: {service_name}")

        except Exception as e:
            self.logger.error(f"Error processing discovery message: {e}")

    def _store_metrics(self, health: ServiceHealth):
        """Store service metrics in database."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO service_metrics
                (service_name, timestamp, cpu_percent, memory_mb, messages_processed,
                 errors, response_time_ms, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                health.service_name,
                health.timestamp,
                health.cpu_percent,
                health.memory_mb,
                health.messages_processed,
                health.errors,
                health.response_time_ms,
                health.status
            ))
            self.db_conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")

    def _check_alerts(self, health: ServiceHealth):
        """Check for health alerts and create if necessary."""
        try:
            current_time = time.time()

            # Check service offline
            if health.status == "unhealthy" or (current_time - health.last_seen) > self.alert_thresholds["max_offline_time"]:
                self._create_alert(
                    health.service_name,
                    "service_down",
                    "critical",
                    f"Service {health.service_name} is offline or unhealthy"
                )

            # Check high CPU usage
            if health.cpu_percent > self.alert_thresholds["cpu_percent"]:
                self._create_alert(
                    health.service_name,
                    "high_cpu",
                    "warning",
                    f"Service {health.service_name} CPU usage: {health.cpu_percent:.1f}%"
                )

            # Check high memory usage
            if health.memory_mb > self.alert_thresholds["memory_mb"]:
                self._create_alert(
                    health.service_name,
                    "high_memory",
                    "warning",
                    f"Service {health.service_name} memory usage: {health.memory_mb:.1f} MB"
                )

            # Check high error rate
            if health.messages_processed > 0:
                error_rate = health.errors / health.messages_processed
                if error_rate > self.alert_thresholds["error_rate"]:
                    self._create_alert(
                        health.service_name,
                        "high_errors",
                        "warning",
                        f"Service {health.service_name} error rate: {error_rate:.1%}"
                    )

            # Check slow response time
            if health.response_time_ms > self.alert_thresholds["response_time_ms"]:
                self._create_alert(
                    health.service_name,
                    "slow_response",
                    "warning",
                    f"Service {health.service_name} response time: {health.response_time_ms:.1f} ms"
                )

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

    def _create_alert(self, service_name: str, alert_type: str, severity: str, message: str):
        """Create a new health alert."""
        try:
            alert_id = f"{service_name}_{alert_type}_{int(time.time())}"

            # Check if alert already exists
            if alert_id in self.active_alerts:
                return

            alert = HealthAlert(
                alert_id=alert_id,
                service_name=service_name,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=time.time()
            )

            self.active_alerts[alert_id] = alert

            # Store alert in database
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO alerts
                (alert_id, service_name, alert_type, severity, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.service_name,
                alert.alert_type,
                alert.severity,
                alert.message,
                alert.timestamp
            ))
            self.db_conn.commit()

            # Publish alert via MQTT
            self.publish_message(
                "alicia/system/health/monitor/alerts",
                asdict(alert)
            )

            self.logger.warning(f"Created alert: {alert.message}")

        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                # Publish overall health status
                self._publish_monitor_status()

                # Clean up old metrics (keep last 7 days)
                self._cleanup_old_data()

                # Check for resolved alerts
                self._check_resolved_alerts()

                time.sleep(self.health_check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _publish_monitor_status(self):
        """Publish overall health monitor status."""
        try:
            total_services = len(self.service_health)
            healthy_services = len([h for h in self.service_health.values() if h.status == "healthy"])
            unhealthy_services = total_services - healthy_services

            status_message = {
                "monitor_name": "health_monitor",
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": unhealthy_services,
                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
                "timestamp": time.time(),
                "uptime": time.time() - self.start_time
            }

            self.publish_message(
                "alicia/system/health/monitor/status",
                status_message
            )

        except Exception as e:
            self.logger.error(f"Failed to publish monitor status: {e}")

    def _cleanup_old_data(self):
        """Clean up old metrics and resolved alerts."""
        try:
            # Keep metrics for last 7 days
            cutoff_time = time.time() - (7 * 24 * 3600)
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM service_metrics WHERE timestamp < ?", (cutoff_time,))

            # Keep resolved alerts for last 30 days
            cutoff_time = time.time() - (30 * 24 * 3600)
            cursor.execute("DELETE FROM alerts WHERE resolved = 1 AND timestamp < ?", (cutoff_time,))

            self.db_conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")

    def _check_resolved_alerts(self):
        """Check for resolved alerts and mark them as such."""
        try:
            current_time = time.time()

            for alert in list(self.active_alerts.values()):
                if alert.resolved:
                    continue

                service_name = alert.service_name
                if service_name in self.service_health:
                    health = self.service_health[service_name]

                    # Check if alert conditions are resolved
                    resolved = False

                    if alert.alert_type == "service_down":
                        resolved = health.status == "healthy" and (current_time - health.last_seen) < 60
                    elif alert.alert_type == "high_cpu":
                        resolved = health.cpu_percent < (self.alert_thresholds["cpu_percent"] - 10)
                    elif alert.alert_type == "high_memory":
                        resolved = health.memory_mb < (self.alert_thresholds["memory_mb"] - 50)
                    elif alert.alert_type == "slow_response":
                        resolved = health.response_time_ms < (self.alert_thresholds["response_time_ms"] - 1000)

                    if resolved:
                        alert.resolved = True
                        alert.resolved_at = current_time

                        # Update database
                        cursor = self.db_conn.cursor()
                        cursor.execute("""
                            UPDATE alerts
                            SET resolved = 1, resolved_at = ?
                            WHERE alert_id = ?
                        """, (current_time, alert.alert_id))
                        self.db_conn.commit()

                        self.logger.info(f"Resolved alert: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Error checking resolved alerts: {e}")

    def start_monitoring(self):
        """Start the background monitoring thread."""
        self.monitoring_thread.start()
        self.logger.info("Health monitoring started")

    def shutdown(self):
        """Gracefully shutdown the health monitor."""
        self.logger.info("Shutting down health monitor...")

        # Close database connection
        if hasattr(self, 'db_conn'):
            self.db_conn.close()

        super().shutdown()


def main():
    """Main entry point for the Health Monitor service."""
    service = HealthMonitorService()
    service.start_monitoring()

    # Start FastAPI server
    api = BusServiceAPI(service)
    uvicorn.run(api.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
