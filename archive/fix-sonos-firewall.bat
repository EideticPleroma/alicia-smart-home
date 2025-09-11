@echo off
echo ========================================
echo    SONOS FIREWALL FIX - OUT OF THE BOX
echo ========================================
echo.
echo This script opens the necessary firewall ports for Sonos audio streaming.
echo You must run this as Administrator for it to work.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Opening firewall ports for Sonos...
echo.

echo Opening HTTP port 80...
netsh advfirewall firewall add rule name="Sonos_HTTP" dir=in action=allow protocol=TCP localport=80
if %errorlevel% neq 0 (
    echo ERROR: Failed to open port 80
) else (
    echo SUCCESS: Port 80 opened
)

echo.
echo Opening HTTPS port 443...
netsh advfirewall firewall add rule name="Sonos_HTTPS" dir=in action=allow protocol=TCP localport=443
if %errorlevel% neq 0 (
    echo ERROR: Failed to open port 443
) else (
    echo SUCCESS: Port 443 opened
)

echo.
echo Opening RTSP port 554...
netsh advfirewall firewall add rule name="Sonos_RTSP" dir=in action=allow protocol=TCP localport=554
if %errorlevel% neq 0 (
    echo ERROR: Failed to open port 554
) else (
    echo SUCCESS: Port 554 opened
)

echo.
echo Opening RTP ports 5004-5005...
netsh advfirewall firewall add rule name="Sonos_RTP" dir=in action=allow protocol=UDP localport=5004-5005
if %errorlevel% neq 0 (
    echo ERROR: Failed to open RTP ports
) else (
    echo SUCCESS: RTP ports opened
)

echo.
echo Opening Sonos controller port 1400...
netsh advfirewall firewall add rule name="Sonos_Controller" dir=in action=allow protocol=TCP localport=1400
if %errorlevel% neq 0 (
    echo ERROR: Failed to open port 1400
) else (
    echo SUCCESS: Port 1400 opened
)

echo.
echo Opening Sonos discovery port 1900...
netsh advfirewall firewall add rule name="Sonos_Discovery" dir=in action=allow protocol=UDP localport=1900
if %errorlevel% neq 0 (
    echo ERROR: Failed to open port 1900
) else (
    echo SUCCESS: Port 1900 opened
)

echo.
echo ========================================
echo         FIREWALL FIX COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your computer to apply changes
echo 2. Test speakers: python mqtt-testing/scripts/test-kitchen-speaker.py
echo 3. Or run full test: python mqtt-testing/scripts/audio-test.py
echo.
echo If you still have issues, check:
echo - Speakers are on the same network
echo - Router firewall settings
echo - Antivirus software blocking ports
echo.
pause
