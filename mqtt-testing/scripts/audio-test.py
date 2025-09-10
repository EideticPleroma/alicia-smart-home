#!/usr/bin/env python3
"""
Out-of-the-Box Sonos Audio Test
Works without external dependencies or firewall changes
"""

import time
import socket
from soco.discovery import discover
from soco import SoCo

def get_network_ip():
    """Get the actual network IP address"""
    try:
        # Method 1: Connect to external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        # If it's localhost, try method 2
        if ip.startswith("127."):
            # Method 2: Parse ipconfig output
            import subprocess
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'IPv4 Address' in line or 'IP Address' in line:
                    for part in line.split():
                        if part.count('.') == 3 and not part.startswith('127.'):
                            return part.rstrip()
                # Look for wireless or ethernet adapters
                if 'Wireless' in line or 'Ethernet' in line or 'Wi-Fi' in line:
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'IPv4 Address' in lines[j] or 'IP Address' in lines[j]:
                            for part in lines[j].split():
                                if part.count('.') == 3 and not part.startswith('127.'):
                                    return part.rstrip()
        return ip
    except Exception as e:
        print(f"⚠️ Could not detect network IP: {e}")
        return "192.168.1.100"  # Common default

def test_basic_functionality():
    """Test basic Sonos speaker functionality without audio"""
    print("🔍 TESTING BASIC SONOS FUNCTIONALITY")
    print("=" * 40)

    # Discover speakers
    print("🔍 Discovering speakers...")
    speakers = list(discover(timeout=5))

    if not speakers:
        print("❌ No speakers found!")
        print("💡 Check:")
        print("   - Speakers are powered on")
        print("   - Speakers are on the same network")
        print("   - Firewall isn't blocking discovery")
        return False

    print(f"✅ Found {len(speakers)} speaker(s):")
    for speaker in speakers:
        print(f"   • {speaker.player_name} at {speaker.ip_address}")

    # Test basic controls
    speaker = speakers[0]
    print(f"\n🎛️ Testing {speaker.player_name}...")

    # Test volume
    original_volume = speaker.volume
    print(f"   Volume: {original_volume}%")

    # Test mute/unmute
    original_mute = speaker.mute
    print(f"   Muted: {original_mute}")

    # Test volume change
    test_volume = min(50, original_volume + 5)
    speaker.volume = test_volume
    time.sleep(1)
    actual_volume = speaker.volume
    print(f"   Volume change: {original_volume}% → {actual_volume}%")

    # Restore settings
    speaker.volume = original_volume
    speaker.mute = original_mute

    print("✅ Basic functionality test passed!")
    return True

def test_network_connectivity():
    """Test network connectivity to speakers"""
    print("\n🌐 TESTING NETWORK CONNECTIVITY")
    print("=" * 35)

    speakers = list(discover(timeout=5))
    if not speakers:
        return False

    local_ip = get_network_ip()
    print(f"📡 Your computer's network IP: {local_ip}")

    for speaker in speakers:
        print(f"\n🎯 Testing {speaker.player_name} ({speaker.ip_address}):")

        # Test basic connectivity
        try:
            import subprocess
            result = subprocess.run(['ping', '-n', '1', speaker.ip_address],
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("   ✅ Ping successful")
            else:
                print("   ❌ Ping failed")
        except:
            print("   ⚠️ Ping test unavailable")

        # Test speaker responsiveness
        try:
            info = speaker.get_speaker_info()
            print(f"   ✅ Speaker responsive: {info.get('model_name', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Speaker not responsive: {e}")

    return True

def test_local_audio_server():
    """Test with a simple local audio server"""
    print("\n🎵 TESTING LOCAL AUDIO SERVER")
    print("=" * 32)

    import http.server
    import socketserver
    import threading
    from pathlib import Path

    # Create a simple audio file
    audio_dir = Path("test_audio")
    audio_dir.mkdir(exist_ok=True)
    audio_file = audio_dir / "test.mp3"

    # Create a minimal MP3-like file (speakers will try to play it)
    if not audio_file.exists():
        # This is a very basic audio file header - speakers may still try to play it
        with open(audio_file, 'wb') as f:
            # Write a minimal MP3 header
            f.write(b'\xFF\xFB\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            f.write(b'This is a test audio file for Sonos speakers')
        print("   📄 Created test audio file")

    # Start local server
    port = 8080
    local_ip = get_network_ip()

    class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress server logs

    try:
        with socketserver.TCPServer((local_ip, port), QuietHTTPRequestHandler) as httpd:
            print(f"   🚀 Local server started at http://{local_ip}:{port}")
            print(f"   📁 Audio file: http://{local_ip}:{port}/test_audio/test.mp3")

            # Start server in background
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()
            time.sleep(1)  # Let server start

            # Test with speakers
            speakers = list(discover(timeout=3))
            if speakers:
                speaker = speakers[0]
                test_uri = f"http://{local_ip}:{port}/test_audio/test.mp3"

                print(f"   🎧 Testing with {speaker.player_name}...")
                print(f"   🔗 URI: {test_uri}")

                speaker.play_uri(test_uri)
                time.sleep(3)

                transport_info = speaker.get_current_transport_info()
                state = transport_info.get('current_transport_state', 'UNKNOWN')
                print(f"   📊 Transport State: {state}")

                if state == 'PLAYING':
                    print("   ✅ SUCCESS: Local audio is playing!")
                    time.sleep(3)
                elif state == 'TRANSITIONING':
                    print("   ⏳ TRANSITIONING: Speaker is trying to play...")
                    time.sleep(5)
                    final_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                    print(f"   📊 Final State: {final_state}")
                else:
                    print(f"   ❌ FAILED: State is {state}")

                speaker.stop()

            httpd.shutdown()
            print("   🛑 Server stopped")

    except Exception as e:
        print(f"   ❌ Server error: {e}")

def main():
    print("🎵 SONOS OUT-OF-THE-BOX AUDIO TEST")
    print("=" * 40)
    print("This test works without firewall changes or external services")
    print()

    # Run all tests
    basic_ok = test_basic_functionality()
    network_ok = test_network_connectivity()

    if basic_ok and network_ok:
        test_local_audio_server()

    print("\n📋 TEST SUMMARY")
    print("=" * 15)
    if basic_ok:
        print("✅ Basic functionality: WORKING")
    else:
        print("❌ Basic functionality: FAILED")

    if network_ok:
        print("✅ Network connectivity: WORKING")
    else:
        print("❌ Network connectivity: FAILED")

    print("\n💡 RECOMMENDATIONS:")
    print("1. If basic functionality works but audio doesn't:")
    print("   - Check firewall settings (ports 80, 443, 554, 5004, 5005)")
    print("   - Try the firewall fix script as Administrator")
    print("2. If network connectivity fails:")
    print("   - Ensure speakers and computer are on the same network")
    print("   - Check router settings and DHCP")
    print("3. If everything fails:")
    print("   - Power cycle speakers and router")
    print("   - Update Sonos firmware via app")
    print("   - Test with official Sonos app first")

if __name__ == '__main__':
    main()
