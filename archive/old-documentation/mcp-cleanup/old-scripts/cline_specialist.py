#!/usr/bin/env python3
"""
Cline Agent as QA Specialist
============================

This module implements the Cline agent as a specialized QA agent within the Alicia
Smart Home AI ecosystem. It focuses on specific QA tasks using the grok-code-fast-1
model and communicates with the Cursor orchestrator via MQTT.

Responsibilities:
- BDD scenario generation from codebase analysis
- Python test code creation using pytest
- Code review and quality analysis
- Specialized QA expertise with grok-code-fast-1 model

Author: Alicia MCP Team
Version: 1.0.0
"""

import asyncio
import json
import uuid
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# MQTT integration
try:
    import asyncio_mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.getLogger(__name__).warning("MQTT dependencies not available")

# Grok API integration
try:
    import requests
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False
    logging.getLogger(__name__).warning("Grok API dependencies not available")

@dataclass
class SpecialistConfig:
    """Configuration for Cline specialist"""
    agent_id: str = "cline_specialist"
    mqtt_broker_url: str = "mqtts://localhost:8883"
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    grok_api_key: Optional[str] = None
    grok_base_url: str = "https://api.grok.com/v1"
    model: str = "grok-code-fast-1"
    max_concurrent_tasks: int = 3
    heartbeat_interval: int = 30
    task_timeout: int = 300
    log_level: str = "INFO"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class Task:
    """Represents a task assigned to the specialist"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    assigned_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GrokAPIClient:
    """Client for Grok API integration"""
    
    def __init__(self, config: SpecialistConfig):
        self.config = config
        self.api_key = config.grok_api_key or os.getenv("GROK_API_KEY")
        self.base_url = config.grok_base_url
        self.logger = logging.getLogger("grok_client")
        
        if not self.api_key:
            raise ValueError("Grok API key not provided")
    
    async def generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate response using Grok API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # Use asyncio to run the request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            self.logger.error(f"Grok API error: {e}")
            raise
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response using Grok API"""
        try:
            # Add schema instruction to prompt
            structured_prompt = f"""
{prompt}

Please respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Ensure the response is valid JSON and follows the schema exactly.
"""
            
            response = await self.generate_response(structured_prompt, max_tokens=4000)
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                # Return a fallback structure
                return {
                    "error": "Failed to parse JSON response",
                    "raw_response": response
                }
                
        except Exception as e:
            self.logger.error(f"Structured response error: {e}")
            raise

class ClineSpecialist:
    """Cline agent as QA specialist"""
    
    def __init__(self, config: SpecialistConfig):
        self.config = config
        self.logger = logging.getLogger("cline_specialist")
        self.mqtt_client = None
        self.grok_client = None
        self.active_tasks: Dict[str, Task] = {}
        self.capabilities = [
            "bdd_generation",
            "test_code_creation",
            "code_review",
            "quality_analysis"
        ]
        self.running = False
        self.heartbeat_task = None
        
        # Initialize Grok client
        if GROK_AVAILABLE:
            try:
                self.grok_client = GrokAPIClient(config)
            except Exception as e:
                self.logger.error(f"Failed to initialize Grok client: {e}")
                self.grok_client = None
        
        # MQTT topics
        self.topics = {
            "specialist": f"alicia/mcp/qa/specialist/{config.agent_id}/",
            "orchestrator": "alicia/mcp/qa/orchestrator/",
            "shared": "alicia/mcp/qa/shared/"
        }
    
    async def start(self):
        """Start the specialist service"""
        self.logger.info(f"Starting Cline Specialist ({self.config.agent_id})...")
        
        if not MQTT_AVAILABLE:
            raise RuntimeError("MQTT dependencies not available")
        
        if not self.grok_client:
            raise RuntimeError("Grok API client not available")
        
        try:
            # Connect to MQTT broker
            await self._connect_mqtt()
            
            # Announce capabilities
            await self._announce_capabilities()
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Start main processing loop
            self.running = True
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start specialist: {e}")
            raise
    
    async def stop(self):
        """Stop the specialist service"""
        self.logger.info("Stopping Cline Specialist...")
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
            f"{self.topics['specialist']}task/request",
            f"{self.topics['orchestrator']}control/command",
            f"{self.topics['shared']}config/update"
        ]
        
        for topic in topics_to_subscribe:
            await self.mqtt_client.subscribe(topic)
            self.logger.debug(f"Subscribed to topic: {topic}")
    
    async def _announce_capabilities(self):
        """Announce specialist capabilities"""
        try:
            capabilities = {
                "agent_id": self.config.agent_id,
                "service_type": "qa_specialist",
                "version": "1.0.0",
                "capabilities": self.capabilities,
                "model": self.config.model,
                "max_concurrent_tasks": self.config.max_concurrent_tasks,
                "status": "online",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.mqtt_client.publish(
                f"{self.topics['specialist']}capability/announce",
                json.dumps(capabilities)
            )
            
            self.logger.info("Announced capabilities")
            
        except Exception as e:
            self.logger.error(f"Failed to announce capabilities: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            try:
                heartbeat = {
                    "agent_id": self.config.agent_id,
                    "service_type": "qa_specialist",
                    "status": "online",
                    "timestamp": datetime.now().isoformat(),
                    "active_tasks": len(self.active_tasks),
                    "model": self.config.model
                }
                
                await self.mqtt_client.publish(
                    f"{self.topics['specialist']}status/heartbeat",
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
                
                # Process active tasks
                await self._process_active_tasks()
                
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
                await self._handle_task_request(message)
            elif topic.endswith("/control/command"):
                await self._handle_control_command(message)
            elif topic.endswith("/config/update"):
                await self._handle_config_update(message)
                
        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {e}")
    
    async def _handle_task_request(self, message: Dict[str, Any]):
        """Handle task request from orchestrator"""
        try:
            task_id = message.get("task_id")
            task_type = message.get("task_type")
            payload = message.get("payload", {})
            
            if not task_id or not task_type:
                self.logger.warning("Invalid task request: missing task_id or task_type")
                return
            
            # Check if we can handle this task type
            if task_type not in self.capabilities:
                self.logger.warning(f"Cannot handle task type: {task_type}")
                return
            
            # Check if we have capacity
            if len(self.active_tasks) >= self.config.max_concurrent_tasks:
                self.logger.warning("At capacity, cannot accept new task")
                return
            
            # Create task
            task = Task(
                task_id=task_id,
                task_type=task_type,
                payload=payload
            )
            
            self.active_tasks[task_id] = task
            self.logger.info(f"Accepted task {task_id} of type {task_type}")
            
        except Exception as e:
            self.logger.error(f"Error handling task request: {e}")
    
    async def _handle_control_command(self, message: Dict[str, Any]):
        """Handle control command from orchestrator"""
        try:
            command = message.get("command")
            
            if command == "shutdown":
                self.logger.info("Received shutdown command")
                await self.stop()
            elif command == "status":
                await self._send_status_update()
            elif command == "capabilities":
                await self._announce_capabilities()
                
        except Exception as e:
            self.logger.error(f"Error handling control command: {e}")
    
    async def _handle_config_update(self, message: Dict[str, Any]):
        """Handle configuration update"""
        try:
            # Update configuration based on message
            self.logger.info("Received configuration update")
            # TODO: Implement configuration update logic
            
        except Exception as e:
            self.logger.error(f"Error handling config update: {e}")
    
    async def _process_active_tasks(self):
        """Process active tasks"""
        for task_id, task in self.active_tasks.items():
            if task.status == TaskStatus.PENDING:
                await self._execute_task(task)
    
    async def _execute_task(self, task: Task):
        """Execute a specific task"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            self.logger.info(f"Executing task {task.task_id} of type {task.task_type}")
            
            # Execute based on task type
            if task.task_type == "bdd_generation":
                result = await self._generate_bdd_scenarios(task.payload)
            elif task.task_type == "test_code_creation":
                result = await self._create_test_code(task.payload)
            elif task.task_type == "code_review":
                result = await self._review_code(task.payload)
            elif task.task_type == "quality_analysis":
                result = await self._analyze_quality(task.payload)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
            # Send response to orchestrator
            await self._send_task_response(task)
            
            self.logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            # Send error response
            await self._send_task_response(task)
    
    async def _generate_bdd_scenarios(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BDD scenarios from codebase analysis"""
        try:
            codebase = payload.get("codebase_snapshot", {})
            requirements = payload.get("requirements", {})
            
            prompt = f"""
You are an expert BDD scenario builder. Analyze this codebase and generate comprehensive BDD scenarios in Gherkin format.

Codebase Information:
- Project: {codebase.get('project_name', 'Unknown')}
- Architecture: {codebase.get('architecture', 'Not specified')}
- Structure: {json.dumps(codebase.get('structure', {}), indent=2)}
- Critical Paths: {codebase.get('critical_paths', [])}
- Integration Points: {codebase.get('integration_points', [])}
- Error Scenarios: {codebase.get('error_scenarios', [])}

Requirements:
{json.dumps(requirements, indent=2)}

Generate BDD scenarios that cover:
1. All critical paths and user journeys
2. Happy path and edge cases
3. Error scenarios and exception handling
4. Integration points and external dependencies
5. Performance and scalability scenarios

Return the result as JSON with this structure:
{{
    "features": [
        {{
            "name": "Feature Name",
            "description": "Feature description",
            "scenarios": [
                {{
                    "name": "Scenario Name",
                    "steps": ["Given...", "When...", "Then..."],
                    "tags": ["@tag1", "@tag2"],
                    "priority": "high|medium|low"
                }}
            ]
        }}
    ],
    "coverage_score": 8.5,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""
            
            result = await self.grok_client.generate_structured_response(prompt, {
                "type": "object",
                "properties": {
                    "features": {"type": "array"},
                    "coverage_score": {"type": "number"},
                    "recommendations": {"type": "array"}
                }
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating BDD scenarios: {e}")
            return {
                "error": str(e),
                "features": [],
                "coverage_score": 0,
                "recommendations": []
            }
    
    async def _create_test_code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create Python test code from BDD scenarios"""
        try:
            codebase = payload.get("codebase_snapshot", {})
            bdd_scenarios = payload.get("bdd_scenarios", {})
            
            prompt = f"""
You are an expert Python test developer. Create comprehensive test code based on the BDD scenarios and codebase structure.

Codebase Structure:
{json.dumps(codebase.get('structure', {}), indent=2)}

BDD Scenarios:
{json.dumps(bdd_scenarios, indent=2)}

Create pytest-compatible test files that:
1. Cover all BDD scenarios
2. Use proper test structure and organization
3. Include fixtures and test data
4. Implement proper assertions and validations
5. Handle edge cases and error scenarios
6. Use appropriate mocking for external dependencies

Return the result as JSON with this structure:
{{
    "files": [
        {{
            "path": "tests/test_feature.py",
            "content": "def test_feature(): ...",
            "test_count": 5,
            "coverage_estimate": 85.0
        }}
    ],
    "quality_score": 8.5,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""
            
            result = await self.grok_client.generate_structured_response(prompt, {
                "type": "object",
                "properties": {
                    "files": {"type": "array"},
                    "quality_score": {"type": "number"},
                    "recommendations": {"type": "array"}
                }
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating test code: {e}")
            return {
                "error": str(e),
                "files": [],
                "quality_score": 0,
                "recommendations": []
            }
    
    async def _review_code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Review generated test code"""
        try:
            test_files = payload.get("test_files", {})
            bdd_scenarios = payload.get("bdd_scenarios", {})
            
            prompt = f"""
You are an expert Python code reviewer specializing in test code. Review the generated test code for quality, correctness, and adherence to best practices.

Test Files:
{json.dumps(test_files, indent=2)}

BDD Scenarios:
{json.dumps(bdd_scenarios, indent=2)}

Review criteria:
1. Code quality and readability
2. Test structure and organization
3. Proper use of pytest features
4. Assertion quality and coverage
5. Error handling and edge cases
6. Mocking and test isolation
7. Adherence to BDD scenarios
8. Integration with codebase

Return the result as JSON with this structure:
{{
    "score": 8.5,
    "green": true,
    "bugs": [
        {{
            "issue": "Bug description",
            "severity": "high|medium|low",
            "location": "file:line",
            "suggestion": "Fix suggestion"
        }}
    ],
    "false_positives": ["False positive 1"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""
            
            result = await self.grok_client.generate_structured_response(prompt, {
                "type": "object",
                "properties": {
                    "score": {"type": "number"},
                    "green": {"type": "boolean"},
                    "bugs": {"type": "array"},
                    "false_positives": {"type": "array"},
                    "recommendations": {"type": "array"}
                }
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error reviewing code: {e}")
            return {
                "error": str(e),
                "score": 0,
                "green": False,
                "bugs": [],
                "false_positives": [],
                "recommendations": []
            }
    
    async def _analyze_quality(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall quality of QA results"""
        try:
            bdd_scenarios = payload.get("bdd_scenarios", {})
            test_files = payload.get("test_files", {})
            review_results = payload.get("review_results", {})
            
            prompt = f"""
You are an expert QA analyst. Analyze the overall quality of the QA results and provide comprehensive recommendations.

BDD Scenarios:
{json.dumps(bdd_scenarios, indent=2)}

Test Files:
{json.dumps(test_files, indent=2)}

Review Results:
{json.dumps(review_results, indent=2)}

Analyze:
1. Overall quality and completeness
2. Coverage gaps and missing scenarios
3. Test effectiveness and maintainability
4. Integration with codebase
5. Performance and scalability considerations
6. Risk assessment and mitigation

Return the result as JSON with this structure:
{{
    "overall_score": 8.5,
    "quality_metrics": {{
        "coverage": 85.0,
        "maintainability": 8.0,
        "testability": 9.0,
        "performance": 7.5
    }},
    "risk_assessment": {{
        "high_risk": ["Risk 1", "Risk 2"],
        "medium_risk": ["Risk 3"],
        "low_risk": ["Risk 4"]
    }},
    "recommendations": [
        {{
            "priority": "high|medium|low",
            "category": "coverage|quality|performance|maintainability",
            "description": "Recommendation description",
            "impact": "Expected impact"
        }}
    ]
}}
"""
            
            result = await self.grok_client.generate_structured_response(prompt, {
                "type": "object",
                "properties": {
                    "overall_score": {"type": "number"},
                    "quality_metrics": {"type": "object"},
                    "risk_assessment": {"type": "object"},
                    "recommendations": {"type": "array"}
                }
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing quality: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "quality_metrics": {},
                "risk_assessment": {},
                "recommendations": []
            }
    
    async def _send_task_response(self, task: Task):
        """Send task response to orchestrator"""
        try:
            response = {
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "sender": self.config.agent_id,
                "recipient": "cursor_orchestrator",
                "message_type": "task_response",
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status.value,
                "result": task.result,
                "error": task.error
            }
            
            await self.mqtt_client.publish(
                f"{self.topics['specialist']}task/response",
                json.dumps(response)
            )
            
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
        except Exception as e:
            self.logger.error(f"Error sending task response: {e}")
    
    async def _send_status_update(self):
        """Send status update to orchestrator"""
        try:
            status = {
                "agent_id": self.config.agent_id,
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "active_tasks": len(self.active_tasks),
                "max_concurrent_tasks": self.config.max_concurrent_tasks,
                "capabilities": self.capabilities,
                "model": self.config.model
            }
            
            await self.mqtt_client.publish(
                f"{self.topics['specialist']}status/update",
                json.dumps(status)
            )
            
        except Exception as e:
            self.logger.error(f"Error sending status update: {e}")

# Main execution
async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = SpecialistConfig(
        agent_id="cline_specialist",
        mqtt_broker_url="mqtts://localhost:8883",
        grok_api_key=os.getenv("GROK_API_KEY"),
        model="grok-code-fast-1"
    )
    
    # Create and start specialist
    specialist = ClineSpecialist(config)
    
    try:
        await specialist.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await specialist.stop()

if __name__ == "__main__":
    asyncio.run(main())
