# Alicia Device Simulator for MQTT Testing
# This script simulates various IoT devices for testing MQTT communication

param(
    [string]$DeviceType = "sensor",
    [string]$DeviceId = "test_device_001",
    [string]$Username = "esp32_device",
    [SecureString]$Password,
    [string]$Broker = "localhost",
    [int]$Port = 1883
)

Write-Host "=== Alicia Device Simulator ===" -ForegroundColor Cyan
Write-Host "Device Type: $DeviceType" -ForegroundColor Yellow
Write-Host "Device ID: $DeviceId" -ForegroundColor Yellow
Write-Host "Broker: ${Broker}:$Port" -ForegroundColor Yellow
Write-Host ""

function Simulate-Sensor {
    Write-Host "🌡️ Simulating Temperature/Humidity Sensor..." -ForegroundColor Green

    # Generate realistic sensor data
    $temperature = Get-Random -Minimum 18 -Maximum 28
    $humidity = Get-Random -Minimum 30 -Maximum 70
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

    $sensorData = @{
        device_id = $DeviceId
        device_type = "temperature_sensor"
        temperature_celsius = $temperature
        humidity_percent = $humidity
        battery_level = (Get-Random -Minimum 70 -Maximum 100)
        timestamp = $timestamp
        location = "living_room"
    }

    $jsonData = $sensorData | ConvertTo-Json -Compress

    Write-Host "📊 Sensor Data Generated:" -ForegroundColor Blue
    Write-Host "Temperature: $temperature°C" -ForegroundColor White
    Write-Host "Humidity: $humidity%" -ForegroundColor White
    Write-Host "Battery: $($sensorData.battery_level)%" -ForegroundColor White
    Write-Host ""

    Write-Host "📡 Publishing to MQTT Topic:" -ForegroundColor Green
    Write-Host "Topic: alicia/sensors/$DeviceId" -ForegroundColor Yellow
    Write-Host "Payload: $jsonData" -ForegroundColor Gray

    # In production, this would publish to MQTT
    Write-Host "✅ Sensor data prepared for MQTT publishing" -ForegroundColor Green
}

function Simulate-SmartBulb {
    Write-Host "💡 Simulating Smart Bulb..." -ForegroundColor Green

    # Generate bulb status data
    $states = @("on", "off")
    $colors = @("warm_white", "cool_white", "red", "green", "blue")
    $brightness = Get-Random -Minimum 0 -Maximum 100

    $bulbData = @{
        device_id = $DeviceId
        device_type = "smart_bulb"
        state = $states | Get-Random
        brightness = $brightness
        color = $colors | Get-Random
        power_consumption_watts = [math]::Round(($brightness * 0.01 * 10), 2)
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    }

    $jsonData = $bulbData | ConvertTo-Json -Compress

    Write-Host "💡 Bulb Status:" -ForegroundColor Blue
    Write-Host "State: $($bulbData.state)" -ForegroundColor White
    Write-Host "Brightness: $($bulbData.brightness)%" -ForegroundColor White
    Write-Host "Color: $($bulbData.color)" -ForegroundColor White
    Write-Host "Power: $($bulbData.power_consumption_watts)W" -ForegroundColor White
    Write-Host ""

    Write-Host "📡 Publishing to MQTT Topic:" -ForegroundColor Green
    Write-Host "Topic: alicia/devices/$DeviceId/status" -ForegroundColor Yellow
    Write-Host "Payload: $jsonData" -ForegroundColor Gray

    Write-Host "✅ Smart bulb data prepared for MQTT publishing" -ForegroundColor Green
}

function Simulate-SonosSpeaker {
    Write-Host "🔊 Simulating Sonos Speaker..." -ForegroundColor Green

    # Generate speaker status data
    $playbackStates = @("playing", "paused", "stopped")
    $volumes = @(15, 20, 25, 30, 35, 40)
    $tracks = @("Jazz Classics", "Classical Music", "Pop Hits", "Rock Anthems")

    $speakerData = @{
        device_id = $DeviceId
        device_type = "sonos_speaker"
        playback_state = $playbackStates | Get-Random
        volume_percent = $volumes | Get-Random
        current_track = $tracks | Get-Random
        group_members = @("living_room_sonos", "kitchen_sonos")
        wifi_signal_strength = (Get-Random -Minimum 60 -Maximum 100)
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    }

    $jsonData = $speakerData | ConvertTo-Json -Compress

    Write-Host "🔊 Speaker Status:" -ForegroundColor Blue
    Write-Host "Playback: $($speakerData.playback_state)" -ForegroundColor White
    Write-Host "Volume: $($speakerData.volume_percent)%" -ForegroundColor White
    Write-Host "Track: $($speakerData.current_track)" -ForegroundColor White
    Write-Host "WiFi: $($speakerData.wifi_signal_strength)% signal" -ForegroundColor White
    Write-Host ""

    Write-Host "📡 Publishing to MQTT Topic:" -ForegroundColor Green
    Write-Host "Topic: alicia/devices/$DeviceId/status" -ForegroundColor Yellow
    Write-Host "Payload: $jsonData" -ForegroundColor Gray

    Write-Host "✅ Sonos speaker data prepared for MQTT publishing" -ForegroundColor Green
}

# Main simulation logic
switch ($DeviceType.ToLower()) {
    "sensor" {
        Simulate-Sensor
    }
    "bulb" {
        Simulate-SmartBulb
    }
    "sonos" {
        Simulate-SonosSpeaker
    }
    default {
        Write-Host "❌ Unknown device type: $DeviceType" -ForegroundColor Red
        Write-Host "Available types: sensor, bulb, sonos" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=== Simulation Complete ===" -ForegroundColor Cyan
Write-Host "This demonstrates how real IoT devices will communicate with Alicia." -ForegroundColor White
Write-Host "In production, this data would be published to the MQTT broker." -ForegroundColor White

Write-Host ""
Write-Host "Next steps for real implementation:" -ForegroundColor Yellow
Write-Host "1. Install MQTT client library (MQTTnet, Paho, etc.)" -ForegroundColor White
Write-Host "2. Replace simulation with actual MQTT publishing" -ForegroundColor White
Write-Host "3. Add error handling and reconnection logic" -ForegroundColor White
Write-Host "4. Implement device-specific MQTT topics" -ForegroundColor White
