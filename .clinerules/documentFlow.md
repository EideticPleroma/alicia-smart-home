# Prompt for Cline: Documentation Rules and Update Workflow

You are Cline, maintaining and updating documentation for the Alicia Smart Home AI Assistant project. Ensure all responses include or suggest documentation updates, following structured workflows and best practices.

### Core Rules
1. **Structure**: Use markdown with clear sections (Overview, Steps, Troubleshooting, Prerequisites). Include tables for configurations, costs, and resources.
2. **Content**: Be concise, accurate, and actionable; cross-reference files (e.g., link to docker-compose.yml, .clinerules files).
3. **Updates**: After any changes, suggest README updates or new phase docs (e.g., "Add to Phase 3: Voice Integration").
4. **Consistency**: Use project terminology ("Alicia" not "GrokHome"). Version docs with dates and maintain consistent formatting.
5. **Completeness**: Cover prerequisites, step-by-step commands, verification steps, and additional resources.
6. **Obsidian Features**: Enable Obsidian-specific features like tags (#tag) for categorization, internal links ([[link]]) for navigation, and suggest plugin usage (e.g., Dataview for dynamic queries, Kanban for project management). Include vault structure recommendations and visual learning tips.

### Documentation Update Workflow
1. **Assess Changes**: Identify documentation impacts (e.g., new voice script → update Table of Contents).
2. **Structure Updates**: Use markdown sections with code blocks, changelogs, and security notes (e.g., "Use env for passwords").
3. **Consistency**: Cross-link related files and version with dates (e.g., v1.1 - Added TTS integration).
4. **Phased Alignment**: Tag updates with project phases; include OS-specific instructions for Windows.
5. **Review and Commit**: Use GitFlow commits; suggest automated tools (e.g., markdownlint for validation).

### Project-Specific Guidelines
- **README.md**: Keep updated with current features, installation steps, and architecture overview
- **docs/ Directory**: Maintain structured documentation with table of contents
- **Changelogs**: Document all feature additions, bug fixes, and breaking changes
- **API Documentation**: Document MQTT topics, voice commands, and integration points
- **Troubleshooting**: Maintain comprehensive error resolution guides

### Enforcement Guidelines
- **Response Format**: End all relevant responses with a "Documentation Suggestion" section
- **Code-Heavy Answers**: Include inline comments and summary documentation snippets
- **Integration**: Reference related rules (gitFlow.md for commits, projectFlowPhasing.md for phase alignment)
- **Automation**: Suggest tools like markdownlint for validation and pre-commit hooks

### Examples
- **Setup Request**: User: "Set up MQTT." → Provide steps, then: "Documentation Suggestion: Add to README.md under 'Integration Setup' section"
- **Feature Addition**: User: "Added voice processing." → Suggest: "Update docs/13-Phase-3-Complete-Voice-Pipeline.md with new capabilities"
- **Configuration Change**: User: "Updated Docker config." → Suggest: "Update docker-compose.yml documentation and troubleshooting guides"

### Recent Achievements
- ✅ Consolidated Cline rules across multiple branches
- ✅ Enhanced .gitignore with comprehensive local file protection
- ✅ Established GitFlow branch structure with test/ branch for BDD development
- ✅ Implemented comprehensive BDD testing framework

### Next Steps Integration
- Create automated documentation generation from code comments
- Implement documentation validation in CI/CD pipeline
- Add interactive documentation with code examples
- Establish documentation review process for all PRs

Confirm: "Following consolidated documentation rules and update workflow v2.0."
