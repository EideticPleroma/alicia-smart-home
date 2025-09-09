# Prompt for Cline: Code Style and Quality Rules for Alicia Project

You are Cline, enforcing code quality and consistency in the Alicia Smart Home AI Assistant project. These consolidated rules ensure readable, maintainable, and secure code across all components including Python, Bash scripts, YAML configurations, and Docker files.

### Core Rules
1. **Formatting Standards**:
   - **Python**: PEP8 compliance with 4-space indentation, max 88 characters per line
   - **YAML/Docker**: 2-space indentation, consistent line endings (LF on Unix, CRLF on Windows)
   - **Bash/Shell**: 2-space indentation, proper shebang (`#!/bin/bash`)
   - **Markdown**: Consistent heading styles, proper code block formatting

2. **Documentation and Comments**:
   - Add docstrings for all Python functions and classes
   - Include inline comments for complex logic
   - Document configuration files with comments
   - Use descriptive variable and function names

3. **Modularity and Structure**:
   - Break code into logical functions/methods
   - Keep files under 300 lines where possible
   - Use consistent file organization patterns
   - Implement proper error handling with try/catch blocks

4. **Security and Best Practices**:
   - Never hardcode secrets or sensitive data
   - Use environment variables for configuration
   - Implement input validation and sanitization
   - Add proper error handling (`set -e` in bash scripts)
   - Use official Docker images with specific tags

5. **Code Quality Tools**:
   - **Python**: flake8, black, mypy for type checking
   - **Bash**: shellcheck for script validation
   - **YAML**: yamllint for configuration validation
   - **Docker**: hadolint for Dockerfile best practices
   - **Windows**: Ensure proper CRLF/LF handling

### Code Review Process
For any code suggestion or generation:
1. **Self-Review**: Include pros, cons, and improvement suggestions
2. **Style Compliance**: Verify adherence to formatting standards
3. **Security Check**: Ensure no hardcoded secrets or vulnerabilities
4. **Documentation**: Confirm proper commenting and docstrings

### Project-Specific Guidelines
- **Docker Compose**: Use health checks, proper networking, volume management
- **Voice Processing**: Document model dependencies and audio formats
- **MQTT Integration**: Standardize topic naming conventions
- **Home Assistant**: Follow HA configuration best practices
- **Testing**: Include comprehensive test coverage with proper mocking

### Enforcement Guidelines
- **Style Review**: Always include style assessment in code responses
- **Rejection Policy**: Reject non-compliant code with specific improvement suggestions
- **Integration**: Reference related rules (gitFlow.md for commits, errorHandling.md for exceptions)
- **Automation**: Suggest pre-commit hooks for automatic style checking

### Examples
- **Python Function**: Include type hints, docstring, and proper error handling
- **Bash Script**: Add shebang, error trapping, and input validation
- **YAML Config**: Use consistent indentation, comments, and environment variables
- **Dockerfile**: Use multi-stage builds, proper user permissions, and security scanning

### Recent Achievements
- ✅ Established comprehensive BDD testing framework
- ✅ Consolidated error handling across all components
- ✅ Implemented GitFlow with dedicated test branches
- ✅ Enhanced .gitignore with local file protection

### Next Steps
- Implement automated code quality checks in CI/CD pipeline
- Add pre-commit hooks for style enforcement
- Create code templates for consistent development
- Establish code review checklists for team collaboration

Confirm: "Enforcing consolidated code style and quality rules v2.0."
