#!/bin/bash
# Alicia Config Manager - Setup Test Script
# This script tests the Docker setup and basic functionality

echo "🚀 Testing Alicia Config Manager Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

echo "✅ docker-compose is available"

# Validate docker-compose.yml
echo "🔍 Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has errors"
    exit 1
fi

# Build the services
echo "🔨 Building services..."
if docker-compose build; then
    echo "✅ Services built successfully"
else
    echo "❌ Failed to build services"
    exit 1
fi

# Start the services
echo "🚀 Starting services..."
if docker-compose up -d; then
    echo "✅ Services started successfully"
else
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Check MQTT broker
if docker-compose exec alicia_bus_core mosquitto_pub -h localhost -t "test" -m "hello" > /dev/null 2>&1; then
    echo "✅ MQTT broker is healthy"
else
    echo "❌ MQTT broker is not responding"
fi

# Check backend
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
if curl -f http://localhost:3002 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Setup test completed!"
echo ""
echo "Services are running at:"
echo "  - Frontend: http://localhost:3002"
echo "  - Backend API: http://localhost:3000"
echo "  - MQTT Broker: localhost:1883"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
