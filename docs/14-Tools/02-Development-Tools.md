# Cline Prompt: Alicia Bus Architecture Migration

## Project Overview
You are tasked with migrating the Alicia Voice Assistant system from its current point-to-point MQTT architecture to a comprehensive bus-based system. This migration will enable plug-and-play device integration, consolidated networking, and enhanced security.

## Reference Documentation
**PRIMARY SOURCE OF TRUTH**: `BUS_ARCHITECTURE_MIGRATION_OUTLINE.md`
**TECHNICAL SPECIFICATIONS**: `BUS_ARCHITECTURE_IMPLEMENTATION_GUIDE.md`
**PHASE-BY-PHASE IMPLEMENTATION**: `BUS_ARCHITECTURE_PHASE_GUIDES.md`
**TECHNOLOGY VERSIONS**: `TECHNOLOGY_VERSIONS_REFERENCE.md`

## Technology Stack - Latest Stable Versions (2025)

### Core Infrastructure
- **Docker**: 24.0.7+ (latest stable)
- **Docker Compose**: 2.21.0+ (latest stable)
- **Python**: 3.11.7+ (latest stable 3.11.x)
- **Node.js**: 20.10.0+ (LTS)
- **PostgreSQL**: 16.1+ (latest stable)

### Message Bus & Communication
- **Eclipse Mosquitto**: 2.0.18+ (latest stable 2.0.x)
- **MQTT Protocol**: 5.0 (latest standard)
- **Paho MQTT Client**: 1.6.1+ (Python), 1.0.15+ (JavaScript)

### Voice Processing
- **Whisper**: 20231117+ (latest OpenAI Whisper)
- **Wyoming Protocol**: 1.5.0+ (latest stable)
- **Piper TTS**: 1.2.0+ (latest stable)
- **Rhasspy Wyoming**: 1.5.0+ (latest stable)

### AI & Machine Learning
- **OpenAI API**: 1.3.0+ (latest Python client)
- **Grok API**: Latest xAI API (as of 2025)
- **Transformers**: 4.36.0+ (Hugging Face)
- **PyTorch**: 2.1.0+ (latest stable)

### Web Frameworks & APIs
- **FastAPI**: 0.104.1+ (latest stable)
- **Uvicorn**: 0.24.0+ (latest stable)
- **React**: 18.2.0+ (latest stable)
- **TypeScript**: 5.3.0+ (latest stable)

### Security & Authentication
- **JWT**: 2.8.0+ (PyJWT)
- **Cryptography**: 41.0.8+ (Python)
- **TLS**: 1.3 (latest standard)
- **OpenSSL**: 3.0.12+ (latest stable)

### Monitoring & Observability
- **Prometheus**: 2.47.0+ (latest stable)
- **Grafana**: 10.2.0+ (latest stable)
- **Redis**: 7.2.0+ (latest stable)
- **InfluxDB**: 2.7.0+ (latest stable)

### Home Automation
- **Home Assistant**: 2024.1.0+ (latest stable)
- **Sonos API**: Latest Sonos Control API
- **ESP32**: ESP-IDF 5.1+ (latest stable)

## Current System Context
- **Project Location**: `D:\Projects\Alicia\Alicia (v1)`
- **Current Architecture**: Point-to-point MQTT with direct service connections
- **Key Services**: Whisper STT, Grok AI, Piper TTS, Sonos Bridge, Home Assistant
- **Monitoring**: Alicia Monitoring App (React + FastAPI)
- **Containerization**: Docker Compose with multiple services

## Available Tools
- **Docker MCP**: Available for container management, log reading, and service monitoring
- **File Operations**: Full read/write access to project files
- **Terminal Commands**: For system operations and testing
- **Code Analysis**: For understanding existing implementations

## Migration Objectives

### Primary Goals
1. **Unified Message Bus**: Single MQTT broker as central communication hub
2. **Plug-and-Play Devices**: Automatic device discovery and registration
3. **Consolidated Networking**: Single network endpoint for all communication
4. **Enhanced Security**: Centralized authentication and message encryption
5. **STT Pipeline Integration**: Move STT processing to bus-based architecture

### Success Criteria
- All services communicate exclusively through the bus
- New devices can be added without code changes
- Centralized security and monitoring
- Zero-downtime migration
- Performance maintained or improved

## Implementation Approach

### Phase-Based Migration
1. **Phase 1**: Bus Core Infrastructure (Weeks 1-2)
2. **Phase 2**: Voice Pipeline Migration (Weeks 3-4)
3. **Phase 3**: Device Integration (Weeks 5-6)
4. **Phase 4**: Advanced Features (Weeks 7-8)

### Parallel Implementation Strategy
- Run new bus architecture alongside existing system
- Gradual migration of services one by one
- A/B testing for critical components
- Rollback capability at each phase

## Key Technical Requirements

### Message Bus Architecture
- **Core Components**: MQTT Broker, Security Gateway, Device Registry, Discovery Service
- **Message Format**: Standardized JSON with security headers
- **Topic Structure**: Hierarchical topics for system, voice, devices, and integration
- **Security**: Certificate-based authentication, message encryption, access control

### Device Discovery Protocol
- Automatic device registration and capability announcement
- Self-describing device schemas
- Dynamic capability updates
- Hot-swappable device connections

### STT Pipeline Integration
- Single STT service publishing to bus
- Multiple STT engines as plugins
- Automatic engine selection
- Load balancing across instances

## Docker MCP Integration
Throughout the migration process, you will:
- Use Docker MCP to monitor container logs and health
- Manage service deployments and configurations
- Monitor performance metrics and resource usage
- Debug issues through container inspection
- Validate service connectivity and functionality

## Configuration Management
- Environment-specific configurations (dev, staging, prod)
- Centralized configuration service
- Dynamic configuration updates
- Validation and testing tools

## Security Considerations
- Device certificate management
- Message encryption (TLS 1.3)
- Access control lists (ACLs)
- Rate limiting and throttling
- Audit logging and monitoring

## Performance Requirements
- Voice command processing: < 500ms
- Device control response: < 100ms
- Audio delivery: < 200ms
- System health checks: < 50ms
- 1000+ messages per second throughput
- 99.9% uptime availability

## Monitoring and Observability
- Real-time service health dashboard
- Message flow tracking and tracing
- Performance metrics and analytics
- Alert management and notification
- Historical data and trending

## Migration Constraints
- Maintain existing functionality during migration
- Zero-downtime deployment where possible
- Preserve all current integrations
- Maintain backward compatibility during transition
- Ensure rollback capability at each phase

## Quality Assurance
- Comprehensive testing at each phase
- Performance benchmarking
- Security validation
- Integration testing
- User acceptance testing

## Documentation Requirements
- Update all existing documentation
- Create new architecture diagrams
- Document new APIs and interfaces
- Provide migration guides
- Create troubleshooting documentation

## Success Metrics
- Message processing latency improvements
- Service availability and uptime
- Device discovery time
- Development velocity
- Security incident reduction
- User experience improvements

## Instructions for Implementation
1. **Read and understand** the reference documentation thoroughly
2. **Use latest stable versions** as specified in TECHNOLOGY_VERSIONS_REFERENCE.md
3. **Analyze current system** using available tools and file access
4. **Follow phase-by-phase implementation** as outlined in the guides
5. **Use Docker MCP** for container management and monitoring
6. **Validate each phase** before proceeding to the next
7. **Document all changes** and maintain version control
8. **Test thoroughly** at each step with rollback capability
9. **Monitor performance** and adjust as needed

## Version Requirements
- **ALWAYS use the latest stable versions** specified in TECHNOLOGY_VERSIONS_REFERENCE.md
- **DO NOT use outdated versions** or deprecated implementations
- **Verify version compatibility** before implementing any component
- **Update version references** if newer stable versions become available
- **Test with specified versions** to ensure compatibility

## Emergency Procedures
- Maintain rollback capability at each phase
- Keep existing system running during migration
- Document all changes for easy reversal
- Test rollback procedures before proceeding
- Monitor system health continuously

## Communication Protocol
- Report progress at each phase completion
- Document any deviations from the plan
- Provide detailed logs and metrics
- Report issues immediately with proposed solutions
- Maintain clear audit trail of all changes

Remember: The reference documentation is your source of truth. Follow the detailed implementation guides, use Docker MCP for monitoring, and maintain the highest standards of quality and security throughout the migration process.
