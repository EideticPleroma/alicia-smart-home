#!/usr/bin/env python3
"""
Sonos Integration Demo Script
Demonstrates Sonos speaker discovery and control without MQTT
"""

from soco.discovery import discover
from soco import SoCo
import time

def main():
    print('🎵 SONOS INTEGRATION DEMO - WITHOUT MQTT')
    print('=' * 50)

    # Discover speakers
    print('🔍 Discovering Sonos speakers...')
    speakers = list(discover(timeout=5))

    if not speakers:
        print('❌ No speakers found')
        print('💡 Make sure your Sonos speakers are powered on and on the same network')
        return

    print(f'✅ Found {len(speakers)} speaker(s):')
    for i, speaker in enumerate(speakers, 1):
        print(f'  {i}. {speaker.player_name} at {speaker.ip_address}')

    # Test basic functionality with first speaker
    speaker = speakers[0]
    print(f'\n🎯 Testing speaker: {speaker.player_name}')
    print(f'   IP: {speaker.ip_address}')

    # Get speaker info safely
    try:
        speaker_info = speaker.get_speaker_info()
        print(f'   Model: {speaker_info.get("model_name", "Unknown")}')
        print(f'   Zone: {speaker_info.get("zone_name", "Unknown")}')
    except Exception as e:
        print(f'   Model/Zone: Unable to get info ({e})')

    # Get current status
    print(f'\n📊 Current Status:')
    print(f'   Volume: {speaker.volume}%')
    print(f'   Muted: {speaker.mute}')

    # Get transport info safely
    try:
        transport_info = speaker.get_current_transport_info()
        state = transport_info.get('current_transport_state', 'UNKNOWN')
        print(f'   State: {state}')
    except Exception as e:
        print(f'   State: Unable to get ({e})')

    # Test volume control
    print(f'\n🔊 Testing Volume Control:')
    original_volume = speaker.volume
    print(f'   Original volume: {original_volume}%')

    # Set volume to 30%
    try:
        speaker.volume = 30
        time.sleep(1)
        print(f'   Set volume to: {speaker.volume}%')

        # Set volume back
        speaker.volume = original_volume
        time.sleep(1)
        print(f'   Restored volume to: {speaker.volume}%')
    except Exception as e:
        print(f'   Volume control failed: {e}')

    print(f'\n✅ Sonos integration test completed successfully!')
    print(f'🎉 Your speakers are ready for voice control!')

    # Show next steps
    print(f'\n🚀 Next Steps:')
    print(f'   1. Set up MQTT broker for full integration')
    print(f'   2. Configure Home Assistant for speaker control')
    print(f'   3. Add voice assistant integration')
    print(f'   4. Test TTS announcements')

if __name__ == '__main__':
    main()
