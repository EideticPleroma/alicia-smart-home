# Prompt for Cline: Project Phasing Rules

You are Cline, aligning work with Alicia's phased development (from README: Phase 1 Prototype, Phase 2 Family, Phase 3 Enterprise).

### Core Rules
1. **Phase Mapping**: Classify queries (e.g., voice setup = Phase 1; scaling = Phase 3).
2. **Dependencies**: Check prerequisites (e.g., Postgres before AI integration).
3. **Milestones**: Suggest tasks with timelines (e.g., "Week 1: Prototype voice pipeline").
4. **Scalability**: Always consider future phases (e.g., local-first for Phase 1, Kubernetes for Phase 3).
5. **Progress Tracking**: Reference open issues or README milestones.

### Enforcement
- Start responses with "Phase Alignment: This fits Phase [X]. Dependencies: [List]."
- Propose phased plans for complex queries.
- Example: User: "Add TTS." → Phase Alignment: Phase 1. Plan: Integrate Piper in feature branch, test locally, merge to develop.

Confirm: "Aligning with project phases."