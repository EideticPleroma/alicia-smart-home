# Prompt for Cline: Voice Processing Workflow for Alicia Project

You are Cline, handling voice pipeline tasks in voice-processing/ (e.g., start-porcupine.sh, start-whisper.sh, start-piper.sh, docker-compose.yml). Align with phases and hardware (e.g., USB mic).

### Core Rules
1. **Component Breakdown**: Identify (e.g., wake-word with Porcupine) and dependencies (e.g., MQTT, mic hardware).
2. **Script Management**: Ensure shebangs, set -e, env vars; add logging/security (e.g., encrypt audio temps).
3. **Integration**: Docker isolation (volumes for models); end-to-end with hardware (e.g., arecord for mic input).
4. **Testing**: Commands (e.g., curl for Whisper) plus automated (e.g., pytest for scripts); edge cases (noise, accents).
5. **Optimization**: Phase-specific (e.g., offline Phase 1); Windows tips (e.g., use WSL for audio devices).

### Enforcement Guidelines
- Sections: "Component Analysis", "Steps/Commands", "Integration Plan", "Testing/Security".
- Integration with Other Rules: gitFlow.md for changes; integrationTesting.md for full pipeline; documentationUpdate.md for docs.
- Request details: e.g., mic model.

### Examples
- User: "Debug start-piper.sh." → Analysis: TTS. Steps: Add debug flags. Commands: bash -x start-piper.sh. Testing: echo "Test" | ./start-piper.sh; check output wav.
- User: "Integrate with USB mic." → Plan: Update script with arecord; Security: Ensure no persistent audio storage.

Confirm: "Following Voice Processing Workflow v1.1."
