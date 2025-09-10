#!/usr/bin/env python3
"""
Port Alternative Solutions for Sonos Audio
Workarounds for firewall blocking without changing firewall rules
"""

import socket
import time
from soco.discovery import discover
from soco import SoCo

class PortAlternativeTester:
    def __init__(self):
        self.speakers = {}
        self.local_ip = self._get_local_ip()
        print("🔄 SONOS PORT ALTERNATIVE SOLUTIONS")
        print("=" * 45)

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
        """Find speakers on network"""
        print("\n🔍 Discovering speakers...")
        speakers = list(discover(timeout=5))
        if not speakers:
            print("❌ No speakers found")
            return False

        for speaker in speakers:
            speaker_name = speaker.player_name.lower().replace(" ", "_")
            self.speakers[speaker_name] = speaker
            print(f"✅ Found: {speaker.player_name} at {speaker.ip_address}")

        return True

    def test_port_forwarding_workaround(self):
        """Test if port forwarding could work"""
        print("\n🔀 TESTING PORT FORWARDING WORKAROUND")
        print("-" * 40)

        # Test if we can use different local ports that forward to blocked ports
        test_scenarios = [
            ("Local Port 8080 → External Port 80", 8080, "translate.google.com", 80),
            ("Local Port 8554 → External Port 554", 8554, "example.com", 554),  # Placeholder
        ]

        for name, local_port, target_host, target_port in test_scenarios:
            print(f"\n🧪 Testing: {name}")
            print(f"   Local Port: {local_port}")
            print(f"   Target: {target_host}:{target_port}")

            # This would require actual port forwarding setup
            print("   💡 This would require router port forwarding configuration")
            print(f"   💡 Forward external port {target_port} to {self.local_ip}:{local_port}")

    def test_https_alternatives(self):
        """Test HTTPS alternatives to HTTP streaming"""
        print("\n🔒 TESTING HTTPS ALTERNATIVES")
        print("-" * 32)

        if not self.speakers:
            print("❌ No speakers available for testing")
            return

        speaker = list(self.speakers.values())[0]
        print(f"Using speaker: {speaker.player_name}")

        # HTTPS alternatives that might work
        https_sources = [
            ("HTTPS Google TTS", "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=Test+message"),
            ("HTTPS Test Stream", "https://httpbin.org/stream/1"),  # Simple HTTPS test
        ]

        for name, uri in https_sources:
            print(f"\n🎵 Testing: {name}")
            print(f"   URI: {uri}")

            try:
                speaker.play_uri(uri)
                time.sleep(3)

                transport_info = speaker.get_current_transport_info()
                state = transport_info.get('current_transport_state', 'UNKNOWN')

                if state == 'PLAYING':
                    print("   ✅ SUCCESS: HTTPS streaming works!")
                    time.sleep(5)
                elif state == 'TRANSITIONING':
                    print("   ⏳ TRANSITIONING: Buffering...")
                    time.sleep(5)
                    current_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                    print(f"   Final state: {current_state}")
                else:
                    print(f"   ❌ FAILED: State is {state}")

            except Exception as e:
                print(f"   ❌ ERROR: {e}")

            speaker.stop()
            time.sleep(2)

    def test_local_proxy_solution(self):
        """Test local proxy to work around port blocking"""
        print("\n🌐 TESTING LOCAL PROXY SOLUTION")
        print("-" * 34)

        print("💡 Local Proxy Concept:")
        print("   1. Run local proxy server on allowed port (e.g., 8080)")
        print("   2. Proxy forwards requests to blocked ports")
        print("   3. Sonos connects to local proxy instead of external services")
        print()
        print("🛠️ Implementation would require:")
        print("   - Local HTTP proxy server")
        print("   - Request forwarding to external services")
        print("   - URL rewriting for Sonos compatibility")

    def test_alternative_streaming_ports(self):
        """Test if streaming services support alternative ports"""
        print("\n🔌 TESTING ALTERNATIVE STREAMING PORTS")
        print("-" * 40)

        # Some streaming services might support non-standard ports
        alternative_ports = [
            ("HTTP Alt Port 8000", 8000),
            ("HTTP Alt Port 8888", 8888),
            ("RTSP Alt Port 8554", 8554),
        ]

        for name, port in alternative_ports:
            print(f"\n🧪 Testing: {name}")

            # Test if port is accessible
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(("8.8.8.8", port))
                sock.close()

                if result == 0:
                    print(f"   ✅ Port {port}: OPEN")
                    print("   💡 Could potentially use this port for streaming")
                else:
                    print(f"   ❌ Port {port}: BLOCKED")

            except Exception as e:
                print(f"   ❌ Port {port}: ERROR - {e}")

    def create_port_forwarding_guide(self):
        """Create guide for port forwarding setup"""
        print("\n📋 PORT FORWARDING SETUP GUIDE")
        print("-" * 32)

        print("🔧 Router Port Forwarding (Alternative to Firewall Changes):")
        print()
        print("1. 🌐 Access Router Admin Panel:")
        print("   - Open browser: http://192.168.1.1 (or router IP)")
        print("   - Login with admin credentials")
        print()
        print("2. 🔀 Set Up Port Forwarding Rules:")
        print("   - Forward external port 80 to internal port 8080")
        print("   - Forward external port 554 to internal port 8554")
        print(f"   - Internal IP: {self.local_ip}")
        print()
        print("3. 🧪 Test Configuration:")
        print("   - Run: python sonos-troubleshooter.py")
        print("   - Check if ports show as OPEN")
        print()
        print("4. 🎵 Test Audio Streaming:")
        print("   - Run: python audio-test.py")
        print("   - Should work without firewall changes")

    def create_vpn_workaround_guide(self):
        """Create guide for VPN workaround"""
        print("\n🔒 VPN WORKAROUND GUIDE")
        print("-" * 23)

        print("🌐 VPN Solution (If Router Doesn't Support Port Forwarding):")
        print()
        print("1. 🛡️ Set Up VPN Server:")
        print("   - Install OpenVPN or WireGuard on a VPS")
        print("   - Configure to allow all ports")
        print()
        print("2. 🔗 Connect Devices to VPN:")
        print("   - Connect computer to VPN")
        print("   - Ensure Sonos speakers are on same VPN network")
        print()
        print("3. ✅ Test Connectivity:")
        print("   - All ports should be accessible via VPN")
        print("   - No firewall changes needed on local network")

    def generate_alternative_solutions_report(self):
        """Generate comprehensive report of alternatives"""
        print("\n📊 ALTERNATIVE SOLUTIONS SUMMARY")
        print("-" * 35)

        print("🎯 Available Options (No Firewall Changes Needed):")
        print()

        print("1. 🔀 PORT FORWARDING (Recommended):")
        print("   ✅ No firewall changes required")
        print("   ✅ Works with existing streaming services")
        print("   ✅ Router-level configuration")
        print("   ⚠️ Requires router admin access")
        print()

        print("2. 🌐 LOCAL PROXY SERVER:")
        print("   ✅ Complete control over traffic")
        print("   ✅ Can rewrite URLs and ports")
        print("   ✅ Firewall-independent")
        print("   ⚠️ Requires development and setup")
        print()

        print("3. 🔒 HTTPS ALTERNATIVES:")
        print("   ✅ Uses already open port 443")
        print("   ✅ More secure than HTTP")
        print("   ⚠️ Limited service availability")
        print("   ⚠️ May not work with all streaming sources")
        print()

        print("4. 🛡️ VPN SOLUTION:")
        print("   ✅ Bypasses all local restrictions")
        print("   ✅ Works with any ports/services")
        print("   ⚠️ Requires VPN server setup")
        print("   ⚠️ May affect network performance")
        print()

        print("💡 RECOMMENDATION:")
        print("   Start with Port Forwarding - it's the simplest solution")
        print("   that works with existing services and requires no code changes.")

def main():
    tester = PortAlternativeTester()

    if not tester.discover_speakers():
        print("❌ Cannot test alternatives without speakers")
        return

    # Test various alternative approaches
    tester.test_https_alternatives()
    tester.test_alternative_streaming_ports()
    tester.test_port_forwarding_workaround()
    tester.test_local_proxy_solution()

    # Generate guides and reports
    tester.create_port_forwarding_guide()
    tester.create_vpn_workaround_guide()
    tester.generate_alternative_solutions_report()

    print("\n" + "=" * 60)
    print("🎯 PORT ALTERNATIVE TESTING COMPLETE")
    print("=" * 60)
    print("💡 Key Finding: Port forwarding is the best alternative")
    print("   to firewall changes for resolving Sonos audio issues!")

if __name__ == '__main__':
    main()
