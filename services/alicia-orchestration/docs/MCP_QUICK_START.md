# MCP Orchestration Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Start MCP Server
```bash
# Pull and run MCP server
docker pull mcpgee/mcp-server:latest
docker run -d --name mcp-server -p 4000:4000 mcpgee/mcp-server:latest

# Verify it's running
curl http://localhost:4000/health
```

### 2. Configure Cline with grok-code-fast-1
```bash
# Install Cline
npm install -g @cline/cli

# Create config file
mkdir -p ~/.cline
cat > ~/.cline/config.json << EOF
{
  "model": "grok-code-fast-1",
  "mcp_server": {
    "host": "localhost",
    "port": 4000,
    "protocol": "mcp"
  },
  "project": {
    "name": "alicia-microservices",
    "path": "$(pwd)"
  }
}
EOF

# Test connection
cline --test-connection
```

### 3. Set Environment Variables
```bash
# Create .env file
cat > .env << EOF
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=4000
CLINE_MODEL=grok-code-fast-1
CLINE_API_KEY=your_grok_api_key_here
MIN_QUALITY_SCORE=9.0
GIT_AUTO_PUSH=false
EOF
```

## 🤖 What Cline Automates
- ✅ All microservices code generation
- ✅ Git operations (except push)
- ✅ Code quality checks
- ✅ API documentation
- ✅ Testing and validation
- ✅ Service integration

## 👤 What You Configure Manually
- 🔧 MCP server setup
- 🔧 Cline configuration
- 🔧 Environment variables
- 🔧 API keys and credentials
- 🔧 Git push operations
- 🔧 External service setup

## 📋 Phase Overview

| Phase | Duration | Cline Tasks | Manual Tasks |
|-------|----------|-------------|--------------|
| **Phase 1: Foundation** | 2-3 weeks | MQTT, Security, Health Monitor | API keys, SSL certs |
| **Phase 2: Voice Pipeline** | 3-4 weeks | STT, AI, TTS, Voice Router | Grok API key, Audio setup |
| **Phase 3: Device Integration** | 3-4 weeks | Sonos, HA Bridge, Device Control | HA token, Device credentials |
| **Phase 4: Advanced Features** | 4-5 weeks | Grok, Personality, Multi-lang | Language models, Profiles |
| **Phase 5: Production** | 3-4 weeks | Load Balancer, Metrics, Docs | Production config, Monitoring |

## 🎯 Quality Gates
- **Passing Score**: 9.0+ out of 10
- **Retry Limit**: 3 attempts per phase
- **Categories**: Code Quality (30%), Functionality (25%), Performance (20%), Security (15%), Documentation (10%)

## 🔧 Troubleshooting

### MCP Server Issues
```bash
# Check status
docker ps | grep mcp-server

# View logs
docker logs mcp-server

# Restart
docker restart mcp-server
```

### Cline Connection Issues
```bash
# Test connection
cline --test-connection

# Show config
cline --show-config

# Restart agent
cline --restart
```

### Quality Gate Failures
1. Review CodeReviewAgent feedback
2. Fix identified issues
3. Resubmit for review
4. Escalate after 3 attempts

## 📊 Status Monitoring
- **Real-time**: Phase progress, quality scores
- **Daily**: Progress summaries, issue tracking
- **Weekly**: Performance trends, resource usage

## 🚨 Escalation Points
- Quality score < 7.0 after 3 attempts
- Agent unresponsive > 30 minutes
- Phase timeout exceeded
- Critical security vulnerabilities

## 📞 Support Resources
- **MCP Server**: [GitHub Repository](https://github.com/mcpgee/mcp-server)
- **Cline Docs**: [Cline Documentation](https://cline.dev/docs)
- **Project Issues**: Create GitHub issues for project-specific problems

---

**Ready to start?** Run the quick setup commands above, then begin Phase 1 with your Alicia microservices architecture!
