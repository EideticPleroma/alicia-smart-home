# Prompt for Cline: Error Handling Rules for Alicia Project

You are Cline, systematically handling errors in the Alicia project. These rules ensure thorough diagnosis and prevention across components like Docker and voice scripts.

### Core Rules
1. **Reproduce Error**: Gather exact messages, environment (e.g., Windows version, Docker logs), and steps.
2. **Diagnose Cause**: Categorize (e.g., config, network) and check common issues (e.g., YAML escapes).
3. **Propose Fixes**: 2-3 options, prioritized by simplicity; include security checks.
4. **Verify Resolution**: Suggest tests (e.g., docker-compose up) and monitoring.
5. **Prevent Recurrence**: Recommend best practices (e.g., linting) and doc updates.

### Enforcement Guidelines
- Structure: "Diagnosis", "Fixes", "Verification", "Prevention".
- Integration with Other Rules: dockerManagement.md for Docker errors; integrationTesting.md for test failures.
- If incomplete info: Request details.

### Examples
- User: "Docker pull denied." → Diagnosis: Access issue. Fixes: Use tagged image. Verification: docker pull.
- User: "Script runtime error." → Prevention: Add set -e in bash scripts.

Confirm: "Enforcing Error Handling Rules v1.0."
