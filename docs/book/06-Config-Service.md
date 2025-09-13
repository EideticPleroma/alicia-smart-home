# Chapter 6.5: Config Service Implementation

## 🎯 **Config Service Overview**

The Config Service is a **centralized configuration management system** that provides dynamic configuration updates, environment-specific settings, and configuration validation for all Alicia services. It serves as the single source of truth for system configuration.

## 🏗️ **Architecture and Purpose**

### **Core Responsibilities**

```python
class ConfigurationService(BusServiceWrapper):
    """
    Configuration Service for centralized config management.
    
    Handles:
    - Dynamic configuration updates
    - Environment-specific settings
    - Configuration validation
    - Service configuration distribution
    """
```

**Why Centralized Configuration?**
- **Single Source of Truth**: All services get config from one place
- **Dynamic Updates**: Configuration changes without service restarts
- **Environment Management**: Different configs for dev/staging/prod
- **Validation**: Ensures configuration consistency and correctness

### **Service Configuration**

```python
# MQTT configuration
mqtt_config = {
    "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
    "port": int(os.getenv("MQTT_PORT", "1883")),
    "username": os.getenv("MQTT_USERNAME", "config_service"),
    "password": os.getenv("MQTT_PASSWORD", "alicia_config_2024")
}
```

**Port**: `8026`  
**Network**: `alicia_network`  
**Dependencies**: MQTT Broker, Device Registry

## 🔧 **Technology Stack Analysis**

### **Core Dependencies**

```python
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
paho-mqtt==1.6.1
pydantic==2.5.0

# Configuration management
pyyaml==6.0.1
python-dotenv==1.0.0

# HTTP client
httpx==0.25.2
```

**Technology Choices:**

1. **FastAPI + Uvicorn**:
   - **Purpose**: High-performance API server
   - **Benefits**: Async support, automatic validation, OpenAPI docs
   - **Use Cases**: Configuration API endpoints, health checks

2. **Pydantic**:
   - **Purpose**: Data validation and settings management
   - **Benefits**: Type safety, automatic validation, serialization
   - **Use Cases**: Configuration schema validation, settings models

3. **PyYAML**:
   - **Purpose**: YAML configuration file parsing
   - **Benefits**: Human-readable configs, hierarchical structure
   - **Use Cases**: Service configuration files, environment settings

4. **python-dotenv**:
   - **Purpose**: Environment variable management
   - **Benefits**: Easy environment configuration, secrets management
   - **Use Cases**: Service credentials, environment-specific settings

## 📊 **Configuration Management Patterns**

### **1. Configuration Schema Definition**

```python
class ServiceConfig(BaseModel):
    """Base configuration schema for all services."""
    service_name: str
    version: str
    environment: str
    mqtt_config: MQTTConfig
    api_config: APIConfig
    features: Dict[str, bool]
    limits: ServiceLimits

class MQTTConfig(BaseModel):
    """MQTT configuration schema."""
    host: str
    port: int
    username: str
    password: str
    tls_enabled: bool = False
    keepalive: int = 60
```

### **2. Dynamic Configuration Updates**

```python
async def update_service_config(self, service_name: str, config: Dict[str, Any]):
    """Update configuration for a specific service."""
    try:
        # Validate configuration
        validated_config = self.validate_config(service_name, config)
        
        # Store in database
        await self.store_config(service_name, validated_config)
        
        # Notify service via MQTT
        await self.publish_config_update(service_name, validated_config)
        
        return {"status": "success", "message": f"Config updated for {service_name}"}
    except ValidationError as e:
        return {"status": "error", "message": f"Invalid configuration: {e}"}
```

### **3. Environment-Specific Configuration**

```python
def load_environment_config(self, environment: str) -> Dict[str, Any]:
    """Load configuration for specific environment."""
    config_files = [
        f"config/base.yaml",
        f"config/{environment}.yaml",
        f"config/{environment}-secrets.yaml"
    ]
    
    merged_config = {}
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                env_config = yaml.safe_load(f)
                merged_config = self.merge_configs(merged_config, env_config)
    
    return merged_config
```

## 🔄 **Configuration Distribution Patterns**

### **1. MQTT-Based Distribution**

```python
async def publish_config_update(self, service_name: str, config: Dict[str, Any]):
    """Publish configuration update via MQTT."""
    topic = f"alicia/config/update/{service_name}"
    message = {
        "timestamp": time.time(),
        "service": service_name,
        "config": config,
        "version": self.get_config_version(service_name)
    }
    
    await self.publish_message(topic, message)
```

### **2. Pull-Based Configuration**

```python
@self.api.app.get("/config/{service_name}")
async def get_service_config(service_name: str):
    """Get current configuration for a service."""
    config = await self.get_stored_config(service_name)
    if not config:
        return {"error": "Configuration not found"}
    
    return {
        "service": service_name,
        "config": config,
        "version": config.get("version"),
        "last_updated": config.get("timestamp")
    }
```

### **3. Configuration Validation**

```python
def validate_config(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration against service schema."""
    schema = self.get_service_schema(service_name)
    
    try:
        validated = schema(**config)
        return validated.dict()
    except ValidationError as e:
        raise ValidationError(f"Configuration validation failed: {e}")
```

## 📈 **Performance and Scalability**

### **1. Configuration Caching**

```python
class ConfigCache:
    """In-memory configuration cache for fast access."""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get configuration from cache if valid."""
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any]):
        """Store configuration in cache."""
        self.cache[key] = value
        self.timestamps[key] = time.time()
```

### **2. Batch Configuration Updates**

```python
async def batch_update_configs(self, updates: List[Dict[str, Any]]):
    """Update multiple service configurations efficiently."""
    validated_updates = []
    
    # Validate all configurations
    for update in updates:
        try:
            validated = self.validate_config(update["service"], update["config"])
            validated_updates.append(validated)
        except ValidationError as e:
            self.logger.error(f"Validation failed for {update['service']}: {e}")
    
    # Batch store in database
    await self.batch_store_configs(validated_updates)
    
    # Batch publish updates
    await self.batch_publish_updates(validated_updates)
```

## 🔒 **Security Considerations**

### **1. Configuration Encryption**

```python
def encrypt_sensitive_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt sensitive configuration values."""
    sensitive_keys = ["password", "secret", "key", "token"]
    encrypted_config = config.copy()
    
    for key, value in config.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            encrypted_config[key] = self.encrypt_value(str(value))
    
    return encrypted_config
```

### **2. Access Control**

```python
def check_config_access(self, service_name: str, requesting_service: str) -> bool:
    """Check if requesting service can access configuration."""
    access_rules = self.get_access_rules(service_name)
    
    # Check if requesting service has access
    if requesting_service in access_rules.get("allowed_services", []):
        return True
    
    # Check if requesting service is in same group
    service_group = self.get_service_group(requesting_service)
    if service_group in access_rules.get("allowed_groups", []):
        return True
    
    return False
```

## 🚀 **Integration with Other Services**

### **1. Service Registration Integration**

```python
async def on_service_registered(self, service_name: str, service_info: Dict[str, Any]):
    """Handle new service registration."""
    # Load default configuration for new service
    default_config = await self.load_default_config(service_name)
    
    # Store configuration
    await self.store_config(service_name, default_config)
    
    # Send initial configuration to service
    await self.publish_config_update(service_name, default_config)
```

### **2. Health Monitoring Integration**

```python
async def get_config_health(self) -> Dict[str, Any]:
    """Get configuration service health status."""
    return {
        "service": "config_service",
        "status": "healthy",
        "configs_managed": len(self.managed_configs),
        "last_update": self.last_config_update,
        "cache_hit_rate": self.cache.get_hit_rate(),
        "validation_errors": self.validation_error_count
    }
```

## 🎯 **Best Practices**

### **1. Configuration Versioning**

- **Semantic Versioning**: Use semantic versioning for configuration changes
- **Backward Compatibility**: Ensure config changes don't break existing services
- **Migration Scripts**: Provide migration scripts for breaking changes

### **2. Environment Management**

- **Environment Isolation**: Separate configs for dev/staging/prod
- **Secret Management**: Use environment variables for sensitive data
- **Configuration Inheritance**: Base configs with environment overrides

### **3. Monitoring and Alerting**

- **Configuration Drift**: Monitor for unauthorized config changes
- **Validation Errors**: Alert on configuration validation failures
- **Performance Metrics**: Track configuration access patterns

## 🔧 **API Endpoints**

### **Configuration Management**

```python
# Get service configuration
GET /config/{service_name}

# Update service configuration
PUT /config/{service_name}

# List all configurations
GET /configs

# Validate configuration
POST /config/validate

# Get configuration schema
GET /config/schema/{service_name}
```

### **Environment Management**

```python
# Get environment configurations
GET /environments

# Switch environment
POST /environments/{environment}/activate

# Compare configurations
GET /config/compare/{service_name}?env1=dev&env2=prod
```

## 🎉 **Summary**

The Config Service provides **centralized, dynamic, and secure configuration management** for the entire Alicia ecosystem. It ensures:

- **Consistency**: All services use validated configurations
- **Flexibility**: Dynamic updates without service restarts
- **Security**: Encrypted sensitive data and access control
- **Scalability**: Efficient caching and batch operations
- **Reliability**: Comprehensive validation and error handling

This service is essential for maintaining a **production-ready, scalable, and maintainable** microservices architecture.
