#!/usr/bin/env python3
"""
Enhanced Voice Processor with Grok Integration
Handles microphone input, STT, Grok processing, and TTS output
"""

import asyncio
import json
import logging
import os
import pyaudio
import paho.mqtt.client as mqtt
import time
import wave
import threading
from typing import Optional, Callable, Dict, Any
from wyoming.client import AsyncTcpClient
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.asr import Transcribe

# Import Grok integration
try:
    from grok_handler import GrokHandler
    from personality_manager import create_personality_manager
    GROK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Grok integration not available: {e}")
    GROK_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedVoiceProcessor:
    """Enhanced voice processor with Grok integration"""
    
    def __init__(self):
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.record_duration = 5  # seconds
        
        # Audio components
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.is_recording = False
        
        # MQTT settings
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "voice_assistant")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "alicia_ha_mqtt_2024")
        self.mqtt_client = None
        
        # Whisper STT settings
        self.whisper_host = os.getenv("WHISPER_HOST", "localhost")
        self.whisper_port = int(os.getenv("WHISPER_PORT", "10300"))
        
        # Grok integration
        self.grok_handler = None
        self.personality_manager = None
        self.grok_enabled = False
        
        # Wake word detection
        self.wake_word = "alicia"
        self.wake_word_detected = False
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_command_processed = None
        self.on_response_generated = None
        
        # Initialize Grok if available
        self._initialize_grok()
        
    def _initialize_grok(self):
        """Initialize Grok integration if available"""
        if not GROK_AVAILABLE:
            logger.warning("⚠️ Grok integration not available - using basic processing")
            return
            
        try:
            # Get API key from environment
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                logger.warning("⚠️ XAI_API_KEY not found - Grok disabled")
                return
                
            # Initialize Grok handler
            self.grok_handler = GrokHandler(api_key=api_key, model="grok-4-0709")
            self.personality_manager = create_personality_manager()
            self.grok_enabled = True
            
            logger.info("✅ Grok integration initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Grok: {e}")
            self.grok_enabled = False
    
    def initialize_audio(self):
        """Initialize PyAudio for microphone access"""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("✅ Audio system initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Audio initialization failed: {e}")
            return False
    
    def initialize_mqtt(self):
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client("enhanced_voice_processor")
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
            client.subscribe("alicia/voice/command")
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
        logger.info("🎤 Starting enhanced voice processing...")
        
        # Start listening in a separate thread
        threading.Thread(target=self._listen_loop, daemon=True).start()
        return True
    
    def stop_listening(self):
        """Stop microphone listening"""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        logger.info("⏹️ Stopped voice processing")
    
    def _listen_loop(self):
        """Main listening loop"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("🎧 Microphone stream opened")
            
            while self.is_listening:
                try:
                    # Read audio chunk
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Simple wake word detection (basic implementation)
                    if self._detect_wake_word(data):
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
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
    
    def _detect_wake_word(self, audio_data: bytes) -> bool:
        """Simple wake word detection (placeholder implementation)"""
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
            # Record for specified duration
            frames = []
            for _ in range(0, int(self.sample_rate / self.chunk_size * self.record_duration)):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            # Save to temporary file
            temp_file = f"voice_command_{int(time.time())}.wav"
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"💾 Voice command saved: {temp_file}")
            
            # Process with enhanced pipeline
            asyncio.run(self._process_voice_command(temp_file))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording voice command: {e}")
            return False
        finally:
            self.is_recording = False
    
    async def _process_voice_command(self, audio_file: str):
        """Enhanced voice command processing with Grok integration"""
        try:
            # Step 1: Speech-to-Text
            transcription = await self._transcribe_with_whisper(audio_file)
            
            if not transcription:
                logger.warning("⚠️ No transcription received")
                return
            
            logger.info(f"📝 Transcription: '{transcription}'")
            
            # Step 2: Grok Processing (if available)
            if self.grok_enabled and self.grok_handler:
                try:
                    logger.info("🧠 Processing with Grok...")
                    
                    # Get device context from MQTT
                    device_context = await self._get_device_context()
                    
                    # Process with Grok
                    response = await self.grok_handler.process_command(transcription, device_context)
                    
                    logger.info(f"🤖 Grok response: '{response}'")
                    
                    # Publish enhanced response
                    self.publish_mqtt("alicia/voice/response", json.dumps({
                        "transcription": transcription,
                        "response": response,
                        "timestamp": time.time(),
                        "grok_enabled": True
                    }))
                    
                    # Call response callback
                    if self.on_response_generated:
                        self.on_response_generated(transcription, response)
                        
                except Exception as e:
                    logger.error(f"❌ Grok processing failed: {e}")
                    # Fallback to basic processing
                    self._handle_basic_command(transcription)
            else:
                # Basic processing without Grok
                self._handle_basic_command(transcription)
            
            # Publish transcription to MQTT
            self.publish_mqtt("alicia/voice/command", transcription)
            
            # Call command processed callback
            if self.on_command_processed:
                self.on_command_processed(transcription)
            
        except Exception as e:
            logger.error(f"❌ Error processing voice command: {e}")
        finally:
            # Clean up audio file
            try:
                os.remove(audio_file)
            except:
                pass
    
    async def _transcribe_with_whisper(self, audio_file: str) -> str:
        """Transcribe audio file with Whisper STT (fixed version)"""
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
                    return None
                
                if transcription:
                    logger.info(f"✅ Whisper STT successful: '{transcription}'")
                    return transcription
                else:
                    logger.warning("⚠️ No transcription received")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error in Whisper processing: {e}")
            return None
    
    async def _get_device_context(self) -> Dict[str, Any]:
        """Get device context from MQTT/Home Assistant"""
        # This would typically query Home Assistant or MQTT for device states
        # For now, return basic context
        return {
            "timestamp": time.time(),
            "devices": {},
            "sensors": {},
            "user_preferences": {}
        }
    
    def _handle_basic_command(self, transcription: str):
        """Handle basic command processing without Grok"""
        logger.info("🔧 Processing with basic command handler")
        
        # Simple command processing
        response = f"I heard: {transcription}. I'm still learning, but I'll help as best I can!"
        
        # Publish basic response
        self.publish_mqtt("alicia/voice/response", json.dumps({
            "transcription": transcription,
            "response": response,
            "timestamp": time.time(),
            "grok_enabled": False
        }))
        
        # Call response callback
        if self.on_response_generated:
            self.on_response_generated(transcription, response)
    
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
    
    def set_response_generated_callback(self, callback: Callable):
        """Set callback for response generation"""
        self.on_response_generated = callback
    
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
    processor = EnhancedVoiceProcessor()
    
    def on_wake_word():
        print("🔔 Wake word detected!")
    
    def on_command(command):
        print(f"🎤 Command processed: {command}")
    
    def on_response(transcription, response):
        print(f"🤖 Response: {response}")
    
    processor.set_wake_word_callback(on_wake_word)
    processor.set_command_processed_callback(on_command)
    processor.set_response_generated_callback(on_response)
    
    if processor.start_listening():
        print("🎧 Enhanced voice processor started. Press Ctrl+C to stop.")
        print(f"🧠 Grok integration: {'Enabled' if processor.grok_enabled else 'Disabled'}")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping enhanced voice processor...")
    else:
        print("❌ Failed to start enhanced voice processor")
    
    processor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
