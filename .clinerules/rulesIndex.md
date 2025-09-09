# Cline Rules and Workflows Index for Alicia Project

This index categorizes the prompts in .clinerules/ into **Rules** (static guidelines for best practices) and **Workflows** (step-by-step processes for tasks). Use this to select and feed into Cline. All are versioned (e.g., v1.1) and integrate with each other for consistency.

## Rules (Foundational Guidelines)
These provide overarching standards, often referenced in workflows.
- **gitFlow.md** (v1.1): Version control and branching rules.
- **projectFlowPhasing.md** (v1.1): Phase mapping and dependency checks.
- **securityRules.md** (v1.0): Security and privacy guidelines for data and credentials.
- **errorHandling.md** (v2.0): Systematic error diagnosis and prevention.
- **codeStyleRules.md** (v2.0): Code formatting and quality standards.

## Workflows (Action-Oriented Processes)
These guide specific tasks with structured steps.
- **dockerManagement.md** (v1.1): Managing Docker configurations and errors.
- **voiceProcessing.md** (v1.1): Handling voice pipeline components and integrations.
- **documentFlow.md** (v2.0): Documentation rules and update workflow.
- **integrationTesting.md** (v1.1): Planning and executing integration tests.
- **phaseDeployment.md** (v1.1): Deploying to project phases.
- **hardwareIntegrationWorkflow.md** (v1.0): Integrating hardware like mics and sensors.
- **ciCdAutomationWorkflow.md** (v1.0): Automating builds, tests, and deployments.
- **featureScenarioWorkflow.md** (v1.0): BDD for features to scenarios.

### Usage Tips
- Feed a file into Cline as a prompt to activate.
- For combined use: Reference multiple (e.g., "Follow gitFlow.md and dockerManagement.md").
- Updates: Core at v1.1; new additions at v1.0—review and version as needed.
- Suggestions: Add more for AI/ML training or cloud integrations if project evolves.
- Cross-Referencing: All rules encourage integration (e.g., security in deployments).

Last Updated: 2025-01-09 (Consolidated duplicate rules v2.0)
