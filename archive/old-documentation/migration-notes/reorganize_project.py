#!/usr/bin/env python3
"""
Alicia Project Reorganization Script
===================================

This script reorganizes the Alicia project structure to follow best practices:
- Single environment file at project root
- Centralized configuration management
- Clear service boundaries
- Consistent directory structure

Usage:
    python reorganize_project.py
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any

class ProjectReorganizer:
    """Reorganizes the Alicia project structure"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / "backup_before_reorganization"
        
    def create_backup(self):
        """Create backup of current structure"""
        print("📦 Creating backup of current project structure...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup key directories
        dirs_to_backup = [
            "alicia-config-manager",
            "alicia-monitor", 
            "alicia-monitor-proxy",
            "mcp-qa-orchestrator",
            "bus-services",
            "bus-config",
            "config"
        ]
        
        for dir_name in dirs_to_backup:
            src = self.project_root / dir_name
            if src.exists():
                dst = self.backup_dir / dir_name
                shutil.copytree(src, dst)
                print(f"  ✅ Backed up {dir_name}")
    
    def create_services_directory(self):
        """Create services directory and move all services"""
        print("📁 Creating services directory structure...")
        
        services_dir = self.project_root / "services"
        services_dir.mkdir(exist_ok=True)
        
        # Move services to services directory
        services_to_move = [
            ("alicia-config-manager", "alicia-config-manager"),
            ("alicia-monitor", "alicia-monitor"),
            ("alicia-monitor-proxy", "alicia-monitor-proxy"),
            ("mcp-qa-orchestrator", "mcp-qa-orchestrator"),
            ("bus-services", "bus-services")
        ]
        
        for src_name, dst_name in services_to_move:
            src_path = self.project_root / src_name
            dst_path = services_dir / dst_name
            
            if src_path.exists():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.move(str(src_path), str(dst_path))
                print(f"  ✅ Moved {src_name} to services/{dst_name}")
    
    def create_centralized_config(self):
        """Create centralized configuration structure"""
        print("⚙️ Creating centralized configuration...")
        
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "environments",
            "mqtt", 
            "services",
            "docker"
        ]
        
        for subdir in subdirs:
            (config_dir / subdir).mkdir(exist_ok=True)
            print(f"  ✅ Created config/{subdir}")
        
        # Move MQTT configuration
        mqtt_src = self.project_root / "bus-config"
        mqtt_dst = config_dir / "mqtt"
        
        if mqtt_src.exists():
            for item in mqtt_src.iterdir():
                if item.is_file():
                    shutil.copy2(item, mqtt_dst)
                    print(f"  ✅ Moved {item.name} to config/mqtt/")
        
        # Create service-specific configs
        self.create_service_configs()
    
    def create_service_configs(self):
        """Create service-specific configuration files"""
        print("🔧 Creating service-specific configurations...")
        
        services_config = {
            "alicia-config-manager": {
                "service_name": "alicia-config-manager",
                "port": 3000,
                "backend_port": 3001,
                "log_level": "INFO",
                "mqtt_topics": [
                    "alicia/config/request",
                    "alicia/config/response",
                    "alicia/config/update"
                ]
            },
            "alicia-monitor": {
                "service_name": "alicia-monitor",
                "port": 3002,
                "log_level": "INFO",
                "mqtt_topics": [
                    "alicia/monitor/status",
                    "alicia/monitor/metrics",
                    "alicia/monitor/alerts"
                ]
            },
            "alicia-monitor-proxy": {
                "service_name": "alicia-monitor-proxy",
                "port": 3003,
                "log_level": "INFO",
                "upstream_services": [
                    "alicia-config-manager:3000",
                    "alicia-monitor:3002"
                ]
            },
            "mcp-qa-orchestrator": {
                "service_name": "mcp-qa-orchestrator",
                "cursor_orchestrator_port": 8080,
                "cline_specialist_port": 8081,
                "log_level": "INFO",
                "mqtt_topics": [
                    "alicia/mcp/qa/orchestrator/+",
                    "alicia/mcp/qa/specialist/+",
                    "alicia/mcp/qa/shared/+"
                ],
                "quality_thresholds": {
                    "bdd_coverage": 8.0,
                    "test_quality": 7.0,
                    "code_review": 7.0,
                    "max_bugs": 3
                }
            }
        }
        
        for service_name, config in services_config.items():
            config_file = self.project_root / "config" / "services" / f"{service_name}.json"
            config_file.parent.mkdir(exist_ok=True)
            
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
            print(f"  ✅ Created config for {service_name}")
    
    def create_environment_configs(self):
        """Create environment-specific configuration files"""
        print("🌍 Creating environment-specific configurations...")
        
        environments = {
            "development": {
                "environment": "development",
                "debug_mode": True,
                "log_level": "DEBUG",
                "mqtt_broker": "mqtts://localhost:8883",
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "alicia_dev"
                }
            },
            "staging": {
                "environment": "staging",
                "debug_mode": False,
                "log_level": "INFO",
                "mqtt_broker": "mqtts://staging.alicia.local:8883",
                "database": {
                    "host": "staging-db.alicia.local",
                    "port": 5432,
                    "name": "alicia_staging"
                }
            },
            "production": {
                "environment": "production",
                "debug_mode": False,
                "log_level": "WARNING",
                "mqtt_broker": "mqtts://mqtt.alicia.local:8883",
                "database": {
                    "host": "prod-db.alicia.local",
                    "port": 5432,
                    "name": "alicia_prod"
                }
            }
        }
        
        for env_name, config in environments.items():
            env_file = self.project_root / "config" / "environments" / f"{env_name}.json"
            
            with open(env_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"  ✅ Created {env_name} environment config")
    
    def create_infrastructure_directory(self):
        """Create infrastructure directory for deployment configs"""
        print("🏗️ Creating infrastructure directory...")
        
        infra_dir = self.project_root / "infrastructure"
        infra_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "docker",
            "kubernetes",
            "terraform",
            "monitoring"
        ]
        
        for subdir in subdirs:
            (infra_dir / subdir).mkdir(exist_ok=True)
            print(f"  ✅ Created infrastructure/{subdir}")
        
        # Move Docker files
        self.organize_docker_files(infra_dir)
    
    def organize_docker_files(self, infra_dir: Path):
        """Organize Docker-related files"""
        print("🐳 Organizing Docker files...")
        
        docker_dir = infra_dir / "docker"
        
        # Move Docker Compose files
        compose_files = [
            "docker-compose.yml",
            "docker-compose.bus.yml",
            "docker-compose.cursor-cline.yml"
        ]
        
        for compose_file in compose_files:
            src = self.project_root / compose_file
            if src.exists():
                dst = docker_dir / compose_file
                shutil.move(str(src), str(dst))
                print(f"  ✅ Moved {compose_file} to infrastructure/docker/")
        
        # Create base Dockerfile
        base_dockerfile = docker_dir / "base" / "Dockerfile"
        base_dockerfile.parent.mkdir(exist_ok=True)
        
        base_dockerfile.write_text("""# Alicia Base Docker Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
""")
        
        print("  ✅ Created base Dockerfile")
    
    def create_tests_directory(self):
        """Create centralized tests directory"""
        print("🧪 Creating tests directory...")
        
        tests_dir = self.project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Create test subdirectories
        test_types = [
            "unit",
            "integration", 
            "e2e",
            "performance"
        ]
        
        for test_type in test_types:
            (tests_dir / test_type).mkdir(exist_ok=True)
            print(f"  ✅ Created tests/{test_type}")
        
        # Move existing test files
        self.move_test_files(tests_dir)
    
    def move_test_files(self, tests_dir: Path):
        """Move existing test files to centralized tests directory"""
        print("📁 Moving test files...")
        
        # Find and move test files
        test_patterns = ["*test*.py", "*_test.py", "test_*.py"]
        
        for service_dir in (self.project_root / "services").iterdir():
            if service_dir.is_dir():
                for pattern in test_patterns:
                    for test_file in service_dir.glob(pattern):
                        if test_file.is_file():
                            # Determine test type based on file name
                            if "integration" in test_file.name:
                                test_type = "integration"
                            elif "e2e" in test_file.name:
                                test_type = "e2e"
                            elif "performance" in test_file.name:
                                test_type = "performance"
                            else:
                                test_type = "unit"
                            
                            dst = tests_dir / test_type / f"{service_dir.name}_{test_file.name}"
                            shutil.move(str(test_file), str(dst))
                            print(f"  ✅ Moved {test_file.name} to tests/{test_type}/")
    
    def update_docker_compose(self):
        """Update main Docker Compose file to use new structure"""
        print("🐳 Updating Docker Compose configuration...")
        
        main_compose = self.project_root / "docker-compose.yml"
        
        compose_content = """version: '3.8'

services:
  # MQTT Broker
  mqtt-broker:
    image: eclipse-mosquitto:2.0.18
    container_name: alicia-mqtt-broker
    ports:
      - "1883:1883"
      - "8883:8883"
    volumes:
      - ./config/mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./config/mqtt/passwords:/mosquitto/config/passwords
      - ./config/mqtt/acl:/mosquitto/config/acl
    networks:
      - alicia_network

  # Alicia Config Manager
  alicia-config-manager:
    build: ./services/alicia-config-manager
    container_name: alicia-config-manager
    ports:
      - "3000:3000"
      - "3001:3001"
    environment:
      - MQTT_BROKER_URL=mqtts://mqtt-broker:8883
    depends_on:
      - mqtt-broker
    networks:
      - alicia_network

  # Alicia Monitor
  alicia-monitor:
    build: ./services/alicia-monitor
    container_name: alicia-monitor
    ports:
      - "3002:3002"
    environment:
      - MQTT_BROKER_URL=mqtts://mqtt-broker:8883
    depends_on:
      - mqtt-broker
    networks:
      - alicia_network

  # MCP QA Orchestrator
  mcp-qa-orchestrator:
    build: ./services/mcp-qa-orchestrator
    container_name: mcp-qa-orchestrator
    ports:
      - "8080:8080"
      - "8081:8081"
    environment:
      - MQTT_BROKER_URL=mqtts://mqtt-broker:8883
      - GROK_API_KEY=free_with_cline
    depends_on:
      - mqtt-broker
    networks:
      - alicia_network

networks:
  alicia_network:
    driver: bridge
"""
        
        with open(main_compose, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        print("  ✅ Updated main Docker Compose file")
    
    def create_centralized_scripts(self):
        """Create centralized scripts directory"""
        print("📜 Creating centralized scripts...")
        
        scripts_dir = self.project_root / "scripts"
        
        # Create script subdirectories
        script_types = [
            "setup",
            "deployment",
            "maintenance",
            "testing"
        ]
        
        for script_type in script_types:
            (scripts_dir / script_type).mkdir(exist_ok=True)
            print(f"  ✅ Created scripts/{script_type}")
        
        # Create main setup script
        setup_script = scripts_dir / "setup" / "setup_alicia.py"
        setup_script.write_text("""#!/usr/bin/env python3
\"\"\"
Alicia Smart Home AI - Main Setup Script
========================================

This script sets up the entire Alicia system with proper configuration.

Usage:
    python setup_alicia.py [environment]
    
Environments:
    - development (default)
    - staging
    - production
\"\"\"

import os
import sys
import json
from pathlib import Path

def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    print(f"🚀 Setting up Alicia Smart Home AI ({environment})")
    print("=" * 50)
    
    # Load environment configuration
    config_file = Path("config/environments") / f"{environment}.json"
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        sys.exit(1)
    
    with open(config_file) as f:
        config = json.load(f)
    
    print(f"✅ Loaded {environment} configuration")
    
    # Set up environment variables
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please copy env.example to .env")
        sys.exit(1)
    
    print("✅ Environment variables configured")
    
    # Create necessary directories
    dirs_to_create = [
        "logs",
        "output",
        "data"
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created {dir_name}/ directory")
    
    print("\\n🎉 Alicia setup completed successfully!")
    print(f"Environment: {environment}")
    print("Next steps:")
    print("1. Review and update .env file")
    print("2. Start services: docker-compose up -d")
    print("3. Check health: python scripts/testing/health_check.py")

if __name__ == "__main__":
    main()
""")
        
        print("  ✅ Created main setup script")
    
    def create_readme(self):
        """Create main project README"""
        print("📚 Creating main project README...")
        
        readme_content = """# Alicia Smart Home AI

A comprehensive smart home AI system with microservices architecture, MQTT communication, and advanced automation capabilities.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Alicia Smart Home AI                        │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Services    │  Backend Services    │  AI Services     │
│  • Config Manager     │  • Device Manager    │  • Voice Router  │
│  • Monitor Dashboard  │  • Security Gateway  │  • STT/TTS       │
│  • Monitor Proxy      │  • Service Registry  │  • AI Service    │
├─────────────────────────────────────────────────────────────────┤
│                    MQTT Message Bus                            │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                         │
│  • Docker Containers  │  • MQTT Broker      │  • Databases     │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend services)

### Setup
1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd alicia
   cp env.example .env
   python scripts/setup/setup_alicia.py
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Check system health:**
   ```bash
   python scripts/testing/health_check.py
   ```

## 📁 Project Structure

```
alicia/
├── .env.example              # Environment template
├── .env                      # Environment variables (gitignored)
├── docker-compose.yml        # Main orchestration
├── services/                 # All microservices
│   ├── alicia-config-manager/
│   ├── alicia-monitor/
│   ├── mcp-qa-orchestrator/
│   └── bus-services/
├── config/                   # Centralized configuration
│   ├── environments/
│   ├── mqtt/
│   └── services/
├── infrastructure/           # Deployment configs
│   ├── docker/
│   └── kubernetes/
├── tests/                    # All tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                  # Utility scripts
│   ├── setup/
│   ├── deployment/
│   └── testing/
└── docs/                     # Documentation
    ├── architecture/
    └── api/
```

## 🔧 Configuration

### Environment Variables
All configuration is managed through a single `.env` file at the project root. Copy `env.example` to `.env` and customize as needed.

### Service Configuration
Each service has its own configuration file in `config/services/` that can be customized per environment.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test types
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

## 📊 Monitoring

- **System Health**: http://localhost:8082/health
- **Config Manager**: http://localhost:3000
- **Monitor Dashboard**: http://localhost:3002
- **MQTT Broker**: mqtts://localhost:8883

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review the troubleshooting guide
"""
        
        with open(self.project_root / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("  ✅ Created main project README")
    
    def cleanup_old_files(self):
        """Clean up old files and directories"""
        print("🧹 Cleaning up old files...")
        
        # Remove old environment files
        old_env_files = [
            "alicia-config-manager/env.example",
            "alicia-orchestration/env.example",
            "mcp-qa-orchestrator/env.example"
        ]
        
        for env_file in old_env_files:
            file_path = self.project_root / env_file
            if file_path.exists():
                file_path.unlink()
                print(f"  ✅ Removed {env_file}")
        
        # Remove old bus-config directory (moved to config/mqtt)
        bus_config_dir = self.project_root / "bus-config"
        if bus_config_dir.exists():
            shutil.rmtree(bus_config_dir)
            print("  ✅ Removed old bus-config directory")
    
    def run_reorganization(self):
        """Run the complete reorganization process"""
        print("🚀 Starting Alicia Project Reorganization")
        print("=" * 60)
        
        try:
            self.create_backup()
            self.create_services_directory()
            self.create_centralized_config()
            self.create_environment_configs()
            self.create_infrastructure_directory()
            self.create_tests_directory()
            self.create_centralized_scripts()
            self.update_docker_compose()
            self.create_readme()
            self.cleanup_old_files()
            
            print("\n" + "=" * 60)
            print("✅ Project reorganization completed successfully!")
            print("=" * 60)
            
            print("\n📋 Summary of changes:")
            print("• Created centralized services/ directory")
            print("• Moved all services to services/ subdirectory")
            print("• Created centralized config/ directory")
            print("• Created single .env.example at project root")
            print("• Organized Docker files in infrastructure/")
            print("• Created centralized tests/ directory")
            print("• Updated Docker Compose configuration")
            print("• Created comprehensive project README")
            
            print("\n🎯 Next steps:")
            print("1. Review the new structure")
            print("2. Copy env.example to .env and configure")
            print("3. Test the reorganized structure")
            print("4. Update any hardcoded paths in your code")
            
        except Exception as e:
            print(f"\n❌ Reorganization failed: {e}")
            print("Check the backup in backup_before_reorganization/")
            raise

def main():
    """Main entry point"""
    reorganizer = ProjectReorganizer()
    reorganizer.run_reorganization()

if __name__ == "__main__":
    main()
