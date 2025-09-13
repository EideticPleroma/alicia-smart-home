# Feature Test Organization

This directory contains organized feature tests following the BDD → Scripts → Results structure.

## Structure

Each feature category has three subdirectories:
- **bdd/**: Gherkin feature files (.feature)
- **scripts/**: Python test implementation files (.py)
- **results/**: Test execution results and reports (.json, .txt)

## Feature Categories

### Core Infrastructure
- MQTT Bus connectivity and health
- Security Gateway authentication
- Device Registry management
- Configuration services
- Service discovery and orchestration

### Voice Pipeline
- Speech-to-Text (STT) processing
- AI conversation handling
- Text-to-Speech (TTS) synthesis
- Voice Router orchestration

### Device Integration
- Device Manager universal control
- Home Assistant bridge
- Sonos multi-room audio
- Device Control execution
- Grok AI integration

### Advanced Features
- Personality System management
- Multi-Language support
- Advanced Voice processing
- Load Balancer distribution

### Monitoring & Analytics
- Metrics Collector performance monitoring
- Event Scheduler automation

## Naming Conventions

- **BDD Files**: `{feature_name}.feature`
- **Script Files**: `test_{feature_name}.py`
- **Result Files**: `{feature_name}_results.json` or `{feature_name}_report.txt`

## Running Tests

```bash
# Run specific feature tests
pytest tests/features/{category}/scripts/

# Run all feature tests
pytest tests/features/

# Run BDD tests with behave
behave tests/features/{category}/bdd/
```
