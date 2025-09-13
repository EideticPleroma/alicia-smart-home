"""
Alicia Bus Architecture - Metrics Collector Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service collects, aggregates, and analyzes metrics from all bus services,
providing comprehensive monitoring, alerting, and performance insights.
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import statistics

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import psutil
from dotenv import load_dotenv

from service_wrapper import BusServiceWrapper, BusServiceAPI

# Load environment variables
load_dotenv()


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class ServiceMetrics:
    """Metrics for a specific service."""
    service_name: str
    instance_id: str
    metrics: List[MetricData] = field(default_factory=list)
    last_updated: float = 0.0
    health_status: str = "unknown"


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric_name: str
    condition: str  # e.g., "value > 90"
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_period: int = 300  # seconds


@dataclass
class Alert:
    """Active alert instance."""
    alert_id: str
    rule_name: str
    service_name: str
    instance_id: str
    severity: AlertSeverity
    message: str
    value: Union[int, float]
    threshold: Union[int, float]
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None


@dataclass
class MetricsSummary:
    """Aggregated metrics summary."""
    total_services: int
    total_instances: int
    active_alerts: int
    total_metrics: int
    system_cpu_percent: float
    system_memory_percent: float
    system_disk_percent: float
    timestamp: float


class MetricsCollectorService(BusServiceWrapper):
    """
    Metrics Collector Service for the Alicia Bus Architecture.

    Collects, aggregates, and analyzes metrics from all bus services,
    providing monitoring, alerting, and performance insights.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": "metrics_collector",
            "password": "alicia_metrics_2024"
        }

        super().__init__("metrics_collector", mqtt_config)

        # Metrics storage
        self.service_metrics: Dict[str, Dict[str, ServiceMetrics]] = {}
        self.metrics_history: Dict[str, List[MetricData]] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}

        # Configuration
        self.collection_interval = 30  # seconds
        self.retention_period = 3600  # 1 hour
        self.max_history_per_metric = 1000
        self.system_metrics_interval = 60  # seconds

        # Alert thresholds
        self.default_alert_rules = self._create_default_alert_rules()

        # FastAPI setup
        self.app = FastAPI(title="Alicia Metrics Collector", version="1.0.0")
        self._setup_api_endpoints()

        # Background threads
        self.collection_thread = threading.Thread(target=self._metrics_collection_loop)
        self.collection_thread.daemon = True

        self.system_thread = threading.Thread(target=self._system_metrics_loop)
        self.system_thread.daemon = True

        self.alert_thread = threading.Thread(target=self._alert_monitoring_loop)
        self.alert_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "metrics_collection",
            "performance_monitoring",
            "alerting",
            "system_monitoring",
            "metrics_aggregation"
        ]

        self.version = "1.0.0"

    def _create_default_alert_rules(self) -> Dict[str, AlertRule]:
        """Create default alert rules."""
        return {
            "high_cpu": AlertRule(
                name="high_cpu",
                metric_name="cpu_percent",
                condition="value > 90",
                severity=AlertSeverity.WARNING,
                description="CPU usage is above 90%"
            ),
            "high_memory": AlertRule(
                name="high_memory",
                metric_name="memory_percent",
                condition="value > 85",
                severity=AlertSeverity.WARNING,
                description="Memory usage is above 85%"
            ),
            "service_down": AlertRule(
                name="service_down",
                metric_name="health_status",
                condition="value == 'unhealthy'",
                severity=AlertSeverity.ERROR,
                description="Service is reporting unhealthy status"
            ),
            "high_error_rate": AlertRule(
                name="high_error_rate",
                metric_name="error_rate",
                condition="value > 5",
                severity=AlertSeverity.ERROR,
                description="Error rate is above 5%"
            ),
            "response_time_high": AlertRule(
                name="response_time_high",
                metric_name="response_time_avg",
                condition="value > 5000",
                severity=AlertSeverity.WARNING,
                description="Average response time is above 5 seconds"
            )
        }

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the metrics collector."""

        @self.app.get("/health")
        async def get_health():
            """Get metrics collector service health."""
            return self.get_health_status()

        @self.app.get("/metrics")
        async def get_all_metrics():
            """Get all collected metrics."""
            all_metrics = []
            for service_instances in self.service_metrics.values():
                for service_metric in service_instances.values():
                    all_metrics.extend(service_metric.metrics)
            return {"metrics": [asdict(metric) for metric in all_metrics]}

        @self.app.get("/metrics/{service_name}")
        async def get_service_metrics(service_name: str):
            """Get metrics for a specific service."""
            if service_name not in self.service_metrics:
                raise HTTPException(status_code=404, detail="Service not found")

            service_data = {}
            for instance_id, metrics in self.service_metrics[service_name].items():
                service_data[instance_id] = {
                    "metrics": [asdict(metric) for metric in metrics.metrics],
                    "last_updated": metrics.last_updated,
                    "health_status": metrics.health_status
                }

            return {"service_name": service_name, "instances": service_data}

        @self.app.get("/metrics/{service_name}/{metric_name}")
        async def get_specific_metric(
            service_name: str,
            metric_name: str,
            instance_id: Optional[str] = None,
            limit: int = Query(100, description="Number of data points to return")
        ):
            """Get specific metric data."""
            if service_name not in self.service_metrics:
                raise HTTPException(status_code=404, detail="Service not found")

            metric_data = []

            if instance_id:
                if instance_id not in self.service_metrics[service_name]:
                    raise HTTPException(status_code=404, detail="Instance not found")

                instance_metrics = self.service_metrics[service_name][instance_id]
                metric_data = [
                    asdict(metric) for metric in instance_metrics.metrics
                    if metric.name == metric_name
                ]
            else:
                for instance_metrics in self.service_metrics[service_name].values():
                    metric_data.extend([
                        asdict(metric) for metric in instance_metrics.metrics
                        if metric.name == metric_name
                    ])

            # Sort by timestamp and limit results
            metric_data.sort(key=lambda x: x["timestamp"], reverse=True)
            return {
                "service_name": service_name,
                "metric_name": metric_name,
                "data": metric_data[:limit]
            }

        @self.app.get("/alerts")
        async def get_alerts(active_only: bool = True):
            """Get alerts."""
            alerts = []
            for alert in self.active_alerts.values():
                if not active_only or not alert.resolved:
                    alerts.append(asdict(alert))

            alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            return {"alerts": alerts}

        @self.app.get("/alerts/rules")
        async def get_alert_rules():
            """Get alert rules."""
            return {"rules": [asdict(rule) for rule in self.alert_rules.values()]}

        @self.app.post("/alerts/rules")
        async def create_alert_rule(rule: Dict[str, Any]):
            """Create a new alert rule."""
            try:
                alert_rule = AlertRule(**rule)
                self.alert_rules[alert_rule.name] = alert_rule
                return {"message": "Alert rule created", "rule": asdict(alert_rule)}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid rule: {str(e)}")

        @self.app.get("/summary")
        async def get_summary():
            """Get metrics summary."""
            total_services = len(self.service_metrics)
            total_instances = sum(len(instances) for instances in self.service_metrics.values())
            total_metrics = sum(
                len(instance.metrics)
                for instances in self.service_metrics.values()
                for instance in instances.values()
            )

            summary = MetricsSummary(
                total_services=total_services,
                total_instances=total_instances,
                active_alerts=len([a for a in self.active_alerts.values() if not a.resolved]),
                total_metrics=total_metrics,
                system_cpu_percent=psutil.cpu_percent(),
                system_memory_percent=psutil.virtual_memory().percent,
                system_disk_percent=psutil.disk_usage('/').percent,
                timestamp=time.time()
            )

            return asdict(summary)

        @self.app.get("/analytics/{service_name}")
        async def get_service_analytics(service_name: str, hours: int = 24):
            """Get analytics for a service."""
            if service_name not in self.service_metrics:
                raise HTTPException(status_code=404, detail="Service not found")

            analytics = self._calculate_service_analytics(service_name, hours)
            return {"service_name": service_name, "analytics": analytics}

    def subscribe_to_topics(self):
        """Subscribe to metrics and monitoring topics."""
        self.mqtt_client.subscribe("alicia/metrics/+")
        self.mqtt_client.subscribe("alicia/system/health/+")
        self.mqtt_client.subscribe("alicia/system/status/+")
        self.logger.info("Subscribed to metrics topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/metrics/"):
                self._process_metrics_message(topic, message)
            elif topic.startswith("alicia/system/health/"):
                self._process_health_message(topic, message)
            elif topic.startswith("alicia/system/status/"):
                self._process_status_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_metrics_message(self, topic: str, message: Dict[str, Any]):
        """Process metrics messages."""
        try:
            service_name = message.get("service_name", "unknown")
            instance_id = message.get("instance_id", f"{service_name}_unknown")
            metrics_data = message.get("metrics", [])

            # Ensure service and instance exist
            if service_name not in self.service_metrics:
                self.service_metrics[service_name] = {}

            if instance_id not in self.service_metrics[service_name]:
                self.service_metrics[service_name][instance_id] = ServiceMetrics(
                    service_name=service_name,
                    instance_id=instance_id
                )

            service_metric = self.service_metrics[service_name][instance_id]

            # Process each metric
            for metric_info in metrics_data:
                metric = MetricData(
                    name=metric_info["name"],
                    value=metric_info["value"],
                    timestamp=metric_info.get("timestamp", time.time()),
                    labels=metric_info.get("labels", {}),
                    metric_type=MetricType(metric_info.get("type", "gauge"))
                )

                # Add to current metrics
                service_metric.metrics.append(metric)
                service_metric.last_updated = time.time()

                # Keep only recent metrics
                if len(service_metric.metrics) > 100:
                    service_metric.metrics = service_metric.metrics[-100:]

                # Store in history
                metric_key = f"{service_name}:{instance_id}:{metric.name}"
                if metric_key not in self.metrics_history:
                    self.metrics_history[metric_key] = []

                self.metrics_history[metric_key].append(metric)

                # Keep history size manageable
                if len(self.metrics_history[metric_key]) > self.max_history_per_metric:
                    self.metrics_history[metric_key] = self.metrics_history[metric_key][-self.max_history_per_metric:]

            self.logger.debug(f"Processed {len(metrics_data)} metrics for {service_name}:{instance_id}")

        except Exception as e:
            self.logger.error(f"Error processing metrics message: {e}")

    def _process_health_message(self, topic: str, message: Dict[str, Any]):
        """Process health status messages."""
        try:
            service_name = message.get("service_name", "unknown")
            instance_id = message.get("instance_id", "unknown")
            health_status = message.get("status", "unknown")

            if service_name in self.service_metrics and instance_id in self.service_metrics[service_name]:
                self.service_metrics[service_name][instance_id].health_status = health_status

                # Create health metric
                health_metric = MetricData(
                    name="health_status",
                    value=1 if health_status == "healthy" else 0,
                    timestamp=time.time(),
                    labels={"status": health_status}
                )

                self.service_metrics[service_name][instance_id].metrics.append(health_metric)

        except Exception as e:
            self.logger.error(f"Error processing health message: {e}")

    def _process_status_message(self, topic: str, message: Dict[str, Any]):
        """Process status messages."""
        try:
            service_name = message.get("service_name", "unknown")
            instance_id = message.get("instance_id", "unknown")

            # Extract performance metrics from status
            if "cpu_percent" in message:
                self._add_metric(service_name, instance_id, "cpu_percent", message["cpu_percent"])

            if "memory_percent" in message:
                self._add_metric(service_name, instance_id, "memory_percent", message["memory_percent"])

            if "response_time" in message:
                self._add_metric(service_name, instance_id, "response_time", message["response_time"])

            if "requests_per_second" in message:
                self._add_metric(service_name, instance_id, "requests_per_second", message["requests_per_second"])

        except Exception as e:
            self.logger.error(f"Error processing status message: {e}")

    def _add_metric(self, service_name: str, instance_id: str, metric_name: str, value: Union[int, float]):
        """Add a metric to the collection."""
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = {}

        if instance_id not in self.service_metrics[service_name]:
            self.service_metrics[service_name][instance_id] = ServiceMetrics(
                service_name=service_name,
                instance_id=instance_id
            )

        metric = MetricData(
            name=metric_name,
            value=value,
            timestamp=time.time()
        )

        self.service_metrics[service_name][instance_id].metrics.append(metric)

    def _metrics_collection_loop(self):
        """Background metrics collection loop."""
        while True:
            try:
                # Clean up old metrics
                self._cleanup_old_metrics()

                # Publish collection summary
                self._publish_collection_summary()

                time.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(5)

    def _system_metrics_loop(self):
        """Background system metrics collection loop."""
        while True:
            try:
                # Collect system metrics
                system_metrics = {
                    "service_name": "system",
                    "instance_id": "host",
                    "metrics": [
                        {
                            "name": "cpu_percent",
                            "value": psutil.cpu_percent(),
                            "type": "gauge"
                        },
                        {
                            "name": "memory_percent",
                            "value": psutil.virtual_memory().percent,
                            "type": "gauge"
                        },
                        {
                            "name": "disk_percent",
                            "value": psutil.disk_usage('/').percent,
                            "type": "gauge"
                        },
                        {
                            "name": "network_connections",
                            "value": len(psutil.net_connections()),
                            "type": "gauge"
                        }
                    ]
                }

                # Publish system metrics
                self.publish_message("alicia/metrics/system", system_metrics)

                time.sleep(self.system_metrics_interval)

            except Exception as e:
                self.logger.error(f"Error in system metrics loop: {e}")
                time.sleep(5)

    def _alert_monitoring_loop(self):
        """Background alert monitoring loop."""
        while True:
            try:
                # Check alert rules
                self._check_alert_rules()

                # Clean up resolved alerts
                self._cleanup_resolved_alerts()

                time.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"Error in alert monitoring loop: {e}")
                time.sleep(5)

    def _check_alert_rules(self):
        """Check all alert rules against current metrics."""
        try:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue

                # Find metrics matching this rule
                for service_name, instances in self.service_metrics.items():
                    for instance_id, service_metric in instances.items():
                        for metric in service_metric.metrics:
                            if metric.name == rule.metric_name:
                                self._evaluate_alert_rule(rule, service_name, instance_id, metric)

        except Exception as e:
            self.logger.error(f"Error checking alert rules: {e}")

    def _evaluate_alert_rule(self, rule: AlertRule, service_name: str, instance_id: str, metric: MetricData):
        """Evaluate an alert rule against a metric."""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            condition = rule.condition.replace("value", str(metric.value))

            # Evaluate the condition
            if eval(condition):  # Note: In production, use a safe expression evaluator
                alert_key = f"{rule.name}:{service_name}:{instance_id}"

                # Check if alert already exists
                if alert_key not in self.active_alerts:
                    alert = Alert(
                        alert_id=alert_key,
                        rule_name=rule.name,
                        service_name=service_name,
                        instance_id=instance_id,
                        severity=rule.severity,
                        message=rule.description,
                        value=metric.value,
                        threshold=float(rule.condition.split()[-1]),  # Simple extraction
                        timestamp=time.time()
                    )

                    self.active_alerts[alert_key] = alert

                    # Publish alert
                    self.publish_message("alicia/alerts/new", asdict(alert))

                    self.logger.warning(f"Alert triggered: {alert_key}")

        except Exception as e:
            self.logger.error(f"Error evaluating alert rule {rule.name}: {e}")

    def _cleanup_old_metrics(self):
        """Clean up old metrics from history."""
        try:
            cutoff_time = time.time() - self.retention_period

            for metric_key in list(self.metrics_history.keys()):
                self.metrics_history[metric_key] = [
                    metric for metric in self.metrics_history[metric_key]
                    if metric.timestamp > cutoff_time
                ]

                if not self.metrics_history[metric_key]:
                    del self.metrics_history[metric_key]

        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")

    def _cleanup_resolved_alerts(self):
        """Clean up old resolved alerts."""
        try:
            cutoff_time = time.time() - 3600  # Keep resolved alerts for 1 hour

            for alert_key in list(self.active_alerts.keys()):
                alert = self.active_alerts[alert_key]
                if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                    del self.active_alerts[alert_key]

        except Exception as e:
            self.logger.error(f"Error cleaning up resolved alerts: {e}")

    def _publish_collection_summary(self):
        """Publish metrics collection summary."""
        try:
            summary = {
                "total_services": len(self.service_metrics),
                "total_instances": sum(len(instances) for instances in self.service_metrics.values()),
                "total_metrics": sum(
                    len(instance.metrics)
                    for instances in self.service_metrics.values()
                    for instance in instances.values()
                ),
                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
                "timestamp": time.time()
            }

            self.publish_message("alicia/metrics/summary", summary)

        except Exception as e:
            self.logger.error(f"Error publishing collection summary: {e}")

    def _calculate_service_analytics(self, service_name: str, hours: int) -> Dict[str, Any]:
        """Calculate analytics for a service."""
        try:
            if service_name not in self.service_metrics:
                return {}

            analytics = {}
            cutoff_time = time.time() - (hours * 3600)

            # Collect all metrics for the time period
            all_metrics = []
            for instance in self.service_metrics[service_name].values():
                all_metrics.extend([
                    metric for metric in instance.metrics
                    if metric.timestamp > cutoff_time
                ])

            if not all_metrics:
                return {"message": "No metrics available for the specified time period"}

            # Group metrics by name
            metrics_by_name = {}
            for metric in all_metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric.value)

            # Calculate statistics for each metric
            for metric_name, values in metrics_by_name.items():
                if len(values) > 1:
                    analytics[metric_name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": statistics.mean(values),
                        "median": statistics.median(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }
                else:
                    analytics[metric_name] = {
                        "count": len(values),
                        "value": values[0]
                    }

            return analytics

        except Exception as e:
            self.logger.error(f"Error calculating service analytics: {e}")
            return {"error": str(e)}

    def start_collection(self):
        """Start background collection threads."""
        self.collection_thread.start()
        self.system_thread.start()
        self.alert_thread.start()
        self.logger.info("Metrics collection started")

    def shutdown(self):
        """Gracefully shutdown the metrics collector."""
        self.logger.info("Shutting down metrics collector...")

        super().shutdown()


async def main():
    """Main entry point for the Metrics Collector service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    service = MetricsCollectorService()
    service.start_collection()

    # Start FastAPI server
    try:
        api = BusServiceAPI(service)
        config = uvicorn.Config(api.app, host="0.0.0.0", port=8024)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
