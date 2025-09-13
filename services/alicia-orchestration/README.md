# Alicia MCP Orchestration System

## 🎯 **Overview**
This directory contains the MCP (Model Context Protocol) orchestration system for the Alicia Smart Home AI Assistant microservices ecosystem. It provides automated development workflows using Cline with grok-code-fast-1 for microservices development.

## 📁 **Directory Structure**
```
alicia-orchestration/
├── README.md                      # This file
├── docs/                          # Documentation
│   ├── MCP_ORCHESTRATION_SYSTEM_DESIGN.md
│   ├── MCP_PHASE_PLANS_DETAILED.md
│   ├── MCP_AGENT_WORKFLOWS.md
│   ├── MCP_IMPLEMENTATION_GUIDE_HUMAN_READABLE.md
│   ├── MCP_QUICK_START.md
│   └── MCP_ORCHESTRATION_SYSTEM_ALICIA_CONTEXT.md
├── config/                        # Configuration files
│   ├── phases.json
│   ├── quality-gates.json
│   ├── service-mappings.json
│   └── cline-config.json
├── phases/                        # Phase definitions
│   ├── phase-1-foundation.md
│   ├── phase-2-voice-pipeline.md
│   ├── phase-3-device-integration.md
│   ├── phase-4-advanced-features.md
│   └── phase-5-production.md
├── scripts/                       # Setup and management scripts
│   ├── setup.sh
│   ├── start-orchestration.sh
│   └── monitor.sh
└── .env.example                   # Environment variables template
```

## 🚀 **Quick Start**

### **1. Setup MCP Server**
```bash
# Start MCP server
docker run -d --name mcp-server -p 4000:4000 mcpgee/mcp-server:latest

# Verify it's running
curl http://localhost:4000/health
```

### **2. Configure Cline**
```bash
# Install Cline
npm install -g @cline/cli

# Configure for Alicia project
cp config/cline-config.json ~/.cline/config.json
```

### **3. Start Orchestration**
```bash
# Run setup script
./scripts/setup.sh

# Start orchestration
./scripts/start-orchestration.sh
```

## 📚 **Documentation**

- **[Quick Start Guide](docs/MCP_QUICK_START.md)** - 5-minute setup
- **[Implementation Guide](docs/MCP_IMPLEMENTATION_GUIDE_HUMAN_READABLE.md)** - Detailed setup
- **[Alicia Context](docs/MCP_ORCHESTRATION_SYSTEM_ALICIA_CONTEXT.md)** - Project-specific integration
- **[Phase Plans](docs/MCP_PHASE_PLANS_DETAILED.md)** - Detailed phase breakdown
- **[Agent Workflows](docs/MCP_AGENT_WORKFLOWS.md)** - Cline and CodeReviewAgent workflows
- **[System Design](docs/MCP_ORCHESTRATION_SYSTEM_DESIGN.md)** - Complete architecture

## 🤖 **What Cline Automates**
- All microservices implementation in `../bus-services/`
- Git operations (branch, merge, tag - no push)
- Code quality checks and self-review
- API documentation and testing
- Service integration and orchestration

## 👤 **What You Configure Manually**
- MCP server setup
- Cline configuration with grok-code-fast-1
- Environment variables and API keys
- Git push operations
- External service dependencies

## 🔧 **Configuration**

### **Environment Variables**
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

### **Phase Configuration**
Edit `config/phases.json` to customize phase requirements and success criteria.

### **Quality Gates**
Modify `config/quality-gates.json` to adjust scoring criteria and thresholds.

## 📊 **Monitoring**

### **Status Monitoring**
```bash
# Check orchestration status
./scripts/monitor.sh

# View logs
docker logs mcp-server
```

### **Quality Metrics**
- Phase completion percentage
- Quality scores and trends
- Agent performance metrics
- System health indicators

## 🚨 **Troubleshooting**

### **Common Issues**
- **MCP Server**: `docker logs mcp-server`
- **Cline Connection**: `cline --test-connection`
- **Quality Gates**: Review CodeReviewAgent feedback

### **Escalation**
- Quality score < 7.0: Immediate escalation
- Agent unresponsive: Restart and investigate
- Phase timeout: Manual intervention needed

## 📞 **Support**

- **MCP Server**: [GitHub Repository](https://github.com/mcpgee/mcp-server)
- **Cline Docs**: [Cline Documentation](https://cline.dev/docs)
- **Project Issues**: Create GitHub issues for project-specific problems

## 🔄 **Integration with Alicia Project**

This orchestration system is designed to work seamlessly with your existing Alicia microservices architecture:

- **Services**: Integrates with `../bus-services/` directory
- **Configuration**: Works with `../alicia-config-manager/`
- **MQTT**: Uses existing `alicia/` topic structure
- **Docker**: Extends `../docker-compose.bus.yml`

The system follows your established patterns and integrates with your existing development workflow while providing automated microservices development capabilities.
