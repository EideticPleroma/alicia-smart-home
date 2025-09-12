# Chapter 18: Event Scheduler

## 🎯 **Event Scheduler Architecture Overview**

The Event Scheduler service provides **comprehensive task scheduling and automation** for the Alicia bus architecture. It manages scheduled events, recurring tasks, and time-based triggers with cron-like functionality, enabling automated system operations and maintenance tasks. This chapter analyzes the Event Scheduler implementation, examining its scheduling capabilities, execution tracking, and automation features.

## ⏰ **Scheduling Architecture**

### **Multi-Type Scheduling Support**

The Event Scheduler implements **comprehensive scheduling types**:

```python
class ScheduleType(Enum):
    ONCE = "once"
    RECURRING = "recurring"
    CRON = "cron"
    INTERVAL = "interval"
```

**Why Multiple Schedule Types?**

1. **Flexibility**: Support different scheduling requirements
2. **Use Cases**: Different tasks need different scheduling patterns
3. **Complexity**: Handle both simple and complex scheduling needs
4. **Integration**: Integrate with existing cron systems
5. **Automation**: Enable various automation scenarios

### **Event Data Structure**

The Event Scheduler uses **sophisticated event data structures**:

```python
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
```

**Event Structure Features:**
- **Flexible Scheduling**: Support multiple schedule types
- **Action Definition**: Define MQTT actions to execute
- **Retry Logic**: Configurable retry mechanisms
- **Status Tracking**: Track event status and execution
- **Metadata**: Support tags and descriptions

### **Execution Tracking**

The Event Scheduler implements **comprehensive execution tracking**:

```python
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
```

**Execution Tracking Features:**
- **Execution Records**: Track each execution attempt
- **Status Management**: Track execution status
- **Result Storage**: Store execution results
- **Error Tracking**: Track execution errors
- **Retry Management**: Track retry attempts

## 📅 **Scheduling Implementation**

### **Cron Scheduling**

The Event Scheduler implements **cron-like scheduling**:

```python
def _parse_cron_schedule(self, cron_expression: str) -> Dict[str, Any]:
    """Parse cron expression into schedule configuration."""
    try:
        # Parse cron expression (minute hour day month weekday)
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression format")
        
        minute, hour, day, month, weekday = parts
        
        # Parse each part
        minute_values = self._parse_cron_part(minute, 0, 59)
        hour_values = self._parse_cron_part(hour, 0, 23)
        day_values = self._parse_cron_part(day, 1, 31)
        month_values = self._parse_cron_part(month, 1, 12)
        weekday_values = self._parse_cron_part(weekday, 0, 6)
        
        return {
            "type": "cron",
            "minute": minute_values,
            "hour": hour_values,
            "day": day_values,
            "month": month_values,
            "weekday": weekday_values
        }
        
    except Exception as e:
        self.logger.error(f"Cron parsing failed: {e}")
        raise
```

**Cron Scheduling Features:**
- **Standard Cron Format**: Support standard cron expressions
- **Field Parsing**: Parse each cron field
- **Range Support**: Support ranges and lists
- **Wildcard Support**: Support wildcard characters
- **Validation**: Validate cron expressions

### **Interval Scheduling**

The Event Scheduler implements **interval-based scheduling**:

```python
def _parse_interval_schedule(self, interval_config: Dict[str, Any]) -> Dict[str, Any]:
    """Parse interval schedule configuration."""
    try:
        interval_type = interval_config.get("type", "seconds")
        interval_value = interval_config.get("value", 60)
        
        if interval_type == "seconds":
            interval_seconds = interval_value
        elif interval_type == "minutes":
            interval_seconds = interval_value * 60
        elif interval_type == "hours":
            interval_seconds = interval_value * 3600
        elif interval_type == "days":
            interval_seconds = interval_value * 86400
        else:
            raise ValueError(f"Unsupported interval type: {interval_type}")
        
        return {
            "type": "interval",
            "interval_seconds": interval_seconds,
            "interval_type": interval_type,
            "interval_value": interval_value
        }
        
    except Exception as e:
        self.logger.error(f"Interval parsing failed: {e}")
        raise
```

**Interval Scheduling Features:**
- **Multiple Units**: Support seconds, minutes, hours, days
- **Flexible Configuration**: Support various interval configurations
- **Validation**: Validate interval values
- **Conversion**: Convert to standard seconds

### **Recurring Task Scheduling**

The Event Scheduler implements **recurring task scheduling**:

```python
def _parse_recurring_schedule(self, recurring_config: Dict[str, Any]) -> Dict[str, Any]:
    """Parse recurring schedule configuration."""
    try:
        frequency = recurring_config.get("frequency", "daily")
        time_of_day = recurring_config.get("time_of_day", "00:00")
        days_of_week = recurring_config.get("days_of_week", [])
        days_of_month = recurring_config.get("days_of_month", [])
        
        # Parse time of day
        hour, minute = map(int, time_of_day.split(":"))
        
        if frequency == "daily":
            return {
                "type": "recurring",
                "frequency": "daily",
                "hour": hour,
                "minute": minute
            }
        elif frequency == "weekly":
            return {
                "type": "recurring",
                "frequency": "weekly",
                "hour": hour,
                "minute": minute,
                "days_of_week": days_of_week
            }
        elif frequency == "monthly":
            return {
                "type": "recurring",
                "frequency": "monthly",
                "hour": hour,
                "minute": minute,
                "days_of_month": days_of_month
            }
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
        
    except Exception as e:
        self.logger.error(f"Recurring parsing failed: {e}")
        raise
```

**Recurring Scheduling Features:**
- **Daily Tasks**: Support daily recurring tasks
- **Weekly Tasks**: Support weekly recurring tasks
- **Monthly Tasks**: Support monthly recurring tasks
- **Time Specification**: Specify exact execution times
- **Day Selection**: Select specific days for execution

## 🚀 **Event Execution Engine**

### **Scheduler Loop**

The Event Scheduler implements **continuous scheduling loop**:

```python
def _scheduler_loop(self):
    """Main scheduler loop for checking and executing events."""
    while True:
        try:
            current_time = time.time()
            
            # Check all scheduled events
            for event_id, event in self.scheduled_events.items():
                if not event.enabled:
                    continue
                
                # Check if event should run
                if self._should_run_event(event, current_time):
                    # Schedule event execution
                    self._schedule_event_execution(event)
            
            # Process active executions
            self._process_active_executions()
            
            time.sleep(self.check_interval)
            
        except Exception as e:
            self.logger.error(f"Scheduler loop failed: {e}")
            time.sleep(self.check_interval)
```

**Scheduler Loop Features:**
- **Continuous Monitoring**: Continuously monitor scheduled events
- **Event Filtering**: Filter enabled events
- **Execution Scheduling**: Schedule event executions
- **Active Processing**: Process active executions
- **Error Handling**: Handle scheduler errors gracefully

### **Event Execution Logic**

The Event Scheduler implements **sophisticated event execution**:

```python
def _should_run_event(self, event: ScheduledEvent, current_time: float) -> bool:
    """Check if event should run at current time."""
    try:
        if event.next_run is None:
            return False
        
        # Check if it's time to run
        if current_time < event.next_run:
            return False
        
        # Check if event is already running
        if event.last_status == EventStatus.RUNNING:
            return False
        
        # Check timeout for running events
        if event.last_status == EventStatus.RUNNING:
            if current_time - event.last_run > event.timeout:
                self.logger.warning(f"Event {event.event_id} timed out")
                event.last_status = EventStatus.FAILED
                return False
        
        return True
        
    except Exception as e:
        self.logger.error(f"Event run check failed: {e}")
        return False
```

**Execution Logic Features:**
- **Time Checking**: Check if it's time to run
- **Status Validation**: Validate event status
- **Timeout Handling**: Handle event timeouts
- **Concurrent Execution**: Prevent concurrent execution
- **Error Handling**: Handle execution logic errors

### **Event Execution Processing**

The Event Scheduler implements **comprehensive execution processing**:

```python
def _schedule_event_execution(self, event: ScheduledEvent):
    """Schedule event for execution."""
    try:
        # Create execution record
        execution = EventExecution(
            execution_id=str(uuid.uuid4()),
            event_id=event.event_id,
            scheduled_time=time.time(),
            status=EventStatus.PENDING
        )
        
        # Store execution
        self.event_executions[execution.execution_id] = execution
        self.active_executions[execution.execution_id] = execution
        
        # Add to event history
        if event.event_id not in self.event_history:
            self.event_history[event.event_id] = []
        self.event_history[event.event_id].append(execution)
        
        # Update event status
        event.last_status = EventStatus.RUNNING
        event.last_run = time.time()
        event.run_count += 1
        
        # Calculate next run time
        event.next_run = self._calculate_next_run_time(event)
        
        # Submit for execution
        self.executor.submit(self._execute_event, execution)
        
        self.logger.info(f"Scheduled execution {execution.execution_id} for event {event.event_id}")
        
    except Exception as e:
        self.logger.error(f"Event execution scheduling failed: {e}")
```

**Execution Processing Features:**
- **Execution Records**: Create execution records
- **Status Updates**: Update event status
- **History Tracking**: Track execution history
- **Next Run Calculation**: Calculate next run time
- **Thread Pool Execution**: Execute in thread pool

## 🔄 **Event Execution Engine**

### **Event Execution**

The Event Scheduler implements **robust event execution**:

```python
def _execute_event(self, execution: EventExecution):
    """Execute a scheduled event."""
    try:
        # Update execution status
        execution.status = EventStatus.RUNNING
        execution.start_time = time.time()
        
        # Get event configuration
        event = self.scheduled_events.get(execution.event_id)
        if not event:
            raise Exception(f"Event {execution.event_id} not found")
        
        # Execute event action
        result = self._execute_event_action(event, execution)
        
        # Update execution result
        execution.status = EventStatus.COMPLETED
        execution.end_time = time.time()
        execution.result = result
        
        # Update event statistics
        event.success_count += 1
        event.last_status = EventStatus.COMPLETED
        
        # Publish execution result
        self._publish_execution_result(execution)
        
        self.logger.info(f"Event {execution.event_id} executed successfully")
        
    except Exception as e:
        # Handle execution failure
        self._handle_execution_failure(execution, str(e))
        
    finally:
        # Remove from active executions
        if execution.execution_id in self.active_executions:
            del self.active_executions[execution.execution_id]
```

**Event Execution Features:**
- **Status Updates**: Update execution status
- **Action Execution**: Execute event actions
- **Result Storage**: Store execution results
- **Statistics Updates**: Update event statistics
- **Event Publishing**: Publish execution results

### **Event Action Execution**

The Event Scheduler implements **flexible event action execution**:

```python
def _execute_event_action(self, event: ScheduledEvent, execution: EventExecution) -> Dict[str, Any]:
    """Execute the action defined in the event."""
    try:
        action = event.action
        action_type = action.get("type", "mqtt_publish")
        
        if action_type == "mqtt_publish":
            return self._execute_mqtt_action(action, execution)
        elif action_type == "http_request":
            return self._execute_http_action(action, execution)
        elif action_type == "service_call":
            return self._execute_service_action(action, execution)
        elif action_type == "script_execution":
            return self._execute_script_action(action, execution)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
        
    except Exception as e:
        self.logger.error(f"Event action execution failed: {e}")
        raise
```

**Action Execution Features:**
- **Multiple Action Types**: Support various action types
- **MQTT Actions**: Execute MQTT message publishing
- **HTTP Actions**: Execute HTTP requests
- **Service Actions**: Execute service calls
- **Script Actions**: Execute scripts

### **MQTT Action Execution**

The Event Scheduler implements **MQTT action execution**:

```python
def _execute_mqtt_action(self, action: Dict[str, Any], execution: EventExecution) -> Dict[str, Any]:
    """Execute MQTT publish action."""
    try:
        topic = action.get("topic")
        message = action.get("message", {})
        qos = action.get("qos", 0)
        retain = action.get("retain", False)
        
        if not topic:
            raise ValueError("MQTT topic is required")
        
        # Add execution metadata to message
        message["execution_id"] = execution.execution_id
        message["event_id"] = execution.event_id
        message["scheduled_time"] = execution.scheduled_time
        message["execution_time"] = time.time()
        
        # Publish message
        self.publish_message(topic, message, qos=qos, retain=retain)
        
        return {
            "action_type": "mqtt_publish",
            "topic": topic,
            "message": message,
            "qos": qos,
            "retain": retain,
            "status": "success"
        }
        
    except Exception as e:
        self.logger.error(f"MQTT action execution failed: {e}")
        raise
```

**MQTT Action Features:**
- **Topic Publishing**: Publish to MQTT topics
- **Message Customization**: Customize message content
- **QoS Support**: Support different QoS levels
- **Retain Support**: Support message retention
- **Metadata Addition**: Add execution metadata

## 🔧 **Error Handling and Retry Logic**

### **Execution Failure Handling**

The Event Scheduler implements **comprehensive failure handling**:

```python
def _handle_execution_failure(self, execution: EventExecution, error_message: str):
    """Handle event execution failure."""
    try:
        # Update execution status
        execution.status = EventStatus.FAILED
        execution.end_time = time.time()
        execution.error_message = error_message
        
        # Get event configuration
        event = self.scheduled_events.get(execution.event_id)
        if not event:
            return
        
        # Update event statistics
        event.failure_count += 1
        event.last_status = EventStatus.FAILED
        
        # Check if retry is needed
        if execution.retry_count < event.max_retries:
            # Schedule retry
            self._schedule_retry(event, execution)
        else:
            # Max retries exceeded
            self.logger.error(f"Event {execution.event_id} failed after {event.max_retries} retries")
            self._publish_execution_failure(execution)
        
    except Exception as e:
        self.logger.error(f"Execution failure handling failed: {e}")
```

**Failure Handling Features:**
- **Status Updates**: Update execution and event status
- **Statistics Updates**: Update failure statistics
- **Retry Logic**: Implement retry logic
- **Max Retry Handling**: Handle max retry exceeded
- **Event Publishing**: Publish failure events

### **Retry Scheduling**

The Event Scheduler implements **intelligent retry scheduling**:

```python
def _schedule_retry(self, event: ScheduledEvent, failed_execution: EventExecution):
    """Schedule retry for failed execution."""
    try:
        # Calculate retry delay
        retry_delay = event.retry_delay * (2 ** failed_execution.retry_count)  # Exponential backoff
        
        # Create retry execution
        retry_execution = EventExecution(
            execution_id=str(uuid.uuid4()),
            event_id=event.event_id,
            scheduled_time=time.time() + retry_delay,
            status=EventStatus.PENDING,
            retry_count=failed_execution.retry_count + 1
        )
        
        # Store retry execution
        self.event_executions[retry_execution.execution_id] = retry_execution
        
        # Add to event history
        if event.event_id not in self.event_history:
            self.event_history[event.event_id] = []
        self.event_history[event.event_id].append(retry_execution)
        
        # Schedule retry
        self.executor.submit(self._execute_retry, retry_execution, retry_delay)
        
        self.logger.info(f"Scheduled retry {retry_execution.execution_id} for event {event.event_id} in {retry_delay}s")
        
    except Exception as e:
        self.logger.error(f"Retry scheduling failed: {e}")
```

**Retry Scheduling Features:**
- **Exponential Backoff**: Implement exponential backoff
- **Retry Tracking**: Track retry attempts
- **Delay Calculation**: Calculate retry delays
- **Retry Execution**: Execute retry attempts
- **History Tracking**: Track retry history

## 📡 **MQTT Integration and Event Publishing**

### **Scheduler Event Publishing**

The Event Scheduler publishes **comprehensive scheduler events**:

```python
def _publish_scheduler_event(self, event_type: str, event_data: Dict[str, Any]):
    """Publish scheduler-related events."""
    try:
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": time.time(),
            "source": "event_scheduler"
        }
        
        # Publish to general scheduler topic
        self.publish_message("alicia/scheduler/events", event)
        
        # Publish to specific event topic
        self.publish_message(f"alicia/scheduler/{event_type}", event)
        
    except Exception as e:
        self.logger.error(f"Failed to publish scheduler event: {e}")
```

**Event Publishing Features:**
- **Execution Events**: Publish execution events
- **Schedule Events**: Publish schedule events
- **Failure Events**: Publish failure events
- **Retry Events**: Publish retry events

### **Execution Result Publishing**

The Event Scheduler publishes **execution results**:

```python
def _publish_execution_result(self, execution: EventExecution):
    """Publish execution result."""
    try:
        result_event = {
            "execution_id": execution.execution_id,
            "event_id": execution.event_id,
            "status": execution.status.value,
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "duration": execution.end_time - execution.start_time if execution.end_time and execution.start_time else 0,
            "result": execution.result,
            "timestamp": time.time()
        }
        
        self.publish_message("alicia/scheduler/execution_results", result_event)
        
    except Exception as e:
        self.logger.error(f"Execution result publishing failed: {e}")
```

**Result Publishing Features:**
- **Execution Details**: Publish execution details
- **Duration Calculation**: Calculate execution duration
- **Status Information**: Publish execution status
- **Result Data**: Publish execution results

## 🚀 **Performance Optimization**

### **Execution Optimization**

The Event Scheduler implements **execution optimization**:

```python
def _optimize_execution_performance(self):
    """Optimize execution performance."""
    try:
        # Clean up completed executions
        completed_executions = [
            eid for eid, execution in self.active_executions.items()
            if execution.status in [EventStatus.COMPLETED, EventStatus.FAILED]
        ]
        
        for execution_id in completed_executions:
            del self.active_executions[execution_id]
        
        # Limit active executions
        if len(self.active_executions) > self.max_concurrent_executions:
            # Cancel oldest pending executions
            pending_executions = [
                (eid, execution) for eid, execution in self.active_executions.items()
                if execution.status == EventStatus.PENDING
            ]
            pending_executions.sort(key=lambda x: x[1].scheduled_time)
            
            for execution_id, _ in pending_executions[:len(self.active_executions) - self.max_concurrent_executions]:
                del self.active_executions[execution_id]
        
    except Exception as e:
        self.logger.error(f"Execution optimization failed: {e}")
```

**Execution Optimization Features:**
- **Cleanup**: Clean up completed executions
- **Concurrency Limits**: Limit concurrent executions
- **Resource Management**: Manage execution resources
- **Performance Improvement**: Optimize execution performance

### **History Management**

The Event Scheduler implements **efficient history management**:

```python
def _cleanup_loop(self):
    """Background loop for cleaning up old data."""
    while True:
        try:
            current_time = time.time()
            
            # Clean up old execution history
            for event_id in list(self.event_history.keys()):
                executions = self.event_history[event_id]
                
                # Remove executions older than retention period
                executions[:] = [
                    e for e in executions 
                    if current_time - e.scheduled_time < self.retention_period
                ]
                
                # Limit executions per event
                if len(executions) > self.max_history_per_event:
                    executions[:] = executions[-self.max_history_per_event:]
                
                # Remove empty histories
                if not executions:
                    del self.event_history[event_id]
            
            time.sleep(self.cleanup_interval)
            
        except Exception as e:
            self.logger.error(f"Cleanup loop failed: {e}")
            time.sleep(self.cleanup_interval)
```

**History Management Features:**
- **Retention Management**: Remove old execution history
- **Size Limits**: Limit history per event
- **Cleanup**: Clean up empty histories
- **Performance Improvement**: Optimize history management

## 🔧 **Error Handling and Recovery**

### **Scheduler Error Handling**

The Event Scheduler implements **comprehensive error handling**:

```python
def _handle_scheduler_error(self, error: Exception, event_id: str = None):
    """Handle scheduler errors."""
    self.logger.error(f"Scheduler error: {error}")
    
    # Publish error event
    error_event = {
        "error": str(error),
        "event_id": event_id,
        "timestamp": time.time()
    }
    
    self.publish_message("alicia/scheduler/errors", error_event)
    
    # Attempt recovery
    if "execution" in str(error).lower():
        self._recover_execution_system()
    elif "scheduling" in str(error).lower():
        self._recover_scheduling_system()
```

**Error Handling Features:**
- **Error Classification**: Classify errors by type
- **Error Publishing**: Publish error events
- **Recovery Strategies**: Implement recovery strategies
- **System Recovery**: Recover scheduler system

### **Scheduler Recovery**

The Event Scheduler implements **automatic recovery**:

```python
def _recover_scheduling_system(self):
    """Recover scheduling system from errors."""
    try:
        # Reset scheduler state
        self.active_executions.clear()
        
        # Recalculate next run times
        for event in self.scheduled_events.values():
            if event.enabled:
                event.next_run = self._calculate_next_run_time(event)
        
        # Publish recovery event
        self.publish_message("alicia/scheduler/recovery", {
            "status": "recovered",
            "timestamp": time.time()
        })
        
        self.logger.info("Scheduling system recovered successfully")
        
    except Exception as e:
        self.logger.error(f"Scheduler recovery failed: {e}")
```

**Recovery Features:**
- **State Reset**: Reset scheduler state
- **Next Run Calculation**: Recalculate next run times
- **Event Publishing**: Publish recovery events
- **Error Handling**: Handle recovery errors gracefully

## 🚀 **Next Steps**

The Event Scheduler provides comprehensive task scheduling and automation. In the next chapter, we'll examine the **Service Orchestrator** that provides centralized service management, including:

1. **Service Lifecycle Management** - Start, stop, and manage services
2. **Dependency Management** - Manage service dependencies
3. **Service Coordination** - Coordinate service operations
4. **Health Monitoring** - Monitor service health
5. **Scaling Operations** - Scale services up and down

The Event Scheduler demonstrates how **sophisticated task scheduling** can be implemented in a microservices architecture, providing automation capabilities that enable self-managing, self-healing systems.

---

**The Event Scheduler in Alicia represents a mature, production-ready approach to task scheduling and automation. Every design decision is intentional, every scheduling pattern serves a purpose, and every optimization contributes to the greater goal of creating an intelligent, automated system that can manage itself.**
