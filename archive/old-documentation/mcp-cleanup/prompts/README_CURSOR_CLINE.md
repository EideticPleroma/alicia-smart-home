# Cursor-Cline MCP Integration - Complete Setup Guide

## 🎯 Overview

This guide provides complete setup instructions for the Cursor-Cline MCP integration within the Alicia Smart Home AI ecosystem. The system uses Cursor as the orchestrator and Cline as the specialized QA agent, communicating via MQTT.

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Run the automated setup script
python setup_environment.py

# Or manually copy environment template
cp env.example .env
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.cursor-cline.txt

# Or install specific packages
pip install asyncio-mqtt aiohttp pydantic structlog rich
```

### 3. Start Services

#### Windows
```cmd
start_mcp_windows.bat
```

#### Linux/Mac
```bash
./start_mcp_unix.sh
```

#### Docker
```bash
docker-compose -f docker-compose.cursor-cline.yml up -d
```

## 🔧 Configuration

### Environment Variables

The system uses the following key environment variables:

```bash
# MQTT Configuration
MQTT_BROKER_URL=mqtts://localhost:8883
MQTT_USERNAME=alicia_mcp_user
MQTT_PASSWORD=alicia_mcp_password

# Grok API (Free with Cline)
GROK_API_KEY=free_with_cline
GROK_MODEL=grok-code-fast-1

# Quality Thresholds
BDD_THRESHOLD=8.0
TEST_QUALITY_THRESHOLD=7.0
CODE_REVIEW_THRESHOLD=7.0

# Service Configuration
CURSOR_ORCHESTRATOR_ID=cursor_orchestrator
CLINE_SPECIALIST_ID=cline_specialist
MAX_CONCURRENT_TASKS=3
```

### Configuration Files

- **`config.cursor-cline.json`** - Main configuration file
- **`.env`** - Environment variables (created from template)
- **`bus-config/`** - MQTT broker configuration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Cursor Agent (Orchestrator)                          │
│                                                                                 │
│  • MCP Orchestration Logic    • Task Distribution & Management                 │
│  • Quality Gate Control       • Error Recovery & Retry Logic                   │
│  • State Machine Management   • Integration with Alicia MQTT Bus               │
│  • Resource Management        • Monitoring & Health Checks                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ MQTT Messages
                                    │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Cline Agent (Specialist)                             │
│                                                                                 │
│  • BDD Scenario Generation    • Python Test Code Creation                      │
│  • Code Quality Analysis      • Test Review & Validation                       │
│  • LangChain Integration      • Specialized QA Expertise                       │
│  • grok-code-fast-1 Model     • Focused Task Execution                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📡 MQTT Topics

### Orchestrator Topics
- `alicia/mcp/qa/orchestrator/task/request` - Task requests to specialists
- `alicia/mcp/qa/orchestrator/task/response` - Task responses from specialists
- `alicia/mcp/qa/orchestrator/status/update` - Orchestrator status updates
- `alicia/mcp/qa/orchestrator/control/command` - Control commands

### Specialist Topics
- `alicia/mcp/qa/specialist/cline/task/request` - Tasks assigned to Cline
- `alicia/mcp/qa/specialist/cline/task/response` - Cline's task responses
- `alicia/mcp/qa/specialist/cline/status/heartbeat` - Cline health status
- `alicia/mcp/qa/specialist/cline/capability/announce` - Cline capabilities

### Shared Topics
- `alicia/mcp/qa/shared/codebase/snapshot` - Codebase snapshots
- `alicia/mcp/qa/shared/results/package` - Generated test packages
- `alicia/mcp/qa/shared/config/update` - Configuration updates

## 🧪 Testing

### Run Integration Tests
```bash
python integration_test.py
```

### Health Checks
```bash
# Check orchestrator health
curl http://localhost:8080/health

# Check specialist health
curl http://localhost:8081/health

# Run health check script
./health_check.sh
```

### Manual Testing
```bash
# Test individual components
python cursor_orchestrator.py
python cline_specialist.py
```

## 📊 Monitoring

### Service Status
- **Cursor Orchestrator**: http://localhost:8080/health
- **Cline Specialist**: http://localhost:8081/health
- **MQTT Broker**: Port 8883 (TLS) / 1883 (non-TLS)

### Logs
- **System Logs**: `logs/mcp_system.log`
- **Orchestrator Logs**: `logs/cursor_orchestrator.log`
- **Specialist Logs**: `logs/cline_specialist.log`

### Metrics
- Active tasks count
- Quality gate pass/fail rates
- Response times
- Error rates
- Resource usage

## 🔧 Troubleshooting

### Common Issues

#### 1. MQTT Connection Failed
```bash
# Check MQTT broker status
docker ps | grep mosquitto

# Check MQTT configuration
cat bus-config/mosquitto.conf
```

#### 2. Service Registration Failed
```bash
# Check service logs
tail -f logs/cursor_orchestrator.log
tail -f logs/cline_specialist.log

# Verify environment variables
echo $MQTT_BROKER_URL
echo $GROK_API_KEY
```

#### 3. Task Processing Issues
```bash
# Check task queue status
curl http://localhost:8080/status

# Check specialist capabilities
curl http://localhost:8081/capabilities
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python cursor_orchestrator.py
python cline_specialist.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start services
docker-compose -f docker-compose.cursor-cline.yml up -d

# Check service status
docker-compose -f docker-compose.cursor-cline.yml ps

# View logs
docker-compose -f docker-compose.cursor-cline.yml logs -f
```

### Production Deployment
1. **Configure MQTT Broker** with proper TLS certificates
2. **Set Environment Variables** for production values
3. **Configure Monitoring** and alerting
4. **Set up Log Aggregation** for centralized logging
5. **Configure Backup** for persistent data

## 📈 Performance Tuning

### Resource Limits
```bash
# Adjust concurrent tasks
export MAX_CONCURRENT_TASKS=5

# Adjust memory limits
export MEMORY_LIMIT_MB=2048

# Adjust CPU limits
export CPU_LIMIT_PERCENT=90
```

### Quality Thresholds
```bash
# Adjust quality thresholds
export BDD_THRESHOLD=9.0
export TEST_QUALITY_THRESHOLD=8.0
export CODE_REVIEW_THRESHOLD=8.0
```

## 🔒 Security

### MQTT Security
- **TLS Encryption**: All MQTT communication encrypted
- **Certificate Authentication**: Mutual TLS for service authentication
- **ACL Authorization**: Topic-based access control
- **JWT Tokens**: Service-to-service authentication

### API Security
- **Input Validation**: All inputs validated
- **Rate Limiting**: Prevent abuse
- **Authentication**: Service authentication required
- **Audit Logging**: Complete audit trail

## 📚 API Reference

### Cursor Orchestrator API
- `GET /health` - Health check
- `GET /status` - Service status
- `POST /task` - Submit QA task
- `GET /tasks` - List active tasks

### Cline Specialist API
- `GET /health` - Health check
- `GET /capabilities` - List capabilities
- `GET /status` - Service status
- `POST /task` - Process task

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Create an issue** on GitHub
- **Check the troubleshooting** section
- **Review the configuration** options
- **Check the logs** for error messages

---

**Ready to automate your QA process with Cursor and Cline!** 🚀
