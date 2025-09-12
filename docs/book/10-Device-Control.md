# Chapter 10: Device Manager & Control Services

## 🎯 **Device Management Architecture Overview**

The Device Manager serves as the **centralized control hub** for all smart home devices in Alicia's ecosystem. It provides a unified interface for device control, capability abstraction, and command routing across different device types and protocols. This chapter analyzes the Device Manager implementation, examining its device-agnostic architecture, command routing system, and integration patterns.

## 🏠 **Device-Agnostic Architecture**

### **Unified Device Interface**

The Device Manager implements a **device-agnostic architecture** that abstracts device-specific details:

```python
class DeviceManager(BusServiceWrapper):
    """
    Device Manager service for the Alicia bus architecture.
    
    Provides centralized device management and control:
    - Generic device command routing
    - Device capability abstraction
    - Status monitoring and aggregation
    - Device discovery coordination
    - Command execution and response handling
    """
```

**Why Device-Agnostic Architecture?**

1. **Protocol Independence**: Support multiple device protocols (Zigbee, Z-Wave, WiFi, etc.)
2. **Vendor Neutrality**: Work with devices from different manufacturers
3. **Scalability**: Easily add new device types without changing core logic
4. **Maintainability**: Centralized device management logic
5. **Consistency**: Uniform interface for all device operations

### **Device Capability Abstraction**

The Device Manager implements **sophisticated capability abstraction**:

```python
def __init__(self):
    # Device management
    self.managed_devices: Dict[str, Dict[str, Any]] = {}
    self.device_capabilities: Dict[str, Dict[str, Any]] = {}
    self.pending_commands: Dict[str, Dict[str, Any]] = {}
    self.command_queue: asyncio.Queue = asyncio.Queue()
```

**Capability Abstraction Features:**
- **Device Registry**: Track all managed devices and their capabilities
- **Command Mapping**: Map generic commands to device-specific actions
- **Status Aggregation**: Aggregate status from multiple devices
- **Capability Discovery**: Automatically discover device capabilities

### **Command Routing System**

The Device Manager implements **intelligent command routing**:

```python
async def _queue_command(self, device_ids: List[str], command: str, parameters: Dict[str, Any], priority: str = "normal") -> str:
    """Queue command for execution."""
    command_id = str(uuid.uuid4())
    
    command_data = {
        "command_id": command_id,
        "device_ids": device_ids,
        "command": command,
        "parameters": parameters,
        "priority": priority,
        "status": "queued",
        "created_at": time.time(),
        "retry_count": 0,
        "max_retries": 3
    }
    
    # Add to command queue
    await self.command_queue.put(command_data)
    
    # Store in pending commands
    self.pending_commands[command_id] = command_data
    
    return command_id
```

**Command Routing Features:**
- **Priority Queuing**: Execute high-priority commands first
- **Batch Processing**: Process multiple commands efficiently
- **Retry Logic**: Automatic retry for failed commands
- **Status Tracking**: Track command execution status

## 🔄 **Asynchronous Command Processing**

### **Queue-Based Command Processing**

The Device Manager uses **asynchronous queue processing** for scalability:

```python
async def _process_command_queue(self):
    """Process commands from the queue."""
    while True:
        try:
            # Get command from queue
            command_data = await self.command_queue.get()
            
            if command_data is None:
                break
            
            # Process command
            await self._execute_command(command_data)
            
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            await asyncio.sleep(1)
```

**Queue Processing Benefits:**
- **Concurrency**: Process multiple commands simultaneously
- **Resource Management**: Control processing load
- **Fault Tolerance**: Isolate command processing errors
- **Performance**: Optimize resource utilization

### **Command Execution Engine**

The Device Manager implements **sophisticated command execution**:

```python
async def _execute_command(self, command_data: Dict[str, Any]):
    """Execute a queued command."""
    command_id = command_data["command_id"]
    device_ids = command_data["device_ids"]
    command = command_data["command"]
    parameters = command_data["parameters"]
    
    try:
        # Update command status
        command_data["status"] = "executing"
        command_data["started_at"] = time.time()
        
        # Execute command on each device
        results = []
        for device_id in device_ids:
            if device_id in self.managed_devices:
                result = await self._execute_device_command(device_id, command, parameters)
                results.append(result)
            else:
                results.append({
                    "device_id": device_id,
                    "status": "error",
                    "error": "Device not found"
                })
        
        # Update command status
        command_data["status"] = "completed"
        command_data["completed_at"] = time.time()
        command_data["results"] = results
        
        # Remove from pending commands
        if command_id in self.pending_commands:
            del self.pending_commands[command_id]
        
        # Add to command history
        self.command_history.append(command_data)
        
        # Publish command completion
        self._publish_command_completion(command_data)
        
    except Exception as e:
        # Handle command execution error
        command_data["status"] = "error"
        command_data["error"] = str(e)
        command_data["failed_at"] = time.time()
        
        # Retry logic
        if command_data["retry_count"] < command_data["max_retries"]:
            command_data["retry_count"] += 1
            command_data["status"] = "queued"
            await self.command_queue.put(command_data)
        else:
            self.logger.error(f"Command {command_id} failed after {command_data['max_retries']} retries")
            self._publish_command_error(command_data)
```

**Command Execution Features:**
- **Multi-Device Support**: Execute commands on multiple devices
- **Error Handling**: Comprehensive error handling and recovery
- **Retry Logic**: Automatic retry for failed commands
- **Status Tracking**: Track command execution status
- **Result Aggregation**: Aggregate results from multiple devices

## 🎛️ **Device-Specific Command Implementation**

### **Capability-Based Command Routing**

The Device Manager implements **capability-based command routing**:

```python
async def _execute_device_command(self, device_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute command on specific device."""
    device_info = self.managed_devices.get(device_id)
    if not device_info:
        return {"device_id": device_id, "status": "error", "error": "Device not found"}
    
    device_type = device_info.get("device_type")
    capabilities = device_info.get("capabilities", {})
    
    # Check if device supports the command
    if command not in capabilities:
        return {
            "device_id": device_id,
            "status": "error",
            "error": f"Device does not support command: {command}"
        }
    
    # Route command based on device type
    if device_type == "light":
        return await self._execute_light_command(device_id, command, parameters)
    elif device_type == "speaker":
        return await self._execute_speaker_command(device_id, command, parameters)
    elif device_type == "thermostat":
        return await self._execute_thermostat_command(device_id, command, parameters)
    elif device_type == "switch":
        return await self._execute_switch_command(device_id, command, parameters)
    else:
        return await self._execute_generic_command(device_id, command, parameters)
```

**Capability-Based Routing Features:**
- **Command Validation**: Validate commands against device capabilities
- **Type-Specific Handling**: Handle different device types appropriately
- **Generic Fallback**: Fallback to generic command handling
- **Error Reporting**: Report unsupported commands clearly

### **Device Type-Specific Implementations**

The Device Manager implements **device type-specific command handling**:

```python
async def _execute_light_command(self, device_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute light-specific commands."""
    try:
        if command == "turn_on":
            brightness = parameters.get("brightness", 255)
            color = parameters.get("color", {"r": 255, "g": 255, "b": 255})
            
            # Send command to light device
            result = await self._send_light_command(device_id, "turn_on", {
                "brightness": brightness,
                "color": color
            })
            
            return {
                "device_id": device_id,
                "command": command,
                "status": "success",
                "result": result
            }
        
        elif command == "turn_off":
            result = await self._send_light_command(device_id, "turn_off", {})
            
            return {
                "device_id": device_id,
                "command": command,
                "status": "success",
                "result": result
            }
        
        elif command == "set_brightness":
            brightness = parameters.get("brightness", 128)
            result = await self._send_light_command(device_id, "set_brightness", {
                "brightness": brightness
            })
            
            return {
                "device_id": device_id,
                "command": command,
                "status": "success",
                "result": result
            }
        
        else:
            return {
                "device_id": device_id,
                "command": command,
                "status": "error",
                "error": f"Unsupported light command: {command}"
            }
            
    except Exception as e:
        return {
            "device_id": device_id,
            "command": command,
            "status": "error",
            "error": str(e)
        }
```

**Device-Specific Features:**
- **Command Mapping**: Map generic commands to device-specific actions
- **Parameter Handling**: Handle device-specific parameters
- **Protocol Translation**: Translate commands to device protocols
- **Error Handling**: Device-specific error handling

## 📡 **MQTT Integration and Device Communication**

### **Device Command Publishing**

The Device Manager publishes **standardized device commands**:

```python
async def _send_light_command(self, device_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Send command to light device via MQTT."""
    try:
        # Create device command message
        command_message = {
            "device_id": device_id,
            "command": command,
            "parameters": parameters,
            "timestamp": time.time(),
            "source": "device_manager"
        }
        
        # Publish to device-specific topic
        topic = f"alicia/devices/{device_id}/command"
        self.publish_message(topic, command_message)
        
        # Wait for device response
        response = await self._wait_for_device_response(device_id, command, timeout=10)
        
        return response
        
    except Exception as e:
        self.logger.error(f"Failed to send light command: {e}")
        raise
```

**Device Communication Features:**
- **Topic-Based Routing**: Use device-specific MQTT topics
- **Response Waiting**: Wait for device responses
- **Timeout Handling**: Handle device response timeouts
- **Error Propagation**: Propagate device errors appropriately

### **Device Status Monitoring**

The Device Manager implements **comprehensive device status monitoring**:

```python
async def _monitor_device_status(self):
    """Monitor device status and health."""
    while True:
        try:
            # Check device health
            for device_id, device_info in self.managed_devices.items():
                await self._check_device_health(device_id, device_info)
            
            # Update device status
            await self._update_device_status()
            
            # Clean up old command history
            await self._cleanup_command_history()
            
            await asyncio.sleep(self.status_update_interval)
            
        except Exception as e:
            self.logger.error(f"Device status monitoring error: {e}")
            await asyncio.sleep(60)
```

**Status Monitoring Features:**
- **Health Checks**: Regular health checks for all devices
- **Status Updates**: Real-time status updates
- **History Cleanup**: Clean up old command history
- **Error Detection**: Detect and report device errors

## 🔄 **Device Discovery and Registration**

### **Automatic Device Discovery**

The Device Manager implements **automatic device discovery**:

```python
def process_message(self, topic: str, message: Dict[str, Any]):
    """Process incoming MQTT messages."""
    try:
        if topic.startswith("alicia/devices/discovery/"):
            if topic.endswith("/found"):
                self._handle_device_discovery(message)
            elif topic.endswith("/lost"):
                self._handle_device_loss(message)
        
        elif topic.startswith("alicia/devices/") and topic.endswith("/status"):
            self._handle_device_status_update(topic, message)
        
        elif topic.startswith("alicia/devices/") and topic.endswith("/response"):
            self._handle_device_response(topic, message)
        
    except Exception as e:
        self.logger.error(f"Message processing error: {e}")
```

**Device Discovery Features:**
- **Automatic Registration**: Automatically register discovered devices
- **Capability Detection**: Detect device capabilities
- **Status Tracking**: Track device availability
- **Loss Detection**: Detect when devices go offline

### **Device Registration Process**

The Device Manager implements **comprehensive device registration**:

```python
def _handle_device_discovery(self, message: Dict[str, Any]):
    """Handle device discovery message."""
    try:
        device_info = message.get("payload", {})
        device_id = device_info.get("device_id")
        
        if not device_id:
            self.logger.warning("Device discovery message missing device_id")
            return
        
        # Register device
        self.managed_devices[device_id] = {
            "device_id": device_id,
            "device_type": device_info.get("device_type"),
            "capabilities": set(device_info.get("capabilities", [])),
            "status": "online",
            "last_seen": time.time(),
            "metadata": device_info.get("metadata", {}),
            "discovered_at": time.time()
        }
        
        # Update device capabilities
        self.device_capabilities[device_id] = device_info.get("capabilities", {})
        
        self.logger.info(f"Registered device: {device_id} ({device_info.get('device_type')})")
        
        # Publish device registration event
        self.publish_message("alicia/devices/registry/registered", {
            "device_id": device_id,
            "device_type": device_info.get("device_type"),
            "capabilities": device_info.get("capabilities", []),
            "timestamp": time.time()
        })
        
    except Exception as e:
        self.logger.error(f"Device discovery handling failed: {e}")
```

**Device Registration Features:**
- **Capability Mapping**: Map device capabilities
- **Status Initialization**: Initialize device status
- **Event Publishing**: Publish registration events
- **Metadata Storage**: Store device metadata

## 🚀 **Performance Optimization**

### **Command Batching and Optimization**

The Device Manager implements **command batching** for efficiency:

```python
async def _batch_commands(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch multiple commands for efficiency."""
    # Group commands by device type
    device_type_groups = {}
    for command in commands:
        device_type = command.get("device_type", "generic")
        if device_type not in device_type_groups:
            device_type_groups[device_type] = []
        device_type_groups[device_type].append(command)
    
    # Process each group
    results = []
    for device_type, type_commands in device_type_groups.items():
        if device_type == "light":
            results.extend(await self._batch_light_commands(type_commands))
        elif device_type == "speaker":
            results.extend(await self._batch_speaker_commands(type_commands))
        else:
            results.extend(await self._batch_generic_commands(type_commands))
    
    return results
```

**Batching Features:**
- **Type Grouping**: Group commands by device type
- **Efficient Processing**: Process similar commands together
- **Resource Optimization**: Optimize resource usage
- **Performance Improvement**: Improve overall performance

### **Caching and Response Optimization**

The Device Manager implements **intelligent caching**:

```python
def _get_cached_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
    """Get cached device status if available."""
    if device_id in self.device_status_cache:
        cached_status = self.device_status_cache[device_id]
        
        # Check if cache is still valid
        if time.time() - cached_status["timestamp"] < self.status_cache_ttl:
            return cached_status["status"]
    
    return None
```

**Caching Features:**
- **Status Caching**: Cache device status information
- **TTL Management**: Time-to-live for cache entries
- **Performance Improvement**: Reduce device query overhead
- **Memory Management**: Limit cache size

## 🔧 **Error Handling and Recovery**

### **Command Error Handling**

The Device Manager implements **comprehensive error handling**:

```python
async def _handle_command_error(self, command_data: Dict[str, Any], error: Exception):
    """Handle command execution errors."""
    command_id = command_data["command_id"]
    device_id = command_data["device_ids"][0] if command_data["device_ids"] else "unknown"
    
    self.logger.error(f"Command {command_id} failed for device {device_id}: {error}")
    
    # Update command status
    command_data["status"] = "error"
    command_data["error"] = str(error)
    command_data["failed_at"] = time.time()
    
    # Determine retry strategy
    if command_data["retry_count"] < command_data["max_retries"]:
        # Retry command
        command_data["retry_count"] += 1
        command_data["status"] = "queued"
        command_data["retry_delay"] = min(2 ** command_data["retry_count"], 60)  # Exponential backoff
        
        # Schedule retry
        asyncio.create_task(self._schedule_command_retry(command_data))
    else:
        # Max retries exceeded
        self.logger.error(f"Command {command_id} failed after {command_data['max_retries']} retries")
        self._publish_command_failure(command_data)
```

**Error Handling Features:**
- **Error Classification**: Classify errors by type
- **Retry Logic**: Automatic retry with exponential backoff
- **Failure Reporting**: Report command failures
- **Recovery Strategies**: Different recovery strategies for different errors

### **Device Health Monitoring**

The Device Manager monitors **device health** continuously:

```python
async def _check_device_health(self, device_id: str, device_info: Dict[str, Any]):
    """Check health of a specific device."""
    try:
        # Send health check command
        health_check = {
            "device_id": device_id,
            "command": "health_check",
            "timestamp": time.time()
        }
        
        # Publish health check
        topic = f"alicia/devices/{device_id}/health_check"
        self.publish_message(topic, health_check)
        
        # Wait for response
        response = await self._wait_for_device_response(device_id, "health_check", timeout=5)
        
        if response and response.get("status") == "healthy":
            device_info["status"] = "online"
            device_info["last_seen"] = time.time()
        else:
            device_info["status"] = "unhealthy"
            self.logger.warning(f"Device {device_id} health check failed")
        
    except Exception as e:
        self.logger.error(f"Health check failed for device {device_id}: {e}")
        device_info["status"] = "error"
```

## 🚀 **Next Steps**

The Device Manager provides the foundation for device control in Alicia. In the next chapter, we'll examine the **Home Assistant Bridge** that integrates with Home Assistant, including:

1. **Home Assistant Integration** - Bidirectional communication with HA
2. **Entity Discovery** - Automatic discovery of HA entities
3. **State Synchronization** - Real-time state synchronization
4. **Service Call Translation** - Translation between HA and bus services
5. **Event Handling** - Comprehensive event handling and processing

The Device Manager demonstrates how **sophisticated device management** can be implemented in a microservices architecture, providing unified control that scales with the system.

---

**The Device Manager in Alicia represents a mature, production-ready approach to smart home device management. Every design decision is intentional, every integration pattern serves a purpose, and every optimization contributes to the greater goal of creating a reliable, scalable, and maintainable device control system.**
