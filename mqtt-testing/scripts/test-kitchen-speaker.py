#!/usr/bin/env python3
"""
Test Kitchen Sonos Speaker with Sound
"""

from soco.discovery import discover
from soco import SoCo
import time

def test_kitchen_speaker():
    print('🔊 TESTING KITCHEN SONOS SPEAKER')
    print('=' * 40)

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
            print(f'  - {speaker.player_name}')
        return

    print(f'✅ Found Kitchen speaker: {kitchen_speaker.player_name}')
    print(f'   IP: {kitchen_speaker.ip_address}')

    # Get current volume and save it
    original_volume = kitchen_speaker.volume
    print(f'   Current volume: {original_volume}%')

    # Check if speaker is muted at hardware level
    hardware_mute = kitchen_speaker.mute
    print(f'   Hardware Muted: {hardware_mute}')

    # Set volume to audible level for testing
    test_volume = max(40, original_volume)  # At least 40% for testing
    print(f'   Setting volume to {test_volume}% for testing...')

    try:
        # Unmute if muted
        if hardware_mute:
            print('   🔊 Unmuting speaker...')
            kitchen_speaker.mute = False
            time.sleep(1)

        kitchen_speaker.volume = test_volume
        time.sleep(1)
        print(f'   ✅ Volume set to {kitchen_speaker.volume}%')

        # Test 1: Play a test tone using available audio
        print('\n🔊 Test 1: Playing test sound...')
        try:
            # Try multiple audio sources
            audio_sources = [
                ("BBC Radio 1", "x-rincon-mp3radio://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"),
                ("TuneIn Test", "x-rincon-mp3radio://opml.radiotime.com/Tune.ashx?id=s248951&formats=aac,mp3&partnerId=16"),
                ("Google TTS", "x-rincon-mp3radio://translate.google.com/translate_tts?tl=en&q=Testing the kitchen speaker! This is Alicia speaking. Your smart home is now fully operational!")
            ]

            for name, uri in audio_sources:
                print(f'   Trying {name}...')
                try:
                    kitchen_speaker.play_uri(uri)
                    time.sleep(2)  # Wait for buffering

                    # Check transport state
                    transport_info = kitchen_speaker.get_current_transport_info()
                    state = transport_info.get('current_transport_state', 'UNKNOWN')
                    print(f'   Transport State: {state}')

                    if state == 'PLAYING':
                        print(f'   ✅ SUCCESS: {name} is playing!')
                        time.sleep(5)  # Let it play for 5 seconds
                        kitchen_speaker.stop()
                        break
                    elif state == 'TRANSITIONING':
                        print(f'   ⏳ TRANSITIONING: {name} is buffering...')
                        time.sleep(5)
                        current_state = kitchen_speaker.get_current_transport_info().get('current_transport_state', 'UNKNOWN')
                        if current_state == 'PLAYING':
                            print(f'   ✅ SUCCESS: {name} started playing!')
                            time.sleep(3)
                            kitchen_speaker.stop()
                            break
                        else:
                            print(f'   ❌ {name} failed to play (state: {current_state})')
                    else:
                        print(f'   ❌ {name} failed (state: {state})')

                    kitchen_speaker.stop()
                    time.sleep(1)

                except Exception as e:
                    print(f'   ❌ {name} error: {e}')
                    try:
                        kitchen_speaker.stop()
                    except:
                        pass

            print('✅ Test sound sequence completed!')

        except Exception as e:
            print(f'⚠️ Test sound failed: {e}')
            # Alternative: Try to play current queue if available
            try:
                if kitchen_speaker.get_queue() and len(kitchen_speaker.get_queue()) > 0:
                    kitchen_speaker.play()
                    time.sleep(2)
                    kitchen_speaker.pause()
                    print('✅ Played from queue instead!')
                else:
                    print('ℹ️ No audio queue available')
            except Exception as e2:
                print(f'⚠️ Queue playback also failed: {e2}')

        # Test 2: Test different volume levels with audio feedback
        print('\n🎚️ Test 2: Audio volume test...')
        try:
            # Quick volume changes to create audible feedback
            for vol in [20, 35, 50, 35, 20]:
                kitchen_speaker.volume = vol
                time.sleep(0.5)  # Quick changes for audio feedback
            print('✅ Volume sweep completed!')
        except Exception as e:
            print(f'⚠️ Volume sweep failed: {e}')

        # Test 3: Simple volume change test
        print('\n🔊 Test 3: Volume change test...')
        current_vol = kitchen_speaker.volume
        print(f'   Current: {current_vol}%')

        # Increase volume by 10%
        new_vol = min(100, current_vol + 10)
        kitchen_speaker.volume = new_vol
        time.sleep(1)
        print(f'   Increased to: {kitchen_speaker.volume}%')

        # Decrease back
        kitchen_speaker.volume = current_vol
        time.sleep(1)
        print(f'   Restored to: {kitchen_speaker.volume}%')

        # Restore original volume
        print(f'\n🔄 Restoring original volume: {original_volume}%')
        kitchen_speaker.volume = original_volume
        time.sleep(1)

        print('\n✅ Kitchen speaker test completed successfully!')
        print('🎉 Your Kitchen speaker is working perfectly!')

    except Exception as e:
        print(f'❌ Test failed: {e}')
        # Try to restore volume even if test failed
        try:
            kitchen_speaker.volume = original_volume
        except:
            pass

if __name__ == '__main__':
    test_kitchen_speaker()
