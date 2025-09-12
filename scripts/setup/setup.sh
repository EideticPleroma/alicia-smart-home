#!/bin/bash
# Alicia Smart Home AI Assistant - Setup Script

set -e

echo "🤖 Alicia Smart Home AI Assistant - Setup Script"
echo "================================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ .env file created from template"
    else
        echo "❌ env.template not found. Please create .env manually."
        exit 1
    fi
else
    echo "ℹ️  .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p bus-data bus-logs logs
mkdir -p alicia-config-manager/logs
echo "✅ Directories created"

# Setup MQTT configuration
echo "🔧 Setting up MQTT configuration..."
if [ -f "mqtt-config-manager.py" ]; then
    python mqtt-config-manager.py dev
    echo "✅ MQTT configuration setup complete"
else
    echo "⚠️  mqtt-config-manager.py not found, skipping MQTT setup"
fi

# Check Docker
echo "🐳 Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Start the system: docker-compose -f docker-compose.bus.yml up -d"
echo "3. Access the web interface: http://localhost:3002"
echo ""
echo "For development:"
echo "1. Start development environment: docker-compose -f alicia-config-manager/docker-compose.yml up -d"
echo "2. Access config manager: http://localhost:3002"
echo ""
echo "Happy coding! 🚀"
