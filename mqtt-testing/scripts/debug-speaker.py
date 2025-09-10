#!/usr/bin/env python3
"""
Debug Kitchen Sonos Speaker - Comprehensive Testing
"""

from soco.discovery import discover
from soco import SoCo
import time

def debug_kitchen_speaker():
    print('🔍 DEBUGGING KITCHEN SONOS SPEAKER')
    print('=' * 45)

    # Discover speakers
    print('🔍 Discovering speakers...')
    speakers = list(discover(timeout=5))

    if not speakers:
        print('❌ No speakers found')
        return

    # Find Kitchen speaker
    kitchen_speaker = None
    for speaker in speakers:
        if 'kitchen' in speaker.player_name.lower():
            kitchen_speaker = speaker
            break

    if not kitchen_speaker:
        print('❌ Kitchen speaker not found')
        print('Available speakers:')
        for speaker in speakers:
            print(f'  - {speaker.player_name} at {speaker.ip_address}')
        return

    print(f'✅ Found Kitchen speaker: {kitchen_speaker.player_name}')
    print(f'   IP: {kitchen_speaker.ip_address}')

    # Comprehensive status check
    print(f'\n📊 COMPREHENSIVE SPEAKER STATUS:')
    print(f'   Volume: {kitchen_speaker.volume}%')
    print(f'   Muted: {kitchen_speaker.mute}')

    try:
        transport_info = kitchen_speaker.get_current_transport_info()
        print(f'   Transport State: {transport_info.get("current_transport_state", "UNKNOWN")}')
        print(f'   Transport Status: {transport_info.get("current_transport_status", "UNKNOWN")}')
    except Exception as e:
        print(f'   Transport Info: Error - {e}')

    try:
        media_info = kitchen_speaker.get_current_media_info()
        print(f'   Current URI: {media_info.get("current_uri", "None")}')
        print(f'   Track: {media_info.get("current_title", "None")}')
    except Exception as e:
        print(f'   Media Info: Error - {e}')

    try:
        speaker_info = kitchen_speaker.get_speaker_info()
        print(f'   Model: {speaker_info.get("model_name", "Unknown")}')
        print(f'   Zone: {speaker_info.get("zone_name", "Unknown")}')
        print(f'   MAC Address: {speaker_info.get("mac_address", "Unknown")}')
    except Exception as e:
        print(f'   Speaker Info: Error - {e}')

    # Check if speaker is part of a group
    try:
        group = kitchen_speaker.group
        if group and len(group.members) > 1:
            print(f'   Group: {group.label} ({len(group.members)} speakers)')
            print(f'   Group Members: {[m.player_name for m in group.members]}')
            print(f'   Coordinator: {group.coordinator.player_name}')
        else:
            print(f'   Group: Standalone (not grouped)')
    except Exception as e:
        print(f'   Group Info: Error - {e}')

    # Test 1: Unmute if muted
    print(f'\n🔊 TEST 1: Ensuring speaker is not muted...')
    if kitchen_speaker.mute:
        print('   Speaker is muted - unmuting...')
        kitchen_speaker.mute = False
        time.sleep(1)
        print(f'   Mute status: {kitchen_speaker.mute}')
    else:
        print('   Speaker is not muted ✓')

    # Test 2: Set volume to audible level
    print(f'\n🎚️ TEST 2: Setting audible volume...')
    original_volume = kitchen_speaker.volume
    test_volume = 40  # Good audible level
    print(f'   Original volume: {original_volume}%')
    print(f'   Setting to: {test_volume}%')

    kitchen_speaker.volume = test_volume
    time.sleep(1)
    actual_volume = kitchen_speaker.volume
    print(f'   Actual volume: {actual_volume}%')

    if actual_volume != test_volume:
        print(f'   ⚠️ Volume setting may not be working correctly')
    else:
        print('   ✓ Volume setting confirmed')

    # Test 3: Try multiple audio sources
    print(f'\n🎵 TEST 3: Testing different audio sources...')

    audio_sources = [
        ("TuneIn Radio", "x-rincon-mp3radio://opml.radiotime.com/Tune.ashx?id=s248951&formats=aac,mp3&partnerId=16"),
        ("Test Tone", "x-rincon-mp3radio://translate.google.com/translate_tts?tl=en&q=testing+one+two+three"),
        ("BBC Radio 1", "x-rincon-mp3radio://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"),
    ]

    for name, uri in audio_sources:
        print(f'   Trying {name}...')
        try:
            kitchen_speaker.play_uri(uri)
            time.sleep(2)  # Let it start

            # Check if it's actually playing
            transport_info = kitchen_speaker.get_current_transport_info()
            state = transport_info.get("current_transport_state", "UNKNOWN")

            if state == "PLAYING":
                print(f'   ✅ {name} is playing!')
                time.sleep(5)  # Let user hear it
                kitchen_speaker.stop()
                time.sleep(1)
                break
            else:
                print(f'   ⚠️ {name} state: {state}')
                kitchen_speaker.stop()
                time.sleep(1)

        except Exception as e:
            print(f'   ❌ {name} failed: {e}')

    # Test 4: Simple beep test
    print(f'\n🔔 TEST 4: Simple beep test...')
    try:
        # Try to play a very short tone
        beep_uri = "x-rincon-mp3radio://translate.google.com/translate_tts?tl=en&q=beep"
        kitchen_speaker.play_uri(beep_uri)
        time.sleep(3)
        kitchen_speaker.stop()
        print('   ✅ Beep test completed')
    except Exception as e:
        print(f'   ❌ Beep test failed: {e}')

    # Restore original volume
    print(f'\n🔄 Restoring original volume: {original_volume}%')
    kitchen_speaker.volume = original_volume
    time.sleep(1)

    print(f'\n📋 DEBUG SUMMARY:')
    print(f'   Speaker: {kitchen_speaker.player_name}')
    print(f'   IP: {kitchen_speaker.ip_address}')
    print(f'   Final Volume: {kitchen_speaker.volume}%')
    print(f'   Final Mute: {kitchen_speaker.mute}')

    print(f'\n💡 POSSIBLE ISSUES TO CHECK:')
    print(f'   1. Is the speaker physically powered on?')
    print(f'   2. Is the speaker connected to the same network?')
    print(f'   3. Is the speaker grouped with other speakers?')
    print(f'   4. Is the speaker volume turned down on the device itself?')
    print(f'   5. Are there any Sonos app restrictions?')

if __name__ == '__main__':
    debug_kitchen_speaker()
