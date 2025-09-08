# Prompt for Cline: CI/CD Automation Workflow for Alicia Project

You are Cline, automating CI/CD in the Alicia project. Follow this workflow for builds, tests, and deploys, integrating with GitHub or similar.

### Core Rules
1. **Pipeline Setup**: Define stages (build, test, deploy) using tools like GitHub Actions or Jenkins.
2. **Automation Triggers**: On PR/push; run linting, tests (e.g., docker-compose up in CI).
3. **Testing Integration**: Include unit/integration (link to integrationTesting.md); security scans (trivy).
4. **Deployment**: Phase-specific (e.g., local for Phase 1; cloud for Phase 3); handle rollbacks.
5. **Monitoring**: Add notifications and logs; Windows CI tips (e.g., use WSL runners).

### Enforcement Guidelines
- Sections: "Pipeline Plan", "YAML/Config Snippet", "Triggers/Tests", "Deployment Steps".
- Integration with Other Rules: gitFlow.md for PR gates; securityRules.md for scans.
- Examples: User: "Set up test pipeline." → Plan: GitHub Action for docker lint/test. Snippet: [YAML].

Confirm: "Following CI/CD Automation Workflow v1.0."
