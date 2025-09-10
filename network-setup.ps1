# PowerShell script to configure Docker for home network access
# Run this as Administrator

param(
    [string]$NetworkInterface = "auto",
    [string]$HomeSubnet = "192.168.1.0/24",
    [string]$HomeGateway = "192.168.1.1",
    [string]$ContainerIP = "192.168.1.250"
)

Write-Host "🐳 Docker Home Network Configuration Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Detect network interface if not specified
if ($NetworkInterface -eq "auto") {
    Write-Host "🔍 Detecting network interfaces..." -ForegroundColor Yellow
    $interfaces = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Name -notlike "*Loopback*" }
    $NetworkInterface = $interfaces[0].Name
    Write-Host "📡 Using network interface: $NetworkInterface" -ForegroundColor Green
}

# Create macvlan network
Write-Host "🌐 Creating Docker macvlan network..." -ForegroundColor Yellow
docker network create `
    --driver macvlan `
    --opt parent=$NetworkInterface `
    --subnet=$HomeSubnet `
    --gateway=$HomeGateway `
    home_network

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Macvlan network created successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create macvlan network" -ForegroundColor Red
    exit 1
}

# Test network connectivity
Write-Host "🧪 Testing network configuration..." -ForegroundColor Yellow
docker run --rm --network home_network alpine ping -c 3 $HomeGateway

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Network connectivity test passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Network connectivity test failed - check your network settings" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "  Network Interface: $NetworkInterface"
Write-Host "  Home Subnet: $HomeSubnet"
Write-Host "  Gateway: $HomeGateway"
Write-Host "  Container IP: $ContainerIP"
Write-Host ""
Write-Host "🚀 To use the Sonos bridge with home network access:" -ForegroundColor Green
Write-Host "  docker-compose -f docker-compose.sonos.yml --profile macvlan up sonos-bridge-macvlan"
Write-Host ""
Write-Host "🔧 To use host networking (simpler but less secure):" -ForegroundColor Green
Write-Host "  docker-compose -f docker-compose.sonos.yml up sonos-bridge"
