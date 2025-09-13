#!/bin/bash

# Alicia MCP Orchestration Monitor Script
# This script monitors the orchestration system status

set -e

echo "📊 Alicia MCP Orchestration System Monitor"
echo "=========================================="

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Check MCP server status
echo "🐳 MCP Server Status:"
if docker ps | grep -q mcp-server; then
    echo "✅ Running on port ${MCP_SERVER_PORT}"
    echo "   Health: $(curl -s http://localhost:${MCP_SERVER_PORT}/health | jq -r '.status' 2>/dev/null || echo 'Unknown')"
else
    echo "❌ Not running"
fi

# Check Cline status
echo ""
echo "🤖 Cline Agent Status:"
if command -v cline &> /dev/null; then
    if cline --test-connection > /dev/null 2>&1; then
        echo "✅ Connected to MCP server"
        echo "   Model: ${CLINE_MODEL}"
        echo "   Project: ${ALICIA_PROJECT_PATH}"
    else
        echo "❌ Connection failed"
    fi
else
    echo "❌ Cline not installed"
fi

# Check current phase
echo ""
echo "📋 Current Phase:"
if command -v cline &> /dev/null; then
    current_phase=$(cline --get-current-phase 2>/dev/null || echo "Unknown")
    echo "   Phase: ${current_phase}"
    
    if [ "$current_phase" != "Unknown" ]; then
        phase_progress=$(cline --get-phase-progress 2>/dev/null || echo "Unknown")
        echo "   Progress: ${phase_progress}"
        
        quality_score=$(cline --get-quality-score 2>/dev/null || echo "Unknown")
        echo "   Quality Score: ${quality_score}"
    fi
else
    echo "   Status: Unknown (Cline not available)"
fi

# Check quality gates
echo ""
echo "🔍 Quality Gates:"
echo "   Min Score: ${MIN_QUALITY_SCORE}"
echo "   Max Retries: ${MAX_RETRY_ATTEMPTS}"
echo "   Timeout: ${PHASE_TIMEOUT_HOURS} hours"

# Check system resources
echo ""
echo "💻 System Resources:"
echo "   CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "   Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "   Disk Usage: $(df -h . | awk 'NR==2{printf "%s", $5}')"

# Check logs
echo ""
echo "📝 Recent Logs:"
echo "   MCP Server: docker logs mcp-server --tail 5"
echo "   Cline Agent: cline --logs --tail 5"

# Check services
echo ""
echo "🔧 Alicia Services:"
if [ -d "../bus-services" ]; then
    service_count=$(find ../bus-services -name "main.py" | wc -l)
    echo "   Services Available: ${service_count}"
    
    # Check if any services are running
    running_services=$(docker ps --format "table {{.Names}}" | grep alicia | wc -l)
    echo "   Services Running: ${running_services}"
else
    echo "   Services Directory: Not found"
fi

echo ""
echo "🛠️  Commands:"
echo "   Start: ./scripts/start-orchestration.sh"
echo "   Stop: docker stop mcp-server"
echo "   Restart: docker restart mcp-server"
echo "   Logs: docker logs mcp-server -f"
echo "   Status: cline --status"
echo "   Help: cline --help"
echo ""
