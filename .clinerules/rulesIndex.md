# Cline Rules and Workflows Index for Alicia Project

This index categorizes the prompts in .clinerules/ into **Rules** (static guidelines for best practices) and **Workflows** (step-by-step processes for tasks). Use this to select and feed into Cline. All are versioned (e.g., v1.1) and integrate with each other for consistency.

## Rules (Foundational Guidelines)
These provide overarching standards, often referenced in workflows.
- **gitFlow.md** (v1.1): Version control and branching rules.
- **projectFlowPhasing.md** (v2.0): Bus architecture phase mapping and dependency checks.
- **busArchitectureRules.md** (v1.0): Core bus architecture principles and service patterns.
- **securityRules.md** (v2.0): Bus architecture security and privacy guidelines.
- **errorHandling.md** (v2.0): Systematic error diagnosis and prevention.
- **codeStyleRules.md** (v2.0): Code formatting and quality standards.
- **windowsEnvironmentRules.md** (v1.0): Windows PowerShell environment and command guidelines.

## Workflows (Action-Oriented Processes)
These guide specific tasks with structured steps.
- **dockerManagement.md** (v2.0): Bus architecture Docker service management and orchestration.
- **voiceProcessing.md** (v2.0): Bus architecture voice pipeline components and integrations.
- **busServiceManagement.md** (v1.0): Managing bus services, discovery, and health monitoring.
- **documentFlow.md** (v2.0): Documentation rules and update workflow.
- **integrationTesting.md** (v1.1): Planning and executing integration tests.
- **phaseDeployment.md** (v1.1): Deploying to project phases.
- **hardwareIntegrationWorkflow.md** (v1.0): Integrating hardware like mics and sensors.
- **ciCdAutomationWorkflow.md** (v1.0): Automating builds, tests, and deployments.
- **featureScenarioWorkflow.md** (v1.0): BDD for features to scenarios.

### Usage Tips
- Feed a file into Cline as a prompt to activate.
- For combined use: Reference multiple (e.g., "Follow busArchitectureRules.md and busServiceManagement.md").
- Bus Architecture: Always start with busArchitectureRules.md for service development.
- Updates: Bus architecture rules at v2.0; new additions at v1.0—review and version as needed.
- Suggestions: Add more for AI/ML training or cloud integrations if project evolves.
- Cross-Referencing: All rules encourage integration (e.g., security in deployments).

### Bus Architecture Integration
- **Service Development**: Use busArchitectureRules.md + busServiceManagement.md
- **Voice Pipeline**: Use voiceProcessing.md + busArchitectureRules.md
- **Security**: Use securityRules.md + busArchitectureRules.md
- **Docker Deployment**: Use dockerManagement.md + busServiceManagement.md

Last Updated: 2025-01-09 (Refactored for bus architecture v2.0)
