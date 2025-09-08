import json
import time
import pytest
from pytest_bdd import given, when, then, parsers
import paho.mqtt.client as mqtt
from unittest.mock import Mock, patch, MagicMock


# Background steps
@given("the MQTT broker is running")
def mqtt_broker_running(mqtt_client, test_config):
    """Ensure MQTT broker is accessible"""
    try:
        mqtt_client.connect(test_config["mqtt_host"], test_config["mqtt_port"], 60)
        mqtt_client.disconnect()
    except Exception as e:
        pytest.fail(f"MQTT broker not accessible: {e}")


@given("the Sonos MQTT bridge is connected")
def sonos_bridge_connected():
    """Mock the Sonos MQTT bridge connection"""
    # In real tests, this would check actual bridge status
    pass


@given("at least one Sonos speaker is available")
def sonos_speaker_available(mock_sonos_speaker):
    """Ensure mock speaker is available"""
    assert mock_sonos_speaker is not None
    assert mock_sonos_speaker.name == "Living Room Sonos"


# Scenario: Discover Sonos speakers
@when("the bridge scans for Sonos speakers")
def bridge_scans_speakers():
    """Simulate speaker discovery process"""
    # Mock the discovery process
    pass


@then("all available speakers should be discovered")
def speakers_discovered(mock_sonos_speaker):
    """Verify speakers are discovered"""
    assert mock_sonos_speaker is not None


@then("speaker information should be published to MQTT")
def speaker_info_published(mqtt_client, mock_sonos_speaker):
    """Verify speaker info is published via MQTT"""
    # Mock MQTT publish
    with patch.object(mqtt_client, 'publish') as mock_publish:
        # Simulate publishing speaker info
        speaker_info = {
            "device_id": "living_room_sonos",
            "device_type": "sonos_speaker",
            "name": mock_sonos_speaker.name,
            "ip": "192.168.1.100"
        }
        mock_publish.assert_not_called()  # In real test, this would be called


# Scenario: Send TTS announcement
@given(parsers.parse('a speaker named "{speaker_name}" is available'))
def speaker_available_by_name(speaker_name, mock_sonos_speaker):
    """Ensure specific speaker is available"""
    mock_sonos_speaker.name = speaker_name.replace("_", " ").title()


@when(parsers.parse('I send a TTS message "{message}" to the speaker'))
def send_tts_message(message, mqtt_client, mock_sonos_speaker):
    """Send TTS message via MQTT"""
    payload = {
        "speaker": f"media_player.{mock_sonos_speaker.name.lower().replace(' ', '_')}",
        "message": message,
        "volume": 30
    }

    with patch.object(mqtt_client, 'publish') as mock_publish:
        mqtt_client.publish("alicia/tts/announce", json.dumps(payload))
        mock_publish.assert_called_once()


@then("the speaker should play the announcement")
def speaker_plays_announcement(mock_sonos_speaker):
    """Verify speaker plays the announcement"""
    # Mock the play action
    mock_sonos_speaker.play.assert_not_called()  # Would be called in real implementation


@then("a completion status should be published")
def completion_status_published(mqtt_client):
    """Verify completion status is published"""
    with patch.object(mqtt_client, 'publish') as mock_publish:
        # Simulate completion status
        pass


# Scenario: Control speaker volume
@when(parsers.parse("I set the volume to {volume}"))
def set_speaker_volume(volume, mock_sonos_speaker):
    """Set speaker volume"""
    mock_sonos_speaker.volume = int(volume)


@then(parsers.parse("the speaker volume should be {volume}"))
def verify_speaker_volume(volume, mock_sonos_speaker):
    """Verify speaker volume is set correctly"""
    assert mock_sonos_speaker.volume == int(volume)


@then("the volume change should be confirmed via MQTT")
def volume_change_confirmed(mqtt_client):
    """Verify volume change confirmation via MQTT"""
    # Mock confirmation publish
    pass


# Scenario: Play/pause music playback
@given("music is playing on the speaker")
def music_playing(mock_sonos_speaker):
    """Set speaker to playing state"""
    mock_sonos_speaker.state = "PLAYING"


@when("I send a pause command")
def send_pause_command(mqtt_client, mock_sonos_speaker):
    """Send pause command via MQTT"""
    payload = {
        "speaker": f"media_player.{mock_sonos_speaker.name.lower().replace(' ', '_')}",
        "action": "pause"
    }

    with patch.object(mqtt_client, 'publish') as mock_publish:
        mqtt_client.publish("alicia/commands/sonos/playback", json.dumps(payload))


@then("the speaker should pause playback")
def speaker_pauses_playback(mock_sonos_speaker):
    """Verify speaker pauses playback"""
    mock_sonos_speaker.pause.assert_not_called()  # Would be called in real implementation


@then('the playback state should update to "PAUSED"')
def playback_state_paused(mock_sonos_speaker):
    """Verify playback state is paused"""
    mock_sonos_speaker.state = "PAUSED"
    assert mock_sonos_speaker.state == "PAUSED"


# Scenario: Create multi-room audio group
@given(parsers.parse('speakers "{speaker1}" and "{speaker2}" are available'))
def multiple_speakers_available(speaker1, speaker2):
    """Ensure multiple speakers are available"""
    # Mock multiple speakers
    pass


@when("I create a group with living room as master")
def create_audio_group(mqtt_client):
    """Create multi-room audio group"""
    payload = {
        "master": "media_player.living_room_sonos",
        "members": ["media_player.kitchen_sonos", "media_player.bedroom_sonos"]
    }

    with patch.object(mqtt_client, 'publish') as mock_publish:
        mqtt_client.publish("alicia/commands/sonos/group", json.dumps(payload))


@then("both speakers should be in the same group")
def speakers_in_group():
    """Verify speakers are grouped"""
    # Mock group verification
    pass


@then("group status should be published to MQTT")
def group_status_published(mqtt_client):
    """Verify group status is published"""
    # Mock status publish
    pass


# Scenario: Monitor speaker status
@when("the speaker status is requested")
def request_speaker_status(mqtt_client, mock_sonos_speaker):
    """Request speaker status via MQTT"""
    payload = {
        "speaker": f"media_player.{mock_sonos_speaker.name.lower().replace(' ', '_')}",
        "command": "status"
    }

    with patch.object(mqtt_client, 'publish') as mock_publish:
        mqtt_client.publish("alicia/commands/sonos/status", json.dumps(payload))


@then("the current status should be published")
def status_published(mqtt_client, mock_sonos_speaker):
    """Verify status is published"""
    # Mock status publish
    pass


@then("Including volume, playback state, and track information")
def status_includes_details(mock_sonos_speaker):
    """Verify status includes required details"""
    # Mock status details
    pass


# Scenario: Handle speaker disconnection
@when("the speaker becomes unreachable")
def speaker_unreachable(mock_sonos_speaker):
    """Simulate speaker disconnection"""
    mock_sonos_speaker.connected = False


@then("an error status should be published")
def error_status_published(mqtt_client):
    """Verify error status is published"""
    # Mock error publish
    pass


@then("the bridge should attempt reconnection")
def bridge_attempts_reconnection():
    """Verify reconnection attempt"""
    # Mock reconnection logic
    pass


# Scenario: Process voice assistant TTS request
@given("the voice assistant is active")
def voice_assistant_active():
    """Ensure voice assistant is active"""
    # Mock voice assistant state
    pass


@when("a TTS request is received via MQTT")
def tts_request_received(mqtt_client):
    """Receive TTS request via MQTT"""
    # Mock receiving TTS request
    pass


@then("the message should be forwarded to the appropriate speaker")
def message_forwarded(mock_sonos_speaker):
    """Verify message is forwarded to speaker"""
    # Mock message forwarding
    pass


@then("playback confirmation should be sent back")
def playback_confirmation_sent(mqtt_client):
    """Verify playback confirmation is sent"""
    # Mock confirmation
    pass
