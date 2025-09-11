# Alicia Monitoring App

A comprehensive monitoring and development tool for the Alicia Voice Assistant ecosystem. This application provides real-time health monitoring, configuration management, testing interfaces, and analytics for all voice assistant components.

## 🎯 Features

### Health Monitoring
- Real-time status monitoring of all Alicia services
- Response time tracking and performance metrics
- WebSocket-based live updates
- Service health cards with detailed information

### Configuration Management
- GUI-based configuration for all services
- Environment-specific settings (production, development, staging)
- Configuration testing and validation
- Secure API key management

### Testing Interface
- Interactive testing of voice assistant components
- End-to-end pipeline testing
- Component isolation testing
- Test result tracking and history

### Analytics & Performance
- Historical metrics and trends
- Performance analytics and insights
- Alert management and monitoring
- Export capabilities for data analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3001    │    │   Port: 8001    │    │   Port: 5433    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Redis Cache   │    │   Alicia        │
│   Real-time     │    │   Port: 6380    │    │   Services      │
│   Updates       │    │                 │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Using Docker Compose (Recommended)

1. **Clone and navigate to the monitoring app:**
   ```bash
   cd alicia-monitoring-app
   ```

2. **Start the monitoring app:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

### Development Setup

1. **Backend Development:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Frontend Development:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📊 Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3001 | React web interface |
| Backend API | 8001 | FastAPI REST API |
| PostgreSQL | 5433 | Monitoring database |
| Redis | 6380 | Caching and sessions |
| Nginx | 8080 | Reverse proxy (optional) |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://alicia:alicia_password@monitoring-postgres:5432/alicia_monitoring
REDIS_URL=redis://monitoring-redis:6379

# Alicia Services
WHISPER_HOST=alicia_wyoming_whisper
WHISPER_PORT=10300
PIPER_HOST=alicia_unified_tts
PIPER_PORT=10200
ALICIA_HOST=alicia_assistant
ALICIA_PORT=8000
MQTT_HOST=alicia_mqtt
MQTT_PORT=1883
HA_HOST=homeassistant
HA_PORT=8123

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_RETENTION_DAYS=30
DEBUG=true
```

### Frontend Configuration

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8001
REACT_APP_WS_URL=ws://localhost:8001
```

## 📱 Usage

### Dashboard
- View real-time health status of all services
- Monitor response times and performance metrics
- See recent activity and alerts

### Configuration
- Manage service configurations across environments
- Test service connectivity and settings
- Update API keys and credentials securely

### Testing
- Run individual component tests
- Execute end-to-end pipeline tests
- View test results and performance metrics

### Analytics
- Analyze historical performance data
- View trends and patterns
- Export data for further analysis

## 🔌 API Endpoints

### Health Monitoring
- `GET /api/health/` - Get overall health status
- `GET /api/health/services` - Get all services status
- `GET /api/health/services/{service}` - Get specific service status
- `POST /api/health/refresh` - Manually refresh health status

### Configuration
- `GET /api/config/` - Get all configurations
- `GET /api/config/{service}` - Get service configuration
- `PUT /api/config/{service}` - Update service configuration
- `POST /api/config/{service}/test` - Test service configuration

### Testing
- `POST /api/testing/run` - Run a test
- `GET /api/testing/results` - Get test results
- `POST /api/testing/run-suite` - Run test suite

### Metrics
- `GET /api/metrics/overview` - Get metrics overview
- `GET /api/metrics/services/{service}` - Get service metrics
- `GET /api/metrics/performance` - Get performance metrics

## 🛠️ Development

### Project Structure
```
alicia-monitoring-app/
├── frontend/                 # React TypeScript app
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Main application pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   └── types/          # TypeScript definitions
│   └── package.json
├── backend/                 # FastAPI Python app
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core business logic
│   │   ├── models/         # Database models
│   │   └── services/       # Service layer
│   └── requirements.txt
├── database/               # Database scripts
├── docker/                 # Docker configurations
└── docker-compose.yml      # Development environment
```

### Adding New Services

1. **Backend:** Add service configuration in `app/core/config.py`
2. **Backend:** Implement health check in `app/core/health_monitor.py`
3. **Frontend:** Add service card in dashboard components

### Adding New Metrics

1. **Backend:** Add metric collection in health monitor
2. **Backend:** Create API endpoint in `app/api/metrics.py`
3. **Frontend:** Add visualization component

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on port 8001
   - Verify WebSocket URL in frontend configuration

2. **Database Connection Error**
   - Ensure PostgreSQL is running on port 5433
   - Check database credentials in environment variables

3. **Service Health Checks Failing**
   - Verify Alicia services are running
   - Check service URLs and ports in configuration

### Logs

View application logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f monitoring-backend
docker-compose logs -f monitoring-frontend
```

## 📈 Performance

### Optimization Tips

1. **Database Indexing:** Ensure proper indexes on frequently queried columns
2. **Caching:** Use Redis for frequently accessed data
3. **WebSocket:** Limit WebSocket message frequency for large datasets
4. **Frontend:** Implement pagination for large data sets

### Monitoring

- Monitor memory usage of containers
- Track database query performance
- Monitor WebSocket connection count
- Set up alerts for service failures

## 🔒 Security

### Best Practices

1. **API Keys:** Store sensitive data encrypted in database
2. **CORS:** Configure appropriate CORS origins
3. **Authentication:** Implement user authentication for production
4. **HTTPS:** Use HTTPS in production environments

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`
