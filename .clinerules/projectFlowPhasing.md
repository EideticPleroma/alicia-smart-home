# Prompt for Cline: Bus Architecture Phasing Rules for Alicia Project

You are Cline, aligning tasks with Alicia's bus architecture phases. These rules provide a phased framework for implementing the message bus architecture, ensuring proper service integration and scalability.

### Core Bus Architecture Phases
1. **Phase 1: Bus Core Infrastructure** (Weeks 1-2): MQTT broker, security gateway, device registry, discovery service
2. **Phase 2: Voice Pipeline Migration** (Weeks 3-4): STT, AI, TTS services with bus integration
3. **Phase 3: Device Integration** (Weeks 5-6): Sonos, sensors, Home Assistant bridge services
4. **Phase 4: Advanced Features** (Weeks 7-8): Analytics, load balancing, performance optimization

### Core Rules
1. **Phase Mapping**: Classify queries by bus architecture phase (e.g., MQTT setup = Phase 1; voice service migration = Phase 2).
2. **Service Dependencies**: List bus service prerequisites (e.g., bus core → security → registry → services).
3. **Message Flow Design**: Ensure proper topic hierarchy and message routing for each phase.
4. **Security Integration**: Implement bus-level security (authentication, encryption, ACLs) appropriate to phase.
5. **Service Discovery**: All services must register with device registry and implement health monitoring.

### Enforcement Guidelines
- Start with "Phase Alignment: [Phase]. Dependencies: [List]. Timeline: [Estimate]."
- Integration with Other Rules: Use gitFlow.md for branching; integrationTesting.md for verification; phaseDeployment.md for execution.
- If misaligned: "This fits better in Phase [X]; adjust plan accordingly."

### Examples
- User: "Setup MQTT broker for voice services." → Alignment: Phase 1. Dependencies: Docker, bus-config directory. Timeline: 1-2 days. Plan: Deploy alicia-bus-core, configure Mosquitto, setup authentication.
- User: "Migrate STT service to bus architecture." → Alignment: Phase 2. Dependencies: Bus core, security gateway, device registry. Timeline: 3-4 days. Plan: Create STT service wrapper, implement bus messaging, register with discovery service.
- User: "Add Sonos integration via bus." → Alignment: Phase 3. Dependencies: Bus core, device registry, Sonos service. Timeline: 2-3 days. Plan: Create Sonos service wrapper, implement device discovery, setup MQTT topics.

### Bus Architecture Phase Checklist
- [ ] **Phase 1**: MQTT broker, security gateway, device registry, discovery service deployed
- [ ] **Phase 2**: Voice services (STT, AI, TTS) migrated to bus architecture
- [ ] **Phase 3**: Device services (Sonos, sensors, HA bridge) integrated with bus
- [ ] **Phase 4**: Analytics, load balancing, performance optimization implemented

Confirm: "Enforcing Bus Architecture Phasing Rules v2.0."