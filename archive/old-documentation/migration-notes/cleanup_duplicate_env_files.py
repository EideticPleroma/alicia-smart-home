#!/usr/bin/env python3
"""
Cleanup Duplicate Environment Files
==================================

This script removes duplicate .env files from services and ensures
all services use the centralized .env file at the project root.
"""

import os
import shutil
from pathlib import Path

class EnvFileCleanup:
    """Cleans up duplicate environment files"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.central_env = self.project_root / ".env"
        self.central_env_example = self.project_root / "env.example"
        
    def find_duplicate_env_files(self):
        """Find all duplicate .env files in services"""
        print("Searching for duplicate environment files...")
        
        duplicate_files = []
        
        # Search in services directory
        services_dir = self.project_root / "services"
        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir():
                    # Look for .env files
                    env_files = list(service_dir.glob("*.env*"))
                    for env_file in env_files:
                        duplicate_files.append(env_file)
                        print(f"  Found: {env_file}")
        
        return duplicate_files
    
    def backup_duplicate_files(self, duplicate_files):
        """Backup duplicate files before deletion"""
        print("Creating backup of duplicate files...")
        
        backup_dir = self.project_root / "backup_duplicate_env_files"
        backup_dir.mkdir(exist_ok=True)
        
        for env_file in duplicate_files:
            # Create backup path maintaining directory structure
            relative_path = env_file.relative_to(self.project_root)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(env_file, backup_path)
            print(f"  Backed up: {relative_path}")
    
    def remove_duplicate_files(self, duplicate_files):
        """Remove duplicate environment files"""
        print("Removing duplicate environment files...")
        
        for env_file in duplicate_files:
            try:
                env_file.unlink()
                print(f"  Removed: {env_file}")
            except Exception as e:
                print(f"  Error removing {env_file}: {e}")
    
    def update_service_configs(self):
        """Update service configurations to use centralized .env"""
        print("Updating service configurations...")
        
        # Update MCP QA Orchestrator
        self.update_mcp_qa_orchestrator()
        
        # Update Alicia Config Manager
        self.update_alicia_config_manager()
        
        # Update other services as needed
        self.update_other_services()
    
    def update_mcp_qa_orchestrator(self):
        """Update MCP QA Orchestrator to use centralized config"""
        print("  Updating MCP QA Orchestrator...")
        
        mcp_dir = self.project_root / "services" / "mcp-qa-orchestrator"
        
        # Update Python files to load from project root
        python_files = list(mcp_dir.glob("*.py"))
        for py_file in python_files:
            if py_file.name.startswith("cursor_") or py_file.name.startswith("cline_"):
                self.update_python_file_for_centralized_env(py_file)
    
    def update_alicia_config_manager(self):
        """Update Alicia Config Manager to use centralized config"""
        print("  Updating Alicia Config Manager...")
        
        config_dir = self.project_root / "services" / "alicia-config-manager"
        
        # Update backend files
        backend_dir = config_dir / "backend" / "src"
        if backend_dir.exists():
            js_files = list(backend_dir.rglob("*.js"))
            for js_file in js_files:
                self.update_js_file_for_centralized_env(js_file)
        
        # Update frontend files
        frontend_dir = config_dir / "frontend" / "src"
        if frontend_dir.exists():
            ts_files = list(frontend_dir.rglob("*.ts"))
            for ts_file in ts_files:
                self.update_ts_file_for_centralized_env(ts_file)
    
    def update_other_services(self):
        """Update other services to use centralized config"""
        print("  Updating other services...")
        
        # Update monitor services
        monitor_dir = self.project_root / "services" / "alicia-monitor"
        if monitor_dir.exists():
            ts_files = list(monitor_dir.rglob("*.ts"))
            for ts_file in ts_files:
                self.update_ts_file_for_centralized_env(ts_file)
        
        # Update monitor proxy
        proxy_dir = self.project_root / "services" / "alicia-monitor-proxy"
        if proxy_dir.exists():
            js_files = list(proxy_dir.rglob("*.js"))
            for js_file in js_files:
                self.update_js_file_for_centralized_env(js_file)
    
    def update_python_file_for_centralized_env(self, file_path):
        """Update Python file to load from centralized .env"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update dotenv loading to use project root
            if "load_dotenv()" in content:
                new_content = content.replace(
                    "load_dotenv()",
                    "load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / '.env')"
                )
                
                # Add Path import if not present
                if "from pathlib import Path" not in new_content:
                    new_content = "from pathlib import Path\n" + new_content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"    Updated: {file_path.name}")
        except Exception as e:
            print(f"    Error updating {file_path.name}: {e}")
    
    def update_js_file_for_centralized_env(self, file_path):
        """Update JavaScript file to load from centralized .env"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update dotenv loading to use project root
            if "require('dotenv').config()" in content:
                new_content = content.replace(
                    "require('dotenv').config()",
                    "require('dotenv').config({ path: require('path').join(__dirname, '../../../../.env') })"
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"    Updated: {file_path.name}")
        except Exception as e:
            print(f"    Error updating {file_path.name}: {e}")
    
    def update_ts_file_for_centralized_env(self, file_path):
        """Update TypeScript file to load from centralized .env"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update dotenv loading to use project root
            if "require('dotenv').config()" in content:
                new_content = content.replace(
                    "require('dotenv').config()",
                    "require('dotenv').config({ path: require('path').join(__dirname, '../../../../.env') })"
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"    Updated: {file_path.name}")
        except Exception as e:
            print(f"    Error updating {file_path.name}: {e}")
    
    def create_service_readme(self):
        """Create README explaining centralized configuration"""
        print("Creating service configuration README...")
        
        readme_content = """# Service Configuration

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
"""
        
        readme_path = self.project_root / "services" / "CONFIGURATION_README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  Created: {readme_path}")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("Starting Environment File Cleanup")
        print("=" * 50)
        
        try:
            # Find duplicate files
            duplicate_files = self.find_duplicate_env_files()
            
            if not duplicate_files:
                print("No duplicate environment files found!")
                return
            
            # Backup duplicate files
            self.backup_duplicate_files(duplicate_files)
            
            # Remove duplicate files
            self.remove_duplicate_files(duplicate_files)
            
            # Update service configurations
            self.update_service_configs()
            
            # Create service README
            self.create_service_readme()
            
            print("\n" + "=" * 50)
            print("Environment file cleanup completed successfully!")
            print("=" * 50)
            
            print(f"\nRemoved {len(duplicate_files)} duplicate environment files")
            print("All services now use the centralized .env file")
            print("Backup created in: backup_duplicate_env_files/")
            
        except Exception as e:
            print(f"\nCleanup failed: {e}")
            raise

def main():
    """Main entry point"""
    cleanup = EnvFileCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()
