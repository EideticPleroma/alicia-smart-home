# Sonos Firewall Configuration Fix for Windows
# This script configures Windows Firewall to allow Sonos audio streaming

Write-Host "🔥 SONOS FIREWALL CONFIGURATION FIX" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ Please run this script as Administrator!" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green

# Function to add firewall rule
function Add-FirewallRule {
    param(
        [string]$Name,
        [string]$DisplayName,
        [int]$Port,
        [string]$Protocol = "TCP"
    )

    Write-Host "🔧 Adding firewall rule: $DisplayName (Port $Port)" -ForegroundColor Yellow

    try {
        # Check if rule already exists
        $existingRule = Get-NetFirewallRule -DisplayName $DisplayName -ErrorAction SilentlyContinue

        if ($existingRule) {
            Write-Host "   ⚠️ Rule already exists, removing and re-creating..." -ForegroundColor Yellow
            Remove-NetFirewallRule -DisplayName $DisplayName
        }

        # Create new rule
        New-NetFirewallRule -DisplayName $DisplayName `
                           -Name $Name `
                           -Direction Inbound `
                           -Action Allow `
                           -Protocol $Protocol `
                           -LocalPort $Port `
                           -Profile Any `
                           -Description "Allow Sonos audio streaming"

        Write-Host "   ✅ Rule added successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Failed to add rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Add rules for critical ports
Write-Host "`n🌐 CONFIGURING FIREWALL RULES" -ForegroundColor Cyan
Write-Host "-" * 35 -ForegroundColor Cyan

# HTTP (Port 80) - Critical for audio streaming
Add-FirewallRule -Name "Sonos_HTTP" -DisplayName "Sonos HTTP Streaming (Port 80)" -Port 80

# HTTPS (Port 443) - Already working but add rule for consistency
Add-FirewallRule -Name "Sonos_HTTPS" -DisplayName "Sonos HTTPS Streaming (Port 443)" -Port 443

# RTSP (Port 554) - Real-time streaming protocol
Add-FirewallRule -Name "Sonos_RTSP" -DisplayName "Sonos RTSP Streaming (Port 554)" -Port 554

# Additional ports that may be needed
Write-Host "`n🔧 ADDING ADDITIONAL SONOS PORTS" -ForegroundColor Cyan

# Sonos controller port
Add-FirewallRule -Name "Sonos_Controller" -DisplayName "Sonos Controller (Port 1400)" -Port 1400

# Sonos discovery ports
Add-FirewallRule -Name "Sonos_Discovery_UDP" -DisplayName "Sonos Discovery UDP" -Port 1900 -Protocol "UDP"

# Enable UPnP if disabled
Write-Host "`n🔌 ENABLING UPNP SERVICE" -ForegroundColor Cyan
try {
    Set-Service -Name "upnphost" -StartupType Automatic -ErrorAction Stop
    Start-Service -Name "upnphost" -ErrorAction Stop
    Write-Host "✅ UPnP service enabled and started" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Could not enable UPnP service: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   You may need to enable it manually in Services.msc" -ForegroundColor Yellow
}

# Display current firewall rules
Write-Host "`n📋 CURRENT SONOS FIREWALL RULES" -ForegroundColor Cyan
Write-Host "-" * 35 -ForegroundColor Cyan

$sonosRules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Sonos*" }
if ($sonosRules) {
    foreach ($rule in $sonosRules) {
        Write-Host "   ✅ $($rule.DisplayName)" -ForegroundColor Green
    }
} else {
    Write-Host "   ❌ No Sonos rules found" -ForegroundColor Red
}

Write-Host "`n🧪 TESTING CONFIGURATION" -ForegroundColor Cyan
Write-Host "-" * 25 -ForegroundColor Cyan

# Test ports
$testPorts = @(80, 443, 554, 1400)
foreach ($port in $testPorts) {
    try {
        $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port $port -ErrorAction Stop
        if ($connection.TcpTestSucceeded) {
            Write-Host "   ✅ Port $port: OPEN" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Port $port: BLOCKED" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "   ❌ Port $port: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📋 NEXT STEPS" -ForegroundColor Cyan
Write-Host "-" * 12 -ForegroundColor Cyan
Write-Host "1. 🔄 Restart your computer to apply all changes" -ForegroundColor White
Write-Host "2. 🧪 Run the Sonos troubleshooter again:" -ForegroundColor White
Write-Host "   cd mqtt-testing/scripts" -ForegroundColor Gray
Write-Host "   python sonos-troubleshooter.py" -ForegroundColor Gray
Write-Host "3. 🎵 Test audio playback with:" -ForegroundColor White
Write-Host "   python audio-test.py" -ForegroundColor Gray
Write-Host "4. 📱 Verify with Sonos mobile app" -ForegroundColor White

Write-Host "`n✅ FIREWALL CONFIGURATION COMPLETE" -ForegroundColor Green
Write-Host "If audio still doesn't work, the issue may be with:" -ForegroundColor Yellow
Write-Host "   - Router firewall settings" -ForegroundColor Yellow
Write-Host "   - ISP blocking ports" -ForegroundColor Yellow
Write-Host "   - Sonos speaker firmware" -ForegroundColor Yellow
Write-Host "   - Parental controls in Sonos app" -ForegroundColor Yellow

# Pause to let user read output
Read-Host "`nPress Enter to exit"
