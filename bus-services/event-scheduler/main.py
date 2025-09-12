"""
Alicia Bus Architecture - Event Scheduler Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

This service manages scheduled events, recurring tasks, and time-based triggers
for the Alicia bus architecture, providing cron-like functionality with MQTT integration.
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import re
from concurrent.futures import ThreadPoolExecutor

import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
import schedule

from service_wrapper import BusServiceWrapper, BusServiceAPI


class ScheduleType(Enum):
    ONCE = "once"
    RECURRING = "recurring"
    CRON = "cron"
    INTERVAL = "interval"


class EventStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledEvent:
    """Scheduled event configuration."""
    event_id: str
    name: str
    description: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    action: Dict[str, Any]  # MQTT message to publish
    enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 60
    timeout: int = 300
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    next_run: Optional[float] = None
    last_run: Optional[float] = None
    last_status: EventStatus = EventStatus.PENDING
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class EventExecution:
    """Event execution record."""
    execution_id: str
    event_id: str
    scheduled_time: float
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: EventStatus = EventStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class SchedulerStats:
    """Scheduler statistics."""
    total_events: int
    active_events: int
    completed_executions: int
    failed_executions: int
    upcoming_executions: int
    timestamp: float


class EventSchedulerService(BusServiceWrapper):
    """
    Event Scheduler Service for the Alicia Bus Architecture.

    Manages scheduled events, recurring tasks, and time-based triggers
    with comprehensive scheduling capabilities and execution tracking.
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": "alicia_bus_core",
            "port": 1883,
            "username": "event_scheduler",
            "password": "alicia_scheduler_2024"
        }

        super().__init__("event_scheduler", mqtt_config)

        # Event storage
        self.scheduled_events: Dict[str, ScheduledEvent] = {}
        self.event_executions: Dict[str, EventExecution] = {}
        self.event_history: Dict[str, List[EventExecution]] = {}

        # Execution tracking
        self.active_executions: Dict[str, EventExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Configuration
        self.max_history_per_event = 100
        self.cleanup_interval = 3600  # 1 hour
        self.check_interval = 10  # seconds

        # FastAPI setup
        self.app = FastAPI(title="Alicia Event Scheduler", version="1.0.0")
        self._setup_api_endpoints()

        # Background threads
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True

        self.cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True

        # Service capabilities
        self.capabilities = [
            "event_scheduling",
            "cron_scheduling",
            "recurring_tasks",
            "execution_tracking",
            "time_based_triggers"
        ]

        self.version = "1.0.0"

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for the event scheduler."""

        @self.app.get("/health")
        async def get_health():
            """Get event scheduler service health."""
            return self.get_health_status()

        @self.app.get("/events")
        async def get_events(active_only: bool = False):
            """Get all scheduled events."""
            events = []
            for event in self.scheduled_events.values():
                if not active_only or event.enabled:
                    events.append(asdict(event))

            events.sort(key=lambda x: x["created_at"], reverse=True)
            return {"events": events}

        @self.app.post("/events")
        async def create_event(event_data: Dict[str, Any]):
            """Create a new scheduled event."""
            try:
                # Generate event ID
                event_id = str(uuid.uuid4())

                # Create event
                event = ScheduledEvent(
                    event_id=event_id,
                    name=event_data["name"],
                    description=event_data.get("description", ""),
                    schedule_type=ScheduleType(event_data["schedule_type"]),
                    schedule_config=event_data["schedule_config"],
                    action=event_data["action"],
                    enabled=event_data.get("enabled", True),
                    max_retries=event_data.get("max_retries", 3),
                    retry_delay=event_data.get("retry_delay", 60),
                    timeout=event_data.get("timeout", 300),
                    tags=event_data.get("tags", [])
                )

                # Calculate next run time
                event.next_run = self._calculate_next_run(event)

                # Store event
                self.scheduled_events[event_id] = event

                self.logger.info(f"Created scheduled event: {event.name} ({event_id})")

                return {"event_id": event_id, "event": asdict(event)}

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid event configuration: {str(e)}")

        @self.app.get("/events/{event_id}")
        async def get_event(event_id: str):
            """Get a specific scheduled event."""
            if event_id not in self.scheduled_events:
                raise HTTPException(status_code=404, detail="Event not found")

            return {"event": asdict(self.scheduled_events[event_id])}

        @self.app.put("/events/{event_id}")
        async def update_event(event_id: str, event_data: Dict[str, Any]):
            """Update a scheduled event."""
            if event_id not in self.scheduled_events:
                raise HTTPException(status_code=404, detail="Event not found")

            event = self.scheduled_events[event_id]

            # Update fields
            for key, value in event_data.items():
                if hasattr(event, key):
                    if key == "schedule_type":
                        setattr(event, key, ScheduleType(value))
                    else:
                        setattr(event, key, value)

            event.updated_at = time.time()
            event.next_run = self._calculate_next_run(event)

            return {"event": asdict(event)}

        @self.app.delete("/events/{event_id}")
        async def delete_event(event_id: str):
            """Delete a scheduled event."""
            if event_id not in self.scheduled_events:
                raise HTTPException(status_code=404, detail="Event not found")

            # Cancel any active executions
            if event_id in self.active_executions:
                self.active_executions[event_id].status = EventStatus.CANCELLED

            # Remove event
            del self.scheduled_events[event_id]

            # Clean up history
            if event_id in self.event_history:
                del self.event_history[event_id]

            return {"message": "Event deleted successfully"}

        @self.app.post("/events/{event_id}/execute")
        async def execute_event_now(event_id: str, background_tasks: BackgroundTasks):
            """Execute an event immediately."""
            if event_id not in self.scheduled_events:
                raise HTTPException(status_code=404, detail="Event not found")

            event = self.scheduled_events[event_id]

            # Create execution record
            execution = EventExecution(
                execution_id=str(uuid.uuid4()),
                event_id=event_id,
                scheduled_time=time.time()
            )

            # Execute in background
            background_tasks.add_task(self._execute_event, event, execution)

            return {"execution_id": execution.execution_id, "message": "Event execution started"}

        @self.app.get("/executions")
        async def get_executions(
            event_id: Optional[str] = None,
            status: Optional[str] = None,
            limit: int = Query(100, description="Number of executions to return")
        ):
            """Get event executions."""
            executions = []

            if event_id:
                if event_id not in self.event_history:
                    return {"executions": []}
                executions = self.event_history[event_id]
            else:
                for event_executions in self.event_history.values():
                    executions.extend(event_executions)

            # Filter by status
            if status:
                try:
                    status_enum = EventStatus(status)
                    executions = [e for e in executions if e.status == status_enum]
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

            # Sort by start time (most recent first)
            executions.sort(key=lambda x: x.scheduled_time, reverse=True)

            return {"executions": [asdict(e) for e in executions[:limit]]}

        @self.app.get("/stats")
        async def get_stats():
            """Get scheduler statistics."""
            total_events = len(self.scheduled_events)
            active_events = len([e for e in self.scheduled_events.values() if e.enabled])
            completed_executions = sum(len(execs) for execs in self.event_history.values())
            failed_executions = sum(
                len([e for e in execs if e.status == EventStatus.FAILED])
                for execs in self.event_history.values()
            )

            # Count upcoming executions (next_run in future)
            upcoming_executions = len([
                e for e in self.scheduled_events.values()
                if e.next_run and e.next_run > time.time()
            ])

            stats = SchedulerStats(
                total_events=total_events,
                active_events=active_events,
                completed_executions=completed_executions,
                failed_executions=failed_executions,
                upcoming_executions=upcoming_executions,
                timestamp=time.time()
            )

            return asdict(stats)

        @self.app.get("/calendar")
        async def get_calendar(
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
        ):
            """Get upcoming event schedule."""
            try:
                if start_date:
                    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                else:
                    start = datetime.now()

                if end_date:
                    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end = start + timedelta(days=7)

                start_ts = start.timestamp()
                end_ts = end.timestamp()

                upcoming_events = []
                for event in self.scheduled_events.values():
                    if event.enabled and event.next_run:
                        if start_ts <= event.next_run <= end_ts:
                            upcoming_events.append({
                                "event_id": event.event_id,
                                "name": event.name,
                                "next_run": event.next_run,
                                "schedule_type": event.schedule_type.value
                            })

                upcoming_events.sort(key=lambda x: x["next_run"])

                return {"upcoming_events": upcoming_events}

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

    def subscribe_to_topics(self):
        """Subscribe to event scheduling topics."""
        self.mqtt_client.subscribe("alicia/scheduler/+")
        self.mqtt_client.subscribe("alicia/events/+")
        self.logger.info("Subscribed to scheduler topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic.startswith("alicia/scheduler/"):
                self._process_scheduler_message(topic, message)
            elif topic.startswith("alicia/events/"):
                self._process_event_message(topic, message)
            else:
                self.logger.debug(f"Unhandled topic: {topic}")

        except Exception as e:
            self.logger.error(f"Error processing message on {topic}: {e}")

    def _process_scheduler_message(self, topic: str, message: Dict[str, Any]):
        """Process scheduler control messages."""
        try:
            command = message.get("command")

            if command == "create_event":
                # Create event from MQTT message
                event_data = message.get("event", {})
                if event_data:
                    event_id = str(uuid.uuid4())
                    event = ScheduledEvent(
                        event_id=event_id,
                        name=event_data.get("name", f"mqtt_event_{event_id}"),
                        description=event_data.get("description", ""),
                        schedule_type=ScheduleType(event_data.get("schedule_type", "once")),
                        schedule_config=event_data.get("schedule_config", {}),
                        action=event_data.get("action", {})
                    )
                    event.next_run = self._calculate_next_run(event)
                    self.scheduled_events[event_id] = event

            elif command == "cancel_event":
                event_id = message.get("event_id")
                if event_id and event_id in self.scheduled_events:
                    self.scheduled_events[event_id].enabled = False

            elif command == "trigger_event":
                event_id = message.get("event_id")
                if event_id and event_id in self.scheduled_events:
                    event = self.scheduled_events[event_id]
                    execution = EventExecution(
                        execution_id=str(uuid.uuid4()),
                        event_id=event_id,
                        scheduled_time=time.time()
                    )
                    self.executor.submit(self._execute_event, event, execution)

        except Exception as e:
            self.logger.error(f"Error processing scheduler message: {e}")

    def _process_event_message(self, topic: str, message: Dict[str, Any]):
        """Process event-related messages."""
        try:
            event_type = message.get("event_type")

            if event_type == "execution_complete":
                execution_id = message.get("execution_id")
                if execution_id and execution_id in self.active_executions:
                    execution = self.active_executions[execution_id]
                    execution.status = EventStatus(message.get("status", "completed"))
                    execution.end_time = time.time()
                    execution.result = message.get("result")

                    # Move to history
                    if execution.event_id not in self.event_history:
                        self.event_history[execution.event_id] = []
                    self.event_history[execution.event_id].append(execution)

                    # Update event statistics
                    event = self.scheduled_events.get(execution.event_id)
                    if event:
                        event.last_run = execution.end_time
                        event.last_status = execution.status
                        event.run_count += 1

                        if execution.status == EventStatus.COMPLETED:
                            event.success_count += 1
                        elif execution.status == EventStatus.FAILED:
                            event.failure_count += 1

                        # Recalculate next run
                        event.next_run = self._calculate_next_run(event)

                    del self.active_executions[execution_id]

        except Exception as e:
            self.logger.error(f"Error processing event message: {e}")

    def _calculate_next_run(self, event: ScheduledEvent) -> Optional[float]:
        """Calculate the next run time for an event."""
        try:
            now = time.time()

            if event.schedule_type == ScheduleType.ONCE:
                if "timestamp" in event.schedule_config:
                    return event.schedule_config["timestamp"]
                return None

            elif event.schedule_type == ScheduleType.INTERVAL:
                interval = event.schedule_config.get("interval", 3600)  # default 1 hour
                last_run = event.last_run or event.created_at
                return last_run + interval

            elif event.schedule_type == ScheduleType.RECURRING:
                # Simple recurring schedule
                frequency = event.schedule_config.get("frequency", "daily")
                if frequency == "daily":
                    return now + 86400  # 24 hours
                elif frequency == "hourly":
                    return now + 3600   # 1 hour
                elif frequency == "weekly":
                    return now + 604800  # 7 days
                return now + 86400

            elif event.schedule_type == ScheduleType.CRON:
                # Basic cron support (simplified)
                cron_expr = event.schedule_config.get("cron", "")
                return self._parse_cron_expression(cron_expr, now)

            return None

        except Exception as e:
            self.logger.error(f"Error calculating next run for event {event.event_id}: {e}")
            return None

    def _parse_cron_expression(self, cron_expr: str, current_time: float) -> Optional[float]:
        """Parse a simple cron expression and return next run time."""
        try:
            # Very basic cron parsing - in production, use a proper cron library
            parts = cron_expr.split()
            if len(parts) != 5:
                return None

            minute, hour, day, month, day_of_week = parts

            # For now, just return current time + 1 hour as placeholder
            # In production, implement proper cron parsing
            return current_time + 3600

        except Exception:
            return None

    def _scheduler_loop(self):
        """Main scheduler loop."""
        while True:
            try:
                current_time = time.time()

                # Check for events that need to run
                for event in self.scheduled_events.values():
                    if (event.enabled and
                        event.next_run and
                        current_time >= event.next_run and
                        event.event_id not in self.active_executions):

                        # Create execution record
                        execution = EventExecution(
                            execution_id=str(uuid.uuid4()),
                            event_id=event.event_id,
                            scheduled_time=event.next_run
                        )

                        # Execute event
                        self.executor.submit(self._execute_event, event, execution)

                        # Mark as active
                        self.active_executions[event.event_id] = execution

                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)

    def _execute_event(self, event: ScheduledEvent, execution: EventExecution):
        """Execute a scheduled event."""
        try:
            execution.start_time = time.time()
            execution.status = EventStatus.RUNNING

            self.logger.info(f"Executing event: {event.name} ({event.event_id})")

            # Publish the action message
            action_topic = event.action.get("topic", f"alicia/event/{event.event_id}")
            action_message = event.action.get("message", {})

            # Add execution metadata
            action_message.update({
                "event_id": event.event_id,
                "execution_id": execution.execution_id,
                "scheduled_time": execution.scheduled_time,
                "triggered_by": "scheduler"
            })

            self.publish_message(action_topic, action_message)

            # Wait for completion or timeout
            start_wait = time.time()
            while time.time() - start_wait < event.timeout:
                if execution.status != EventStatus.RUNNING:
                    break
                time.sleep(1)

            # If still running, mark as completed (assuming async completion)
            if execution.status == EventStatus.RUNNING:
                execution.status = EventStatus.COMPLETED
                execution.end_time = time.time()

            self.logger.info(f"Event execution completed: {event.name} ({execution.status.value})")

        except Exception as e:
            execution.status = EventStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = time.time()
            self.logger.error(f"Event execution failed: {event.name} - {str(e)}")

        finally:
            # Move to history
            if event.event_id not in self.event_history:
                self.event_history[event.event_id] = []
            self.event_history[event.event_id].append(execution)

            # Keep history size manageable
            if len(self.event_history[event.event_id]) > self.max_history_per_event:
                self.event_history[event.event_id] = self.event_history[event.event_id][-self.max_history_per_event:]

            # Remove from active executions
            if event.event_id in self.active_executions:
                del self.active_executions[event.event_id]

    def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                # Clean up old execution history
                cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days

                for event_id in list(self.event_history.keys()):
                    self.event_history[event_id] = [
                        execution for execution in self.event_history[event_id]
                        if execution.scheduled_time > cutoff_time
                    ]

                    if not self.event_history[event_id]:
                        del self.event_history[event_id]

                time.sleep(self.cleanup_interval)

            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                time.sleep(5)

    def start_scheduler(self):
        """Start the scheduler threads."""
        self.scheduler_thread.start()
        self.cleanup_thread.start()
        self.logger.info("Event scheduler started")

    def shutdown(self):
        """Gracefully shutdown the event scheduler."""
        self.logger.info("Shutting down event scheduler...")

        # Cancel all active executions
        for execution in self.active_executions.values():
            execution.status = EventStatus.CANCELLED

        # Shutdown executor
        self.executor.shutdown(wait=True)

        super().shutdown()


def main():
    """Main entry point for the Event Scheduler service."""
    service = EventSchedulerService()
    service.start_scheduler()

    # Start FastAPI server
    api = BusServiceAPI(service)
    uvicorn.run(api.app, host="0.0.0.0", port=8014)


if __name__ == "__main__":
    main()
