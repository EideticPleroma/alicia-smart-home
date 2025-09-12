# Archive - Alicia Bus Architecture

This archive contains historical documentation and files from the previous monolithic implementation that have been superseded by the new bus architecture.

## What's Here

### ✅ **Kept Files**
- `xAI API Key.md` - API key documentation (still relevant)

### ❌ **Removed Files**
The following files were removed as they are no longer relevant with the bus architecture:

#### **Outdated Implementation Guides**
- `ALICIA_MONITORING_APP_ROADMAP.md` - Replaced by bus architecture monitoring
- `GROK_INTEGRATION_GUIDE.md` - Now handled by `grok-integration` service
- `STT_GROK_INTEGRATION_GUIDE.md` - Superseded by bus services
- `ALICIA_PERSONALITY_GUIDE.md` - Now handled by `personality-system` service
- `GROK4_INTEGRATION_GUIDE.md` - Superseded by bus services

#### **Old Implementation Code**
- `configure_grok_api.py` - Old Grok setup script
- `demo_stt_grok_integration.py` - Old demo script
- `setup_grok_integration.py` - Old setup script
- `simple_tts_test.py` - Old test script
- `requirements_voice_test.txt` - Old requirements

#### **Outdated Docker Configs**
- `docker-compose.sonos-fixed.yml` - Old Sonos config
- `docker-compose.sonos.yml` - Old Sonos config
- `Dockerfile.sonos` - Old Sonos Dockerfile

#### **Old Documentation**
- `DEPLOYMENT_SUCCESS.md` - Old deployment info
- `MQTT_FIXES_SUMMARY.md` - Old MQTT fixes
- `TECHNOLOGY_VERSIONS_REFERENCE.md` - Outdated versions
- `STT_MONITORING_README.md` - Old monitoring docs
- `MICROPHONE_CONFIGURATION_README.md` - Old mic config
- `CLINE_CORRECTION_PROMPT.md` - Implementation-specific
- `CLINE_MICROPHONE_CONFIGURATION_PROMPT.md` - Implementation-specific
- `CLINE_PROMPT_en-gb-jenny_implementation.md` - Implementation-specific

#### **Old Scripts**
- `fix-sonos-firewall.bat` - Old firewall fix
- `network-setup.ps1` - Old network setup
- `start-audio-server.ps1` - Old audio server

## Current Architecture

The new bus architecture is documented in:
- `ALICIA_BUS_ARCHITECTURE_COMPLETE_REPORT.md` - Complete implementation report
- `docker-compose.bus.yml` - Current service orchestration
- `bus-services/` - Individual microservices
- `README.md` - Updated project overview

## Migration

If you need to reference old implementation details, they may be available in git history. The new bus architecture provides all the same functionality with better scalability, maintainability, and performance.
