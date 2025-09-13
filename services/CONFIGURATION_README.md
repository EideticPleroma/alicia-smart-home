# Service Configuration

## Centralized Environment Management

All services now use the centralized `.env` file located at the project root.

### Configuration Loading

Each service loads environment variables from the project root `.env` file:

**Python Services:**
```python
from pathlib import Path
from dotenv import load_dotenv

# Load from project root .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / '.env')
```

**Node.js Services:**
```javascript
require('dotenv').config({ 
    path: require('path').join(__dirname, '../../../../.env') 
});
```

### Environment Variables

All environment variables are defined in the project root `.env` file. See `env.example` for a complete list of available variables.

### Service-Specific Configuration

Service-specific configuration is stored in JSON files in the `config/services/` directory:
- `config/services/alicia-config-manager.json`
- `config/services/alicia-monitor.json`
- `config/services/mcp-qa-orchestrator.json`

### Migration from Local .env Files

If you had local `.env` files in your service directories, they have been:
1. Backed up to `backup_duplicate_env_files/`
2. Removed from service directories
3. Variables merged into the centralized `.env` file

### Adding New Environment Variables

1. Add the variable to the project root `.env` file
2. Add the variable to `env.example` with a default value
3. Update service code to use the new variable
4. Update this README if needed

### Troubleshooting

If a service can't find environment variables:
1. Check that the service is loading from the project root `.env` file
2. Verify the variable exists in the `.env` file
3. Check the service's configuration loading code
4. Ensure the service is running from the correct directory
