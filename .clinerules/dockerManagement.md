# Prompt for Cline: Docker Management Workflow for Alicia Project

You are Cline, managing Docker setups in the Alicia project. Follow this workflow for queries involving docker-compose.yml files (e.g., in postgres/, home-assistant/, voice-processing/), ensuring validation and scalability.

### Core Rules
1. **Validate Config**: Run 'docker-compose config' and yamllint for checks; on Windows, verify UTF-8 encoding and LF line endings.
2. **Handle Errors**: Diagnose (e.g., \$ escapes, pull denials) with fixes like specific tags (e.g., eclipse-mosquitto:2.0) or volume permissions (icacls on Windows).
3. **Orchestrate Services**: Use commands for multi-dir (e.g., docker-compose -f postgres/docker-compose.yml up -d); consider dependencies and networks (alicia_network).
4. **Best Practices**: Official images, healthchecks, volumes; add security (e.g., no exposed passwords, use secrets).
5. **Updates and Scaling**: Safe pulls (docker-compose pull --ignore-pull-failures); phase notes (e.g., add replicas for Phase 3).

### Enforcement Guidelines
- Structure: "Validation", "Proposed Changes", "Commands", "Testing/Security Check".
- Integration with Other Rules: Use gitFlow.md for commits; integrationTesting.md for post-change tests; projectFlowPhasing.md for phase fit.
- If info missing: Request docker version or logs.

### Examples
- User: "Fix image pull in voice-processing." → Validation: Denied access. Changes: Use tagged image. Commands: Edit yml to ahmetoner/whisper-asr-webservice:1.0; docker-compose pull. Testing: docker-compose up -d; check logs.
- User: "Orchestrate all for Phase 1." → Commands: Script to up postgres, then voice-processing; Security: Mask passwords in env.

Confirm: "Following Docker Management Workflow v1.1."
