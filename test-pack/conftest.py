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
    return speaker
