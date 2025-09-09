"""
Step definitions for Sonos integration BDD tests
"""
import pytest
from pytest_bdd import given, when, then, parsers
from unittest.mock import Mock
import json


@given("the MQTT broker is running")
def mqtt_broker_running(mock_mqtt_client):
    """Given the MQTT broker is running"""
    mock_mqtt_client.connect.return_value = True
    mock_mqtt_client.is_connected.return_value = True


@given("the Sonos MQTT bridge is connected")
def sonos_bridge_connected(mock_sonos_bridge):
    """Given the Sonos MQTT bridge is connected"""
    mock_sonos_bridge.is_connected = True


@given("at least one Sonos speaker is available")
def sonos_speaker_available(mock_sonos_bridge, mock_sonos_speaker):
    """Given at least one Sonos speaker is available"""
    mock_sonos_bridge.discovered_speakers[mock_sonos_speaker.name] = mock_sonos_speaker


@given(parsers.parse('a speaker named "{speaker_name}" is available'))
def named_speaker_available(mock_sonos_bridge, speaker_name):
    """Given a speaker with specific name is available"""
    speaker = Mock()
    speaker.name = speaker_name
    speaker.volume = 30
    speaker.is_playing = False
    mock_sonos_bridge.discovered_speakers[speaker_name] = speaker


@given(parsers.parse('speakers "{speaker1}" and "{speaker2}" are available'))
def multiple_speakers_available(mock_sonos_bridge, speaker1, speaker2):
    """Given multiple speakers are available"""
    for name in [speaker1, speaker2]:
        speaker = Mock()
        speaker.name = name
        speaker.volume = 30
        speaker.is_playing = False
        mock_sonos_bridge.discovered_speakers[name] = speaker


@given("music is playing on the speaker")
def music_playing_on_speaker(mock_sonos_bridge):
    """Given music is playing on the speaker"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.is_playing = True
        speaker.current_track = "Test Song"


@given("the voice assistant is active")
def voice_assistant_active():
    """Given the voice assistant is active"""
    # This would typically check if the voice processing pipeline is running
    pass


@when("the bridge scans for Sonos speakers")
def bridge_scans_for_speakers(mock_sonos_bridge):
    """When the bridge scans for Sonos speakers"""
    # Simulate discovering speakers
    mock_sonos_bridge.scan_network()


@when(parsers.parse('I send a TTS message "{message}" to the speaker'))
def send_tts_message(mock_sonos_bridge, mock_mqtt_client, message):
    """When I send a TTS message to the speaker"""
    topic = "sonos/living_room_sonos/tts"
    payload = json.dumps({"message": message, "volume": 50})
    mock_mqtt_client.publish(topic, payload)


@when(parsers.parse("I set the volume to {volume:d}"))
def set_speaker_volume(mock_sonos_bridge, volume):
    """When I set the speaker volume"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.set_volume(volume)


@when("I send a pause command")
def send_pause_command(mock_sonos_bridge, mock_mqtt_client):
    """When I send a pause command"""
    topic = "sonos/living_room_sonos/control"
    payload = json.dumps({"command": "pause"})
    mock_mqtt_client.publish(topic, payload)


@when(parsers.parse("I create a group with {master} as master"))
def create_audio_group(mock_sonos_bridge, master):
    """When I create a multi-room audio group"""
    mock_sonos_bridge.create_group(master_speaker=master)


@when("the speaker status is requested")
def request_speaker_status(mock_sonos_bridge, mock_mqtt_client):
    """When the speaker status is requested"""
    topic = "sonos/living_room_sonos/status"
    payload = json.dumps({"request": "status"})
    mock_mqtt_client.publish(topic, payload)


@when("the speaker becomes unreachable")
def speaker_becomes_unreachable(mock_sonos_bridge):
    """When the speaker becomes unreachable"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.is_available = False


@when("a TTS request is received via MQTT")
def receive_tts_request(mock_mqtt_client):
    """When a TTS request is received via MQTT"""
    topic = "voice/tts/request"
    payload = json.dumps({"message": "Test message", "speaker": "living_room_sonos"})
    mock_mqtt_client.on_message(topic, payload)


@then("all available speakers should be discovered")
def speakers_should_be_discovered(mock_sonos_bridge):
    """Then all available speakers should be discovered"""
    assert len(mock_sonos_bridge.discovered_speakers) > 0


@then("speaker information should be published to MQTT")
def speaker_info_published(mock_mqtt_client):
    """Then speaker information should be published to MQTT"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "sonos/discovery" in call_args[0][0]


@then("the speaker should play the announcement")
def speaker_should_play_announcement(mock_sonos_bridge):
    """Then the speaker should play the announcement"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.play_tts.assert_called()


@then("a completion status should be published")
def completion_status_published(mock_mqtt_client):
    """Then a completion status should be published"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "completed" in call_args[0][1]


@then(parsers.parse("the speaker volume should be {volume:d}"))
def speaker_volume_should_be(mock_sonos_bridge, volume):
    """Then the speaker volume should be set correctly"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        assert speaker.volume == volume


@then("the volume change should be confirmed via MQTT")
def volume_change_confirmed(mock_mqtt_client):
    """Then the volume change should be confirmed via MQTT"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "volume" in call_args[0][1]


@then("the speaker should pause playback")
def speaker_should_pause(mock_sonos_bridge):
    """Then the speaker should pause playback"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.pause.assert_called()


@then('the playback state should update to "PAUSED"')
def playback_state_should_update(mock_mqtt_client):
    """Then the playback state should update to PAUSED"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    payload = json.loads(call_args[0][1])
    assert payload.get("state") == "PAUSED"


@then("both speakers should be in the same group")
def speakers_in_same_group(mock_sonos_bridge):
    """Then both speakers should be in the same group"""
    speakers = list(mock_sonos_bridge.discovered_speakers.values())
    assert len(speakers) == 2
    # Check that group creation was called
    mock_sonos_bridge.create_group.assert_called()


@then("group status should be published to MQTT")
def group_status_published(mock_mqtt_client):
    """Then group status should be published to MQTT"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "group" in call_args[0][1]


@then("the current status should be published")
def current_status_published(mock_mqtt_client):
    """Then the current status should be published"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    payload = json.loads(call_args[0][1])
    assert "volume" in payload
    assert "state" in payload


@then("an error status should be published")
def error_status_published(mock_mqtt_client):
    """Then an error status should be published"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "error" in call_args[0][1]


@then("the bridge should attempt reconnection")
def bridge_should_attempt_reconnection(mock_sonos_bridge):
    """Then the bridge should attempt reconnection"""
    mock_sonos_bridge.reconnect.assert_called()


@then("the message should be forwarded to the appropriate speaker")
def message_forwarded_to_speaker(mock_sonos_bridge):
    """Then the message should be forwarded to the appropriate speaker"""
    for speaker in mock_sonos_bridge.discovered_speakers.values():
        speaker.play_tts.assert_called()


@then("playback confirmation should be sent back")
def playback_confirmation_sent(mock_mqtt_client):
    """Then playback confirmation should be sent back"""
    mock_mqtt_client.publish.assert_called()
    call_args = mock_mqtt_client.publish.call_args
    assert "confirmation" in call_args[0][1]
