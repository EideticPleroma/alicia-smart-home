# Chapter 4: Core Infrastructure Services

## 🎯 **Foundation Services Overview**

Alicia's core infrastructure consists of six essential services that provide the foundation for all other services. These services handle security, device management, service discovery, health monitoring, and configuration management. This chapter analyzes each service in detail, examining their implementation, technology choices, and integration patterns.

## 🔐 **Security Gateway Service**

### **Architecture and Purpose**

The Security Gateway serves as the **centralized security authority** for the entire Alicia ecosystem. It handles authentication, authorization, encryption, and security event logging for all services and devices.

```python
class SecurityGateway(BusServiceWrapper):
    """
    Security Gateway service for the Alicia bus architecture.
    
    Handles all security-related operations:
    - Device certificate validation
    - Message encryption/decryption
    - Access token management
    - Security event logging
    """
```

**Why Centralized Security?**
- **Single Point of Control**: All security decisions are made in one place
- **Consistent Policies**: Uniform security policies across all services
- **Audit Trail**: Centralized logging of all security events
- **Key Management**: Centralized management of encryption keys and certificates

### **Technology Stack Analysis**

The Security Gateway uses **cryptography libraries** for robust security implementation:

```python
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import jwt
```

**Technology Choices:**

1. **cryptography Library**:
   - **Purpose**: Low-level cryptographic operations
   - **Benefits**: Industry-standard, well-tested, secure by default
   - **Use Cases**: Certificate generation, key management, encryption

2. **PyJWT**:
   - **Purpose**: JSON Web Token handling
   - **Benefits**: Standardized token format, stateless authentication
   - **Use Cases**: Service-to-service authentication, API access tokens

3. **FastAPI Security**:
   - **Purpose**: HTTP-based security endpoints
   - **Benefits**: Built-in security features, automatic documentation
   - **Use Cases**: External API authentication, token validation

### **Key Management Implementation**

The Security Gateway implements **sophisticated key management**:

```python
def _setup_encryption(self):
    """Setup encryption keys and certificates."""
    try:
        # Create directories if they don't exist
        os.makedirs(self.encryption_key_path, exist_ok=True)
        os.makedirs(self.certificate_path, exist_ok=True)
        
        # Generate or load encryption key
        key_path = os.path.join(self.encryption_key_path, "encryption_key.pem")
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                self.encryption_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
        else:
            # Generate new key
            self.encryption_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
```

**Key Management Features:**
- **RSA 2048-bit Keys**: Industry-standard key size for security
- **Persistent Storage**: Keys are stored securely and reused across restarts
- **Automatic Generation**: New keys are generated if none exist
- **Certificate Support**: Full X.509 certificate chain support

### **Authentication and Authorization**

The Security Gateway implements **multi-layered authentication**:

```python
# In-memory stores (in production, use database)
self.device_certificates: Dict[str, Dict[str, Any]] = {}
self.active_tokens: Dict[str, Dict[str, Any]] = {}
self.security_events: list = []
```

**Authentication Layers:**

1. **Device Certificates**: X.509 certificates for device authentication
2. **JWT Tokens**: Short-lived tokens for service authentication
3. **MQTT Credentials**: Username/password for MQTT broker access
4. **API Keys**: Long-lived keys for external API access

### **Security Event Logging**

All security events are **logged and monitored**:

```python
def log_security_event(self, event_type: str, details: Dict[str, Any]):
    """Log a security event."""
    event = {
        "timestamp": time.time(),
        "event_type": event_type,
        "details": details,
        "source": "security_gateway"
    }
    self.security_events.append(event)
    
    # Publish to monitoring system
    self.publish_message("alicia/system/security/events", event)
```

**Security Event Types:**
- **Authentication Events**: Login attempts, token generation
- **Authorization Events**: Access denied, permission changes
- **Encryption Events**: Key generation, certificate validation
- **Threat Detection**: Suspicious activity, brute force attempts

## 🏠 **Device Registry Service**

### **Architecture and Purpose**

The Device Registry serves as the **centralized device management system** for all smart home devices. It provides device registration, capability tracking, status monitoring, and real-time device discovery.

```python
class DeviceRegistry(BusServiceWrapper):
    """
    Device Registry Service for the Alicia bus architecture.
    
    Provides centralized device management with the following features:
    - Device registration and deregistration
    - Device capability tracking and classification
    - Real-time device status monitoring
    - Device authentication and authorization
    - Device discovery and heartbeat monitoring
    """
```

**Why Centralized Device Management?**
- **Single Source of Truth**: All device information in one place
- **Capability Discovery**: Services can discover what devices can do
- **Status Monitoring**: Real-time device health and availability
- **Access Control**: Centralized device permissions and authentication

### **Database Architecture**

The Device Registry uses **SQLite** for persistent device storage:

```python
def _setup_database(self):
    """Setup SQLite database for device storage."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            device_type TEXT NOT NULL,
            device_name TEXT NOT NULL,
            location TEXT,
            capabilities TEXT,  -- JSON array of capabilities
            status TEXT DEFAULT 'offline',
            last_seen REAL,
            created_at REAL,
            updated_at REAL
        )
    ''')
    
    # Create device_groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_groups (
            group_id TEXT PRIMARY KEY,
            group_name TEXT NOT NULL,
            device_ids TEXT,  -- JSON array of device IDs
            created_at REAL
        )
    ''')
```

**Database Design Rationale:**
- **SQLite**: Lightweight, embedded database perfect for device metadata
- **JSON Columns**: Flexible storage for device capabilities and groups
- **Timestamps**: Track device lifecycle and status changes
- **Indexes**: Optimized queries for device discovery and filtering

### **Device Lifecycle Management**

The Device Registry implements **comprehensive device lifecycle management**:

```python
def register_device(self, device_info: Dict[str, Any]) -> bool:
    """Register a new device."""
    try:
        device_id = device_info["device_id"]
        
        # Check if device already exists
        if device_id in self.devices:
            self.logger.warning(f"Device {device_id} already registered")
            return False
        
        # Validate device information
        if not self._validate_device_info(device_info):
            return False
        
        # Store device information
        self.devices[device_id] = device_info
        self.device_capabilities[device_id] = set(device_info.get("capabilities", []))
        
        # Update database
        self._save_device_to_db(device_info)
        
        # Publish device registration event
        self.publish_message("alicia/devices/registry/registered", {
            "device_id": device_id,
            "device_type": device_info["device_type"],
            "capabilities": device_info.get("capabilities", [])
        })
        
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to register device: {e}")
        return False
```

**Device Lifecycle Stages:**

1. **Discovery**: Device announces itself to the registry
2. **Registration**: Device information is stored and validated
3. **Authentication**: Device credentials are verified
4. **Capability Mapping**: Device capabilities are catalogued
5. **Status Monitoring**: Continuous health and availability tracking
6. **Deregistration**: Device is removed when no longer available

### **Real-time Device Monitoring**

The Device Registry implements **real-time device status monitoring**:

```python
def update_device_status(self, device_id: str, status: str, metadata: Dict[str, Any] = None):
    """Update device status and metadata."""
    if device_id not in self.devices:
        self.logger.warning(f"Device {device_id} not found in registry")
        return
    
    # Update device status
    self.devices[device_id]["status"] = status
    self.devices[device_id]["last_seen"] = time.time()
    
    if metadata:
        self.devices[device_id].update(metadata)
    
    # Update database
    self._update_device_in_db(device_id, status, metadata)
    
    # Publish status update
    self.publish_message(f"alicia/devices/status/{device_id}", {
        "device_id": device_id,
        "status": status,
        "timestamp": time.time(),
        "metadata": metadata or {}
    })
```

**Monitoring Features:**
- **Heartbeat Tracking**: Devices send periodic heartbeats
- **Status Changes**: Real-time status updates via MQTT
- **Capability Updates**: Dynamic capability changes
- **Location Tracking**: Device location and grouping

## 🏥 **Health Monitor Service**

### **Architecture and Purpose**

The Health Monitor Service provides **comprehensive system health monitoring** for all services in the Alicia ecosystem. It collects metrics, detects issues, and provides alerting capabilities.

```python
class HealthMonitorService(BusServiceWrapper):
    """
    Health Monitor Service for the Alicia Bus Architecture.
    
    Monitors all services, collects performance metrics, and provides
    alerting capabilities for service failures and performance issues.
    """
```

**Why Centralized Health Monitoring?**
- **System-wide Visibility**: Monitor all services from one place
- **Proactive Alerting**: Detect issues before they become problems
- **Performance Analysis**: Track system performance over time
- **Capacity Planning**: Understand resource usage patterns

### **Health Data Structures**

The Health Monitor uses **structured data classes** for type safety:

```python
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
```

**Data Structure Benefits:**
- **Type Safety**: Compile-time type checking
- **Serialization**: Easy conversion to JSON for MQTT
- **Validation**: Built-in data validation
- **Documentation**: Self-documenting data structures

### **Performance Metrics Collection**

The Health Monitor collects **comprehensive performance metrics**:

```python
def collect_service_metrics(self, service_name: str) -> ServiceHealth:
    """Collect performance metrics for a service."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_mb = memory.used / 1024 / 1024
        
        # Get service-specific metrics
        service_data = self.service_health.get(service_name, {})
        
        # Calculate response time
        response_time_ms = self._calculate_response_time(service_name)
        
        # Create health object
        health = ServiceHealth(
            service_name=service_name,
            status=service_data.get("status", "unknown"),
            last_seen=time.time(),
            uptime=service_data.get("uptime", 0),
            messages_processed=service_data.get("messages_processed", 0),
            errors=service_data.get("errors", 0),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            response_time_ms=response_time_ms,
            timestamp=time.time()
        )
        
        return health
        
    except Exception as e:
        self.logger.error(f"Failed to collect metrics for {service_name}: {e}")
        return None
```

**Metrics Collected:**
- **System Metrics**: CPU usage, memory consumption, disk I/O
- **Service Metrics**: Message processing rate, error rate, response time
- **Network Metrics**: MQTT connection status, message throughput
- **Custom Metrics**: Service-specific performance indicators

### **Alerting System**

The Health Monitor implements **intelligent alerting**:

```python
def check_alert_conditions(self, health: ServiceHealth) -> List[HealthAlert]:
    """Check if any alert conditions are met."""
    alerts = []
    
    # Service down alert
    if health.status == "unhealthy":
        alert = HealthAlert(
            alert_id=f"service_down_{health.service_name}_{int(time.time())}",
            service_name=health.service_name,
            alert_type="service_down",
            severity="critical",
            message=f"Service {health.service_name} is down",
            timestamp=time.time()
        )
        alerts.append(alert)
    
    # High CPU alert
    if health.cpu_percent > self.alert_thresholds["cpu_percent"]:
        alert = HealthAlert(
            alert_id=f"high_cpu_{health.service_name}_{int(time.time())}",
            service_name=health.service_name,
            alert_type="high_cpu",
            severity="warning",
            message=f"High CPU usage: {health.cpu_percent}%",
            timestamp=time.time()
        )
        alerts.append(alert)
    
    # High memory alert
    if health.memory_mb > self.alert_thresholds["memory_mb"]:
        alert = HealthAlert(
            alert_id=f"high_memory_{health.service_name}_{int(time.time())}",
            service_name=health.service_name,
            alert_type="high_memory",
            severity="warning",
            message=f"High memory usage: {health.memory_mb}MB",
            timestamp=time.time()
        )
        alerts.append(alert)
    
    return alerts
```

**Alert Types:**
- **Service Down**: Critical alerts for service failures
- **High CPU**: Warning alerts for high CPU usage
- **High Memory**: Warning alerts for high memory usage
- **High Error Rate**: Warning alerts for high error rates
- **Slow Response**: Warning alerts for slow response times

## 🔧 **Configuration Service**

### **Architecture and Purpose**

The Configuration Service provides **centralized configuration management** for all services. It handles configuration updates, validation, and distribution across the entire system.

```python
class ConfigurationService(BusServiceWrapper):
    """
    Configuration Service for the Alicia bus architecture.
    
    Provides centralized configuration management with the following features:
    - Configuration storage and retrieval
    - Configuration validation and schema checking
    - Real-time configuration updates
    - Configuration versioning and rollback
    - Environment-specific configurations
    """
```

**Why Centralized Configuration?**
- **Consistency**: All services use the same configuration format
- **Real-time Updates**: Configuration changes take effect immediately
- **Validation**: Centralized validation prevents invalid configurations
- **Versioning**: Track configuration changes and enable rollbacks

### **Configuration Schema Management**

The Configuration Service implements **schema-based validation**:

```python
def validate_configuration(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate configuration against schema."""
    try:
        # Check required fields
        for field in schema.get("required", []):
            if field not in config:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate field types
        for field, field_schema in schema.get("properties", {}).items():
            if field in config:
                if not self._validate_field_type(config[field], field_schema):
                    self.logger.error(f"Invalid type for field {field}")
                    return False
        
        # Validate field values
        for field, field_schema in schema.get("properties", {}).items():
            if field in config:
                if not self._validate_field_value(config[field], field_schema):
                    self.logger.error(f"Invalid value for field {field}")
                    return False
        
        return True
        
    except Exception as e:
        self.logger.error(f"Configuration validation failed: {e}")
        return False
```

**Schema Validation Features:**
- **Type Checking**: Ensure fields have correct data types
- **Value Validation**: Validate field values against constraints
- **Required Fields**: Ensure all required fields are present
- **Custom Validators**: Service-specific validation rules

### **Real-time Configuration Updates**

The Configuration Service provides **real-time configuration distribution**:

```python
def update_service_configuration(self, service_name: str, config: Dict[str, Any]) -> bool:
    """Update configuration for a specific service."""
    try:
        # Validate configuration
        schema = self.get_service_schema(service_name)
        if not self.validate_configuration(config, schema):
            return False
        
        # Store configuration
        self.configurations[service_name] = config
        self.configuration_versions[service_name].append({
            "config": config,
            "timestamp": time.time(),
            "version": len(self.configuration_versions[service_name])
        })
        
        # Publish configuration update
        self.publish_message(f"alicia/system/config/update/{service_name}", {
            "service_name": service_name,
            "configuration": config,
            "timestamp": time.time(),
            "version": len(self.configuration_versions[service_name]) - 1
        })
        
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to update configuration for {service_name}: {e}")
        return False
```

**Configuration Update Features:**
- **Immediate Distribution**: Configuration changes are published immediately
- **Version Tracking**: Each configuration change is versioned
- **Rollback Support**: Previous configurations can be restored
- **Service-specific**: Each service gets only its relevant configuration

## 🔍 **Discovery Service**

### **Architecture and Purpose**

The Discovery Service provides **automatic service discovery** for the entire Alicia ecosystem. It tracks service availability, capabilities, and dependencies.

```python
class DiscoveryService(BusServiceWrapper):
    """
    Discovery Service for the Alicia bus architecture.
    
    Provides automatic service discovery with the following features:
    - Service registration and deregistration
    - Service capability discovery
    - Service dependency tracking
    - Service health monitoring
    - Service load balancing
    """
```

**Why Automatic Service Discovery?**
- **Dynamic Scaling**: Services can be added/removed without configuration changes
- **Load Balancing**: Distribute load across multiple service instances
- **Fault Tolerance**: Automatically detect and handle service failures
- **Capability Discovery**: Services can discover what other services can do

### **Service Registration Process**

The Discovery Service implements **comprehensive service registration**:

```python
def register_service(self, service_info: Dict[str, Any]) -> bool:
    """Register a new service."""
    try:
        service_name = service_info["service_name"]
        
        # Validate service information
        if not self._validate_service_info(service_info):
            return False
        
        # Store service information
        self.services[service_name] = service_info
        self.service_capabilities[service_name] = set(service_info.get("capabilities", []))
        self.service_dependencies[service_name] = service_info.get("dependencies", [])
        
        # Update service status
        self.service_status[service_name] = {
            "status": "online",
            "last_seen": time.time(),
            "instances": 1
        }
        
        # Publish service registration event
        self.publish_message("alicia/system/discovery/registered", {
            "service_name": service_name,
            "capabilities": service_info.get("capabilities", []),
            "dependencies": service_info.get("dependencies", []),
            "timestamp": time.time()
        })
        
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to register service {service_name}: {e}")
        return False
```

**Service Registration Features:**
- **Capability Tracking**: Track what each service can do
- **Dependency Mapping**: Map service dependencies
- **Instance Counting**: Track multiple instances of the same service
- **Status Monitoring**: Monitor service health and availability

## 🔗 **Service Integration Patterns**

### **Inter-Service Communication**

The core infrastructure services work together through **well-defined communication patterns**:

```python
# Example: Health Monitor subscribing to all service health updates
def subscribe_to_topics(self):
    """Subscribe to relevant MQTT topics."""
    self.mqtt_client.subscribe("alicia/system/health/#")
    self.mqtt_client.subscribe("alicia/system/discovery/#")
    self.mqtt_client.subscribe("alicia/devices/registry/#")
```

**Communication Patterns:**

1. **Health Monitoring**: All services publish health status to Health Monitor
2. **Device Management**: Device Registry coordinates with all device-related services
3. **Security Events**: Security Gateway publishes security events to all services
4. **Configuration Updates**: Configuration Service distributes updates to all services
5. **Service Discovery**: Discovery Service coordinates service registration and discovery

### **Data Flow Architecture**

The core infrastructure services implement **sophisticated data flow patterns**:

```
Device Registration Flow:
Device → Device Registry → Security Gateway → Discovery Service → All Services

Health Monitoring Flow:
All Services → Health Monitor → Metrics Collector → Alert System

Configuration Update Flow:
Configuration Service → All Services → Device Registry → Security Gateway

Security Event Flow:
Security Gateway → All Services → Health Monitor → Alert System
```

## 🚀 **Next Steps**

The core infrastructure services provide the foundation for all other services in Alicia. In the next chapter, we'll examine the **Voice Processing Pipeline** that builds on this foundation, including:

1. **STT Service Implementation** - Speech-to-text processing with Whisper
2. **AI Service & Grok Integration** - Natural language processing and conversation management
3. **TTS Service & Voice Router** - Text-to-speech synthesis and voice pipeline orchestration

The core infrastructure demonstrates how **well-designed foundational services** can enable complex, distributed systems to work together seamlessly, providing security, monitoring, and management capabilities that scale with the system.

---

**The core infrastructure services in Alicia represent a mature, production-ready approach to building distributed systems. Every service has a clear purpose, every technology choice is justified, and every integration pattern serves the greater goal of creating a reliable, scalable, and maintainable smart home AI ecosystem.**
