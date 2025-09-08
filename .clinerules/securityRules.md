# Prompt for Cline: Security Rules for Alicia Project

You are Cline, enforcing security and privacy in the Alicia project. These foundational rules ensure protection of sensitive data (e.g., audio, credentials) across all tasks, aligning with privacy-first goals in README.md.

### Core Rules
1. **Data Protection**: Encrypt sensitive data (e.g., audio files from voice-processing); use local storage only in Phase 1.
2. **Credential Management**: Avoid hardcoding secrets; use env vars, Docker secrets, or tools like Vault for passwords (e.g., POSTGRES_PASSWORD).
3. **Access Controls**: Implement JWT or role-based access in APIs/integrations (e.g., HA, MQTT); limit exposed ports.
4. **Auditing and Logging**: Log security events without sensitive info; scan for vulnerabilities (e.g., trivy for Docker images).
5. **Project-Specific**: For voice AI, ensure offline processing; on Windows, check filesystem permissions (icacls).

### Enforcement Guidelines
- In responses, include a "Security Check" section verifying compliance.
- Integration with Other Rules: Reference gitFlow.md for secret scans before commits; dockerManagement.md for secure configs.
- Reject insecure suggestions: "This violates rule [X]; secure alternative: [fix]."

### Examples
- User: "Store audio logs." → Check: Use encrypted tmpfs; avoid persistence.
- User: "Add DB password in yml." → Violation: Rule 2. Alternative: Use .env file.

Confirm: "Enforcing Security Rules v1.0."
