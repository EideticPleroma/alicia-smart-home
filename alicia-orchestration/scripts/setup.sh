#!/bin/bash

# Alicia MCP Orchestration Setup Script
# This script sets up the MCP orchestration system for the Alicia project

set -e

echo "🚀 Setting up Alicia MCP Orchestration System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "   - Set your Grok API key"
    echo "   - Configure MQTT credentials"
    echo "   - Adjust quality gate settings"
    read -p "Press Enter to continue after editing .env file..."
fi

# Load environment variables
source .env

# Start MCP server
echo "🐳 Starting MCP server..."
if docker ps | grep -q mcp-server; then
    echo "MCP server is already running"
else
    docker run -d --name mcp-server -p ${MCP_SERVER_PORT}:4000 mcpgee/mcp-server:latest
    echo "✅ MCP server started on port ${MCP_SERVER_PORT}"
fi

# Wait for MCP server to be ready
echo "⏳ Waiting for MCP server to be ready..."
sleep 10

# Test MCP server connection
if curl -s http://localhost:${MCP_SERVER_PORT}/health > /dev/null; then
    echo "✅ MCP server is ready"
else
    echo "❌ MCP server is not responding. Please check the logs:"
    echo "   docker logs mcp-server"
    exit 1
fi

# Install Cline if not already installed
if ! command -v cline &> /dev/null; then
    echo "📦 Installing Cline..."
    npm install -g @cline/cli
    echo "✅ Cline installed"
else
    echo "✅ Cline is already installed"
fi

# Configure Cline
echo "⚙️  Configuring Cline..."
mkdir -p ~/.cline
cp config/cline-config.json ~/.cline/config.json
echo "✅ Cline configured"

# Test Cline connection
echo "🔍 Testing Cline connection..."
if cline --test-connection > /dev/null 2>&1; then
    echo "✅ Cline connection successful"
else
    echo "❌ Cline connection failed. Please check your configuration:"
    echo "   cline --test-connection"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p temp
echo "✅ Directories created"

# Set up monitoring
echo "📊 Setting up monitoring..."
chmod +x scripts/monitor.sh
chmod +x scripts/start-orchestration.sh
echo "✅ Monitoring setup complete"

echo ""
echo "🎉 Alicia MCP Orchestration System setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and edit .env file with your settings"
echo "2. Run: ./scripts/start-orchestration.sh"
echo "3. Monitor with: ./scripts/monitor.sh"
echo ""
echo "Documentation:"
echo "- Quick Start: docs/MCP_QUICK_START.md"
echo "- Full Guide: docs/MCP_IMPLEMENTATION_GUIDE_HUMAN_READABLE.md"
echo "- Alicia Context: docs/MCP_ORCHESTRATION_SYSTEM_ALICIA_CONTEXT.md"
echo ""
