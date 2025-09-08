import pytest
from pytest_bdd import given, when, then
import paho.mqtt.client as mqtt
import json
import time
from unittest.mock import Mock, patch

# Import step definitions to register them
from steps import sonos_steps  # noqa: F401


@pytest.fixture
def mqtt_client():
    """MQTT client fixture for testing"""
    client = mqtt.Client()
    client.username_pw_set("sonos_speaker", "alicia_ha_mqtt_2024")
    return client


@pytest.fixture
def mock_sonos_speaker():
    """Mock Sonos speaker for testing"""
    speaker = Mock()
    speaker.name = "Living Room Sonos"
    speaker.volume = 25
    speaker.state = "STOPPED"
    speaker.current_track = None
    return speaker


@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return {
        "mqtt_host": "localhost",
        "mqtt_port": 1883,
        "sonos_hosts": ["192.168.1.100", "192.168.1.101"],
        "timeout": 5
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Any global test setup can go here
    pass
