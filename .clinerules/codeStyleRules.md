# Prompt for Cline: Code Style Rules for Alicia Project

You are Cline, enforcing code quality in the Alicia project. These rules apply to scripts (e.g., bash), YAML, and code for readability and maintainability.

### Core Rules
1. **Formatting**: PEP8 for Python; 2-space indent for YAML/bash; consistent line endings (LF).
2. **Comments and Docs**: Add inline comments; use docstrings for functions.
3. **Modularity**: Break into functions; keep files <300 lines.
4. **Security/Best Practices**: No hardcoded secrets; error handling (set -e in bash).
5. **Tools**: Use linters (shellcheck for bash, yamllint for Docker); Windows: Check CRLF.

### Enforcement Guidelines
- Include "Style Review" in responses with suggestions.
- Integration with Other Rules: gitFlow.md for pre-commit checks; documentationUpdate.md for code docs.
- Reject non-compliant: "Revise for rule [X]."

### Examples
- User: "Write bash script." → Review: Add shebang and comments.
- User: "Update YAML." → Ensure indentation and no escapes.

Confirm: "Enforcing Code Style Rules v1.0."
