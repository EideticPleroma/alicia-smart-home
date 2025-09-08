# Home Assistant Docker Setup Guide for Alicia Project

This document provides a structured guide to setting up Home Assistant (HA) in Docker for the Alicia/GrokHome project. It's organized into clear sections with prompts and steps to facilitate processing by Cline (e.g., for code generation, analysis, or automation). Each section includes objectives, detailed instructions, and verification steps.

## 1. Overview and Objectives
**Objective**: Establish a containerized Home Assistant instance as the core software layer for voice processing, AI integration, and device control in the Alicia system.

**Key Benefits**:
- Local processing for privacy.
- Easy integration with existing components (e.g., PostgreSQL, MQTT, Sonos).
- Scalable from prototype to enterprise.

**Prompt for Cline**: Analyze this setup for compatibility with Raspberry Pi hardware and suggest optimizations for low-resource environments.

## 2. Prerequisites
**Requirements**:
- Docker and Docker Compose installed.
- Windows OS (as per project info) with Docker Desktop running.
- Project root: `D:\Projects\Alicia\Alicia (v1)`.
- Allocate at least 2GB RAM in Docker settings.

**Prompt for Cline**: Generate a script to check and install prerequisites on Windows.

## 3. Directory Structure
Create the following structure in `home-assistant/`:
```
home-assistant/
├── docker-compose.yml  # Configuration file
├── config/             # Persistent HA configuration directory (create if needed)
└── Home-Assistant-Setup.md  # This guide
```

**Prompt for Cline**: Validate this structure against best practices for Docker projects and propose additions for logging or backups.

## 4. Docker Compose Configuration
Use this `docker-compose.yml` file (already created):

```yaml
version: '3'

services:
  homeassistant:
    container_name: homeassistant
    image: "ghcr.io/home-assistant/home-assistant:stable"
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```

**Explanation**:
- **Image**: Official stable HA image.
- **Volumes**: Persists config and syncs timezone.
- **Network**: Host mode for device discovery.
- **Privileged**: For hardware access.

**Prompt for Cline**: Modify this YAML to integrate with an existing 'alicia_network' from another docker-compose file, ensuring PostgreSQL connectivity.

## 5. Step-by-Step Setup Instructions
Follow these steps in sequence:

1. **Navigate to Directory**:
   - Command: `cd home-assistant`

2. **Create Config Directory** (if not exists):
   - Command: `mkdir config`

3. **Start the Container**:
   - Command: `docker-compose up -d`
   - Expected Output: Container starts; initial setup may take 5-10 minutes.

4. **Access HA Interface**:
   - URL: `http://localhost:8123`
   - Steps: Create admin user, set location/timezone, complete wizard.

5. **Verify Running Status**:
   - Command: `docker-compose logs -f homeassistant`
   - Check: Look for "Starting Home Assistant" and port 8123 listener.

**Prompt for Cline**: Automate these steps into a single bash script, including error handling for common Windows Docker issues.

## 6. Post-Setup Configurations
**Integrations to Add via HA UI**:
- MQTT for IoT (e.g., ESP32 sensors).
- Sonos for audio output.
- PostgreSQL for database (connect to existing alicia_db).
- Whisper/Porcupine for voice (custom add-ons).

**Updates**:
- Command: `docker-compose pull && docker-compose up -d`

**Prompt for Cline**: Outline YAML configurations for adding MQTT and Sonos integrations in HA, including any required environment variables.

## 7. Troubleshooting
**Common Issues**:
- **Port Conflicts**: Check with `netstat -ano | findstr :8123`.
- **Resource Limits**: Increase Docker RAM/CPU allocation.
- **Network Issues**: If host mode fails, switch to a bridged network and expose ports.

**Prompt for Cline**: Create a diagnostic flowchart in Mermaid syntax for troubleshooting HA startup errors.

## 8. Next Steps in Alicia Project
- Integrate AI layer (e.g., Ollama for LLMs).
- Set up voice engine (Whisper STT, Piper TTS).
- Test with existing hardware (USB mic, Sonos, ESP32).

**Prompt for Cline**: Based on the Alicia README, generate a phased implementation plan for integrating HA with the full tech stack, including timelines and dependencies.

## 9. Resources
- [Home Assistant Docker Docs](https://www.home-assistant.io/installation/linux#install-home-assistant-container)
- [HA Integrations](https://www.home-assistant.io/integrations/)

**Prompt for Cline**: Summarize key HA documentation links and suggest custom add-ons for voice AI in the context of this project.

This structure ensures organized processing: Use the prompts to guide Cline in generating outputs, scripts, or enhancements.
