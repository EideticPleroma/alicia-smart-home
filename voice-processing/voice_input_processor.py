#!/usr/bin/env python3
"""
Voice Input Processor for Alicia Voice Assistant
Handles microphone input, wake word detection, and voice command recording
"""

import asyncio
import json
import logging
import os
import sounddevice as sd
import paho.mqtt.client as mqtt
import time
import wave
import threading
from typing import Optional, Callable
from wyoming.client import AsyncTcpClient
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.asr import Transcribe

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceInputProcessor:
    """Handles microphone input and voice command processing"""
    
    def __init__(self):
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = 'int16'
        self.record_duration = 5  # seconds
        
        # Audio components
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.is_recording = False
        
        # MQTT settings
        self.mqtt_broker = os.getenv("MQTT_BROKER", "alicia_mqtt")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "voice_assistant")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")
        self.mqtt_client = None
        
        # Whisper STT settings
        self.whisper_host = os.getenv("WHISPER_HOST", "alicia_wyoming_whisper")
        self.whisper_port = int(os.getenv("WHISPER_PORT", "10300"))
        
        # Wake word detection
        self.wake_word = "alicia"
        self.wake_word_detected = False
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_command_processed = None
        
    def initialize_audio(self):
        """Initialize sounddevice for microphone access"""
        try:
            # sounddevice doesn't need explicit initialization
            self.audio = True
            logger.info("✅ Audio system initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Audio initialization failed: {e}")
            return False
    
    def initialize_mqtt(self):
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client("voice_input_processor")
            self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info("✅ MQTT client connected")
            return True
        except Exception as e:
            logger.error(f"❌ MQTT connection failed: {e}")
            return False
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("🔗 Connected to MQTT broker")
            client.subscribe("alicia/voice/wake")
        else:
            logger.error(f"❌ MQTT connection failed: {rc}")
    
    def start_listening(self):
        """Start continuous microphone listening"""
        if not self.audio:
            if not self.initialize_audio():
                return False
        
        if not self.mqtt_client:
            if not self.initialize_mqtt():
                return False
        
        self.is_listening = True
        logger.info("🎤 Starting continuous microphone listening...")
        
        # Start listening in a separate thread
        threading.Thread(target=self._listen_loop, daemon=True).start()
        return True
    
    def stop_listening(self):
        """Stop microphone listening"""
        self.is_listening = False
        logger.info("⏹️ Stopped microphone listening")
    
    def _listen_loop(self):
        """Main listening loop"""
        try:
            logger.info("🎧 Starting microphone listening with sounddevice")
            
            while self.is_listening:
                try:
                    # Record a small chunk of audio
                    audio_data = sd.rec(
                        int(self.sample_rate * 0.1),  # 0.1 seconds
                        samplerate=self.sample_rate,
                        channels=self.channels,
                        dtype=self.format
                    )
                    sd.wait()  # Wait for recording to complete
                    
                    # Convert to bytes for processing
                    audio_bytes = audio_data.tobytes()
                    
                    # Simple wake word detection (basic implementation)
                    if self._detect_wake_word(audio_bytes):
                        logger.info("👂 Wake word detected!")
                        self._handle_wake_word()
                        
                        # Record command after wake word
                        if self._record_voice_command():
                            logger.info("✅ Voice command recorded and processed")
                        
                except Exception as e:
                    logger.error(f"❌ Error in listening loop: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"❌ Error starting listening loop: {e}")
    
    def _detect_wake_word(self, audio_data: bytes) -> bool:
        """Simple wake word detection (placeholder implementation)"""
        # This is a basic implementation - in production, you'd use a proper wake word detector
        # For now, we'll use a simple volume-based trigger
        import numpy as np
        
        try:
            # Convert audio data to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate RMS volume
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Simple threshold-based detection
            threshold = 1000  # Adjust based on your microphone sensitivity
            return rms > threshold
            
        except Exception as e:
            logger.error(f"❌ Error in wake word detection: {e}")
            return False
    
    def _handle_wake_word(self):
        """Handle wake word detection"""
        self.wake_word_detected = True
        self.publish_mqtt("alicia/voice/wake", json.dumps({
            "status": "wake_word_detected",
            "timestamp": time.time()
        }))
        
        if self.on_wake_word_detected:
            self.on_wake_word_detected()
    
    def _record_voice_command(self) -> bool:
        """Record voice command after wake word detection"""
        if self.is_recording:
            return False
        
        self.is_recording = True
        logger.info("🎙️ Recording voice command...")
        
        try:
            # Record for specified duration using sounddevice
            audio_data = sd.rec(
                int(self.sample_rate * self.record_duration),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.format
            )
            sd.wait()  # Wait for recording to complete
            
            # Save to temporary file
            temp_file = f"/tmp/voice_command_{int(time.time())}.wav"
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            logger.info(f"💾 Voice command saved: {temp_file}")
            
            # Process with Whisper STT
            asyncio.run(self._process_with_whisper(temp_file))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording voice command: {e}")
            return False
        finally:
            self.is_recording = False
    
    async def _process_with_whisper(self, audio_file: str):
        """Process audio file with Whisper STT"""
        try:
            logger.info("🤖 Processing with Whisper STT...")
            
            # Read audio file
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # Connect to Whisper service
            async with AsyncTcpClient(self.whisper_host, self.whisper_port) as client:
                # Send transcription request first
                await client.write_event(Transcribe().event())
                
                # Send audio start event
                await client.write_event(AudioStart(
                    rate=self.sample_rate,
                    width=2,  # 16-bit
                    channels=self.channels
                ).event())
                
                # Send audio data in chunks
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    await client.write_event(AudioChunk(
                        rate=self.sample_rate,
                        width=2,  # 16-bit
                        channels=self.channels,
                        audio=chunk
                    ).event())
                
                # Send audio stop event
                await client.write_event(AudioStop().event())
                
                # Read response with timeout
                transcription = ""
                try:
                    while True:
                        event = await asyncio.wait_for(client.read_event(), timeout=10.0)
                        if event is None:
                            logger.warning("⚠️ Received None event from service")
                            break
                        if event.type == "transcript":
                            transcription = event.data.get("text", "").strip()
                            break
                        else:
                            logger.info(f"📨 Received event: {event.type}")
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Timeout waiting for transcription response")
                    return
                
                if transcription:
                    logger.info(f"📝 Transcription: '{transcription}'")
                    
                    # Publish to MQTT
                    self.publish_mqtt("alicia/voice/command", transcription)
                    
                    if self.on_command_processed:
                        self.on_command_processed(transcription)
                else:
                    logger.warning("⚠️ No transcription received")
            
            # Clean up audio file
            try:
                os.remove(audio_file)
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Error processing with Whisper: {e}")
    
    def publish_mqtt(self, topic: str, payload: str):
        """Publish message to MQTT"""
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload)
            logger.info(f"📡 Published to MQTT: {topic}")
    
    def set_wake_word_callback(self, callback: Callable):
        """Set callback for wake word detection"""
        self.on_wake_word_detected = callback
    
    def set_command_processed_callback(self, callback: Callable):
        """Set callback for command processing"""
        self.on_command_processed = callback
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

async def main():
    """Main function for testing"""
    processor = VoiceInputProcessor()
    
    def on_wake_word():
        print("🔔 Wake word detected!")
    
    def on_command(command):
        print(f"🎤 Command processed: {command}")
    
    processor.set_wake_word_callback(on_wake_word)
    processor.set_command_processed_callback(on_command)
    
    if processor.start_listening():
        print("🎧 Voice input processor started. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping voice input processor...")
    else:
        print("❌ Failed to start voice input processor")
    
    processor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
