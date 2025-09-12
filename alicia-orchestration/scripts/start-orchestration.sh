#!/bin/bash

# Alicia MCP Orchestration Start Script
# This script starts the MCP orchestration system

set -e

echo "🚀 Starting Alicia MCP Orchestration System..."

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Check if MCP server is running
if ! docker ps | grep -q mcp-server; then
    echo "❌ MCP server is not running. Please run setup.sh first."
    exit 1
fi

# Check if Cline is configured
if ! cline --test-connection > /dev/null 2>&1; then
    echo "❌ Cline is not properly configured. Please run setup.sh first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start orchestration
echo "🎯 Starting orchestration..."

# Initialize phase manager
echo "📋 Initializing phase manager..."
cline --init-phase-manager --config config/phases.json

# Start quality gates
echo "🔍 Starting quality gates..."
cline --start-quality-gates --config config/quality-gates.json

# Begin Phase 1
echo "🏁 Starting Phase 1: Foundation Setup"
cline --start-phase phase-1 --config config/phases.json

echo ""
echo "🎉 Alicia MCP Orchestration System started!"
echo ""
echo "Current Status:"
echo "- Phase: 1 (Foundation Setup)"
echo "- MCP Server: Running on port ${MCP_SERVER_PORT}"
echo "- Cline Agent: Active with grok-code-fast-1"
echo "- Quality Gates: Active (min score: ${MIN_QUALITY_SCORE})"
echo ""
echo "Monitoring:"
echo "- Run: ./scripts/monitor.sh"
echo "- Logs: docker logs mcp-server"
echo "- Status: cline --status"
echo ""
echo "Next Phase:"
echo "- Phase 2 will start automatically when Phase 1 passes quality gates"
echo "- Manual approval required for phase progression"
echo ""
