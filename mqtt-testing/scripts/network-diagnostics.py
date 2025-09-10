#!/usr/bin/env python3
"""
Network Diagnostics for Sonos Speakers
Tests connectivity, DNS resolution, and firewall issues
"""

import socket
import subprocess
import time
from soco.discovery import discover
from soco import SoCo

def test_dns_resolution():
    """Test DNS resolution for common streaming services"""
    print('🌐 TESTING DNS RESOLUTION')
    print('=' * 30)

    test_domains = [
        'translate.google.com',
        'opml.radiotime.com',
        'stream.live.vc.bbcmedia.co.uk',
        'www.bbc.co.uk'
    ]

    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f'✅ {domain} → {ip}')
        except socket.gaierror as e:
            print(f'❌ {domain} → DNS resolution failed: {e}')

def test_speaker_connectivity():
    """Test speaker network connectivity"""
    print('\n🔌 TESTING SPEAKER CONNECTIVITY')
    print('=' * 35)

    speakers = list(discover(timeout=5))
    if not speakers:
        print('❌ No speakers found')
        return

    for speaker in speakers:
        print(f'\n📡 Testing {speaker.player_name} ({speaker.ip_address})')

        # Test basic connectivity
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((speaker.ip_address, 1400))  # Sonos port
            sock.close()

            if result == 0:
                print(f'✅ Basic connectivity: OK')
            else:
                print(f'❌ Basic connectivity: FAILED (port 1400)')
        except Exception as e:
            print(f'❌ Basic connectivity: ERROR - {e}')

        # Test internet connectivity from speaker's perspective
        try:
            # Try to get speaker's view of internet
            speaker_info = speaker.get_speaker_info()
            print(f'✅ Speaker info retrieved: {speaker_info.get("model_name", "Unknown")}')
        except Exception as e:
            print(f'❌ Speaker info: ERROR - {e}')

def test_firewall_ports():
    """Test common streaming ports"""
    print('\n🔥 TESTING FIREWALL PORTS')
    print('=' * 28)

    test_ports = [
        ('HTTP', 80),
        ('HTTPS', 443),
        ('RTSP', 554),  # Real Time Streaming Protocol
        ('RTP', 5004),  # Real-time Transport Protocol
        ('RTCP', 5005), # Real-time Transport Control Protocol
    ]

    test_host = '8.8.8.8'  # Google DNS

    for service, port in test_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((test_host, port))
            sock.close()

            if result == 0:
                print(f'✅ {service} (port {port}): OPEN')
            else:
                print(f'❌ {service} (port {port}): BLOCKED')
        except Exception as e:
            print(f'❌ {service} (port {port}): ERROR - {e}')

def test_streaming_uris():
    """Test various streaming URIs that should work"""
    print('\n🎵 TESTING STREAMING URIS')
    print('=' * 28)

    speakers = list(discover(timeout=5))
    if not speakers:
        print('❌ No speakers found')
        return

    speaker = speakers[0]
    print(f'Using speaker: {speaker.player_name}')

    # Test URIs that should work
    test_uris = [
        ("Sonos Test Stream", "x-sonos-http:track%3a.mp3?sid=2&flags=32"),
        ("Simple HTTP Test", "http://httpbin.org/stream/1"),
        ("Local Test", "http://127.0.0.1:8080/test.mp3"),  # Will fail but test connectivity
    ]

    for name, uri in test_uris:
        print(f'\n🎧 Testing: {name}')
        print(f'   URI: {uri}')

        try:
            speaker.play_uri(uri)
            time.sleep(3)  # Wait for attempt

            transport_info = speaker.get_current_transport_info()
            state = transport_info.get('current_transport_state', 'UNKNOWN')
            print(f'   Transport State: {state}')

            if state == 'PLAYING':
                print(f'   ✅ SUCCESS: Audio is playing!')
                time.sleep(5)
                speaker.stop()
            elif state == 'TRANSITIONING':
                print(f'   ⏳ TRANSITIONING: May be buffering...')
                time.sleep(5)
                current_state = speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                print(f'   Final State: {current_state}')
                speaker.stop()
            else:
                print(f'   ❌ FAILED: State is {state}')

        except Exception as e:
            print(f'   ❌ ERROR: {e}')

        speaker.stop()
        time.sleep(2)

def main():
    print('🔍 SONOS NETWORK DIAGNOSTICS')
    print('=' * 35)
    print('This tool diagnoses network issues preventing audio playback')
    print()

    test_dns_resolution()
    test_speaker_connectivity()
    test_firewall_ports()
    test_streaming_uris()

    print('\n📋 DIAGNOSTIC SUMMARY')
    print('=' * 22)
    print('🔍 Check the results above for:')
    print('   - DNS resolution failures')
    print('   - Blocked firewall ports')
    print('   - Speaker connectivity issues')
    print('   - Streaming URI problems')
    print()
    print('💡 Common solutions:')
    print('   1. Check firewall settings for ports 80, 443, 554, 5004, 5005')
    print('   2. Verify DNS server configuration')
    print('   3. Test speakers with native Sonos app')
    print('   4. Power cycle speakers and router')
    print('   5. Check for Sonos app restrictions or parental controls')

if __name__ == '__main__':
    main()
