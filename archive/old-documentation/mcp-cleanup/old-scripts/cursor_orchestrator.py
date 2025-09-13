#!/usr/bin/env python3
"""
Cursor Agent as MCP Orchestrator
=================================

This module implements the Cursor agent as the Master Control Program (MCP) orchestrator
for the Alicia Smart Home AI QA system. It coordinates with Cline specialists and other
agents through the MQTT bus to provide comprehensive QA automation.

Responsibilities:
- Task orchestration and distribution
- Quality gate enforcement
- Error recovery and retry logic
- Resource management and monitoring
- Integration with Alicia MQTT bus

Author: Alicia MCP Team
Version: 1.0.0
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiofiles
import aiohttp

# MQTT integration
try:
    import asyncio_mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.getLogger(__name__).warning("MQTT dependencies not available")

# Configuration
@dataclass
class OrchestratorConfig:
    """Configuration for Cursor orchestrator"""
    mqtt_broker_url: str = "mqtts://localhost:8883"
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_ca_cert: Optional[str] = None
    alicia_security_gateway_url: str = "https://localhost:8443"
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "bdd_coverage": 8.0,
        "test_quality": 7.0,
        "code_review": 7.0
    })
    max_iterations: int = 3
    task_timeout: int = 300
    retry_attempts: int = 3
    heartbeat_interval: int = 30
    log_level: str = "INFO"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """Types of tasks that can be assigned"""
    BDD_GENERATION = "bdd_generation"
    TEST_CODE_CREATION = "test_code_creation"
    CODE_REVIEW = "code_review"
    QUALITY_ANALYSIS = "quality_analysis"
    FULL_QA_PIPELINE = "full_qa_pipeline"

@dataclass
class Task:
    """Represents a task in the orchestration system"""
    task_id: str
    task_type: TaskType
    priority: int = 1  # 1=highest, 5=lowest
    payload: Dict[str, Any] = field(default_factory=dict)
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class SpecialistInfo:
    """Information about a specialist agent"""
    agent_id: str
    capabilities: List[TaskType]
    status: str = "offline"
    last_heartbeat: Optional[datetime] = None
    current_tasks: int = 0
    max_concurrent_tasks: int = 3
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class QualityGates:
    """Quality gate enforcement system"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.thresholds = config.quality_thresholds
        self.logger = logging.getLogger("quality_gates")
    
    def evaluate_bdd_quality(self, bdd_result: Dict[str, Any]) -> bool:
        """Evaluate BDD generation quality"""
        coverage_score = bdd_result.get("coverage_score", 0)
        return coverage_score >= self.thresholds["bdd_coverage"]
    
    def evaluate_test_quality(self, test_result: Dict[str, Any]) -> bool:
        """Evaluate test code quality"""
        quality_score = test_result.get("quality_score", 0)
        return quality_score >= self.thresholds["test_quality"]
    
    def evaluate_review_quality(self, review_result: Dict[str, Any]) -> bool:
        """Evaluate code review quality"""
        review_score = review_result.get("score", 0)
        bugs_count = len(review_result.get("bugs", []))
        return (review_score >= self.thresholds["code_review"] and 
                bugs_count <= 3)
    
    def evaluate_overall_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate overall quality and provide recommendations"""
        evaluation = {
            "overall_pass": True,
            "gate_results": {},
            "recommendations": []
        }
        
        # Evaluate BDD quality
        bdd_pass = self.evaluate_bdd_quality(results.get("bdd_scenarios", {}))
        evaluation["gate_results"]["bdd_quality"] = bdd_pass
        if not bdd_pass:
            evaluation["overall_pass"] = False
            evaluation["recommendations"].append("Improve BDD scenario coverage")
        
        # Evaluate test quality
        test_pass = self.evaluate_test_quality(results.get("test_files", {}))
        evaluation["gate_results"]["test_quality"] = test_pass
        if not test_pass:
            evaluation["overall_pass"] = False
            evaluation["recommendations"].append("Improve test code quality")
        
        # Evaluate review quality
        review_pass = self.evaluate_review_quality(results.get("review_results", {}))
        evaluation["gate_results"]["review_quality"] = review_pass
        if not review_pass:
            evaluation["overall_pass"] = False
            evaluation["recommendations"].append("Address code review issues")
        
        return evaluation

class CursorOrchestrator:
    """Cursor agent as MCP orchestrator"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.logger = logging.getLogger("cursor_orchestrator")
        self.mqtt_client = None
        self.specialists: Dict[str, SpecialistInfo] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.quality_gates = QualityGates(config)
        self.running = False
        self.heartbeat_task = None
        
        # MQTT topics
        self.topics = {
            "orchestrator": "alicia/mcp/qa/orchestrator/",
            "specialist": "alicia/mcp/qa/specialist/",
            "shared": "alicia/mcp/qa/shared/",
            "system": "alicia/system/"
        }
    
    async def start(self):
        """Start the orchestrator service"""
        self.logger.info("Starting Cursor MCP Orchestrator...")
        
        if not MQTT_AVAILABLE:
            raise RuntimeError("MQTT dependencies not available")
        
        try:
            # Connect to MQTT broker
            await self._connect_mqtt()
            
            # Register with Alicia system
            await self._register_with_alicia()
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Start main processing loop
            self.running = True
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start orchestrator: {e}")
            raise
    
    async def stop(self):
        """Stop the orchestrator service"""
        self.logger.info("Stopping Cursor MCP Orchestrator...")
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        if self.mqtt_client:
            await self.mqtt_client.disconnect()
    
    async def _connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client = asyncio_mqtt.Client(
                hostname=self.config.mqtt_broker_url.replace("mqtts://", "").replace("mqtt://", ""),
                port=8883 if "mqtts://" in self.config.mqtt_broker_url else 1883,
                username=self.config.mqtt_username,
                password=self.config.mqtt_password,
                tls_context=None,  # TODO: Implement TLS context
                keepalive=60
            )
            
            await self.mqtt_client.connect()
            self.logger.info("Connected to MQTT broker")
            
            # Subscribe to relevant topics
            await self._setup_subscriptions()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    async def _setup_subscriptions(self):
        """Setup MQTT topic subscriptions"""
        topics_to_subscribe = [
            f"{self.topics['orchestrator']}task/request",
            f"{self.topics['specialist']}+/task/response",
            f"{self.topics['specialist']}+/status/heartbeat",
            f"{self.topics['specialist']}+/capability/announce",
            f"{self.topics['shared']}codebase/snapshot",
            f"{self.topics['system']}shutdown"
        ]
        
        for topic in topics_to_subscribe:
            await self.mqtt_client.subscribe(topic)
            self.logger.debug(f"Subscribed to topic: {topic}")
    
    async def _register_with_alicia(self):
        """Register with Alicia system"""
        try:
            # Announce orchestrator capabilities
            capabilities = {
                "service_type": "mcp_orchestrator",
                "version": "1.0.0",
                "capabilities": [
                    "task_orchestration",
                    "quality_gate_enforcement",
                    "error_recovery",
                    "resource_management"
                ],
                "status": "online",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.mqtt_client.publish(
                f"{self.topics['orchestrator']}status/announce",
                json.dumps(capabilities)
            )
            
            self.logger.info("Registered with Alicia system")
            
        except Exception as e:
            self.logger.error(f"Failed to register with Alicia: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            try:
                heartbeat = {
                    "service_type": "mcp_orchestrator",
                    "status": "online",
                    "timestamp": datetime.now().isoformat(),
                    "active_tasks": len(self.active_tasks),
                    "specialists": len(self.specialists)
                }
                
                await self.mqtt_client.publish(
                    f"{self.topics['orchestrator']}status/heartbeat",
                    json.dumps(heartbeat)
                )
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def _main_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Process incoming messages
                await self._process_mqtt_messages()
                
                # Process task queue
                await self._process_task_queue()
                
                # Monitor active tasks
                await self._monitor_active_tasks()
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                await asyncio.sleep(1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                await asyncio.sleep(5)
    
    async def _process_mqtt_messages(self):
        """Process incoming MQTT messages"""
        try:
            async with self.mqtt_client.messages() as messages:
                async for message in messages:
                    await self._handle_mqtt_message(message.topic, message.payload)
        except Exception as e:
            self.logger.error(f"Error processing MQTT messages: {e}")
    
    async def _handle_mqtt_message(self, topic: str, payload: bytes):
        """Handle individual MQTT message"""
        try:
            message = json.loads(payload.decode())
            self.logger.debug(f"Received message on {topic}: {message}")
            
            if topic.endswith("/task/request"):
                await self._handle_qa_request(message)
            elif topic.endswith("/task/response"):
                await self._handle_task_response(message)
            elif topic.endswith("/status/heartbeat"):
                await self._handle_specialist_heartbeat(message)
            elif topic.endswith("/capability/announce"):
                await self._handle_capability_announcement(message)
            elif topic.endswith("/shutdown"):
                await self._handle_system_shutdown(message)
                
        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {e}")
    
    async def _handle_qa_request(self, message: Dict[str, Any]):
        """Handle incoming QA request"""
        try:
            codebase_snapshot = message.get("codebase_snapshot", {})
            requirements = message.get("requirements", {})
            
            # Create task plan
            task_plan = await self._create_task_plan(codebase_snapshot, requirements)
            
            # Add tasks to queue
            for task_data in task_plan:
                task = Task(
                    task_id=str(uuid.uuid4()),
                    task_type=TaskType(task_data["type"]),
                    priority=task_data.get("priority", 1),
                    payload=task_data["payload"],
                    timeout=task_data.get("timeout", self.config.task_timeout)
                )
                self.task_queue.append(task)
            
            self.logger.info(f"Created {len(task_plan)} tasks for QA request")
            
        except Exception as e:
            self.logger.error(f"Error handling QA request: {e}")
    
    async def _create_task_plan(self, codebase: Dict[str, Any], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a task plan for QA processing"""
        tasks = []
        
        # BDD Generation task
        tasks.append({
            "type": "bdd_generation",
            "priority": 1,
            "payload": {
                "codebase_snapshot": codebase,
                "requirements": requirements
            },
            "timeout": 300
        })
        
        # Test Code Creation task (depends on BDD)
        tasks.append({
            "type": "test_code_creation",
            "priority": 2,
            "payload": {
                "codebase_snapshot": codebase,
                "requirements": requirements
            },
            "timeout": 400
        })
        
        # Code Review task (depends on test code)
        tasks.append({
            "type": "code_review",
            "priority": 3,
            "payload": {
                "codebase_snapshot": codebase,
                "requirements": requirements
            },
            "timeout": 200
        })
        
        return tasks
    
    async def _process_task_queue(self):
        """Process tasks in the queue"""
        for task in self.task_queue[:]:  # Copy to avoid modification during iteration
            if task.status == TaskStatus.PENDING:
                # Find available specialist
                specialist = await self._find_available_specialist(task.task_type)
                if specialist:
                    await self._assign_task(task, specialist)
                    self.task_queue.remove(task)
    
    async def _find_available_specialist(self, task_type: TaskType) -> Optional[str]:
        """Find an available specialist for the task type"""
        for agent_id, specialist in self.specialists.items():
            if (specialist.status == "online" and 
                task_type in specialist.capabilities and
                specialist.current_tasks < specialist.max_concurrent_tasks):
                return agent_id
        return None
    
    async def _assign_task(self, task: Task, specialist_id: str):
        """Assign task to specialist"""
        try:
            task.assigned_to = specialist_id
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.now()
            
            # Update specialist task count
            self.specialists[specialist_id].current_tasks += 1
            
            # Add to active tasks
            self.active_tasks[task.task_id] = task
            
            # Send task to specialist
            task_message = {
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "sender": "cursor_orchestrator",
                "recipient": specialist_id,
                "message_type": "task_request",
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "priority": task.priority,
                "payload": task.payload,
                "timeout": task.timeout
            }
            
            await self.mqtt_client.publish(
                f"{self.topics['specialist']}{specialist_id}/task/request",
                json.dumps(task_message)
            )
            
            self.logger.info(f"Assigned task {task.task_id} to {specialist_id}")
            
        except Exception as e:
            self.logger.error(f"Error assigning task: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
    
    async def _handle_task_response(self, message: Dict[str, Any]):
        """Handle task response from specialist"""
        try:
            task_id = message.get("task_id")
            if task_id not in self.active_tasks:
                self.logger.warning(f"Received response for unknown task: {task_id}")
                return
            
            task = self.active_tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = message.get("result", {})
            
            # Update specialist task count
            if task.assigned_to in self.specialists:
                self.specialists[task.assigned_to].current_tasks -= 1
            
            self.logger.info(f"Task {task_id} completed by {task.assigned_to}")
            
            # Evaluate quality gates
            if task.result:
                quality_evaluation = self.quality_gates.evaluate_overall_quality(task.result)
                if not quality_evaluation["overall_pass"]:
                    self.logger.warning(f"Task {task_id} failed quality gates")
                    # TODO: Implement retry logic or escalation
            
        except Exception as e:
            self.logger.error(f"Error handling task response: {e}")
    
    async def _handle_specialist_heartbeat(self, message: Dict[str, Any]):
        """Handle specialist heartbeat"""
        try:
            agent_id = message.get("agent_id")
            if agent_id:
                if agent_id not in self.specialists:
                    self.specialists[agent_id] = SpecialistInfo(
                        agent_id=agent_id,
                        capabilities=[]
                    )
                
                self.specialists[agent_id].status = "online"
                self.specialists[agent_id].last_heartbeat = datetime.now()
                
        except Exception as e:
            self.logger.error(f"Error handling specialist heartbeat: {e}")
    
    async def _handle_capability_announcement(self, message: Dict[str, Any]):
        """Handle specialist capability announcement"""
        try:
            agent_id = message.get("agent_id")
            capabilities = message.get("capabilities", [])
            
            if agent_id:
                if agent_id not in self.specialists:
                    self.specialists[agent_id] = SpecialistInfo(
                        agent_id=agent_id,
                        capabilities=[]
                    )
                
                # Convert string capabilities to TaskType enums
                task_types = []
                for cap in capabilities:
                    try:
                        task_types.append(TaskType(cap))
                    except ValueError:
                        self.logger.warning(f"Unknown capability: {cap}")
                
                self.specialists[agent_id].capabilities = task_types
                self.logger.info(f"Updated capabilities for {agent_id}: {capabilities}")
                
        except Exception as e:
            self.logger.error(f"Error handling capability announcement: {e}")
    
    async def _handle_system_shutdown(self, message: Dict[str, Any]):
        """Handle system shutdown request"""
        self.logger.info("Received system shutdown request")
        await self.stop()
    
    async def _monitor_active_tasks(self):
        """Monitor active tasks for timeouts"""
        current_time = datetime.now()
        for task in self.active_tasks.values():
            if (task.status == TaskStatus.ASSIGNED or task.status == TaskStatus.IN_PROGRESS):
                if task.started_at and (current_time - task.started_at).seconds > task.timeout:
                    task.status = TaskStatus.TIMEOUT
                    task.error = "Task timeout"
                    self.logger.warning(f"Task {task.task_id} timed out")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        completed_tasks = [
            task_id for task_id, task in self.active_tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]
        ]
        
        for task_id in completed_tasks:
            del self.active_tasks[task_id]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "status": "online" if self.running else "offline",
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "specialists": len(self.specialists),
            "specialist_details": {
                agent_id: {
                    "status": specialist.status,
                    "capabilities": [cap.value for cap in specialist.capabilities],
                    "current_tasks": specialist.current_tasks
                }
                for agent_id, specialist in self.specialists.items()
            }
        }

# Main execution
async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = OrchestratorConfig(
        mqtt_broker_url="mqtts://localhost:8883",
        quality_thresholds={
            "bdd_coverage": 8.0,
            "test_quality": 7.0,
            "code_review": 7.0
        }
    )
    
    # Create and start orchestrator
    orchestrator = CursorOrchestrator(config)
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
