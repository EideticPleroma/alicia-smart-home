#!/bin/bash
# Alicia MCP QA Orchestration System - Unix Startup Script

echo "Starting Alicia MCP QA Orchestration System..."

# Set environment variables
export MQTT_BROKER_URL=mqtts://localhost:8883
export MQTT_USERNAME=alicia_mcp_user
export MQTT_PASSWORD=alicia_mcp_password
export GROK_API_KEY=free_with_cline
export LOG_LEVEL=INFO

# Start services in background
echo "Starting Cursor Orchestrator..."
python cursor_orchestrator.py &

sleep 5

echo "Starting Cline Specialist..."
python cline_specialist.py &

echo "All services started!"
echo "Check logs in the logs/ directory"
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'kill $(jobs -p); exit' INT
wait
