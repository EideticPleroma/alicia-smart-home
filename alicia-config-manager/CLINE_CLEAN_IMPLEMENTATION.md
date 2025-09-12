# Cline Implementation Guide: Alicia Configuration Manager

## 🎯 **Project Overview**

This is a **separate** configuration management web application for the Alicia Smart Home AI Assistant Docker microservices ecosystem. It provides real-time configuration management, device management, and service topology visualization.

## 🏗️ **Architecture**

- **alicia-monitor**: Health monitoring and service discovery
- **alicia-config-manager**: Configuration management and device management
- **Shared infrastructure**: MQTT broker, Docker network, and database

## 🚀 **Quick Start**

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Access to Alicia MQTT broker

### Development Setup
```bash
cd alicia-config-manager
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

### Production Deployment
```bash
docker-compose up -d
```

## 📁 **Project Structure**

```
alicia-config-manager/
├── .clinerules                    # Cline development rules
├── package.json                   # Workspace configuration
├── docker-compose.yml             # Docker orchestration
├── .env.example                   # Environment variables template
├── README.md                      # Project documentation
├── frontend/                      # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/            # React components
│       ├── hooks/                # Custom React hooks
│       ├── services/             # API and MQTT services
│       ├── types/                # TypeScript definitions
│       └── utils/                # Utility functions
├── backend/                       # Node.js backend
│   ├── package.json
│   ├── src/
│   │   ├── index.js              # Server entry point
│   │   ├── routes/               # Express routes
│   │   ├── services/             # Business logic
│   │   └── utils/                # Utility functions
│   └── Dockerfile
└── config/                        # Configuration files (Docker volumes)
    ├── config.json               # Service configurations
    └── devices.json              # Device configurations
```

## 🔧 **Technology Stack**

### Frontend
- **React 18.2.0** with TypeScript 5.0.0
- **React Flow 11.10.1** for service topology visualization
- **Socket.io Client 4.7.0** for real-time communication
- **Tailwind CSS 3.3.0** for styling
- **Vite 4.4.0** for fast development and building

### Backend
- **Node.js 18+** with Express 4.18.2
- **Socket.io 4.7.0** for WebSocket communication
- **MQTT 5.1.0** for bus integration
- **Joi 17.9.0** for configuration validation
- **Winston 3.10.0** for structured logging

### Infrastructure
- **Docker** for containerization
- **Docker Compose** for orchestration
- **MQTT Broker** (Eclipse Mosquitto) for inter-service communication
- **Volume mounts** for configuration persistence

## 🎮 **Features**

### Service Configuration Management
- **Visual service topology** using React Flow
- **Click-to-configure** service nodes
- **Real-time configuration updates** via MQTT
- **API key management** with secure masking
- **Service-specific settings** (voice, model, endpoints)

### Device Management
- **External device registration** (APIs, local services, hardware)
- **Device status monitoring** with ping checks
- **Authentication management** for various device types
- **Integration with service graph** (device status affects node colors)

### Real-time Updates
- **Socket.io integration** for live updates
- **MQTT message monitoring** for bus activity
- **Service health polling** every 60 seconds
- **Smooth animations** and transitions

### Configuration Persistence
- **JSON file storage** mounted as Docker volumes
- **Live updates** without container restart
- **Backup/restore** functionality
- **Atomic file operations** for data integrity

## 🔌 **API Endpoints**

### Configuration Management
- `GET /api/config` - Get all service configurations
- `GET /api/config/{service}` - Get specific service configuration
- `PATCH /api/config/{service}` - Update service configuration
- `DELETE /api/config/{service}` - Delete service configuration
- `POST /api/config/reload` - Reload all configurations

### Device Management
- `GET /api/devices` - Get all devices
- `GET /api/devices/{id}` - Get specific device
- `POST /api/devices` - Create new device
- `PATCH /api/devices/{id}` - Update device
- `DELETE /api/devices/{id}` - Delete device
- `POST /api/devices/{id}/ping` - Ping device

### System Management
- `GET /api/health` - System health status
- `GET /api/services` - List all services
- `GET /api/topology` - Get service topology
- `POST /api/reload` - Reload system

## 🔄 **MQTT Integration**

### Subscribed Topics
- `alicia/system/health/#` - Service health updates
- `alicia/system/discovery/#` - Service discovery
- `alicia/config/#` - Configuration changes
- `alicia/device/#` - Device management

### Published Topics
- `alicia/config/update/{service_name}` - Configuration updates
- `alicia/config/reload` - Configuration reload signal
- `alicia/device/register` - Device registration
- `alicia/device/status/{device_id}` - Device status updates

## 🧪 **Testing**

### Unit Tests
```bash
cd frontend && npm test
cd backend && npm test
```

### Integration Tests
```bash
npm run test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 📊 **Monitoring and Logging**

### Health Checks
- **Application Health**: `GET /api/health`
- **Docker Health**: Built-in Docker health checks
- **MQTT Connection**: Automatic reconnection with exponential backoff

### Logging
- **Structured Logging**: JSON format with Winston
- **Log Levels**: error, warn, info, debug
- **Log Files**: `logs/error.log`, `logs/combined.log`
- **Console Output**: Human-readable format for development

### Metrics
- **Service Count**: Number of configured services
- **Device Count**: Number of registered devices
- **Connection Status**: MQTT and Socket.io connection status
- **Response Times**: API endpoint performance

## 🔒 **Security**

### Current Security Features
- **Input Validation**: Joi schema validation for all inputs
- **API Key Masking**: Never expose full API keys in UI
- **CORS Configuration**: Restricted cross-origin requests
- **Rate Limiting**: 100 requests per 15 minutes per IP
- **Helmet**: Security headers for Express

### Future Security Enhancements
- **JWT Authentication**: Multi-user support
- **Role-based Access Control**: User permissions
- **Configuration Encryption**: Sensitive data encryption
- **Audit Logging**: Change tracking and compliance

## 🚀 **Deployment**

### Docker Deployment
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f alicia-config-manager

# Stop services
docker-compose down
```

### Environment-specific Configuration
- **Development**: Hot reload, debug logging
- **Production**: Optimized builds, error logging
- **Testing**: Mock services, isolated databases

## 🤝 **Integration with Existing System**

### MQTT Broker
- **Shared MQTT Broker**: Uses existing `alicia_mqtt` service
- **Topic Namespace**: Uses `alicia/config/#` and `alicia/device/#` topics
- **Authentication**: Separate MQTT credentials for config manager

### Docker Network
- **Shared Network**: Uses existing `alicia_network`
- **Service Discovery**: Can discover services via MQTT
- **Port Separation**: Uses port 3002 (monitor uses 3000/3001)

### Data Persistence
- **Volume Mounts**: Separate config directories
- **File Format**: JSON files for easy editing and backup
- **Atomic Operations**: Safe concurrent access to configuration files

## 🐛 **Troubleshooting**

### Common Issues

1. **MQTT Connection Failed**
   - Check MQTT broker is running
   - Verify credentials in .env file
   - Check network connectivity

2. **Configuration Not Saving**
   - Check file permissions on config directory
   - Verify disk space available
   - Check logs for validation errors

3. **Real-time Updates Not Working**
   - Check Socket.io connection
   - Verify MQTT message flow
   - Check browser console for errors

4. **Service Graph Not Loading**
   - Check React Flow dependencies
   - Verify service data format
   - Check browser compatibility

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=debug npm run dev

# Check MQTT messages
docker-compose logs alicia_mqtt

# Check application logs
docker-compose logs alicia-config-manager
```

## 📚 **Development**

### Code Standards
- **TypeScript Strict Mode**: All code must be properly typed
- **ESLint + Prettier**: Consistent code formatting
- **Functional Components**: React hooks only, no class components
- **Custom Hooks**: Extract reusable logic
- **Error Boundaries**: Graceful error handling

### Contributing
1. Follow the .clinerules for code quality
2. Write tests for new features
3. Update documentation
4. Test with existing Alicia system
5. Submit pull request with clear description

## 📄 **License**

This project is part of the Alicia Smart Home AI Assistant ecosystem and follows the same licensing terms.

## 🆘 **Support**

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Check the existing Alicia system documentation
4. Create an issue with detailed information

---

**Note**: This is a separate application from `alicia-monitor`. Both applications work together to provide comprehensive monitoring and configuration management for the Alicia microservices ecosystem.

