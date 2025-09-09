# Prompt for Cline: Integration Testing Workflow for Alicia Project

You are Cline, testing integrations (e.g., Postgres + voice-processing). Cover dependencies, phases, and automation.

### Core Rules
1. **Identify Scope**: List components/interactions (e.g., MQTT in voice flow).
2. **Setup Tests**: Prereqs (services up); tools (docker logs, curl, pytest).
3. **Run Tests**: Step-by-step (e.g., simulate mic input); include security (e.g., check for leaks) and metrics (e.g., latency <2s).
4. **Handle Failures**: Diagnose/retry; Windows: Use PowerShell equivalents (e.g., netstat).
5. **Phase-Specific**: Local for Phase 1; load tests (e.g., locust) for Phase 3.

### Enforcement Guidelines
- Structure: "Test Plan", "Commands", "Expected Outputs/Metrics", "Failure Handling".
- Integration with Other Rules: gitFlow.md for pre-merge; dockerManagement.md for setups.
- Examples with metrics: User: "Test voice pipeline." → Plan: Start services. Commands: docker-compose up; curl Whisper API. Metrics: Response time <1s.

Confirm: "Following Integration Testing Workflow v1.1."
