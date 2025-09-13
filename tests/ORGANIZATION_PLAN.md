# Test Folder Organization Plan

## Current Issues
- Mixed test files in root tests/ directory
- No clear BDD → Scripts → Results structure
- Scattered feature tests without organization
- Multiple duplicate test files
- Inconsistent naming conventions

## Target Structure

```
tests/
├── README.md                           # Main test documentation
├── requirements.txt                    # Test dependencies
├── conftest.py                        # Pytest configuration
├── features/                          # BDD Feature Tests
│   ├── core_infrastructure/
│   │   ├── bdd/
│   │   │   ├── mqtt_bus.feature
│   │   │   ├── security_gateway.feature
│   │   │   └── device_registry.feature
│   │   ├── scripts/
│   │   │   ├── test_mqtt_bus.py
│   │   │   ├── test_security_gateway.py
│   │   │   └── test_device_registry.py
│   │   └── results/
│   │       ├── mqtt_bus_results.json
│   │       ├── security_gateway_results.json
│   │       └── device_registry_results.json
│   ├── voice_pipeline/
│   │   ├── bdd/
│   │   │   ├── stt_service.feature
│   │   │   ├── ai_service.feature
│   │   │   ├── tts_service.feature
│   │   │   └── voice_router.feature
│   │   ├── scripts/
│   │   │   ├── test_stt_service.py
│   │   │   ├── test_ai_service.py
│   │   │   ├── test_tts_service.py
│   │   │   └── test_voice_router.py
│   │   └── results/
│   │       ├── stt_service_results.json
│   │       ├── ai_service_results.json
│   │       ├── tts_service_results.json
│   │       └── voice_router_results.json
│   ├── device_integration/
│   │   ├── bdd/
│   │   │   ├── device_manager.feature
│   │   │   ├── ha_bridge.feature
│   │   │   ├── sonos_service.feature
│   │   │   └── device_control.feature
│   │   ├── scripts/
│   │   │   ├── test_device_manager.py
│   │   │   ├── test_ha_bridge.py
│   │   │   ├── test_sonos_service.py
│   │   │   └── test_device_control.py
│   │   └── results/
│   │       ├── device_manager_results.json
│   │       ├── ha_bridge_results.json
│   │       ├── sonos_service_results.json
│   │       └── device_control_results.json
│   ├── advanced_features/
│   │   ├── bdd/
│   │   │   ├── personality_system.feature
│   │   │   ├── multi_language.feature
│   │   │   ├── advanced_voice.feature
│   │   │   └── load_balancer.feature
│   │   ├── scripts/
│   │   │   ├── test_personality_system.py
│   │   │   ├── test_multi_language.py
│   │   │   ├── test_advanced_voice.py
│   │   │   └── test_load_balancer.py
│   │   └── results/
│   │       ├── personality_system_results.json
│   │       ├── multi_language_results.json
│   │       ├── advanced_voice_results.json
│   │       └── load_balancer_results.json
│   └── monitoring_analytics/
│       ├── bdd/
│       │   ├── metrics_collector.feature
│       │   └── event_scheduler.feature
│       ├── scripts/
│       │   ├── test_metrics_collector.py
│       │   └── test_event_scheduler.py
│       └── results/
│           ├── metrics_collector_results.json
│           └── event_scheduler_results.json
├── integration/                       # Integration Tests
│   ├── bdd/
│   │   ├── end_to_end_workflows.feature
│   │   └── service_integration.feature
│   ├── scripts/
│   │   ├── test_end_to_end.py
│   │   └── test_service_integration.py
│   └── results/
│       ├── end_to_end_results.json
│       └── service_integration_results.json
├── performance/                       # Performance Tests
│   ├── bdd/
│   │   ├── load_testing.feature
│   │   └── stress_testing.feature
│   ├── scripts/
│   │   ├── test_load_performance.py
│   │   └── test_stress_performance.py
│   └── results/
│       ├── load_testing_results.json
│       └── stress_testing_results.json
├── unit/                             # Unit Tests
│   ├── bdd/
│   │   └── unit_testing.feature
│   ├── scripts/
│   │   ├── test_service_units.py
│   │   └── test_utility_functions.py
│   └── results/
│       ├── service_units_results.json
│       └── utility_functions_results.json
└── archive/                          # Archived Test Files
    ├── old_test_files/
    ├── deprecated_scripts/
    └── legacy_results/
```

## Migration Steps

1. **Create new folder structure**
2. **Move existing files to appropriate locations**
3. **Rename files to follow conventions**
4. **Update import paths and references**
5. **Create missing BDD feature files**
6. **Archive old/unused files**
7. **Update documentation**

## File Naming Conventions

- **BDD Files**: `{feature_name}.feature`
- **Script Files**: `test_{feature_name}.py`
- **Result Files**: `{feature_name}_results.json`
- **Folders**: `{feature_name}/` (snake_case)
