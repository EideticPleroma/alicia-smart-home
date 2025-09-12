# Configuration Directory

This directory contains configuration files and templates for the Alicia project.

## Directory Structure

### `services/`
Service-specific configuration files:
- Individual service configurations
- Service-specific environment variables
- Service deployment configurations

### `environments/`
Environment-specific configuration templates:
- `env.template` - Base environment template
- Development environment configurations
- Production environment configurations
- Staging environment configurations

### `templates/`
Configuration templates and schemas:
- Docker Compose templates
- Service configuration templates
- Environment variable templates
- MQTT configuration templates

## Usage

### Environment Configuration
```bash
# Copy template to create your environment file
cp config/environments/env.template .env

# Edit the .env file with your specific values
# Required variables:
# - GROK_API_KEY=your_grok_api_key
# - OPENAI_API_KEY=your_openai_api_key
# - HA_TOKEN=your_home_assistant_token
# - MQTT_BROKER=alicia_bus_core
# - MQTT_USERNAME=admin
# - MQTT_PASSWORD=alicia_admin_2024
```

### Service Configuration
Each service can be configured through:
1. Environment variables (runtime configuration)
2. Configuration files in `config/services/`
3. Web interface (dynamic configuration)

### MQTT Configuration
MQTT broker configuration is managed through:
- `bus-config/mosquitto.conf` - Main broker configuration
- `bus-config/passwords` - User authentication
- `bus-config/acl` - Access control lists

## Configuration Management

The project uses a hierarchical configuration system:
1. **Default values** - Hardcoded in service code
2. **Environment variables** - Runtime overrides
3. **Configuration files** - Persistent settings
4. **Web interface** - Dynamic updates

## Security Notes

- Never commit `.env` files to version control
- Keep API keys and passwords secure
- Use environment-specific configurations
- Regularly rotate credentials in production
