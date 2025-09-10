#!/usr/bin/env python3
"""
Sonos Audio Troubleshooter
Comprehensive diagnostic and testing tool for Sonos audio playback issues
"""

import json
import time
import socket
import subprocess
from pathlib import Path
from soco.discovery import discover
from soco import SoCo

class SonosTroubleshooter:
    def __init__(self):
        self.speakers = {}
        self.local_ip = self._get_local_ip()
        print("🔧 SONOS AUDIO TROUBLESHOOTER")
        print("=" * 40)

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def discover_speakers(self):
        """Step 1: Discover speakers"""
        print("\n🔍 STEP 1: SPEAKER DISCOVERY")
        print("-" * 30)

        speakers = list(discover(timeout=5))
        if not speakers:
            print("❌ No speakers found!")
            print("💡 Check:")
            print("   - Speakers are powered on")
            print("   - Speakers are on the same network")
            print("   - Firewall isn't blocking discovery")
            return False

        print(f"✅ Found {len(speakers)} speaker(s):")
        for i, speaker in enumerate(speakers, 1):
            speaker_name = speaker.player_name.lower().replace(" ", "_")
            self.speakers[speaker_name] = speaker
            print(f"   {i}. {speaker.player_name} at {speaker.ip_address}")

        return True

    def test_basic_connectivity(self):
        """Step 2: Test basic connectivity"""
        print("\n🔌 STEP 2: BASIC CONNECTIVITY TEST")
        print("-" * 35)

        success = True
        for name, speaker in self.speakers.items():
            print(f"\n📡 Testing {speaker.player_name}:")

            # Test volume control
            try:
                original_vol = speaker.volume
                speaker.volume = 25
                time.sleep(0.5)
                speaker.volume = original_vol
                print("   ✅ Volume control: OK")
            except Exception as e:
                print(f"   ❌ Volume control: FAILED - {e}")
                success = False

            # Test mute/unmute
            try:
                original_mute = speaker.mute
                speaker.mute = True
                time.sleep(0.5)
                speaker.mute = original_mute
                print("   ✅ Mute control: OK")
            except Exception as e:
                print(f"   ❌ Mute control: FAILED - {e}")
                success = False

            # Test status retrieval
            try:
                transport_info = speaker.get_current_transport_info()
                state = transport_info.get('current_transport_state', 'UNKNOWN')
                print(f"   ✅ Status retrieval: OK (State: {state})")
            except Exception as e:
                print(f"   ❌ Status retrieval: FAILED - {e}")
                success = False

        return success

    def test_network_connectivity(self):
        """Step 3: Test network connectivity"""
        print("\n🌐 STEP 3: NETWORK CONNECTIVITY TEST")
        print("-" * 38)

        success = True

        # Test DNS resolution
        print("Testing DNS resolution:")
        test_domains = ['translate.google.com', 'www.bbc.co.uk']
        for domain in test_domains:
            try:
                ip = socket.gethostbyname(domain)
                print(f"   ✅ {domain} → {ip}")
            except socket.gaierror:
                print(f"   ❌ {domain} → DNS resolution failed")
                success = False

        # Test firewall ports
        print("\nTesting firewall ports:")
        test_ports = [80, 443, 554]
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(("8.8.8.8", port))
                sock.close()
                if result == 0:
                    print(f"   ✅ Port {port}: OPEN")
                else:
                    print(f"   ❌ Port {port}: BLOCKED")
                    success = False
            except:
                print(f"   ❌ Port {port}: ERROR")
                success = False

        return success

    def test_local_audio_server(self):
        """Step 4: Test local audio server"""
        print("\n🎵 STEP 4: LOCAL AUDIO SERVER TEST")
        print("-" * 35)

        # Create test audio directory
        audio_dir = Path("../../mqtt-testing/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple test MP3 (placeholder)
        test_file = audio_dir / "test-beep.mp3"
        if not test_file.exists():
            with open(test_file, 'w') as f:
                f.write("# This should be replaced with actual MP3 audio file\n")
            print("   📝 Created placeholder audio file")
            print("   💡 Replace with real MP3 file for actual testing")

        # Start local HTTP server
        try:
            import http.server
            import socketserver
            import threading

            # Simple HTTP server
            handler = http.server.SimpleHTTPRequestHandler

            # Change to audio directory
            original_dir = Path.cwd()
            audio_dir.chdir()

            server = socketserver.TCPServer(("", 8080), handler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()

            print("   ✅ Local audio server started on port 8080")
            print(f"   📁 Serving files from: {audio_dir.absolute()}")

            # Test with speakers
            for name, speaker in self.speakers.items():
                print(f"\n🎧 Testing {speaker.player_name} with local audio:")

                test_uri = f"http://{self.local_ip}:8080/test-beep.mp3"
                print(f"   URI: {test_uri}")

                try:
                    speaker.play_uri(test_uri)
                    time.sleep(3)

                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state', 'UNKNOWN')

                    if state == 'PLAYING':
                        print("   ✅ LOCAL AUDIO: SUCCESS!")
                        time.sleep(3)
                    elif state == 'TRANSITIONING':
                        print("   ⏳ LOCAL AUDIO: BUFFERING...")
                        time.sleep(5)
                        current_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                        print(f"   Final state: {current_state}")
                    else:
                        print(f"   ❌ LOCAL AUDIO: FAILED (State: {state})")

                except Exception as e:
                    print(f"   ❌ LOCAL AUDIO: ERROR - {e}")

                speaker.stop()
                time.sleep(2)

            server.shutdown()
            original_dir.chdir()

        except Exception as e:
            print(f"   ❌ Local audio server failed: {e}")
            return False

        return True

    def test_external_audio_sources(self):
        """Step 5: Test external audio sources"""
        print("\n🌍 STEP 5: EXTERNAL AUDIO SOURCES TEST")
        print("-" * 40)

        external_sources = [
            ("Google TTS", "http://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=Test+message"),
            ("BBC Radio Test", "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"),
        ]

        for name, uri in external_sources:
            print(f"\n🎧 Testing {name}:")
            print(f"   URI: {uri}")

            for speaker_name, speaker in self.speakers.items():
                print(f"   With {speaker.player_name}:")

                try:
                    speaker.play_uri(uri)
                    time.sleep(3)

                    transport_info = speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state', 'UNKNOWN')

                    if state == 'PLAYING':
                        print("     ✅ SUCCESS!")
                        time.sleep(5)
                    elif state == 'TRANSITIONING':
                        print("     ⏳ BUFFERING...")
                        time.sleep(5)
                        current_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                        print(f"     Final state: {current_state}")
                    else:
                        print(f"     ❌ FAILED (State: {state})")

                except Exception as e:
                    print(f"     ❌ ERROR - {e}")

                speaker.stop()
                time.sleep(2)

    def generate_report(self):
        """Step 6: Generate troubleshooting report"""
        print("\n📋 STEP 6: TROUBLESHOOTING REPORT")
        print("-" * 35)

        print("\n🔍 DIAGNOSTIC SUMMARY:")
        print("=" * 25)

        print("\n📊 Current Configuration:")
        print(f"   Local IP: {self.local_ip}")
        print(f"   Speakers found: {len(self.speakers)}")
        for name, speaker in self.speakers.items():
            print(f"   - {speaker.player_name}: {speaker.ip_address}")

        print("\n💡 RECOMMENDED NEXT STEPS:")

        print("\n1. 🔧 IMMEDIATE FIXES:")
        print("   - Power cycle all Sonos speakers (unplug for 30 seconds)")
        print("   - Restart your router and check network connectivity")
        print("   - Test speakers with native Sonos app")

        print("\n2. 🌐 NETWORK ISSUES:")
        print("   - Check firewall settings for ports 80, 443, 554")
        print("   - Verify DNS server configuration")
        print("   - Ensure speakers have internet access")

        print("\n3. 🎵 AUDIO SPECIFIC:")
        print("   - Test with different streaming services")
        print("   - Check Sonos app for firmware updates")
        print("   - Verify parental controls aren't blocking content")

        print("\n4. 🧪 TESTING TOOLS:")
        print("   - Run: python network-diagnostics.py")
        print("   - Run: python local-audio-server.py --test")
        print("   - Run: python debug-speaker.py")

        print("\n5. 📚 DOCUMENTATION:")
        print("   - Check docs/15-Sonos-Integration-Guide.md")
        print("   - Review troubleshooting section")

    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("Starting comprehensive Sonos audio diagnostic...")

        # Step 1: Discovery
        if not self.discover_speakers():
            print("\n❌ Cannot continue without speakers. Please check speaker setup.")
            return

        # Step 2: Basic connectivity
        basic_ok = self.test_basic_connectivity()

        # Step 3: Network connectivity
        network_ok = self.test_network_connectivity()

        # Step 4: Local audio
        local_ok = self.test_local_audio_server()

        # Step 5: External sources
        self.test_external_audio_sources()

        # Step 6: Report
        self.generate_report()

        print("\n" + "=" * 50)
        print("🎯 DIAGNOSTIC COMPLETE")
        print("=" * 50)

        if basic_ok and network_ok and local_ok:
            print("✅ All basic tests passed!")
            print("💡 If external audio still fails, issue is likely with:")
            print("   - External streaming service availability")
            print("   - Firewall blocking specific services")
            print("   - Sonos app restrictions")
        else:
            print("❌ Some tests failed. Follow the recommended next steps above.")

def main():
    troubleshooter = SonosTroubleshooter()
    troubleshooter.run_full_diagnostic()

if __name__ == '__main__':
    main()
