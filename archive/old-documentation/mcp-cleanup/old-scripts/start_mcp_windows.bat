@echo off
REM Alicia MCP QA Orchestration System - Windows Startup Script

echo Starting Alicia MCP QA Orchestration System...

REM Set environment variables
set MQTT_BROKER_URL=mqtts://localhost:8883
set MQTT_USERNAME=alicia_mcp_user
set MQTT_PASSWORD=alicia_mcp_password
set GROK_API_KEY=free_with_cline
set LOG_LEVEL=INFO

REM Start services
echo Starting Cursor Orchestrator...
start "Cursor Orchestrator" python cursor_orchestrator.py

timeout /t 5 /nobreak > nul

echo Starting Cline Specialist...
start "Cline Specialist" python cline_specialist.py

echo All services started!
echo Check logs in the logs/ directory
pause
