# Alicia Project Organization Plan

## 🎯 Current Issues
- Multiple environment files scattered across services
- Inconsistent configuration management
- Duplicate files and unclear ownership
- Mixed responsibilities between services

## 🏗️ Proposed Clean Structure

```
alicia/
├── .env.example                    # SINGLE environment template
├── .env                           # SINGLE environment file (gitignored)
├── docker-compose.yml             # Main orchestration
├── docker-compose.dev.yml         # Development environment
├── docker-compose.prod.yml        # Production environment
├── README.md                      # Main project documentation
│
├── config/                        # CENTRALIZED CONFIGURATION
│   ├── environments/
│   │   ├── development.json
│   │   ├── staging.json
│   │   └── production.json
│   ├── mqtt/
│   │   ├── mosquitto.conf
│   │   ├── acl.conf
│   │   └── passwords
│   └── services/
│       ├── alicia-config-manager.json
│       ├── alicia-monitor.json
│       └── mcp-qa-orchestrator.json
│
├── services/                      # ALL SERVICES
│   ├── alicia-config-manager/     # Configuration management service
│   ├── alicia-monitor/            # Monitoring service
│   ├── alicia-monitor-proxy/      # Monitor proxy service
│   ├── mcp-qa-orchestrator/       # MCP QA orchestration
│   └── bus-services/              # MQTT bus services
│       ├── ai-service/
│       ├── device-manager/
│       ├── security-gateway/
│       └── ...
│
├── infrastructure/                # INFRASTRUCTURE
│   ├── docker/
│   │   ├── base/
│   │   ├── services/
│   │   └── monitoring/
│   ├── kubernetes/                # Future K8s manifests
│   └── terraform/                 # Future IaC
│
├── docs/                          # DOCUMENTATION
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── user-guides/
│
├── scripts/                       # UTILITY SCRIPTS
│   ├── setup/
│   ├── deployment/
│   ├── maintenance/
│   └── testing/
│
└── tests/                         # ALL TESTS
    ├── unit/
    ├── integration/
    ├── e2e/
    └── performance/
```

## 🔧 Environment Management Strategy

### Single Environment File
- **`.env.example`** - Template with all possible variables
- **`.env`** - Actual environment file (gitignored)
- **Service-specific configs** - JSON files in `config/services/`

### Environment Variables Hierarchy
1. **System environment variables** (highest priority)
2. **`.env` file** (project level)
3. **Service-specific configs** (service level)
4. **Default values** (lowest priority)

## 📋 Migration Steps

### Phase 1: Consolidate Environment Files
1. Create single `.env.example` at project root
2. Move all environment variables to centralized file
3. Update all services to use centralized config
4. Remove duplicate environment files

### Phase 2: Reorganize Services
1. Move all services to `services/` directory
2. Update Docker Compose files
3. Update documentation paths
4. Update CI/CD scripts

### Phase 3: Centralize Configuration
1. Move all config files to `config/` directory
2. Create service-specific JSON configs
3. Update services to load from centralized config
4. Remove duplicate configuration files

### Phase 4: Clean Up Documentation
1. Update all README files
2. Consolidate documentation in `docs/`
3. Remove duplicate documentation
4. Create clear service boundaries

## 🎯 Benefits of This Structure

### Clear Separation of Concerns
- **Services** - Business logic and functionality
- **Config** - All configuration in one place
- **Infrastructure** - Deployment and infrastructure code
- **Docs** - All documentation centralized
- **Scripts** - Utility and maintenance scripts

### Single Source of Truth
- **One environment file** for the entire project
- **Centralized configuration** management
- **Consistent** across all services
- **Easy to maintain** and update

### Scalability
- **Easy to add new services**
- **Clear service boundaries**
- **Consistent patterns** across services
- **Infrastructure as code** ready

## 🚀 Implementation Priority

1. **HIGH**: Consolidate environment files
2. **HIGH**: Centralize configuration
3. **MEDIUM**: Reorganize directory structure
4. **LOW**: Update documentation and scripts

This will create a clean, maintainable, and scalable project structure.
