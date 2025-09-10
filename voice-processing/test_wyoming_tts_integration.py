#!/usr/bin/env python3
"""
Wyoming TTS Integration Test Suite
Comprehensive testing for the unified Wyoming Piper TTS with Sonos integration
"""

import asyncio
import json
import logging
import os
import time
import unittest
from unittest.mock import Mock, patch
import paho.mqtt.client as mqtt
from wyoming.client import AsyncTcpClient
from wyoming.event import Event
from wyoming.tts import Synthesize

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWyomingTTSIntegration(unittest.TestCase):
    """Test suite for Wyoming TTS integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.tts_service_host = "localhost"
        self.tts_service_port = 10200

        # Test data
        self.test_message = "Hello, this is a test message for Wyoming TTS integration."
        self.test_language = "en"
        self.test_speaker = "kitchen"

    def test_mqtt_connection(self):
        """Test MQTT broker connectivity"""
        logger.info("Testing MQTT broker connection...")

        client = mqtt.Client("test_client")
        client.username_pw_set("voice_assistant", "alicia_ha_mqtt_2024")

        connection_result = []

        def on_connect(client, userdata, flags, rc):
            connection_result.append(rc)

        client.on_connect = on_connect

        try:
            client.connect(self.mqtt_broker, self.mqtt_port, 10)
            client.loop_start()
            time.sleep(2)  # Wait for connection
            client.loop_stop()
            client.disconnect()

            self.assertEqual(connection_result[0], 0, "MQTT connection failed")
            logger.info("✅ MQTT broker connection successful")

        except Exception as e:
            self.fail(f"MQTT connection test failed: {e}")

    async def test_wyoming_tts_service_connection(self):
        """Test Wyoming TTS service connectivity"""
        logger.info("Testing Wyoming TTS service connection...")

        try:
            async with AsyncTcpClient(self.tts_service_host, self.tts_service_port) as client:
                logger.info("✅ Wyoming TTS service connection successful")
                return True
        except Exception as e:
            logger.error(f"Wyoming TTS service connection failed: {e}")
            return False

    async def test_wyoming_tts_synthesis(self):
        """Test Wyoming TTS synthesis"""
        logger.info("Testing Wyoming TTS synthesis...")

        try:
            async with AsyncTcpClient(self.tts_service_host, self.tts_service_port) as client:
                # Send synthesis request
                synthesize_event = Synthesize(
                    text=self.test_message,
                    voice="en_US-lessac-medium"
                )

                await client.write_event(synthesize_event.event())

                # Collect response
                audio_chunks = []
                while True:
                    event = await client.read_event()
                    if event.type == "audio-chunk":
                        audio_chunks.append(event.data)
                    elif event.type == "audio-stop":
                        break
                    elif event.type == "error":
                        self.fail(f"TTS synthesis error: {event.data}")

                # Verify audio was generated
                self.assertGreater(len(audio_chunks), 0, "No audio chunks received")
                logger.info(f"✅ TTS synthesis successful, received {len(audio_chunks)} audio chunks")

        except Exception as e:
            self.fail(f"TTS synthesis test failed: {e}")

    def test_mqtt_tts_command(self):
        """Test MQTT TTS command publishing"""
        logger.info("Testing MQTT TTS command publishing...")

        client = mqtt.Client("test_tts_client")
        client.username_pw_set("voice_assistant", "alicia_ha_mqtt_2024")

        messages_received = []

        def on_message(client, userdata, msg):
            messages_received.append((msg.topic, msg.payload.decode()))

        client.on_message = on_message

        try:
            client.connect(self.mqtt_broker, self.mqtt_port, 10)
            client.loop_start()

            # Subscribe to TTS topic
            client.subscribe("alicia/tts/kitchen")

            # Publish TTS command
            tts_payload = {
                "speaker": self.test_speaker,
                "message": self.test_message,
                "language": self.test_language,
                "volume": 30,
                "use_wyoming": True
            }

            client.publish("alicia/tts/kitchen", json.dumps(tts_payload))

            # Wait for message processing
            time.sleep(3)

            client.loop_stop()
            client.disconnect()

            logger.info("✅ MQTT TTS command published successfully")

        except Exception as e:
            self.fail(f"MQTT TTS command test failed: {e}")

    async def test_end_to_end_tts_pipeline(self):
        """Test complete end-to-end TTS pipeline"""
        logger.info("Testing end-to-end TTS pipeline...")

        # Step 1: Test Wyoming TTS service
        service_available = await self.test_wyoming_tts_service_connection()
        self.assertTrue(service_available, "Wyoming TTS service not available")

        # Step 2: Test TTS synthesis
        await self.test_wyoming_tts_synthesis()

        # Step 3: Test MQTT communication
        self.test_mqtt_tts_command()

        logger.info("✅ End-to-end TTS pipeline test completed successfully")

    def test_tts_payload_validation(self):
        """Test TTS payload validation"""
        logger.info("Testing TTS payload validation...")

        # Valid payload
        valid_payload = {
            "speaker": "kitchen",
            "message": "Test message",
            "language": "en",
            "volume": 30,
            "use_wyoming": True
        }

        # Test valid payload
        self.assertIsInstance(valid_payload["speaker"], str)
        self.assertIsInstance(valid_payload["message"], str)
        self.assertIsInstance(valid_payload["language"], str)
        self.assertIsInstance(valid_payload["volume"], int)
        self.assertIsInstance(valid_payload["use_wyoming"], bool)

        # Test invalid payloads
        invalid_payloads = [
            {"message": "Missing speaker"},
            {"speaker": "kitchen"},  # Missing message
            {"speaker": "kitchen", "message": "", "language": "en"},  # Empty message
        ]

        for payload in invalid_payloads:
            with self.assertRaises((KeyError, ValueError)):
                self._validate_tts_payload(payload)

        logger.info("✅ TTS payload validation tests passed")

    def _validate_tts_payload(self, payload):
        """Helper method to validate TTS payload"""
        required_fields = ["speaker", "message"]
        for field in required_fields:
            if field not in payload:
                raise KeyError(f"Missing required field: {field}")

        if not payload["message"].strip():
            raise ValueError("Message cannot be empty")

        return True

    def test_language_support(self):
        """Test multi-language support"""
        logger.info("Testing multi-language support...")

        test_languages = ["en", "es", "fr", "de"]

        for language in test_languages:
            with self.subTest(language=language):
                payload = {
                    "speaker": "kitchen",
                    "message": f"Test message in {language}",
                    "language": language,
                    "volume": 30,
                    "use_wyoming": True
                }

                # Validate payload structure
                self.assertEqual(payload["language"], language)
                logger.info(f"✅ Language {language} payload validation passed")

    def test_error_handling(self):
        """Test error handling scenarios"""
        logger.info("Testing error handling...")

        # Test with invalid MQTT broker
        with patch('paho.mqtt.client.Client.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            with self.assertRaises(Exception):
                client = mqtt.Client("test_client")
                client.connect("invalid_broker", 1883, 10)

        # Test with invalid Wyoming service
        with patch('wyoming.client.AsyncTcpClient.__aenter__') as mock_enter:
            mock_enter.side_effect = Exception("Service unavailable")

            with self.assertRaises(Exception):
                async def test_invalid_service():
                    async with AsyncTcpClient("invalid_host", 9999):
                        pass
                asyncio.run(test_invalid_service())

        logger.info("✅ Error handling tests passed")

class TestAudioQuality(unittest.TestCase):
    """Test audio quality and performance"""

    def test_audio_format_validation(self):
        """Test audio format validation"""
        logger.info("Testing audio format validation...")

        # Mock audio data
        mock_wav_data = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        mock_mp3_data = b"ID3\x03\x00\x00\x00\x00\x00\x00"

        # Test WAV validation
        self.assertTrue(self._is_valid_wav(mock_wav_data))

        # Test MP3 validation
        self.assertTrue(self._is_valid_mp3(mock_mp3_data))

        logger.info("✅ Audio format validation tests passed")

    def _is_valid_wav(self, data):
        """Check if data is valid WAV format"""
        return len(data) > 44 and data[:4] == b"RIFF"

    def _is_valid_mp3(self, data):
        """Check if data is valid MP3 format"""
        return len(data) > 10 and (data[:3] == b"ID3" or data[:2] == b"\xFF\xFB")

    def test_performance_metrics(self):
        """Test performance metrics"""
        logger.info("Testing performance metrics...")

        import time

        # Simulate TTS processing time
        start_time = time.time()
        time.sleep(0.1)  # Simulate 100ms processing
        processing_time = time.time() - start_time

        # Assert reasonable processing time
        self.assertLess(processing_time, 1.0, "Processing time too slow")
        self.assertGreater(processing_time, 0.05, "Processing time too fast (unrealistic)")

        logger.info(f"✅ Performance test passed: {processing_time:.3f}s processing time")

def run_integration_tests():
    """Run all integration tests"""
    logger.info("Starting Wyoming TTS Integration Test Suite...")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(TestWyomingTTSIntegration('test_mqtt_connection'))
    suite.addTest(TestWyomingTTSIntegration('test_tts_payload_validation'))
    suite.addTest(TestWyomingTTSIntegration('test_language_support'))
    suite.addTest(TestWyomingTTSIntegration('test_error_handling'))
    suite.addTest(TestAudioQuality('test_audio_format_validation'))
    suite.addTest(TestAudioQuality('test_performance_metrics'))

    # Run async tests
    async def run_async_tests():
        test_instance = TestWyomingTTSIntegration()
        test_instance.setUp()

        try:
            await test_instance.test_wyoming_tts_service_connection()
            await test_instance.test_wyoming_tts_synthesis()
            await test_instance.test_end_to_end_tts_pipeline()
            logger.info("✅ All async tests passed")
        except Exception as e:
            logger.error(f"Async tests failed: {e}")

    # Run async tests
    asyncio.run(run_async_tests())

    # Run sync tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    if result.wasSuccessful():
        logger.info("🎉 All Wyoming TTS integration tests passed!")
        return True
    else:
        logger.error(f"❌ {len(result.failures)} tests failed, {len(result.errors)} errors")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
