# Cline-Optimized Grok Prompt for Alicia Bus Architecture

## 🚀 **Master Prompt for Fast Code Generation**

Use this prompt in Cline with Grok to generate production-ready microservice code at maximum speed.

---

## 📋 **Base Prompt Template**

```
You are an expert Python developer specializing in microservices architecture. Generate production-ready code for the Alicia Bus Architecture.

CONTEXT:
- Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+
- Message bus architecture with 23 microservices
- All services use BusServiceWrapper pattern
- MQTT for inter-service communication
- Docker containerization

TASK: Generate complete service implementation

SERVICE: {SERVICE_NAME}
PURPOSE: {SERVICE_PURPOSE}
FEATURES: {SERVICE_FEATURES}

REQUIREMENTS:
1. Follow BusServiceWrapper pattern exactly
2. Include comprehensive error handling
3. Add proper MQTT integration
4. Include health check endpoints
5. Add logging and monitoring
6. Use async/await patterns
7. Include proper type hints
8. Add comprehensive docstrings

GENERATE:
1. main.py (complete service implementation)
2. Dockerfile (Python 3.11.7+ based)
3. requirements.txt (all dependencies)

PATTERN TO FOLLOW:
- Use existing services as reference (ai-service, grok-integration, etc.)
- Maintain consistent API structure
- Include proper MQTT topic handling
- Add comprehensive error handling
- Include health monitoring
- Use proper logging levels

OUTPUT FORMAT:
- Complete, production-ready code
- No placeholders or TODOs
- Proper imports and dependencies
- Comprehensive error handling
- Ready for immediate deployment
```

---

## 🎯 **Service-Specific Prompts**

### **1. Health Monitor Service (PRIORITY 0)**

```
SERVICE: Health Monitor
PURPOSE: Monitor health and performance of all bus services
FEATURES: 
- Real-time health monitoring
- Performance metrics collection
- Alert system for failures
- Dashboard API for status
- MQTT integration for updates
- Service dependency tracking
- Resource usage monitoring
- Automated recovery suggestions

IMPLEMENTATION DETAILS:
- Monitor all 23 services via MQTT health topics
- Collect CPU, memory, response time metrics
- Send alerts when services fail health checks
- Provide REST API for health dashboard
- Store metrics in time-series format
- Implement circuit breaker pattern
- Auto-restart failed services
- Generate health reports

MQTT TOPICS:
- Subscribe: alicia/system/health/+
- Publish: alicia/system/health/monitor/status
- Publish: alicia/system/health/monitor/alerts

API ENDPOINTS:
- GET /health - Service health status
- GET /metrics - Performance metrics
- GET /alerts - Active alerts
- GET /services - All service status
- POST /restart/{service} - Restart service
```

### **2. Load Balancer Service (PRIORITY 1)**

```
SERVICE: Load Balancer
PURPOSE: Distribute requests across service instances
FEATURES:
- Round-robin load balancing
- Health-based routing
- Service discovery integration
- Performance monitoring
- Circuit breaker pattern
- Request queuing
- Service instance management
- Load balancing algorithms

IMPLEMENTATION DETAILS:
- Maintain registry of healthy service instances
- Implement multiple load balancing algorithms
- Track service performance metrics
- Implement circuit breaker for failing services
- Queue requests when services are overloaded
- Auto-discover new service instances
- Health check integration

MQTT TOPICS:
- Subscribe: alicia/system/health/+
- Subscribe: alicia/system/discovery/+
- Publish: alicia/system/loadbalancer/status

API ENDPOINTS:
- POST /route/{service} - Route request to service
- GET /instances/{service} - Get service instances
- GET /metrics - Load balancing metrics
- POST /algorithm/{service} - Set load balancing algorithm
```

### **3. Metrics Collector Service (PRIORITY 1)**

```
SERVICE: Metrics Collector
PURPOSE: Collect and aggregate performance metrics
FEATURES:
- Service performance metrics
- Resource usage tracking
- Custom metric collection
- Time-series data storage
- Metric aggregation
- Performance analysis
- Trend detection
- Alert threshold management

IMPLEMENTATION DETAILS:
- Collect metrics from all services via MQTT
- Store in time-series database (SQLite)
- Aggregate metrics by service, time period
- Detect performance trends and anomalies
- Generate performance reports
- Set up alert thresholds
- Export metrics to external systems

MQTT TOPICS:
- Subscribe: alicia/system/metrics/+
- Publish: alicia/system/metrics/collector/status

API ENDPOINTS:
- GET /metrics - All collected metrics
- GET /metrics/{service} - Service-specific metrics
- GET /trends - Performance trends
- POST /thresholds - Set alert thresholds
- GET /reports - Performance reports
```

### **4. Event Scheduler Service (PRIORITY 2)**

```
SERVICE: Event Scheduler
PURPOSE: Handle timed operations and cron jobs
FEATURES:
- Cron job scheduling
- One-time event scheduling
- Recurring task management
- MQTT event publishing
- Task persistence
- Error handling and retries
- Task prioritization
- Resource management

IMPLEMENTATION DETAILS:
- Parse cron expressions for scheduling
- Store tasks in SQLite database
- Execute tasks asynchronously
- Publish results via MQTT
- Handle task failures and retries
- Prioritize tasks by importance
- Manage resource usage

MQTT TOPICS:
- Subscribe: alicia/system/scheduler/+
- Publish: alicia/system/scheduler/events
- Publish: alicia/system/scheduler/results

API ENDPOINTS:
- POST /schedule - Schedule new task
- GET /tasks - List all tasks
- DELETE /tasks/{id} - Cancel task
- GET /tasks/{id} - Get task details
- POST /tasks/{id}/run - Run task immediately
```

### **5. Configuration Manager Service (PRIORITY 2)**

```
SERVICE: Configuration Manager
PURPOSE: Advanced configuration management
FEATURES:
- Dynamic configuration updates
- Configuration versioning
- Environment-specific configs
- Configuration validation
- Hot reloading
- Configuration backup
- Rollback capabilities
- Configuration templates

IMPLEMENTATION DETAILS:
- Store configurations in SQLite database
- Validate configurations against schemas
- Support environment-specific overrides
- Implement hot reloading for services
- Version control for configurations
- Backup and restore functionality
- Template system for common configs

MQTT TOPICS:
- Subscribe: alicia/system/config/+
- Publish: alicia/system/config/updates
- Publish: alicia/system/config/validation

API ENDPOINTS:
- GET /configs - List all configurations
- GET /configs/{service} - Get service config
- POST /configs/{service} - Update service config
- GET /versions/{service} - Get config versions
- POST /rollback/{service} - Rollback config
- GET /templates - Get config templates
```

### **6. Service Orchestrator Service (PRIORITY 3)**

```
SERVICE: Service Orchestrator
PURPOSE: High-level service coordination
FEATURES:
- Service lifecycle management
- Dependency resolution
- Service startup ordering
- Failure recovery
- Service scaling
- Resource allocation
- Service monitoring
- Automated deployments

IMPLEMENTATION DETAILS:
- Manage service startup/shutdown order
- Resolve service dependencies
- Handle service failures and recovery
- Scale services based on load
- Allocate resources efficiently
- Monitor service health
- Coordinate deployments

MQTT TOPICS:
- Subscribe: alicia/system/orchestrator/+
- Publish: alicia/system/orchestrator/commands
- Publish: alicia/system/orchestrator/status

API ENDPOINTS:
- POST /start - Start all services
- POST /stop - Stop all services
- POST /restart - Restart all services
- GET /status - Orchestration status
- POST /scale/{service} - Scale service
- GET /dependencies - Service dependencies
```

---

## 🔧 **Docker File Generation Prompts**

### **Standard Dockerfile Template**

```
Generate a Dockerfile for {SERVICE_NAME} service:

REQUIREMENTS:
- Python 3.11.7+ base image
- FastAPI 0.104.1+
- Paho MQTT 1.6.1+
- Service-specific dependencies
- Health check endpoint
- Proper logging configuration
- Security best practices
- Multi-stage build if needed

STRUCTURE:
- Use python:3.11.7-slim base
- Install system dependencies
- Copy requirements.txt first
- Install Python dependencies
- Copy service code
- Set proper working directory
- Expose service port
- Add health check
- Use non-root user
- Set proper entrypoint

OUTPUT: Complete, production-ready Dockerfile
```

### **Requirements.txt Template**

```
Generate requirements.txt for {SERVICE_NAME} service:

CORE DEPENDENCIES:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- paho-mqtt==1.6.1
- pydantic==2.5.0
- sqlalchemy==2.0.23
- aiofiles==23.2.1
- python-multipart==0.0.6

SERVICE-SPECIFIC:
- Add dependencies based on service purpose
- Include monitoring libraries
- Add database drivers if needed
- Include utility libraries

OUTPUT: Complete requirements.txt with versions
```

---

## ⚡ **Fast Generation Tips**

### **1. Use Reference Services**
Always reference existing services for patterns:
- `ai-service` - For AI/ML integration
- `grok-integration` - For external API calls
- `voice-router` - For orchestration patterns
- `device-manager` - For device management

### **2. Copy-Paste Patterns**
Use these common patterns:

**MQTT Connection Pattern:**
```python
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        self.logger.info("Connected to MQTT broker")
        client.subscribe(f"alicia/{self.service_name}/+")
    else:
        self.logger.error(f"Failed to connect to MQTT: {rc}")
```

**Health Check Pattern:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": self.service_name,
        "timestamp": datetime.utcnow().isoformat(),
        "version": self.version
    }
```

**Error Handling Pattern:**
```python
try:
    result = await self.process_request(data)
    return {"success": True, "data": result}
except Exception as e:
    self.logger.error(f"Error processing request: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### **3. Batch Generation**
Generate multiple services in one prompt:
```
Generate all missing services for Alicia Bus Architecture:
1. Health Monitor
2. Load Balancer  
3. Metrics Collector
4. Event Scheduler
5. Configuration Manager
6. Service Orchestrator

For each service, generate:
- main.py
- Dockerfile
- requirements.txt

Use the patterns from existing services and follow the BusServiceWrapper architecture.
```

---

## 🎯 **Expected Output Quality**

Each generated service should include:

✅ **Complete Implementation** - No TODOs or placeholders  
✅ **Proper Error Handling** - Comprehensive try/catch blocks  
✅ **MQTT Integration** - Proper topic handling  
✅ **Health Checks** - /health endpoint  
✅ **Logging** - Structured logging throughout  
✅ **Type Hints** - Full type annotation  
✅ **Documentation** - Comprehensive docstrings  
✅ **Docker Ready** - Complete Dockerfile and requirements.txt  
✅ **Production Quality** - Ready for immediate deployment  

---

## 🚀 **Usage Instructions**

1. **Copy the base prompt template**
2. **Replace {SERVICE_NAME}, {SERVICE_PURPOSE}, {SERVICE_FEATURES}**
3. **Paste into Cline with Grok**
4. **Generate complete service implementation**
5. **Review and test generated code**
6. **Deploy to bus-services directory**

This approach will generate production-ready microservice code at maximum speed while maintaining consistency with the existing Alicia Bus Architecture patterns.
