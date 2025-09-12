# Cline Prompt: Docker Microservices Configuration Management Web App

## Project Context
Alicia Smart Home AI Assistant - Docker-based microservices ecosystem with MQTT bus architecture. Existing monitoring system with React + TypeScript frontend and Node.js + Express backend.

## Task: Generate Configuration Management Web App

Create a **separate** web application for configuration management that integrates with the existing monitoring system.

### Technology Stack
- **Frontend**: React 18, React Flow 11, Socket.io client 4.7
- **Backend**: Node.js + Express proxy in Docker
- **Storage**: JSON files (config.json, devices.json) as Docker volumes
- **Integration**: MQTT client for bus communication

### Core Features

#### 1. Service Graph Visualization
- React Flow graph with Docker services as nodes
- Live message flows as animated edges
- Real-time status updates (green/red indicators)
- Hover effects showing latency and message counts
- Auto-layout with manual positioning
- Service death handling (fade nodes, grey edges)

#### 2. Service Configuration Management
- Click node to open configuration modal
- Editable fields:
  - API keys (sk-xxxx, grok-api-key)
  - Voice selection (ara-female-2, male-deep-1)
  - TTS provider (ElevenLabs, Google, Piper)
  - Enabled/disabled toggle
  - Endpoint list: [{type: "llm", model: "grok-1.5", ip: "http://llm:8000"}]
- Real-time validation and save/cancel functionality

#### 3. Device Management
- Devices section for external IPs and authentication
- Add device form with name, IP, API key, device type
- Device status monitoring with ping checks
- Integration with service graph (device status affects node colors)

#### 4. Configuration Persistence
- config.json and devices.json as Docker volumes
- Live updates without container restart
- Backup/restore functionality

#### 5. Real-time Updates
- Socket.io integration for live updates
- MQTT message monitoring for bus activity
- Service health polling every 60 seconds
- Smooth transitions and animations

#### 6. Configuration Reload
- "Reload Config" button for instant updates
- Two methods: HTTP /reload requests or MQTT CONFIG_CHANGED topic
- Progress indicator and success/error feedback

### Integration with Existing System

#### MQTT Topics
- Subscribe: `alicia/system/health/#`, `alicia/system/discovery/#`, `alicia/voice/#`, `alicia/config/#`
- Publish: `alicia/config/update/{service_name}`, `alicia/config/reload`

#### API Endpoints
- GET/PATCH /api/config/{service} - Service configuration
- GET/POST/DELETE /api/devices - Device management
- POST /api/reload - Trigger configuration reload

### Sample Service Topology
```json
{
  "services": {
    "whisper-service": {
      "name": "Whisper STT",
      "type": "stt",
      "status": "healthy",
      "config": {
        "api_key": "sk-whisper-xxxx",
        "model": "whisper-1",
        "language": "en",
        "enabled": true,
        "endpoints": [{"type": "stt", "model": "whisper-1", "ip": "http://whisper:8001"}]
      }
    },
    "tts-service": {
      "name": "Text-to-Speech",
      "type": "tts",
      "status": "healthy",
      "config": {
        "provider": "ElevenLabs",
        "voice": "ara-female-2",
        "api_key": "sk-elevenlabs-xxxx",
        "enabled": true,
        "endpoints": [{"type": "tts", "provider": "elevenlabs", "ip": "http://tts:8002"}]
      }
    },
    "grok-service": {
      "name": "Grok AI",
      "type": "llm",
      "status": "healthy",
      "config": {
        "api_key": "sk-grok-xxxx",
        "model": "grok-1.5",
        "temperature": 0.7,
        "enabled": true,
        "endpoints": [{"type": "llm", "model": "grok-1.5", "ip": "http://grok:8003"}]
      }
    }
  }
}
```

### Frontend Rules

#### Component Structure
- Functional components with React hooks
- Custom hooks for state management
- Context API for global state
- Error boundaries for graceful error handling

#### Styling and UX
- Tailwind CSS for styling
- Dark theme with modern UI
- Responsive design
- Smooth animations
- Loading states and toast notifications

#### State Management
- useState for local state
- useEffect for side effects
- useCallback and useMemo for performance
- Custom hooks for complex logic

### Backend Implementation

#### Express Server
- RESTful API for configuration management
- WebSocket support via Socket.io
- MQTT client for bus communication
- File system operations for JSON persistence
- Error handling and logging

#### Configuration Management
- JSON file operations with atomic writes
- Configuration validation using JSON schemas
- Backup and restore functionality
- Change tracking and audit logs

### Docker Configuration

```yaml
version: '3.8'
services:
  alicia-config-manager:
    build: .
    ports:
      - "3002:3000"
    volumes:
      - ./config:/app/config
      - ./devices:/app/devices
    environment:
      - MQTT_BROKER=alicia_mqtt
      - MQTT_PORT=1883
      - MQTT_USERNAME=config_manager
      - MQTT_PASSWORD=alicia_config_2024
    depends_on:
      - alicia_mqtt
    networks:
      - alicia_network
```

### Security Considerations
- Input validation for configuration changes
- Rate limiting for API endpoints
- CORS configuration
- API key masking in UI
- MQTT authentication
- Future: JWT authentication, role-based access control

### Expected Output
Generate a complete, runnable project with:
1. Full React application with all components and hooks
2. Express server with MQTT integration
3. Docker configuration for easy deployment
4. Sample data for testing
5. Documentation and setup instructions
6. Clean, maintainable code with proper error handling
7. Real-time functionality that feels alive and responsive

The application should be production-ready and integrate seamlessly with the existing Alicia monitoring system while providing powerful configuration management capabilities for the Docker microservices ecosystem.