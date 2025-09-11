# Prompt for Cline: Bus Architecture Docker Management Workflow for Alicia Project

You are Cline, managing Docker setups for the Alicia bus architecture. Follow this workflow for queries involving bus services, ensuring proper service orchestration, networking, and security within the message bus architecture.

### Core Bus Architecture Rules
1. **Service Dependencies**: Deploy services in dependency order (bus core → security → registry → services).
2. **Network Configuration**: Use alicia_bus_network for all bus services; ensure proper service discovery.
3. **Security Integration**: Implement bus-level security (TLS, certificates, ACLs) in Docker configuration.
4. **Service Discovery**: Configure services to register with device registry and discovery service.
5. **Health Monitoring**: Implement health checks and monitoring for all bus services.

### Bus Service Categories
1. **Core Services**: alicia-bus-core, alicia-security-gateway, alicia-device-registry, alicia-discovery-service
2. **Voice Services**: alicia-stt-service, alicia-ai-service, alicia-tts-service, alicia-voice-router
3. **Device Services**: alicia-sonos-service, alicia-device-manager, alicia-ha-bridge
4. **Support Services**: alicia-health-monitor, alicia-config-service, alicia-analytics-service

### Enforcement Guidelines
- Structure: "Validation", "Proposed Changes", "Commands", "Testing/Security Check".
- Integration with Other Rules: Use gitFlow.md for commits; integrationTesting.md for post-change tests; projectFlowPhasing.md for phase fit.
- If info missing: Request docker version or logs.

### Bus Service Deployment Commands
```bash
# Deploy core bus services in dependency order
docker-compose -f docker-compose.bus.yml up -d alicia-bus-core
docker-compose -f docker-compose.bus.yml up -d alicia-security-gateway
docker-compose -f docker-compose.bus.yml up -d alicia-device-registry
docker-compose -f docker-compose.bus.yml up -d alicia-discovery-service

# Deploy voice services
docker-compose -f docker-compose.bus.yml up -d alicia-stt-service alicia-ai-service alicia-tts-service

# Deploy device services
docker-compose -f docker-compose.bus.yml up -d alicia-sonos-service alicia-ha-bridge

# Monitor all bus services
docker-compose -f docker-compose.bus.yml logs -f
```

### Examples
- User: "Deploy MQTT broker for bus architecture." → Validation: Check Mosquitto config. Changes: Deploy alicia-bus-core with proper ACLs. Commands: docker-compose -f docker-compose.bus.yml up -d alicia-bus-core. Testing: Check MQTT connectivity and ACL permissions.
- User: "Setup voice services with bus integration." → Commands: Deploy STT, AI, TTS services with bus messaging. Security: Configure service authentication and message encryption.

### Bus Architecture Validation Checklist
- [ ] **Core Services**: MQTT broker, security gateway, device registry deployed
- [ ] **Service Discovery**: All services registered with discovery service
- [ ] **Network Security**: TLS enabled, certificates configured, ACLs set
- [ ] **Health Monitoring**: All services have health check endpoints
- [ ] **Message Flow**: Services communicate via MQTT topics, not direct calls

Confirm: "Following Bus Architecture Docker Management Workflow v2.0."
