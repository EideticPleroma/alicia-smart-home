"""
Alicia Bus Architecture - Load Balancer Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service distributes requests across multiple service instances,
providing load balancing, health-based routing, and performance monitoring.
"""

import asyncio
import json
import logging
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..service_wrapper import BusServiceWrapper, BusServiceAPI


class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"


@dataclass
class ServiceInstance:
    """Service instance information."""
    instance_id: str
    service_name: str
    host: str
    port: int
    health_status: str  # 'healthy', 'unhealthy', 'unknown'
    active_connections: int
    weight: int
    last_health_check: float
    response_time: float
    total_requests: int
    failed_requests: int


@dataclass
class LoadBalancerStats:
    """Load balancer statistics."""
    total_requests: int
    active_connections: int
    healthy_instances: int
    unhealthy_instances: int
    average_response_time: float
    algorithm: str
    timestamp: float


class LoadBalancerService(BusServiceWrapper):
    """
    Load Balancer Service for the Alicia Bus Architecture.

    Distributes requests across multiple service instances using various
    load balancing algorithms and provides health monitoring.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": "alicia_bus_core",
            "port": 1883,
            "username": "load_balancer",
            "password": "alicia_load_2024"
        }

        super().__init__("load_balancer", mqtt_config)

        # Service instance tracking
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        self.current_round_robin: Dict[str, int] = {}
        self.load_stats: Dict[str, LoadBalancerStats] = {}

        # Configuration
        self.health_check_interval = 30  # seconds
        self.max_connections_per_instance = 100
        self.default_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.service_algorithms: Dict[str, LoadBalancingAlgorithm] = {}

        # Circuit breaker settings
        self.failure_threshold = 5
        self.recovery_timeout = 60
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

        # FastAPI setup
        self.app = FastAPI(title="Alicia Load Balancer", version="1.0.0")
        self._setup_api_endpoints()

        # Background monitoring
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "load_balancing",
            "service_discovery",
            "health_monitoring",
            "circuit_breaker",
            "performance_monitoring"
        ]

        self.version = "1.0.0"

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the load balancer."""

        @self.app.get("/health")
        async def get_health():
            """Get load balancer service health."""
            return self.get_health_status()

        @self.app.get("/services")
        async def get_services():
            """Get all registered services and their instances."""
            services = {}
            for service_name, instances in self.service_instances.items():
                services[service_name] = {
                    "instances": [asdict(instance) for instance in instances],
                    "algorithm": self.service_algorithms.get(service_name, self.default_algorithm).value,
                    "stats": asdict(self.load_stats.get(service_name, LoadBalancerStats(
                        total_requests=0,
                        active_connections=0,
                        healthy_instances=len([i for i in instances if i.health_status == "healthy"]),
                        unhealthy_instances=len([i for i in instances if i.health_status == "unhealthy"]),
                        average_response_time=0.0,
                        algorithm=self.service_algorithms.get(service_name, self.default_algorithm).value,
                        timestamp=time.time()
                    )))
                }
            return {"services": services}

        @self.app.get("/services/{service_name}")
        async def get_service_instances(service_name: str):
            """Get instances for a specific service."""
            if service_name not in self.service_instances:
                raise HTTPException(status_code=404, detail="Service not found")

            instances = self.service_instances[service_name]
            return {
                "service_name": service_name,
                "instances": [asdict(instance) for instance in instances],
                "healthy_count": len([i for i in instances if i.health_status == "healthy"]),
                "total_count": len(instances)
            }

        @self.app.post("/route/{service_name}")
        async def route_request(service_name: str, request_data: Dict[str, Any] = None):
            """Route a request to an appropriate service instance."""
            if service_name not in self.service_instances:
                raise HTTPException(status_code=404, detail="Service not found")

            instance = self._select_instance(service_name)
            if not instance:
                raise HTTPException(status_code=503, detail="No healthy instances available")

            # Update statistics
            instance.active_connections += 1
            instance.total_requests += 1

            # Simulate request routing (in real implementation, this would proxy the request)
            try:
                # Publish routing information via MQTT
                routing_info = {
                    "service_name": service_name,
                    "instance_id": instance.instance_id,
                    "request_data": request_data or {},
                    "timestamp": time.time()
                }

                self.publish_message(
                    f"alicia/loadbalancer/route/{service_name}",
                    routing_info
                )

                return {
                    "service_name": service_name,
                    "instance_id": instance.instance_id,
                    "instance_host": instance.host,
                    "instance_port": instance.port,
                    "algorithm": self.service_algorithms.get(service_name, self.default_algorithm).value
                }

            except Exception as e:
                instance.failed_requests += 1
                raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")
            finally:
                instance.active_connections -= 1

        @self.app.post("/algorithm/{service_name}")
        async def set_algorithm(service_name: str, algorithm: str):
            """Set load balancing algorithm for a service."""
            try:
                algo_enum = LoadBalancingAlgorithm(algorithm)
                self.service_algorithms[service_name] = algo_enum
                return {"service_name": service_name, "algorithm": algorithm}
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid algorithm: {algorithm}")

        @self.app.get("/stats")
        async def get_stats():
            """Get overall load balancer statistics."""
            total_requests = sum(stats.total_requests for stats in self.load_stats.values())
            total_connections = sum(stats.active_connections for stats in self.load_stats.values())
            total_healthy = sum(stats.healthy_instances for stats in self.load_stats.values())
            total_unhealthy = sum(stats.unhealthy_instances for stats in self.load_stats.values())

            return {
                "total_services": len(self.service_instances),
                "total_instances": sum(len(instances) for instances in self.service_instances.values()),
                "total_requests": total_requests,
                "active_connections": total_connections,
                "healthy_instances": total_healthy,
                "unhealthy_instances": total_unhealthy,
                "timestamp": time.time()
            }

    def subscribe_to_topics(self):
        """Subscribe to load balancing and service discovery topics."""
        self.mqtt_client.subscribe("alicia/system/discovery/+")
        self.mqtt_client.subscribe("alicia/system/health/+")
        self.mqtt_client.subscribe("alicia/loadbalancer/+")
        self.logger.info("Subscribed to load balancing topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/system/discovery/"):
                self._process_discovery_message(topic, message)
            elif topic.startswith("alicia/system/health/"):
                self._process_health_message(topic, message)
            elif topic.startswith("alicia/loadbalancer/"):
                self._process_loadbalancer_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_discovery_message(self, topic: str, message: Dict[str, Any]):
        """Process service discovery messages."""
        try:
            if "register" in topic:
                service_name = message.get("service_name", "unknown")
                instance_id = message.get("instance_id", f"{service_name}_{int(time.time())}")
                host = message.get("host", "localhost")
                port = message.get("port", 8000)

                # Create service instance
                instance = ServiceInstance(
                    instance_id=instance_id,
                    service_name=service_name,
                    host=host,
                    port=port,
                    health_status="healthy",
                    active_connections=0,
                    weight=1,
                    last_health_check=time.time(),
                    response_time=0.0,
                    total_requests=0,
                    failed_requests=0
                )

                # Add to service instances
                if service_name not in self.service_instances:
                    self.service_instances[service_name] = []
                    self.current_round_robin[service_name] = 0

                self.service_instances[service_name].append(instance)

                self.logger.info(f"Registered instance {instance_id} for service {service_name}")

            elif "unregister" in topic:
                service_name = message.get("service_name", "unknown")
                instance_id = message.get("instance_id", "unknown")

                if service_name in self.service_instances:
                    self.service_instances[service_name] = [
                        i for i in self.service_instances[service_name]
                        if i.instance_id != instance_id
                    ]

                    if not self.service_instances[service_name]:
                        del self.service_instances[service_name]
                        if service_name in self.current_round_robin:
                            del self.current_round_robin[service_name]

                    self.logger.info(f"Unregistered instance {instance_id} from service {service_name}")

        except Exception as e:
            self.logger.error(f"Error processing discovery message: {e}")

    def _process_health_message(self, topic: str, message: Dict[str, Any]):
        """Process health status messages."""
        try:
            service_name = message.get("service_name", "unknown")
            instance_id = message.get("instance_id", "unknown")
            health_status = message.get("status", "unknown")

            # Update instance health status
            if service_name in self.service_instances:
                for instance in self.service_instances[service_name]:
                    if instance.instance_id == instance_id:
                        instance.health_status = health_status
                        instance.last_health_check = time.time()
                        if "response_time" in message:
                            instance.response_time = message["response_time"]
                        break

        except Exception as e:
            self.logger.error(f"Error processing health message: {e}")

    def _process_loadbalancer_message(self, topic: str, message: Dict[str, Any]):
        """Process load balancer specific messages."""
        try:
            # Handle load balancer commands
            if "command" in message:
                command = message["command"]
                if command == "update_weights":
                    self._update_instance_weights(message)
                elif command == "set_algorithm":
                    service_name = message.get("service_name")
                    algorithm = message.get("algorithm")
                    if service_name and algorithm:
                        try:
                            self.service_algorithms[service_name] = LoadBalancingAlgorithm(algorithm)
                        except ValueError:
                            self.logger.error(f"Invalid algorithm: {algorithm}")

        except Exception as e:
            self.logger.error(f"Error processing load balancer message: {e}")

    def _select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Select an instance using the configured load balancing algorithm."""
        if service_name not in self.service_instances:
            return None

        instances = [i for i in self.service_instances[service_name] if i.health_status == "healthy"]
        if not instances:
            return None

        algorithm = self.service_algorithms.get(service_name, self.default_algorithm)

        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(service_name, instances)
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(instances)
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(service_name, instances)
        elif algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(instances)
        else:
            return self._round_robin_select(service_name, instances)

    def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin instance selection."""
        current = self.current_round_robin.get(service_name, 0)
        instance = instances[current % len(instances)]
        self.current_round_robin[service_name] = (current + 1) % len(instances)
        return instance

    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections instance selection."""
        return min(instances, key=lambda i: i.active_connections)

    def _weighted_round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin instance selection."""
        total_weight = sum(i.weight for i in instances)
        if total_weight == 0:
            return random.choice(instances)

        current = self.current_round_robin.get(service_name, 0)
        target = (current + 1) % total_weight

        cumulative_weight = 0
        for instance in instances:
            cumulative_weight += instance.weight
            if cumulative_weight > target:
                self.current_round_robin[service_name] = target
                return instance

        return instances[0]

    def _update_instance_weights(self, message: Dict[str, Any]):
        """Update instance weights based on performance."""
        try:
            service_name = message.get("service_name")
            weights = message.get("weights", {})

            if service_name in self.service_instances:
                for instance in self.service_instances[service_name]:
                    if instance.instance_id in weights:
                        instance.weight = max(1, weights[instance.instance_id])

        except Exception as e:
            self.logger.error(f"Error updating instance weights: {e}")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                # Update load balancer statistics
                self._update_statistics()

                # Check circuit breakers
                self._check_circuit_breakers()

                # Publish load balancer status
                self._publish_status()

                time.sleep(self.health_check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _update_statistics(self):
        """Update load balancer statistics."""
        try:
            for service_name, instances in self.service_instances.items():
                total_requests = sum(i.total_requests for i in instances)
                active_connections = sum(i.active_connections for i in instances)
                healthy_instances = len([i for i in instances if i.health_status == "healthy"])
                unhealthy_instances = len([i for i in instances if i.health_status == "unhealthy"])
                avg_response_time = sum(i.response_time for i in instances) / len(instances) if instances else 0

                stats = LoadBalancerStats(
                    total_requests=total_requests,
                    active_connections=active_connections,
                    healthy_instances=healthy_instances,
                    unhealthy_instances=unhealthy_instances,
                    average_response_time=avg_response_time,
                    algorithm=self.service_algorithms.get(service_name, self.default_algorithm).value,
                    timestamp=time.time()
                )

                self.load_stats[service_name] = stats

        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")

    def _check_circuit_breakers(self):
        """Check and update circuit breaker states."""
        try:
            current_time = time.time()

            for service_name, instances in self.service_instances.items():
                for instance in instances:
                    breaker_key = f"{service_name}:{instance.instance_id}"

                    if breaker_key not in self.circuit_breakers:
                        self.circuit_breakers[breaker_key] = {
                            "state": "closed",
                            "failures": 0,
                            "last_failure": 0,
                            "next_attempt": 0
                        }

                    breaker = self.circuit_breakers[breaker_key]

                    # Check if instance should be marked as unhealthy due to failures
                    if instance.failed_requests > self.failure_threshold:
                        if breaker["state"] == "closed":
                            breaker["state"] = "open"
                            breaker["last_failure"] = current_time
                            breaker["next_attempt"] = current_time + self.recovery_timeout
                            instance.health_status = "unhealthy"
                            self.logger.warning(f"Circuit breaker opened for {breaker_key}")

                    # Check if circuit breaker should be half-open
                    elif breaker["state"] == "open" and current_time >= breaker["next_attempt"]:
                        breaker["state"] = "half-open"
                        instance.health_status = "unknown"  # Test the instance
                        self.logger.info(f"Circuit breaker half-open for {breaker_key}")

        except Exception as e:
            self.logger.error(f"Error checking circuit breakers: {e}")

    def _publish_status(self):
        """Publish load balancer status."""
        try:
            status_message = {
                "load_balancer_name": "load_balancer",
                "total_services": len(self.service_instances),
                "total_instances": sum(len(instances) for instances in self.service_instances.values()),
                "healthy_instances": sum(len([i for i in instances if i.health_status == "healthy"])
                                       for instances in self.service_instances.values()),
                "timestamp": time.time(),
                "uptime": time.time() - self.start_time
            }

            self.publish_message(
                "alicia/loadbalancer/status",
                status_message
            )

        except Exception as e:
            self.logger.error(f"Failed to publish status: {e}")

    def start_monitoring(self):
        """Start the background monitoring thread."""
        self.monitoring_thread.start()
        self.logger.info("Load balancer monitoring started")

    def shutdown(self):
        """Gracefully shutdown the load balancer."""
        self.logger.info("Shutting down load balancer...")

        super().shutdown()


def main():
    """Main entry point for the Load Balancer service."""
    service = LoadBalancerService()
    service.start_monitoring()

    # Start FastAPI server
    api = BusServiceAPI(service)
    uvicorn.run(api.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
