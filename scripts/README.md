# Scripts Directory

This directory contains utility scripts for managing the Alicia project.

## Directory Structure

### `setup/`
Scripts for initial project setup and configuration:
- `mqtt-config-manager.py` - MQTT broker configuration and certificate generation
- `setup.bat` - Windows setup script
- `setup.sh` - Linux/macOS setup script

### `maintenance/`
Scripts for project maintenance and cleanup:
- `cleanup_dockerfiles.py` - Remove health-check references from Dockerfiles
- `cleanup_health_checks.py` - Remove health-check.py files from services
- `final_cleanup.py` - Comprehensive project cleanup

### `testing/`
Test scripts and test data:
- `test-pack/` - Complete test suite with BDD tests
  - `conftest.py` - Pytest configuration
  - `features/` - BDD feature files
  - `steps/` - Step definitions
  - `tests/` - Unit and integration tests

## Usage

### Setup Scripts
```bash
# Configure MQTT for development
python scripts/setup/mqtt-config-manager.py dev

# Configure MQTT for production
python scripts/setup/mqtt-config-manager.py prod

# Run setup script
scripts/setup/setup.bat  # Windows
scripts/setup/setup.sh   # Linux/macOS
```

### Maintenance Scripts
```bash
# Clean up Dockerfiles
python scripts/maintenance/cleanup_dockerfiles.py

# Clean up health checks
python scripts/maintenance/cleanup_health_checks.py

# Run final cleanup
python scripts/maintenance/final_cleanup.py
```

### Testing
```bash
# Run all tests
cd scripts/testing/test-pack
python -m pytest

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## Notes

- All scripts are designed to be run from the project root directory
- Python scripts require Python 3.11+ and the appropriate dependencies
- Setup scripts may require additional system dependencies (OpenSSL for MQTT certificates)
- Maintenance scripts should be run carefully as they modify project files
