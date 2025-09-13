#!/bin/bash
# Health check script for MCP services

# Check Cursor Orchestrator
curl -f http://localhost:8080/health || exit 1

# Check Cline Specialist
curl -f http://localhost:8081/health || exit 1

echo "All MCP services are healthy"
