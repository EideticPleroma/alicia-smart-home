@echo off
REM Alicia Config Manager - Setup Test Script (Windows)
REM This script tests the Docker setup and basic functionality

echo 🚀 Testing Alicia Config Manager Setup...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    exit /b 1
)

echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed
    exit /b 1
)

echo ✅ docker-compose is available

REM Validate docker-compose.yml
echo 🔍 Validating docker-compose.yml...
docker-compose config >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose.yml has errors
    exit /b 1
)

echo ✅ docker-compose.yml is valid

REM Build the services
echo 🔨 Building services...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Failed to build services
    exit /b 1
)

echo ✅ Services built successfully

REM Start the services
echo 🚀 Starting services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)

echo ✅ Services started successfully

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo 🏥 Checking service health...

REM Check MQTT broker
docker-compose exec alicia_bus_core mosquitto_pub -h localhost -t "test" -m "hello" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MQTT broker is healthy
) else (
    echo ❌ MQTT broker is not responding
)

REM Check backend
curl -f http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is healthy
) else (
    echo ❌ Backend is not responding
)

REM Check frontend
curl -f http://localhost:3002 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is healthy
) else (
    echo ❌ Frontend is not responding
)

echo.
echo 🎉 Setup test completed!
echo.
echo Services are running at:
echo   - Frontend: http://localhost:3002
echo   - Backend API: http://localhost:3000
echo   - MQTT Broker: localhost:1883
echo.
echo To stop services: docker-compose down
echo To view logs: docker-compose logs -f
