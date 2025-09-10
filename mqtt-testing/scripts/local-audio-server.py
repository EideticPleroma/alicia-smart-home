#!/usr/bin/env python3
"""
Local Audio Server for Sonos Testing
Provides local audio files for testing without external dependencies
"""

import http.server
import socketserver
import threading
import time
import os
from pathlib import Path

class LocalAudioServer:
    def __init__(self, port=8080, audio_dir="audio"):
        self.port = port
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        self.server = None
        self.server_thread = None

    def create_test_audio_files(self):
        """Create simple test audio files"""
        print("🎵 Creating test audio files...")

        # Create a simple test file (this would be a real audio file in production)
        test_files = [
            ("test-tone.mp3", "Simple test tone"),
            ("beep.mp3", "Short beep sound"),
            ("announcement.mp3", "Test announcement")
        ]

        for filename, description in test_files:
            filepath = self.audio_dir / filename
            if not filepath.exists():
                # Create a placeholder file (in real implementation, you'd have actual audio)
                with open(filepath, 'w') as f:
                    f.write(f"# This is a placeholder for {description}\n")
                    f.write("# Replace with actual MP3 audio file\n")
                print(f"   Created: {filepath}")

    def start(self):
        """Start the local audio server"""
        print(f"🚀 Starting local audio server on port {self.port}")

        # Create test files
        self.create_test_audio_files()

        # Set up HTTP server
        handler = http.server.SimpleHTTPRequestHandler

        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                self.server = httpd
                print(f"✅ Server running at http://localhost:{self.port}")
                print(f"📁 Audio files available at http://localhost:{self.port}/{self.audio_dir}/")

                # List available files
                print("\n📋 Available test files:")
                for file in self.audio_dir.glob("*.mp3"):
                    print(f"   http://localhost:{self.port}/{file}")

                print("\n💡 To test with Sonos:")
                print("   Use URIs like: http://192.168.1.100:8080/audio/test-tone.mp3")
                print("   (Replace 192.168.1.100 with your computer's IP)")

                httpd.serve_forever()

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")

    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()
            print("🛑 Server stopped")

def get_local_ip():
    """Get the local IP address accessible from network"""
    try:
        import socket
        # Try multiple methods to get network IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Validate it's not localhost
        if local_ip.startswith("127."):
            # Try to get network interface IP
            import subprocess
            try:
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if '192.168.' in line or '10.' in line or '172.' in line:
                        parts = line.split()
                        for part in parts:
                            if part.count('.') == 3 and not part.startswith('127.'):
                                return part.split('/')[0]  # Remove subnet mask
            except:
                pass

        return local_ip
    except Exception:
        return "192.168.1.100"  # Fallback

def test_sonos_with_local_audio():
    """Test Sonos speakers with local audio files"""
    print("🎵 TESTING SONOS WITH LOCAL AUDIO")
    print("=" * 40)

    from soco.discovery import discover

    # Start local server in background
    server = LocalAudioServer()
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    # Get local IP for URIs
    local_ip = get_local_ip()
    print(f"📡 Local IP: {local_ip}")

    # Discover speakers
    speakers = list(discover(timeout=5))
    if not speakers:
        print("❌ No speakers found")
        return

    speaker = speakers[0]
    print(f"🎯 Testing with: {speaker.player_name}")

    # Test local audio files
    test_uris = [
        f"http://{local_ip}:8080/audio/test-tone.mp3",
        f"http://{local_ip}:8080/audio/beep.mp3",
    ]

    for uri in test_uris:
        print(f"\n🎧 Testing: {uri}")

        try:
            speaker.play_uri(uri)
            time.sleep(3)  # Wait for playback attempt

            transport_info = speaker.get_current_transport_info()
            state = transport_info.get('current_transport_state', 'UNKNOWN')
            print(f"   Transport State: {state}")

            if state == 'PLAYING':
                print("   ✅ SUCCESS: Local audio is playing!")
                time.sleep(5)
            elif state == 'TRANSITIONING':
                print("   ⏳ TRANSITIONING: Buffering local audio...")
                time.sleep(5)
                current_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                print(f"   Final State: {current_state}")
            else:
                print(f"   ❌ FAILED: State is {state}")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")

        speaker.stop()
        time.sleep(2)

    print("\n📋 LOCAL AUDIO TEST RESULTS")
    print("=" * 30)
    print("If local audio works:")
    print("   ✅ Audio playback is functional")
    print("   ✅ Issue is with external streaming services")
    print("   💡 Check firewall, DNS, or service availability")

    print("\nIf local audio also fails:")
    print("   ❌ Audio playback has deeper issues")
    print("   💡 Check speaker hardware, firmware, or network configuration")

def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run test mode
        test_sonos_with_local_audio()
    else:
        # Run server mode
        print("🎵 LOCAL AUDIO SERVER")
        print("=" * 25)
        print("This server provides local audio files for Sonos testing")
        print("without relying on external streaming services.")
        print()
        print("Usage:")
        print("  python local-audio-server.py        # Start server")
        print("  python local-audio-server.py --test # Test with Sonos")
        print()

        server = LocalAudioServer()
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()

if __name__ == '__main__':
    main()
