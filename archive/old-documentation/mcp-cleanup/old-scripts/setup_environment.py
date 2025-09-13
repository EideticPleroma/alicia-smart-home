#!/usr/bin/env python3
"""
Environment Setup Script for Cursor-Cline MCP Integration
=========================================================

This script sets up the environment for the Cursor-Cline MCP integration
within the Alicia Smart Home AI ecosystem.

Usage:
    python setup_environment.py
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("environment_setup")

class EnvironmentSetup:
    """Environment setup for Cursor-Cline MCP integration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.cursor-cline.json"""
        config_path = self.project_root / "config.cursor-cline.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return {}
    
    def setup_directories(self):
        """Create necessary directories"""
        logger.info("📁 Setting up directories...")
        
        directories = [
            "logs",
            "output",
            "output/bdd_scenarios",
            "output/test_files",
            "output/reports",
            "certs",
            "config",
            "data"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  ✅ Created directory: {directory}")
    
    def setup_environment_file(self):
        """Create .env file from template"""
        logger.info("🔧 Setting up environment file...")
        
        env_example_path = self.project_root / "env.example"
        env_path = self.project_root / ".env"
        
        if not env_example_path.exists():
            logger.error("Environment template not found: env.example")
            return
        
        if env_path.exists():
            logger.info("  ⚠️  .env file already exists, skipping creation")
            return
        
        # Copy template to .env
        shutil.copy2(env_example_path, env_path)
        logger.info("  ✅ Created .env file from template")
        
        # Update with project-specific values
        self.update_env_file(env_path)
    
    def update_env_file(self, env_path: Path):
        """Update .env file with project-specific values"""
        logger.info("  🔄 Updating .env with project-specific values...")
        
        # Read current content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update values based on config
        updates = {
            "MQTT_BROKER_URL": self.config.get("mqtt_broker", {}).get("host", "localhost"),
            "MQTT_USERNAME": self.config.get("mqtt_broker", {}).get("username", "alicia_mcp_user"),
            "MQTT_PASSWORD": self.config.get("mqtt_broker", {}).get("password", "alicia_mcp_password"),
            "BDD_THRESHOLD": str(self.config.get("cursor_orchestrator", {}).get("quality_gates", {}).get("bdd_coverage", 8.0)),
            "TEST_QUALITY_THRESHOLD": str(self.config.get("cursor_orchestrator", {}).get("quality_gates", {}).get("test_quality", 7.0)),
            "CODE_REVIEW_THRESHOLD": str(self.config.get("cursor_orchestrator", {}).get("quality_gates", {}).get("code_review", 7.0)),
            "MAX_CONCURRENT_TASKS": str(self.config.get("cline_specialist", {}).get("task_processing", {}).get("max_concurrent_tasks", 3)),
            "LOG_LEVEL": self.config.get("logging", {}).get("level", "INFO"),
            "OUTPUT_BASE_DIR": self.config.get("output", {}).get("base_dir", "./output")
        }
        
        # Apply updates
        for key, value in updates.items():
            content = content.replace(f"{key}=your_value_here", f"{key}={value}")
            content = content.replace(f"{key}=localhost", f"{key}={value}")
            content = content.replace(f"{key}=alicia_mcp_user", f"{key}={value}")
            content = content.replace(f"{key}=alicia_mcp_password", f"{key}={value}")
        
        # Write updated content
        with open(env_path, 'w') as f:
            f.write(content)
        
        logger.info("  ✅ Updated .env with project-specific values")
    
    def setup_mqtt_config(self):
        """Setup MQTT broker configuration"""
        logger.info("📡 Setting up MQTT configuration...")
        
        # Create MQTT ACL file for MCP services
        acl_content = f"""# Alicia MCP QA Services ACL Configuration
# User: {self.config.get("mqtt_broker", {}).get("username", "alicia_mcp_user")}

# Cursor Orchestrator permissions
user {self.config.get("mqtt_broker", {}).get("username", "alicia_mcp_user")}
topic read alicia/mcp/qa/orchestrator/+
topic write alicia/mcp/qa/orchestrator/+
topic read alicia/mcp/qa/specialist/+
topic write alicia/mcp/qa/specialist/+
topic read alicia/mcp/qa/shared/+
topic write alicia/mcp/qa/shared/+
topic read alicia/system/+
topic write alicia/system/+

# Allow system status monitoring
topic read $SYS/#
"""
        
        acl_path = self.project_root / "bus-config" / "acl-mcp"
        acl_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(acl_path, 'w') as f:
            f.write(acl_content)
        
        logger.info("  ✅ Created MQTT ACL configuration")
        
        # Create MQTT password file
        password_content = f"{self.config.get('mqtt_broker', {}).get('username', 'alicia_mcp_user')}:{self.config.get('mqtt_broker', {}).get('password', 'alicia_mcp_password')}\n"
        
        password_path = self.project_root / "bus-config" / "passwords-mcp"
        with open(password_path, 'w') as f:
            f.write(password_content)
        
        logger.info("  ✅ Created MQTT password file")
    
    def setup_docker_compose(self):
        """Setup Docker Compose configuration"""
        logger.info("🐳 Setting up Docker Compose configuration...")
        
        # Update docker-compose.cursor-cline.yml with project-specific values
        compose_path = self.project_root / "docker-compose.cursor-cline.yml"
        
        if compose_path.exists():
            logger.info("  ✅ Docker Compose file already exists")
        else:
            logger.warning("  ⚠️  Docker Compose file not found")
    
    def setup_health_checks(self):
        """Setup health check endpoints"""
        logger.info("🏥 Setting up health check endpoints...")
        
        # Create health check script
        health_check_script = """#!/bin/bash
# Health check script for MCP services

# Check Cursor Orchestrator
curl -f http://localhost:8080/health || exit 1

# Check Cline Specialist
curl -f http://localhost:8081/health || exit 1

echo "All MCP services are healthy"
"""
        
        health_check_path = self.project_root / "health_check.sh"
        with open(health_check_path, 'w') as f:
            f.write(health_check_script)
        
        # Make executable
        health_check_path.chmod(0o755)
        
        logger.info("  ✅ Created health check script")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logger.info("📝 Setting up logging configuration...")
        
        # Create log configuration
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": "./logs/mcp_system.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "cursor_orchestrator": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "cline_specialist": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "mcp_system": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        }
        
        log_config_path = self.project_root / "logging_config.json"
        with open(log_config_path, 'w') as f:
            json.dump(log_config, f, indent=2)
        
        logger.info("  ✅ Created logging configuration")
    
    def setup_startup_scripts(self):
        """Setup startup scripts"""
        logger.info("🚀 Setting up startup scripts...")
        
        # Create startup script for Windows
        startup_script_windows = """@echo off
REM Alicia MCP QA Orchestration System - Windows Startup Script

echo Starting Alicia MCP QA Orchestration System...

REM Set environment variables
set MQTT_BROKER_URL=mqtts://localhost:8883
set MQTT_USERNAME=alicia_mcp_user
set MQTT_PASSWORD=alicia_mcp_password
set GROK_API_KEY=free_with_cline
set LOG_LEVEL=INFO

REM Start services
echo Starting Cursor Orchestrator...
start "Cursor Orchestrator" python cursor_orchestrator.py

timeout /t 5 /nobreak > nul

echo Starting Cline Specialist...
start "Cline Specialist" python cline_specialist.py

echo All services started!
echo Check logs in the logs/ directory
pause
"""
        
        startup_script_path = self.project_root / "start_mcp_windows.bat"
        with open(startup_script_path, 'w') as f:
            f.write(startup_script_windows)
        
        # Create startup script for Linux/Mac
        startup_script_unix = """#!/bin/bash
# Alicia MCP QA Orchestration System - Unix Startup Script

echo "Starting Alicia MCP QA Orchestration System..."

# Set environment variables
export MQTT_BROKER_URL=mqtts://localhost:8883
export MQTT_USERNAME=alicia_mcp_user
export MQTT_PASSWORD=alicia_mcp_password
export GROK_API_KEY=free_with_cline
export LOG_LEVEL=INFO

# Start services in background
echo "Starting Cursor Orchestrator..."
python cursor_orchestrator.py &

sleep 5

echo "Starting Cline Specialist..."
python cline_specialist.py &

echo "All services started!"
echo "Check logs in the logs/ directory"
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'kill $(jobs -p); exit' INT
wait
"""
        
        startup_script_path = self.project_root / "start_mcp_unix.sh"
        with open(startup_script_path, 'w') as f:
            f.write(startup_script_unix)
        
        # Make executable
        startup_script_path.chmod(0o755)
        
        logger.info("  ✅ Created startup scripts")
    
    def run_setup(self):
        """Run complete environment setup"""
        logger.info("🚀 Starting Alicia MCP QA Environment Setup")
        logger.info("=" * 60)
        
        try:
            self.setup_directories()
            self.setup_environment_file()
            self.setup_mqtt_config()
            self.setup_docker_compose()
            self.setup_health_checks()
            self.setup_logging()
            self.setup_startup_scripts()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Environment setup completed successfully!")
            logger.info("=" * 60)
            
            logger.info("\n📋 Next steps:")
            logger.info("1. Review and update .env file if needed")
            logger.info("2. Start MQTT broker: docker-compose -f docker-compose.bus.yml up -d")
            logger.info("3. Start MCP services: python start_mcp_unix.sh (or start_mcp_windows.bat)")
            logger.info("4. Check health: python health_check.sh")
            logger.info("5. Run integration tests: python integration_test.py")
            
        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            raise

def main():
    """Main entry point"""
    setup = EnvironmentSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
