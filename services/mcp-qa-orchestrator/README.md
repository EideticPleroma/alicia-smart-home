# MCP QA Orchestration System

![MCP QA Orchestrator](https://img.shields.io/badge/MCP-QA%20Orchestrator-blue?style=for-the-badge&logo=ai&logoColor=white)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

## 🎯 Overview

The **MCP QA Orchestration System** is a comprehensive AI-powered testing framework that automates the generation of Behavior-Driven Development (BDD) scenarios and Python test code. Using LangChain AI agents, this system analyzes codebases and provides detailed quality reports with actionable recommendations.

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Scenario Builder│───▶│    Reviewer     │───▶│   Test-Coder    │───▶│  Code-Reviewer  │
│     Agent       │    │     Agent       │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MCP Orchestrator                                         │
│                    (Master Control Program)                                        │
│                                                                                     │
│  • State Machine Management    • Quality Threshold Control                        │
│  • Error Recovery System       • Async Pipeline Execution                         │
│  • File Packaging & Encoding   • JSON Communication Protocol                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🤖 AI Agent System
- **Scenario Builder Agent**: Generates comprehensive BDD scenarios from codebase analysis
- **Reviewer Agent**: Reviews and improves BDD scenario quality
- **Test-Coder Agent**: Creates Python test skeletons with pytest
- **Code-Reviewer Agent**: Reviews generated test code for best practices

### 🛠️ Core Capabilities
- **Automated BDD Generation**: Creates Gherkin-formatted scenarios
- **Python Test Generation**: Produces pytest-compatible test files
- **Quality Assessment**: Comprehensive scoring and recommendations
- **Error Recovery**: Robust retry logic with exponential backoff
- **Async Architecture**: High-performance concurrent processing
- **Modular Design**: Easy to extend and customize

### 📊 Quality Assurance
- **Iterative Improvement**: Multiple passes until quality thresholds met
- **Coverage Scoring**: Detailed metrics on test coverage
- **Bug Detection**: Automatic identification of potential issues
- **Recommendations**: Actionable suggestions for improvement

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for GPT-4 access)
- Git

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd mcp-qa-orchestrator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API key**:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

4. **Run a quick test**:
```bash
python mcp_qa_orchestrator.py test
```

## 📖 Usage

### Basic Usage

```python
import asyncio
from mcp_qa_orchestrator import MCPOrchestrator, create_default_config

async def main():
    # Create configuration
    config = create_default_config("your-openai-api-key")

    # Initialize orchestrator
    orchestrator = MCPOrchestrator(config)

    # Define your codebase
    codebase = {
        "project_name": "MyProject",
        "structure": {
            "src": {
                "main.py": "Main application file",
                "utils.py": "Utility functions"
            },
            "tests": {}
        },
        "language": "python",
        "critical_paths": ["authentication", "data_processing"],
        "integration_points": ["database", "external_api"],
        "error_scenarios": ["network_failure", "invalid_input"]
    }

    # Run MCP orchestration
    result = await orchestrator.spin_up_mcp(codebase)

    # Process results
    print(f"Quality Score: {result['quality_assessment']['overall_score']}")
    print("Recommendations:", result['quality_assessment']['recommendations'])

# Run the orchestration
asyncio.run(main())
```

### Advanced Configuration

```python
from mcp_qa_orchestrator import MCPConfig, MCPOrchestrator

# Custom configuration
config = MCPConfig(
    bdd_threshold=9.5,      # Require 95% BDD coverage
    quality_threshold=8.5,  # Require 85% test quality
    max_iterations=5,       # Allow up to 5 iterations
    max_bugs=2,            # Maximum 2 bugs allowed
    llm_provider="openai",
    api_key="your-api-key",
    timeout=45,             # 45 second timeout per agent
    retry_attempts=5        # 5 retry attempts per agent
)

orchestrator = MCPOrchestrator(config)
```

## 📋 Configuration

### MCP Configuration (`config.json`)

```json
{
  "mcp_config": {
    "bdd_threshold": 9.0,
    "quality_threshold": 8.0,
    "max_iterations": 3,
    "max_bugs": 3,
    "llm_provider": "openai",
    "timeout": 30,
    "retry_attempts": 3
  },
  "agent_configs": {
    "scenario_builder": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 3000,
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Quality Thresholds
- **BDD Threshold**: Minimum coverage score (0-10)
- **Quality Threshold**: Minimum test quality score (0-10)
- **Max Bugs**: Maximum allowed bugs before stopping iteration
- **Max Iterations**: Maximum refinement iterations

## 🔧 API Reference

### Core Classes

#### MCPOrchestrator
Main orchestration class that manages the entire process.

**Methods:**
- `spin_up_mcp(codebase: Dict[str, Any])`: Main orchestration method
- `get_orchestrator_status()`: Get current orchestrator state
- `reset()`: Reset orchestrator to initial state

#### BaseAgent
Abstract base class for all MCP agents.

**Methods:**
- `run(input_data: Dict[str, Any])`: Execute agent with retry logic
- `get_status()`: Get agent status information
- `reset()`: Reset agent state

### Specialized Agents

#### ScenarioBuilderAgent
Generates BDD scenarios from codebase analysis.

#### ReviewerAgent
Reviews and improves BDD scenario quality.

#### TestCoderAgent
Creates Python test code from BDD scenarios.

#### CodeReviewerAgent
Reviews generated test code quality.

## 🎯 Supported Languages

- ✅ **Python** (Full support)
- ✅ **JavaScript/TypeScript** (Beta)
- ✅ **Java** (Experimental)
- 🚧 **C#** (Planned)
- 🚧 **Go** (Planned)

## 📊 Output Formats

### BDD Scenarios
```gherkin
Feature: User Authentication
  @critical @security
  Scenario: Successful user login
    Given a registered user with valid credentials
    When the user attempts to log in
    Then the user should be authenticated
    And a session token should be returned
```

### Python Tests
```python
import pytest
from myapp.auth import authenticate_user

class TestUserAuthentication:
    """Test cases for user authentication functionality"""

    def test_successful_login(self):
        """Test successful user login with valid credentials"""
        # Given: a registered user with valid credentials
        user_credentials = {"username": "testuser", "password": "validpass"}

        # When: the user attempts to log in
        result = authenticate_user(user_credentials)

        # Then: the user should be authenticated
        assert result["authenticated"] is True
        assert "token" in result
        assert result["token"] is not None
```

### Quality Reports
```json
{
  "status": "success",
  "summary": {
    "overall_score": 8.7,
    "total_iterations": 2,
    "total_time_seconds": 45.23
  },
  "quality_assessment": {
    "overall_score": 8.7,
    "thresholds_met": true,
    "recommendations": [
      "Consider adding more edge case scenarios",
      "Improve test coverage for error handling"
    ]
  }
}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_qa_orchestrator --cov-report=html

# Run specific test categories
pytest -k "test_agent"
pytest -k "test_orchestrator"
```

### Testing Architecture
- **Unit Tests**: Test individual components
- **Integration Tests**: Test agent interactions
- **End-to-End Tests**: Test complete orchestration
- **Performance Tests**: Test under load conditions

## 🔧 Development

### Setting Up Development Environment

1. **Install development dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Set up pre-commit hooks**:
```bash
pre-commit install
```

3. **Run linting and formatting**:
```bash
black mcp_qa_orchestrator/
flake8 mcp_qa_orchestrator/
mypy mcp_qa_orchestrator/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Standards

- **Type Hints**: All functions must have comprehensive type hints
- **Documentation**: All classes and methods must have docstrings
- **Testing**: Minimum 80% test coverage required
- **Style**: Black formatting, PEP 8 compliance

## 🚨 Troubleshooting

### Common Issues

#### API Key Errors
```
Error: API key is required for MCP operations
```
**Solution**: Set `OPENAI_API_KEY` environment variable or pass API key to `MCPConfig`

#### Model Not Found
```
Error: Unsupported LLM provider: custom_provider
```
**Solution**: Use supported providers: `openai` or `grok`

#### Timeout Errors
```
Error: Agent scenario_builder timed out
```
**Solution**: Increase timeout in configuration or check API rate limits

#### Memory Issues
```
Error: Insufficient memory for orchestration
```
**Solution**: Reduce `max_concurrent_agents` or increase system memory

## 📈 Performance

### Benchmarks
- **Scenario Generation**: ~15 seconds for medium codebase
- **Test Generation**: ~20 seconds for generated scenarios
- **Full Orchestration**: ~45 seconds for complete cycle
- **Memory Usage**: ~200MB for typical operations

### Performance Tuning
- Adjust `max_concurrent_agents` based on system capabilities
- Configure quality thresholds to meet requirements
- Use appropriate LLM model for your needs
- Monitor system resources during operation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📚 Related Projects

- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [pytest](https://github.com/pytest-dev/pytest) - Testing framework

## 🙋 Support

- 📧 Email: support@mcp-qa.example.com
- 💬 Discord: [MCP QA Community](https://discord.gg/mcp-qa)
- 📖 Documentation: [Full Documentation](https://docs.mcp-qa.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/mcp-qa/mcp-qa-orchestrator/issues)

---

## 🎉 Acknowledgments

- **LangChain** for the excellent LLM framework
- **OpenAI** for GPT-4 model capabilities
- **Pydantic** for robust data validation
- **Community contributors** for their valuable input

---

**Built with ❤️ for automated QA excellence**

---

*If you found this helpful, please ⭐ the repository!*
