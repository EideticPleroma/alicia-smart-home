"""
Pytest configuration and fixtures for BDD tests
"""
import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT client for testing"""
    return Mock()


@pytest.fixture
def mock_sonos_bridge():
    """Mock Sonos MQTT bridge"""
    bridge = Mock()
    bridge.discovered_speakers = {}
    return bridge


@pytest.fixture
def mock_sonos_speaker():
    """Mock Sonos speaker for testing"""
    speaker = Mock()
    speaker.name = "living_room_sonos"
    speaker.volume = 30
    speaker.is_playing = False
    speaker.current_track = None
    speaker.player_name = "Living Room Sonos"
    speaker.ip_address = "192.168.1.100"
    speaker.get_current_transport_info.return_value = {'current_transport_state': 'STOPPED'}
    speaker.get_current_track_info.return_value = {'title': 'No Track'}

    # Make set_volume actually update the volume attribute
    def set_volume_mock(value):
        speaker.volume = value
    speaker.set_volume = set_volume_mock

    return speaker
