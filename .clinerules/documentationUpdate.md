# Prompt for Cline: Documentation Update Workflow for Alicia Project

You are Cline, updating docs (README.md, docs/00-Table-of-Contents.md). Ensure reflections of changes with structure and links.

### Core Rules
1. **Assess Changes**: Identify impacts (e.g., new voice script → update Table of Contents).
2. **Structure Updates**: Markdown sections; include code blocks, changelogs, security notes (e.g., "Use env for passwords").
3. **Consistency**: Cross-link (e.g., to docker-compose.yml); version with dates (e.g., v1.1 - Added TTS).
4. **Phased Alignment**: Tag with phases; on Windows, note OS-specific instructions.
5. **Review and Commit**: GitFlow commits; suggest automated tools (e.g., markdownlint).

### Enforcement Guidelines
- End with "Updated Doc Snippet" (with version).
- Integration with Other Rules: projectFlowPhasing.md for tags; gitFlow.md for commits.
- Example: User: "Doc Piper integration." → Assess: Phase 3. Snippet: [Updated markdown with changelog entry].

Confirm: "Following Documentation Update Workflow v1.1."
