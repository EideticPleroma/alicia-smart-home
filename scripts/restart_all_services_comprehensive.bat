@echo off
echo ========================================
echo Alicia Microservices - Comprehensive Restart
echo ========================================

echo.
echo [1/4] Stopping all existing containers...
docker stop $(docker ps -aq) 2>nul
docker rm $(docker ps -aq) 2>nul

echo.
echo [2/4] Creating network...
docker network create alicia_network 2>nul

echo.
echo [3/4] Starting MQTT Broker...
docker run -d --name alicia_mqtt_broker --network alicia_network -p 1884:1883 eclipse-mosquitto:2.0.18

echo.
echo [4/4] Starting all services...
echo Starting Core Infrastructure Services...

echo - Security Gateway (8009)...
docker run -d --name alicia_security_gateway --network alicia_network -p 8009:8009 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-security-gateway

echo - Device Registry (8010)...
docker run -d --name alicia_device_registry --network alicia_network -p 8010:8010 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-device-registry

echo - Configuration Manager (8015)...
docker run -d --name alicia_configuration_manager --network alicia_network -p 8015:8015 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-configuration-manager

echo - Config Service (8026)...
docker run -d --name alicia_config_service --network alicia_network -p 8026:8026 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-config-service

echo - Discovery Service (8012)...
docker run -d --name alicia_discovery_service --network alicia_network -p 8012:8012 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-discovery-service

echo - Health Monitor (8013)...
docker run -d --name alicia_health_monitor --network alicia_network -p 8013:8013 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-health-monitor

echo - Service Orchestrator (8014)...
docker run -d --name alicia_service_orchestrator --network alicia_network -p 8014:8014 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-service-orchestrator

echo.
echo Starting Voice Processing Pipeline...
echo - STT Service (8001)...
docker run -d --name alicia_stt_service --network alicia_network -p 8001:8001 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-stt-service

echo - AI Service (8002)...
docker run -d --name alicia_ai_service --network alicia_network -p 8002:8002 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-ai-service

echo - TTS Service (8003)...
docker run -d --name alicia_tts_service --network alicia_network -p 8003:8003 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-tts-service

echo - Voice Router (8004)...
docker run -d --name alicia_voice_router --network alicia_network -p 8004:8004 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-voice-router

echo.
echo Starting Device Integration Services...
echo - Device Manager (8006)...
docker run -d --name alicia_device_manager --network alicia_network -p 8006:8006 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-device-manager

echo - HA Bridge (8016)...
docker run -d --name alicia_ha_bridge --network alicia_network -p 8016:8016 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-ha-bridge

echo - Sonos Service (8017)...
docker run -d --name alicia_sonos_service --network alicia_network -p 8017:8017 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-sonos-service

echo - Device Control (8018)...
docker run -d --name alicia_device_control --network alicia_network -p 8018:8018 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-device-control

echo - Grok Integration (8019)...
docker run -d --name alicia_grok_integration --network alicia_network -p 8019:8019 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-grok-integration

echo.
echo Starting Advanced Features Services...
echo - Advanced Voice (8020)...
docker run -d --name alicia_advanced_voice --network alicia_network -p 8020:8020 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-advanced-voice

echo - Personality System (8021)...
docker run -d --name alicia_personality_system --network alicia_network -p 8021:8021 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-personality-system

echo - Multi-Language (8022)...
docker run -d --name alicia_multi_language --network alicia_network -p 8022:8022 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-multi-language

echo - Load Balancer (8023)...
docker run -d --name alicia_load_balancer --network alicia_network -p 8023:8023 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-load-balancer

echo.
echo Starting Monitoring & Analytics Services...
echo - Metrics Collector (8024)...
docker run -d --name alicia_metrics_collector --network alicia_network -p 8024:8024 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-metrics-collector

echo - Event Scheduler (8025)...
docker run -d --name alicia_event_scheduler --network alicia_network -p 8025:8025 -e MQTT_BROKER=alicia_mqtt_broker -e MQTT_PORT=1883 alicia-event-scheduler

echo.
echo ========================================
echo All services started! Checking status...
echo ========================================
timeout /t 10 /nobreak >nul
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ========================================
echo Health Check Summary
echo ========================================
echo MQTT Broker: http://localhost:1884
echo Security Gateway: http://localhost:8009/health
echo Device Registry: http://localhost:8010/health
echo Configuration Manager: http://localhost:8015/health
echo Config Service: http://localhost:8026/health
echo Discovery Service: http://localhost:8012/health
echo Health Monitor: http://localhost:8013/health
echo Service Orchestrator: http://localhost:8014/health
echo.
echo Voice Pipeline:
echo - STT Service: http://localhost:8001/health
echo - AI Service: http://localhost:8002/health
echo - TTS Service: http://localhost:8003/health
echo - Voice Router: http://localhost:8004/health
echo.
echo Device Integration:
echo - Device Manager: http://localhost:8006/health
echo - HA Bridge: http://localhost:8016/health
echo - Sonos Service: http://localhost:8017/health
echo - Device Control: http://localhost:8018/health
echo - Grok Integration: http://localhost:8019/health
echo.
echo Advanced Features:
echo - Advanced Voice: http://localhost:8020/health
echo - Personality System: http://localhost:8021/health
echo - Multi-Language: http://localhost:8022/health
echo - Load Balancer: http://localhost:8023/health
echo.
echo Monitoring & Analytics:
echo - Metrics Collector: http://localhost:8024/health
echo - Event Scheduler: http://localhost:8025/health
echo ========================================
