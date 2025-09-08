# Prompt for Cline: Project Flow Phasing Rules for Alicia Project

You are Cline, aligning tasks with Alicia's phases (from README.md: Phase 1 Prototype, Phase 2 Family, Phase 3 Enterprise). These rules provide a phased framework, checking dependencies and resources for scalable development.

### Core Rules
1. **Phase Mapping**: Classify queries (e.g., initial voice setup = Phase 1; scaling to multiple devices = Phase 3).
2. **Dependencies and Resources**: List prereqs (e.g., Docker running) and allocate resources (e.g., 2GB RAM for Phase 1 on Pi; Kubernetes for Phase 3).
3. **Timelines and Milestones**: Suggest realistic timelines (e.g., 1 week for Phase 1 tasks) and track via issues/changelog.
4. **Security/Privacy**: Ensure phase-appropriate checks (e.g., local-only in Phase 1 for privacy; encrypted backups in Phase 3).
5. **Windows Considerations**: Note OS-specific tweaks (e.g., WSL for Docker stability in prototypes).

### Enforcement Guidelines
- Start with "Phase Alignment: [Phase]. Dependencies: [List]. Timeline: [Estimate]."
- Integration with Other Rules: Use gitFlow.md for branching; integrationTesting.md for verification; phaseDeployment.md for execution.
- If misaligned: "This fits better in Phase [X]; adjust plan accordingly."

### Examples
- User: "Integrate Postgres with voice-processing." → Alignment: Phase 1. Dependencies: Docker installed, alicia_network. Timeline: 2-3 days. Plan: Test connection via psql in container.
- User: "Add enterprise scaling." → Alignment: Phase 3. Resources: Add replicas in docker-compose. Security: Implement JWT auth.

Confirm: "Enforcing Project Flow Phasing Rules v1.1."