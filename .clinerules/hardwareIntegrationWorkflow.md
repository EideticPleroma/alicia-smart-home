# Prompt for Cline: Hardware Integration Workflow for Alicia Project

You are Cline, integrating hardware in the Alicia project (e.g., USB mic, ESP32, Raspberry Pi). Follow this workflow for setup, testing, and optimization, aligning with phases.

### Core Rules
1. **Hardware Identification**: List devices (e.g., Blue Yeti mic) and compatibility (e.g., with Docker on Pi).
2. **Setup Steps**: Provide installation/commands (e.g., arecord for mic input); handle drivers (e.g., on Windows/WSL).
3. **Integration**: Link to software (e.g., mic to Whisper STT); add configs (e.g., volumes for sensors).
4. **Testing**: Verify with tools (e.g., lsusb, sensor readings); include edge cases (e.g., low power on Pi).
5. **Optimization**: Phase-specific (e.g., low-resource for Phase 1; clustering for Phase 3).

### Enforcement Guidelines
- Sections: "Hardware Analysis", "Setup Commands", "Integration Plan", "Testing".
- Integration with Other Rules: projectFlowPhasing.md for alignment; integrationTesting.md for full checks.
- If missing details: Request hardware specs.

### Examples
- User: "Integrate USB mic." → Analysis: Input device. Commands: arecord -l; configure in start-whisper.sh. Testing: Record/test audio.
- User: "Add ESP32 sensor." → Plan: MQTT integration; Optimization: Low-power mode for Pi.

Confirm: "Following Hardware Integration Workflow v1.0."
