@echo off
REM Alicia Smart Home AI Assistant - Setup Script (Windows)

echo 🤖 Alicia Smart Home AI Assistant - Setup Script
echo =================================================

REM Check if .env exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    if exist "env.template" (
        copy env.template .env
        echo ✅ .env file created from template
    ) else (
        echo ❌ env.template not found. Please create .env manually.
        pause
        exit /b 1
    )
) else (
    echo ℹ️  .env file already exists
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "bus-data" mkdir bus-data
if not exist "bus-logs" mkdir bus-logs
if not exist "logs" mkdir logs
if not exist "alicia-config-manager\logs" mkdir alicia-config-manager\logs
echo ✅ Directories created

REM Setup MQTT configuration
echo 🔧 Setting up MQTT configuration...
if exist "mqtt-config-manager.py" (
    python mqtt-config-manager.py dev
    echo ✅ MQTT configuration setup complete
) else (
    echo ⚠️  mqtt-config-manager.py not found, skipping MQTT setup
)

REM Check Docker
echo 🐳 Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed
) else (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose is installed
) else (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys and configuration
echo 2. Start the system: docker-compose -f docker-compose.bus.yml up -d
echo 3. Access the web interface: http://localhost:3002
echo.
echo For development:
echo 1. Start development environment: docker-compose -f alicia-config-manager\docker-compose.yml up -d
echo 2. Access config manager: http://localhost:3002
echo.
echo Happy coding! 🚀
pause
