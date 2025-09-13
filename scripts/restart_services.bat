@echo off
echo 🚀 Restarting All Alicia Services...
echo ==================================================

echo 🌐 Creating Docker network...
docker network create alicia_network 2>nul

echo.
echo 📦 Starting MQTT Broker...
docker run -d --name alicia_bus_core --network alicia_network -p 1883:1883 -p 8883:8883 -p 9001:9001 -v "D:\Projects\Alicia\Alicia (v1)\config\mqtt\mosquitto-simple.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto:2.0.18
timeout /t 5 /nobreak >nul

echo.
echo 📦 Starting STT Service...
docker run -d --name alicia_stt_service --network alicia_network -p 8004:8004 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-stt-service
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting AI Service...
docker run -d --name alicia_ai_service --network alicia_network -p 8005:8005 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-ai-service
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting TTS Service...
docker run -d --name alicia_tts_service --network alicia_network -p 8006:8006 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-tts-service
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting Voice Router...
docker run -d --name alicia_voice_router --network alicia_network -p 8007:8007 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-voice-router
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting Device Manager...
docker run -d --name alicia_device_manager --network alicia_network -p 8008:8008 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-device-manager
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting Security Gateway...
docker run -d --name alicia_security_gateway --network alicia_network -p 8009:8009 -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-security-gateway
timeout /t 10 /nobreak >nul

echo.
echo 📦 Starting Device Registry...
docker run -d --name alicia_device_registry --network alicia_network -p 8010:8010 -v "D:\Projects\Alicia\Alicia (v1)\data:/app/data" -e MQTT_BROKER=alicia_bus_core -e MQTT_PORT=1883 alicia-device-registry
timeout /t 10 /nobreak >nul

echo.
echo ==================================================
echo 📊 Final Service Status:
docker ps --filter name=alicia

echo.
echo 🎉 All services restarted successfully!
pause


