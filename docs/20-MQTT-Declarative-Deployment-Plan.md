# MQTT Declarative Deployment Implementation Plan

## Overview
This document outlines the phased implementation plan for creating a fully declarative, one-click deployment of MQTT + Home Assistant integration. The key insight is that MQTT integration cannot be defined in `configuration.yaml` - it must be configured via HA's REST API.

## Key Principles
- **No Manual UI Configuration**: Everything must be automated
- **Version Control**: All configurations in Git
- **Security First**: No hardcoded credentials
- **Idempotent**: Scripts can run multiple times safely
- **Discovery-Based**: Use MQTT discovery for automatic device detection

## Implementation Phases

### Phase 1: Configuration Setup
**Goal:** Configure YAML files for entities and discovery (no MQTT connection config)

**Tasks:**
1. **Clean HA Configuration**
   - Remove any `mqtt:` section from `configuration.yaml` (not supported)
   - Keep only MQTT entity definitions (sensors, switches, etc.)

2. **Configure MQTT Discovery**
   - Add discovery settings to `configuration.yaml`
   - Set discovery prefix: `mqtt: discovery: true, discovery_prefix: homeassistant`
   - Enable auto-discovery for devices

3. **Update Environment Variables**
   - Ensure MQTT-related env vars in `home-assistant/.env`
   - Add discovery-specific variables if needed

**Success Criteria:**
- ✅ `configuration.yaml` contains no MQTT connection config
- ✅ Discovery is enabled
- ✅ Entity definitions are preserved

### Phase 2: Security & Authentication
**Goal:** Set up secure MQTT authentication for all users

**Tasks:**
1. **Generate MQTT Passwords**
   - Create secure passwords for all ACL users:
     - `alicia` (HA user)
     - `esp32_device` (sensors/actuators)
     - `voice_assistant` (voice processing)
     - `mobile_app` (remote control)
     - `sonos_speaker` (audio devices)
   - Use `mosquitto_passwd` for secure hashing
   - Update `mqtt/config/passwords`

2. **Verify ACL Permissions**
   - Review `mqtt/config/acl` for completeness
   - Ensure topic permissions match use cases
   - Test ACL rules against planned scenarios

**Success Criteria:**
- ✅ All users have secure passwords
- ✅ ACL permissions are appropriate
- ✅ No anonymous access allowed

### Phase 3: Automation Scripts
**Goal:** Create comprehensive HA MQTT configuration via REST API

**Tasks:**
1. **Create HA MQTT Setup Script**
   - Use HA REST API to add MQTT integration
   - Endpoint: `POST /api/config/config_entries/flow`
   - Include broker details, credentials, discovery settings
   - Handle authentication and error cases
   - Make script idempotent (check if already configured)

2. **Create Docker Init Script**
   - Bash/Python script to run after HA container starts
   - Wait for HA API availability (health check)
   - Execute MQTT configuration script
   - Log success/failure with timestamps

3. **Update Docker Compose**
   - Add init script to HA service: `command: ["sh", "-c", "/init/setup-mqtt.sh && homeassistant"]`
   - Ensure startup order: MQTT → HA → init script
   - Add health checks for verification

**Success Criteria:**
- ✅ Script configures MQTT via HA API
- ✅ Idempotent execution
- ✅ Proper error handling and logging

### Phase 4: Integration & Wiring
**Goal:** Connect components via discovery and API

**Tasks:**
1. **Configure MQTT Discovery Topics**
   - Set up discovery topics for devices: `homeassistant/sensor/...`
   - Define discovery payload templates
   - Ensure devices publish discovery messages on connect

2. **Wire MQTT Entities in HA Config**
   - Keep entity definitions in YAML for static devices
   - Add availability topics: `availability_topic: "homeassistant/sensor/+/status"`
   - Include device classes and icons for better UX

3. **Update Network Configuration**
   - Verify `alicia_network` bridge network
   - Ensure all services communicate via network
   - Test inter-container connectivity

**Success Criteria:**
- ✅ Devices auto-discover via MQTT
- ✅ Static entities work alongside discovered ones
- ✅ Network communication verified

### Phase 5: Testing & Validation
**Goal:** Verify one-click deployment works end-to-end

**Tasks:**
1. **Test Docker Compose Deployment**
   - Run `docker-compose down && docker-compose up -d`
   - Verify all services start successfully
   - Check container logs for errors

2. **Validate MQTT Connection**
   - Test HA can connect to MQTT broker
   - Verify authentication works for all users
   - Check topic permissions with test publishes

3. **Test Device Integration**
   - Simulate MQTT device publishing discovery messages
   - Verify HA creates entities automatically
   - Test bidirectional communication (commands/responses)

4. **Performance & Security Testing**
   - Load test MQTT broker with multiple clients
   - Verify no security vulnerabilities
   - Check resource usage and memory consumption

**Success Criteria:**
- ✅ `docker-compose up -d` deploys full stack
- ✅ HA automatically connects to MQTT
- ✅ All entities appear without manual config
- ✅ MQTT authentication works for all users
- ✅ No hardcoded secrets in repository

## Rollback Plan
- Stop all services: `docker-compose down`
- Reset HA config: Remove MQTT integration via UI if needed
- Clean volumes: `docker volume prune` for fresh start
- Reset MQTT data: Remove `mqtt/data/` and `mqtt/log/`

## Files to Create/Modify
- `docs/20-MQTT-Declarative-Deployment-Plan.md` (this file)
- `home-assistant/config/configuration.yaml` (remove MQTT config, add discovery)
- `mqtt/config/passwords` (add user passwords)
- `home-assistant/setup-mqtt.sh` (new script)
- `home-assistant/docker-compose.yml` (add init script)
- `home-assistant/.env` (MQTT credentials)

## Dependencies
- Docker Compose
- Home Assistant API access
- Mosquitto MQTT broker
- Network connectivity between containers

## Timeline Estimate
- Phase 1: 30 minutes
- Phase 2: 45 minutes
- Phase 3: 2 hours
- Phase 4: 1 hour
- Phase 5: 1 hour
- **Total: ~5 hours**

## Risk Mitigation
- Test each phase incrementally
- Keep backups of working configurations
- Use version control for all changes
- Document all assumptions and dependencies

---
**Status:** Phase 5 - Final Testing & Validation
**Last Updated:** 2025-01-09
**Version:** 1.4

## Progress Update
- ✅ **Phase 1 Complete**: HA configuration cleaned, MQTT discovery enabled
- ✅ **Phase 2 Complete**: All MQTT user passwords generated (alicia, voice_assistant, mobile_app, sonos_speaker)
- ✅ **Phase 3 Complete**: HA MQTT setup script created and executing
- ✅ **Phase 4 Complete**: MQTT discovery test script and documentation created
- 🔄 **Phase 5 In Progress**: Running full deployment and validation tests

## Files Created/Modified (Phase 4)
- `mqtt-testing/scripts/mqtt-discovery-test.py` (new test script)
- `docs/21-MQTT-Discovery-Testing.md` (new testing guide)
