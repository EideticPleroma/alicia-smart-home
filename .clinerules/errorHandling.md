# Prompt for Cline: Error Handling and Troubleshooting Rules

You are Cline, systematically handling errors in the Alicia Smart Home AI Assistant project. These consolidated rules ensure thorough diagnosis and prevention across all components including Docker, voice processing, MQTT, and Home Assistant integrations.

### Core Rules
1. **Reproduce Error**: Gather exact error messages, environment details (OS, Docker version, Python version), and precise reproduction steps.
2. **Diagnose Root Cause**: Categorize errors (syntax, config, network, permissions, resource constraints) and check common pitfalls:
   - YAML escaping issues in docker-compose files
   - Permission problems with device access (microphones, speakers)
   - Network connectivity for MQTT/Home Assistant
   - Model loading failures in voice processing
   - Windows-specific path and encoding issues
3. **Propose Fixes**: Provide 2-3 prioritized solutions with specific commands, considering:
   - Simplicity and speed of implementation
   - Security implications
   - Minimal disruption to running services
4. **Verify Resolution**: Test fixes with appropriate commands and monitor for edge cases:
   - `docker-compose config` for YAML validation
   - `docker logs` for container issues
   - `python -c "import [module]"` for import problems
   - Device connectivity tests
5. **Prevent Recurrence**: Implement best practices and monitoring:
   - Add linting tools (yamllint, shellcheck, flake8)
   - Implement health checks in docker-compose
   - Add error handling with try/catch blocks
   - Create monitoring dashboards
   - Update documentation with troubleshooting guides

### Project-Specific Error Categories
- **Docker Issues**: Container startup, networking, volume permissions
- **Voice Processing**: Model loading, audio device access, TTS failures
- **MQTT Communication**: Broker connectivity, topic permissions, message parsing
- **Home Assistant**: Integration setup, entity discovery, automation triggers
- **BDD Testing**: Test framework setup, fixture configuration, assertion failures

### Enforcement Guidelines
- **Response Structure**: Always use "Diagnosis", "Fixes", "Verification", "Prevention" sections
- **Information Gathering**: Request missing details before proceeding with solutions
- **Integration**: Reference related rules (dockerManagement.md, integrationTesting.md, securityRules.md)
- **Documentation**: Suggest updates to troubleshooting guides and error reference docs

### Examples
- **Docker Pull Denied**: Diagnosis: Authentication/network issue → Fixes: Use tagged images, check registry access → Verification: `docker pull [image]` → Prevention: Implement image caching strategy
- **Microphone Access Error**: Diagnosis: Permission/device issue → Fixes: Check device permissions, restart services → Verification: `arecord -l` → Prevention: Add device permission checks in startup scripts
- **MQTT Connection Failed**: Diagnosis: Network/broker configuration → Fixes: Verify broker URL, check firewall rules → Verification: `mosquitto_sub` test → Prevention: Implement connection retry logic

### Recent Project Achievements
- ✅ Implemented comprehensive BDD test framework with proper error handling
- ✅ Consolidated Cline rules across multiple branches
- ✅ Enhanced .gitignore with comprehensive local file protection
- ✅ Established GitFlow branch structure with test/ branch for BDD development

### Next Steps Integration
- Integrate error monitoring with Home Assistant dashboards
- Add automated error reporting to development workflow
- Create error pattern recognition for common issues
- Implement proactive health checks in Phase 3 enterprise deployment

Confirm: "Enforcing consolidated error handling rules v2.0."
