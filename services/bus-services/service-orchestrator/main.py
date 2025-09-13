"""
Alicia Bus Architecture - Service Orchestrator Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service provides centralized service orchestration and lifecycle management
for all bus services, including dependency management, startup sequencing,
and service coordination.
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from pathlib import Path
from collections import defaultdict, deque

import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
import networkx as nx

from service_wrapper import BusServiceWrapper, BusServiceAPI


class ServiceState(Enum):
    UNKNOWN = "unknown"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class ServiceAction(Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    SCALE = "scale"
    UPDATE = "update"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceDefinition:
    """Service definition with metadata."""
    service_name: str
    container_name: str
    image: str
    ports: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    healthcheck: Optional[Dict[str, Any]] = None
    restart_policy: str = "unless-stopped"
    networks: List[str] = field(default_factory=lambda: ["alicia_bus_network"])
    labels: Dict[str, str] = field(default_factory=dict)
    priority: int = 1
    category: str = "core"
    description: str = ""


@dataclass
class ServiceInstance:
    """Service instance information."""
    service_name: str
    instance_id: str
    container_id: Optional[str]
    state: ServiceState
    health_status: str = "unknown"
    last_seen: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    restart_count: int = 0
    version: str = "1.0.0"
    ip_address: Optional[str] = None
    ports: Dict[str, int] = field(default_factory=dict)


@dataclass
class ServiceDependency:
    """Service dependency relationship."""
    service_name: str
    depends_on: List[str] = field(default_factory=list)
    required_by: List[str] = field(default_factory=list)
    optional_deps: List[str] = field(default_factory=list)


@dataclass
class OrchestrationTask:
    """Orchestration task definition."""
    task_id: str
    action: ServiceAction
    service_name: str
    instance_id: Optional[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"
    progress: float = 0.0
    error_message: Optional[str] = None
    created_by: str = "system"


@dataclass
class ServiceGroup:
    """Service group for coordinated operations."""
    group_name: str
    services: List[str] = field(default_factory=list)
    description: str = ""
    start_order: List[str] = field(default_factory=list)
    stop_order: List[str] = field(default_factory=list)


class ServiceOrchestratorService(BusServiceWrapper):
    """
    Service Orchestrator Service for the Alicia Bus Architecture.

    Provides centralized service orchestration and lifecycle management,
    including dependency management, startup sequencing, and service coordination.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": "service_orchestrator",
            "password": "alicia_orchestrator_2024"
        }

        super().__init__("service_orchestrator", mqtt_config)

        # Service management
        self.service_definitions: Dict[str, ServiceDefinition] = {}
        self.service_instances: Dict[str, ServiceInstance] = {}
        self.service_dependencies: Dict[str, ServiceDependency] = {}
        self.orchestration_tasks: Dict[str, OrchestrationTask] = {}
        self.service_groups: Dict[str, ServiceGroup] = {}

        # Orchestration state
        self.dependency_graph = nx.DiGraph()
        self.task_queue = deque()
        self.active_tasks: Set[str] = set()

        # Configuration
        self.max_concurrent_tasks = 5
        self.task_timeout = 300  # 5 minutes
        self.health_check_interval = 30
        self.auto_recovery = True

        # FastAPI setup
        self.app = FastAPI(title="Alicia Service Orchestrator", version="1.0.0")
        self._setup_api_endpoints()

        # Background threads
        self.orchestration_thread = threading.Thread(target=self._orchestration_loop)
        self.orchestration_thread.daemon = True

        self.health_thread = threading.Thread(target=self._health_monitoring_loop)
        self.health_thread.daemon = True

        self.recovery_thread = threading.Thread(target=self._auto_recovery_loop)
        self.recovery_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "service_orchestration",
            "lifecycle_management",
            "dependency_management",
            "service_coordination",
            "auto_recovery"
        ]

        self.version = "1.0.0"

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the service orchestrator."""

        @self.app.get("/health")
        async def get_health():
            """Get service orchestrator health."""
            return self.get_health_status()

        @self.app.get("/services")
        async def get_services(
            category: Optional[str] = None,
            state: Optional[str] = None,
            group: Optional[str] = None
        ):
            """Get all services with optional filtering."""
            services = []

            for service_name, definition in self.service_definitions.items():
                if category and definition.category != category:
                    continue

                instance = self.service_instances.get(service_name)
                if state and instance and instance.state.value != state:
                    continue

                if group and group not in self.service_groups:
                    continue
                if group and service_name not in self.service_groups[group].services:
                    continue

                service_info = asdict(definition)
                if instance:
                    service_info["instance"] = asdict(instance)

                services.append(service_info)

            services.sort(key=lambda x: (x["priority"], x["service_name"]))
            return {"services": services}

        @self.app.post("/services/{service_name}/start")
        async def start_service(service_name: str, background_tasks: BackgroundTasks):
            """Start a service."""
            if service_name not in self.service_definitions:
                raise HTTPException(status_code=404, detail="Service not found")

            task = self._create_orchestration_task(
                ServiceAction.START,
                service_name,
                created_by="api"
            )

            background_tasks.add_task(self._execute_task, task.task_id)

            return {"task_id": task.task_id, "message": f"Starting service {service_name}"}

        @self.app.post("/services/{service_name}/stop")
        async def stop_service(service_name: str, background_tasks: BackgroundTasks):
            """Stop a service."""
            if service_name not in self.service_definitions:
                raise HTTPException(status_code=404, detail="Service not found")

            task = self._create_orchestration_task(
                ServiceAction.STOP,
                service_name,
                created_by="api"
            )

            background_tasks.add_task(self._execute_task, task.task_id)

            return {"task_id": task.task_id, "message": f"Stopping service {service_name}"}

        @self.app.post("/services/{service_name}/restart")
        async def restart_service(service_name: str, background_tasks: BackgroundTasks):
            """Restart a service."""
            if service_name not in self.service_definitions:
                raise HTTPException(status_code=404, detail="Service not found")

            task = self._create_orchestration_task(
                ServiceAction.RESTART,
                service_name,
                created_by="api"
            )

            background_tasks.add_task(self._execute_task, task.task_id)

            return {"task_id": task.task_id, "message": f"Restarting service {service_name}"}

        @self.app.post("/services/{service_name}/scale")
        async def scale_service(service_name: str, replicas: int, background_tasks: BackgroundTasks):
            """Scale a service."""
            if service_name not in self.service_definitions:
                raise HTTPException(status_code=404, detail="Service not found")

            task = self._create_orchestration_task(
                ServiceAction.SCALE,
                service_name,
                parameters={"replicas": replicas},
                created_by="api"
            )

            background_tasks.add_task(self._execute_task, task.task_id)

            return {"task_id": task.task_id, "message": f"Scaling service {service_name} to {replicas} replicas"}

        @self.app.get("/services/{service_name}/status")
        async def get_service_status(service_name: str):
            """Get service status."""
            if service_name not in self.service_definitions:
                raise HTTPException(status_code=404, detail="Service not found")

            instance = self.service_instances.get(service_name)
            definition = self.service_definitions[service_name]

            status = {
                "service_name": service_name,
                "definition": asdict(definition),
                "state": ServiceState.UNKNOWN.value,
                "health_status": "unknown",
                "last_seen": None
            }

            if instance:
                status.update({
                    "state": instance.state.value,
                    "health_status": instance.health_status,
                    "last_seen": instance.last_seen,
                    "start_time": instance.start_time,
                    "restart_count": instance.restart_count
                })

            return status

        @self.app.get("/groups")
        async def get_groups():
            """Get all service groups."""
            return {"groups": [asdict(group) for group in self.service_groups.values()]}

        @self.app.post("/groups/{group_name}/start")
        async def start_group(group_name: str, background_tasks: BackgroundTasks):
            """Start all services in a group."""
            if group_name not in self.service_groups:
                raise HTTPException(status_code=404, detail="Group not found")

            group = self.service_groups[group_name]
            tasks = []

            for service_name in group.start_order or group.services:
                if service_name in self.service_definitions:
                    task = self._create_orchestration_task(
                        ServiceAction.START,
                        service_name,
                        created_by="api"
                    )
                    tasks.append(task.task_id)
                    background_tasks.add_task(self._execute_task, task.task_id)

            return {
                "group_name": group_name,
                "task_ids": tasks,
                "message": f"Starting {len(tasks)} services in group {group_name}"
            }

        @self.app.post("/groups/{group_name}/stop")
        async def stop_group(group_name: str, background_tasks: BackgroundTasks):
            """Stop all services in a group."""
            if group_name not in self.service_groups:
                raise HTTPException(status_code=404, detail="Group not found")

            group = self.service_groups[group_name]
            tasks = []

            for service_name in group.stop_order or reversed(group.services):
                if service_name in self.service_definitions:
                    task = self._create_orchestration_task(
                        ServiceAction.STOP,
                        service_name,
                        created_by="api"
                    )
                    tasks.append(task.task_id)
                    background_tasks.add_task(self._execute_task, task.task_id)

            return {
                "group_name": group_name,
                "task_ids": tasks,
                "message": f"Stopping {len(tasks)} services in group {group_name}"
            }

        @self.app.get("/tasks")
        async def get_tasks(status: Optional[str] = None, limit: int = Query(50, description="Number of tasks to return")):
            """Get orchestration tasks."""
            tasks = []

            for task in self.orchestration_tasks.values():
                if status and task.status != status:
                    continue
                tasks.append(asdict(task))

            tasks.sort(key=lambda x: x["created_at"], reverse=True)

            return {"tasks": tasks[:limit]}

        @self.app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            """Get a specific task."""
            if task_id not in self.orchestration_tasks:
                raise HTTPException(status_code=404, detail="Task not found")

            return {"task": asdict(self.orchestration_tasks[task_id])}

        @self.app.get("/dependencies")
        async def get_dependencies():
            """Get service dependency graph."""
            dependencies = {}

            for service_name, deps in self.service_dependencies.items():
                dependencies[service_name] = {
                    "depends_on": deps.depends_on,
                    "required_by": deps.required_by,
                    "optional_deps": deps.optional_deps
                }

            return {"dependencies": dependencies}

        @self.app.get("/topology")
        async def get_topology():
            """Get service topology information."""
            try:
                # Calculate topological order
                topo_order = list(nx.topological_sort(self.dependency_graph))

                # Find cycles
                cycles = list(nx.simple_cycles(self.dependency_graph))

                return {
                    "topological_order": topo_order,
                    "cycles": cycles,
                    "strongly_connected": list(nx.strongly_connected_components(self.dependency_graph))
                }

            except nx.NetworkXError as e:
                raise HTTPException(status_code=400, detail=f"Topology error: {str(e)}")

    def subscribe_to_topics(self):
        """Subscribe to orchestration topics."""
        self.mqtt_client.subscribe("alicia/orchestrator/+")
        self.mqtt_client.subscribe("alicia/services/+/status")
        self.mqtt_client.subscribe("alicia/services/+/health")
        self.logger.info("Subscribed to orchestration topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/services/") and topic.endswith("/status"):
                self._process_service_status_message(topic, message)
            elif topic.startswith("alicia/services/") and topic.endswith("/health"):
                self._process_service_health_message(topic, message)
            elif topic.startswith("alicia/orchestrator/"):
                self._process_orchestrator_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_service_status_message(self, topic: str, message: Dict[str, Any]):
        """Process service status messages."""
        try:
            service_name = topic.split("/")[2]
            state = ServiceState(message.get("state", "unknown"))
            instance_id = message.get("instance_id", service_name)

            instance_key = f"{service_name}:{instance_id}" if instance_id != service_name else service_name

            if instance_key not in self.service_instances:
                self.service_instances[instance_key] = ServiceInstance(
                    service_name=service_name,
                    instance_id=instance_id,
                    container_id=message.get("container_id"),
                    state=state
                )
            else:
                instance = self.service_instances[instance_key]
                instance.state = state
                instance.last_seen = time.time()
                instance.container_id = message.get("container_id", instance.container_id)
                instance.version = message.get("version", instance.version)
                instance.ip_address = message.get("ip_address", instance.ip_address)
                instance.ports = message.get("ports", instance.ports)

                if state == ServiceState.RUNNING and not instance.start_time:
                    instance.start_time = time.time()
                elif state == ServiceState.STOPPED and instance.start_time:
                    instance.stop_time = time.time()

        except Exception as e:
            self.logger.error(f"Error processing service status message: {e}")

    def _process_service_health_message(self, topic: str, message: Dict[str, Any]):
        """Process service health messages."""
        try:
            service_name = topic.split("/")[2]
            health_status = message.get("health_status", "unknown")
            instance_id = message.get("instance_id", service_name)

            instance_key = f"{service_name}:{instance_id}" if instance_id != service_name else service_name

            if instance_key in self.service_instances:
                instance = self.service_instances[instance_key]
                instance.health_status = health_status
                instance.last_seen = time.time()

        except Exception as e:
            self.logger.error(f"Error processing service health message: {e}")

    def _process_orchestrator_message(self, topic: str, message: Dict[str, Any]):
        """Process orchestrator control messages."""
        try:
            command = message.get("command")

            if command == "start_service":
                service_name = message.get("service_name")
                if service_name and service_name in self.service_definitions:
                    task = self._create_orchestration_task(
                        ServiceAction.START,
                        service_name,
                        created_by="mqtt"
                    )
                    self.task_queue.append(task.task_id)

            elif command == "stop_service":
                service_name = message.get("service_name")
                if service_name and service_name in self.service_definitions:
                    task = self._create_orchestration_task(
                        ServiceAction.STOP,
                        service_name,
                        created_by="mqtt"
                    )
                    self.task_queue.append(task.task_id)

            elif command == "restart_service":
                service_name = message.get("service_name")
                if service_name and service_name in self.service_definitions:
                    task = self._create_orchestration_task(
                        ServiceAction.RESTART,
                        service_name,
                        created_by="mqtt"
                    )
                    self.task_queue.append(task.task_id)

        except Exception as e:
            self.logger.error(f"Error processing orchestrator message: {e}")

    def _create_orchestration_task(
        self,
        action: ServiceAction,
        service_name: str,
        instance_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        created_by: str = "system"
    ) -> OrchestrationTask:
        """Create a new orchestration task."""
        task = OrchestrationTask(
            task_id=str(uuid.uuid4()),
            action=action,
            service_name=service_name,
            instance_id=instance_id,
            parameters=parameters or {},
            created_by=created_by
        )

        self.orchestration_tasks[task.task_id] = task
        return task

    def _execute_task(self, task_id: str):
        """Execute an orchestration task."""
        try:
            if task_id not in self.orchestration_tasks:
                self.logger.error(f"Task {task_id} not found")
                return

            task = self.orchestration_tasks[task_id]
            task.started_at = time.time()
            task.status = "running"
            self.active_tasks.add(task_id)

            self.logger.info(f"Executing task {task_id}: {task.action.value} {task.service_name}")

            # Execute based on action
            if task.action == ServiceAction.START:
                self._execute_start_task(task)
            elif task.action == ServiceAction.STOP:
                self._execute_stop_task(task)
            elif task.action == ServiceAction.RESTART:
                self._execute_restart_task(task)
            elif task.action == ServiceAction.SCALE:
                self._execute_scale_task(task)
            elif task.action == ServiceAction.UPDATE:
                self._execute_update_task(task)
            elif task.action == ServiceAction.MAINTENANCE:
                self._execute_maintenance_task(task)

            task.completed_at = time.time()
            task.status = "completed"
            task.progress = 100.0

            self.logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = time.time()

        finally:
            self.active_tasks.discard(task_id)

    def _execute_start_task(self, task: OrchestrationTask):
        """Execute a start service task."""
        try:
            # Check dependencies
            if not self._check_dependencies(task.service_name):
                raise Exception(f"Dependencies not satisfied for {task.service_name}")

            # Send start command via MQTT
            self.publish_message(f"alicia/services/{task.service_name}/control", {
                "command": "start",
                "task_id": task.task_id,
                "timestamp": time.time()
            })

            # Wait for service to start (simplified)
            time.sleep(5)

        except Exception as e:
            raise Exception(f"Failed to start service: {e}")

    def _execute_stop_task(self, task: OrchestrationTask):
        """Execute a stop service task."""
        try:
            # Send stop command via MQTT
            self.publish_message(f"alicia/services/{task.service_name}/control", {
                "command": "stop",
                "task_id": task.task_id,
                "timestamp": time.time()
            })

            # Wait for service to stop (simplified)
            time.sleep(5)

        except Exception as e:
            raise Exception(f"Failed to stop service: {e}")

    def _execute_restart_task(self, task: OrchestrationTask):
        """Execute a restart service task."""
        try:
            # Stop first
            self._execute_stop_task(task)

            # Wait a moment
            time.sleep(2)

            # Start again
            self._execute_start_task(task)

        except Exception as e:
            raise Exception(f"Failed to restart service: {e}")

    def _execute_scale_task(self, task: OrchestrationTask):
        """Execute a scale service task."""
        try:
            replicas = task.parameters.get("replicas", 1)

            self.publish_message(f"alicia/services/{task.service_name}/control", {
                "command": "scale",
                "replicas": replicas,
                "task_id": task.task_id,
                "timestamp": time.time()
            })

        except Exception as e:
            raise Exception(f"Failed to scale service: {e}")

    def _execute_update_task(self, task: OrchestrationTask):
        """Execute an update service task."""
        try:
            # This would involve updating the service image/version
            # For now, just restart with new configuration
            self._execute_restart_task(task)

        except Exception as e:
            raise Exception(f"Failed to update service: {e}")

    def _execute_maintenance_task(self, task: OrchestrationTask):
        """Execute a maintenance service task."""
        try:
            # Put service in maintenance mode
            self.publish_message(f"alicia/services/{task.service_name}/control", {
                "command": "maintenance",
                "mode": task.parameters.get("mode", "on"),
                "task_id": task.task_id,
                "timestamp": time.time()
            })

        except Exception as e:
            raise Exception(f"Failed to set maintenance mode: {e}")

    def _check_dependencies(self, service_name: str) -> bool:
        """Check if service dependencies are satisfied."""
        try:
            if service_name not in self.service_dependencies:
                return True

            deps = self.service_dependencies[service_name]

            # Check required dependencies
            for dep in deps.depends_on:
                if dep not in self.service_instances:
                    return False

                instance = self.service_instances[dep]
                if instance.state != ServiceState.RUNNING:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking dependencies for {service_name}: {e}")
            return False

    def _orchestration_loop(self):
        """Main orchestration loop."""
        while True:
            try:
                # Process queued tasks
                while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
                    task_id = self.task_queue.popleft()

                    if task_id in self.orchestration_tasks:
                        task = self.orchestration_tasks[task_id]
                        if task.status == "pending":
                            threading.Thread(target=self._execute_task, args=(task_id,)).start()

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in orchestration loop: {e}")
                time.sleep(5)

    def _health_monitoring_loop(self):
        """Health monitoring loop."""
        while True:
            try:
                current_time = time.time()

                # Check for stale service instances
                stale_instances = []
                for instance_key, instance in self.service_instances.items():
                    if current_time - instance.last_seen > 300:  # 5 minutes
                        stale_instances.append(instance_key)

                for instance_key in stale_instances:
                    instance = self.service_instances[instance_key]
                    instance.state = ServiceState.UNKNOWN
                    instance.health_status = "stale"

                time.sleep(self.health_check_interval)

            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(30)

    def _auto_recovery_loop(self):
        """Auto recovery loop."""
        while True:
            try:
                if self.auto_recovery:
                    current_time = time.time()

                    # Check for failed services
                    for instance_key, instance in self.service_instances.items():
                        if instance.state == ServiceState.FAILED:
                            # Check if we should attempt recovery
                            if current_time - instance.last_seen > 60:  # 1 minute since failure
                                self.logger.info(f"Attempting auto-recovery for {instance_key}")

                                task = self._create_orchestration_task(
                                    ServiceAction.RESTART,
                                    instance.service_name,
                                    instance.instance_id,
                                    created_by="auto_recovery"
                                )

                                self.task_queue.append(task.task_id)

                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in auto recovery loop: {e}")
                time.sleep(60)

    def start_orchestration(self):
        """Start the orchestration threads."""
        self.orchestration_thread.start()
        self.health_thread.start()
        self.recovery_thread.start()
        self.logger.info("Service orchestration started")

    def shutdown(self):
        """Gracefully shutdown the service orchestrator."""
        self.logger.info("Shutting down service orchestrator...")

        super().shutdown()


async def main():
    """Main entry point for the Service Orchestrator service."""
    service = ServiceOrchestratorService()
    service.start_orchestration()

    # Start FastAPI server
    api = BusServiceAPI(service)
    config = uvicorn.Config(api.app, host="0.0.0.0", port=8014)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
