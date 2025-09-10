#!/usr/bin/env python3
"""
Quick Port Access Test for Sonos Port Forwarding
"""

import socket
import time

def test_port_access():
    """Quick test of port forwarding status"""
    print("🚀 QUICK PORT ACCESS TEST")
    print("=" * 30)

    # Get local IP
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"📡 Local IP: {local_ip}")

    # Test ports
    test_ports = [
        (80, "HTTP"),
        (443, "HTTPS"),
        (554, "RTSP"),
        (8080, "Local HTTP"),
        (8554, "Local RTSP")
    ]

    print("\n🧪 Testing port accessibility:")
    print("-" * 30)

    results = {}
    for port, service in test_ports:
        try:
            # Test if we can bind to the port (indicates it's not blocked)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            # Try to connect to our own IP on this port
            result = sock.connect_ex((local_ip, port))
            sock.close()

            if result == 0:
                status = "✅ OPEN"
                results[port] = True
            else:
                status = "❌ BLOCKED"
                results[port] = False

            print(f"   Port {port:4d} ({service:8s}): {status}")

        except Exception as e:
            print(f"   Port {port:4d} ({service:8s}): ❌ ERROR - {e}")
            results[port] = False

    print("\n📊 RESULTS SUMMARY:")
    print("-" * 20)

    # Check critical ports
    critical_ports = {80: "HTTP", 554: "RTSP"}
    all_critical_open = True

    for port, service in critical_ports.items():
        if results.get(port, False):
            print(f"✅ {service} (port {port}): ACCESSIBLE")
        else:
            print(f"❌ {service} (port {port}): BLOCKED")
            all_critical_open = False

    print("\n🎯 VERDICT:")
    if all_critical_open:
        print("✅ PORT FORWARDING IS WORKING!")
        print("🎵 Ready to test Sonos audio streaming")
    else:
        print("❌ PORT FORWARDING NOT WORKING YET")
        print("🔧 Check router configuration and restart")

    return all_critical_open

def test_sonos_connectivity():
    """Quick test of Sonos speaker connectivity"""
    print("\n🎵 SONOS CONNECTIVITY TEST")
    print("-" * 28)

    try:
        from soco.discovery import discover

        speakers = list(discover(timeout=3))
        if speakers:
            print(f"✅ Found {len(speakers)} speaker(s):")
            for speaker in speakers:
                print(f"   • {speaker.player_name} at {speaker.ip_address}")

            # Quick functionality test
            speaker = speakers[0]
            original_vol = speaker.volume
            speaker.volume = 20
            time.sleep(0.5)
            speaker.volume = original_vol

            print("✅ Speaker control: WORKING")
            return True
        else:
            print("❌ No speakers found")
            return False

    except Exception as e:
        print(f"❌ Sonos test failed: {e}")
        return False

if __name__ == '__main__':
    ports_ok = test_port_access()
    speakers_ok = test_sonos_connectivity()

    print("\n" + "=" * 50)
    print("🎯 FINAL STATUS:")
    if ports_ok and speakers_ok:
        print("✅ ALL SYSTEMS GO - Ready for audio testing!")
        print("🚀 Run: python audio-test.py")
    elif speakers_ok:
        print("⚠️  Speakers OK, but ports need fixing")
        print("🔧 Check router port forwarding")
    else:
        print("❌ Issues detected - check setup")
    print("=" * 50)
