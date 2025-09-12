# Chapter 3: Service Communication Patterns

## 🎯 **Overview**

This chapter examines the sophisticated communication patterns that enable Alicia's 23 microservices to work together seamlessly. We'll analyze the MQTT-based message bus architecture, service discovery mechanisms, and the various communication patterns that make the system robust and scalable.

## 🏗️ **Communication Architecture**

### **Message Bus Foundation**

Alicia's communication is built on a sophisticated MQTT message bus that provides:

- **Asynchronous Communication**: Services don't block waiting for responses
- **Decoupled Architecture**: Services can be added/removed without affecting others
- **Scalable Design**: Multiple instances of services can handle increased load
- **Reliable Delivery**: MQTT QoS levels ensure message delivery

### **Service Communication Matrix**

| Service | Publishes To | Subscribes To | Communication Type |
|---------|-------------|---------------|-------------------|
| STT Service | `alicia/voice/stt/result` | `alicia/voice/stt/request` | Request/Response |
| AI Service | `alicia/ai/response` | `alicia/ai/request` | Request/Response |
| TTS Service | `alicia/voice/tts/result` | `alicia/voice/tts/request` | Request/Response |
| Voice Router | `alicia/voice/command` | `alicia/voice/result` | Orchestration |
| Device Manager | `alicia/device/command` | `alicia/device/response` | Command/Response |
| Health Monitor | `alicia/health/status` | `alicia/health/heartbeat` | Event Streaming |

## 📡 **MQTT Topic Structure**

### **Hierarchical Topic Design**

```
alicia/
├── voice/
│   ├── stt/
│   │   ├── request/          # STT processing requests
│   │   └── result/           # STT processing results
│   ├── tts/
│   │   ├── request/          # TTS synthesis requests
│   │   └── result/           # TTS synthesis results
│   └── command/              # Voice commands
├── ai/
│   ├── request/              # AI processing requests
│   └── response/             # AI responses
├── device/
│   ├── command/              # Device control commands
│   ├── response/             # Device responses
│   └── status/               # Device status updates
├── health/
│   ├── heartbeat/            # Service health heartbeats
│   └── status/               # Health status reports
└── system/
    ├── discovery/            # Service discovery
    └── config/               # Configuration updates
```

### **Topic Naming Conventions**

- **Service-specific topics**: `alicia/{service}/{action}`
- **Broadcast topics**: `alicia/broadcast/{message_type}`
- **System topics**: `alicia/system/{component}`
- **Health topics**: `alicia/health/{service_name}`

## 🔄 **Communication Patterns**

### **Pattern 1: Request/Response**

#### **Implementation Example: STT Service**

```python
class STTService(BusServiceWrapper):
    def __init__(self):
        super().__init__("stt_service", mqtt_config)
        # Subscribe to STT requests
        self.subscribe("alicia/voice/stt/request", self.handle_stt_request)
    
    def handle_stt_request(self, client, userdata, message):
        """Handle STT processing request"""
        try:
            # Parse request
            request_data = json.loads(message.payload.decode())
            audio_data = request_data.get('audio_data')
            session_id = request_data.get('session_id')
            
            # Process audio
            transcription = self.process_audio(audio_data)
            
            # Send response
            response = {
                'session_id': session_id,
                'transcription': transcription,
                'confidence': self.calculate_confidence(transcription),
                'timestamp': time.time()
            }
            
            self.publish("alicia/voice/stt/result", response)
            
        except Exception as e:
            self.logger.error(f"STT processing error: {e}")
            self.publish("alicia/voice/stt/error", {
                'session_id': session_id,
                'error': str(e)
            })
```

#### **Why This Pattern Works**

- **Asynchronous**: STT processing doesn't block other services
- **Scalable**: Multiple STT instances can handle requests
- **Reliable**: MQTT QoS ensures message delivery
- **Traceable**: Session IDs enable request tracking

### **Pattern 2: Event Streaming**

#### **Implementation Example: Health Monitor**

```python
class HealthMonitorService(BusServiceWrapper):
    def __init__(self):
        super().__init__("health_monitor", mqtt_config)
        # Subscribe to all health heartbeats
        self.subscribe("alicia/health/heartbeat/+", self.handle_heartbeat)
        self.subscribe("alicia/health/status/+", self.handle_status_update)
    
    def handle_heartbeat(self, client, userdata, message):
        """Process service heartbeat"""
        service_name = message.topic.split('/')[-1]
        heartbeat_data = json.loads(message.payload.decode())
        
        # Update service status
        self.update_service_status(service_name, heartbeat_data)
        
        # Check for health issues
        if self.is_service_unhealthy(service_name):
            self.trigger_alert(service_name, "Service unhealthy")
    
    def handle_status_update(self, client, userdata, message):
        """Process service status updates"""
        service_name = message.topic.split('/')[-1]
        status_data = json.loads(message.payload.decode())
        
        # Update service metrics
        self.update_service_metrics(service_name, status_data)
        
        # Publish aggregated health status
        self.publish_health_summary()
```

#### **Why This Pattern Works**

- **Real-time**: Immediate health status updates
- **Efficient**: Only interested services receive updates
- **Scalable**: Can handle hundreds of services
- **Fault-tolerant**: Continues working if individual services fail

### **Pattern 3: Command Orchestration**

#### **Implementation Example: Voice Router**

```python
class VoiceRouter(BusServiceWrapper):
    def __init__(self):
        super().__init__("voice_router", mqtt_config)
        # Subscribe to voice commands
        self.subscribe("alicia/voice/command", self.handle_voice_command)
        # Subscribe to pipeline results
        self.subscribe("alicia/voice/stt/result", self.handle_stt_result)
        self.subscribe("alicia/ai/response", self.handle_ai_response)
        self.subscribe("alicia/voice/tts/result", self.handle_tts_result)
    
    def handle_voice_command(self, client, userdata, message):
        """Orchestrate voice processing pipeline"""
        command_data = json.loads(message.payload.decode())
        session_id = command_data.get('session_id')
        
        # Start STT processing
        self.publish("alicia/voice/stt/request", {
            'session_id': session_id,
            'audio_data': command_data.get('audio_data')
        })
        
        # Track pipeline state
        self.pipeline_sessions[session_id] = {
            'state': 'stt_processing',
            'start_time': time.time()
        }
    
    def handle_stt_result(self, client, userdata, message):
        """Continue pipeline after STT processing"""
        result_data = json.loads(message.payload.decode())
        session_id = result_data.get('session_id')
        
        if session_id in self.pipeline_sessions:
            # Update pipeline state
            self.pipeline_sessions[session_id]['state'] = 'ai_processing'
            self.pipeline_sessions[session_id]['transcription'] = result_data.get('transcription')
            
            # Send to AI service
            self.publish("alicia/ai/request", {
                'session_id': session_id,
                'text': result_data.get('transcription'),
                'context': self.get_conversation_context(session_id)
            })
```

#### **Why This Pattern Works**

- **Sequential**: Ensures proper pipeline order
- **Stateful**: Tracks pipeline progress
- **Resilient**: Can handle failures at any stage
- **Efficient**: Only processes when needed

## 🔧 **Service Discovery**

### **Discovery Mechanism**

```python
class DiscoveryService(BusServiceWrapper):
    def __init__(self):
        super().__init__("discovery_service", mqtt_config)
        self.services = {}
        self.subscribe("alicia/system/discovery/register", self.handle_service_registration)
        self.subscribe("alicia/system/discovery/heartbeat", self.handle_service_heartbeat)
    
    def handle_service_registration(self, client, userdata, message):
        """Register new service"""
        service_data = json.loads(message.payload.decode())
        service_name = service_data.get('service_name')
        
        self.services[service_name] = {
            'name': service_name,
            'endpoint': service_data.get('endpoint'),
            'capabilities': service_data.get('capabilities', []),
            'last_seen': time.time(),
            'status': 'active'
        }
        
        # Notify other services
        self.publish("alicia/system/discovery/update", {
            'action': 'registered',
            'service': service_name
        })
    
    def handle_service_heartbeat(self, client, userdata, message):
        """Update service heartbeat"""
        heartbeat_data = json.loads(message.payload.decode())
        service_name = heartbeat_data.get('service_name')
        
        if service_name in self.services:
            self.services[service_name]['last_seen'] = time.time()
            self.services[service_name]['status'] = 'active'
```

### **Service Registration**

```python
class BusServiceWrapper(ABC):
    def register_service(self):
        """Register service with discovery"""
        registration_data = {
            'service_name': self.service_name,
            'endpoint': f"http://{self.service_name}:{self.port}",
            'capabilities': self.get_capabilities(),
            'timestamp': time.time()
        }
        
        self.publish("alicia/system/discovery/register", registration_data)
    
    def send_heartbeat(self):
        """Send periodic heartbeat"""
        heartbeat_data = {
            'service_name': self.service_name,
            'status': 'healthy',
            'timestamp': time.time()
        }
        
        self.publish("alicia/system/discovery/heartbeat", heartbeat_data)
```

## 🛡️ **Error Handling & Resilience**

### **Retry Logic**

```python
class ResilientService(BusServiceWrapper):
    def __init__(self):
        super().__init__("resilient_service", mqtt_config)
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'backoff_factor': 2.0
        }
    
    def publish_with_retry(self, topic, message, qos=1):
        """Publish message with retry logic"""
        for attempt in range(self.retry_config['max_retries']):
            try:
                self.publish(topic, message, qos)
                return True
            except Exception as e:
                if attempt < self.retry_config['max_retries'] - 1:
                    delay = self.retry_config['retry_delay'] * (self.retry_config['backoff_factor'] ** attempt)
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to publish after {self.retry_config['max_retries']} attempts: {e}")
                    return False
```

### **Circuit Breaker Pattern**

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

## 📊 **Performance Optimization**

### **Message Batching**

```python
class BatchedPublisher:
    def __init__(self, batch_size=10, flush_interval=1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.message_queue = []
        self.last_flush = time.time()
    
    def add_message(self, topic, message):
        """Add message to batch"""
        self.message_queue.append((topic, message))
        
        if (len(self.message_queue) >= self.batch_size or 
            time.time() - self.last_flush > self.flush_interval):
            self.flush()
    
    def flush(self):
        """Flush all queued messages"""
        for topic, message in self.message_queue:
            self.publish(topic, message)
        
        self.message_queue.clear()
        self.last_flush = time.time()
```

### **Connection Pooling**

```python
class MQTTConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.available_connections = []
    
    def get_connection(self):
        """Get available MQTT connection"""
        if self.available_connections:
            return self.available_connections.pop()
        
        if len(self.connections) < self.max_connections:
            connection = self.create_connection()
            self.connections.append(connection)
            return connection
        
        # Wait for available connection
        return self.wait_for_connection()
    
    def return_connection(self, connection):
        """Return connection to pool"""
        self.available_connections.append(connection)
```

## 🔍 **Monitoring & Debugging**

### **Message Tracing**

```python
class MessageTracer:
    def __init__(self):
        self.traces = {}
    
    def trace_message(self, message_id, source, destination, message_type):
        """Trace message flow"""
        self.traces[message_id] = {
            'source': source,
            'destination': destination,
            'message_type': message_type,
            'timestamp': time.time(),
            'status': 'sent'
        }
    
    def update_trace(self, message_id, status, additional_data=None):
        """Update message trace"""
        if message_id in self.traces:
            self.traces[message_id]['status'] = status
            self.traces[message_id]['updated'] = time.time()
            
            if additional_data:
                self.traces[message_id].update(additional_data)
```

### **Performance Metrics**

```python
class CommunicationMetrics:
    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'message_latency': [],
            'error_count': 0,
            'throughput': 0
        }
    
    def record_message_sent(self, topic, size):
        """Record sent message"""
        self.metrics['messages_sent'] += 1
        self.metrics['throughput'] += size
    
    def record_message_received(self, topic, size, latency):
        """Record received message"""
        self.metrics['messages_received'] += 1
        self.metrics['message_latency'].append(latency)
        self.metrics['throughput'] += size
    
    def get_average_latency(self):
        """Get average message latency"""
        if self.metrics['message_latency']:
            return sum(self.metrics['message_latency']) / len(self.metrics['message_latency'])
        return 0
```

## 🎯 **Best Practices**

### **1. Topic Design**
- Use hierarchical topic structure
- Include service name in topics
- Use consistent naming conventions
- Avoid topic conflicts

### **2. Message Format**
- Use JSON for structured data
- Include timestamps and IDs
- Version your message formats
- Validate message schemas

### **3. Error Handling**
- Implement retry logic
- Use circuit breakers
- Log all errors
- Provide fallback mechanisms

### **4. Performance**
- Batch messages when possible
- Use connection pooling
- Monitor message latency
- Optimize topic subscriptions

### **5. Security**
- Use MQTT authentication
- Encrypt sensitive data
- Implement access control
- Monitor for anomalies

## 🚀 **Conclusion**

Alicia's service communication patterns demonstrate sophisticated microservices architecture principles. The MQTT-based message bus provides a robust foundation for asynchronous, scalable communication between services. The combination of request/response, event streaming, and command orchestration patterns enables complex workflows while maintaining system reliability and performance.

The implementation shows how modern microservices can be designed for both functionality and maintainability, with comprehensive error handling, monitoring, and optimization techniques that ensure production-ready operation.

---

**Next Chapter**: [04-Core-Infrastructure.md](04-Core-Infrastructure.md) - Deep dive into the core infrastructure services that form the foundation of Alicia's architecture.
