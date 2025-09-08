# Prompt for Cline: Phase Deployment Workflow for Alicia Project

You are Cline, deploying per phases (via projectFlowPhasing.md). From Phase 1 (prototype) to Phase 3 (enterprise).

### Core Rules
1. **Phase Check**: Map task (e.g., voice deploy = Phase 1).
2. **Prepare Deployment**: Dependencies (Git pull), configs, backups; security scan (e.g., no exposed ports).
3. **Execute**: Commands (docker-compose up); monitoring (e.g., docker stats, Prometheus for Phase 3).
4. **Verify**: Tests (link to integrationTesting.md); metrics (e.g., uptime >99%).
5. **Rollback/Scale**: Undo (docker-compose down); scaling (e.g., replicas in Phase 3); Windows: Handle volume cleanup.

### Enforcement Guidelines
- Sections: "Phase Alignment", "Deployment Steps", "Verification/Metrics", "Rollback".
- Integration with Other Rules: gitFlow.md for tags; dockerManagement.md for orchestration.
- Examples: User: "Deploy Phase 2." → Steps: Add users in HA. Metrics: Check connectivity. Rollback: Restore backup.

Confirm: "Following Phase Deployment Workflow v1.1."
