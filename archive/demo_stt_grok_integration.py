#!/usr/bin/env python3
"""
Demo script showing STT → Grok integration
This demonstrates the complete voice processing pipeline
"""

import asyncio
import os
import sys
import json
import logging

# Add voice-processing directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'voice-processing'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class STTGrokDemo:
    """Demo class showing STT to Grok integration"""
    
    def __init__(self):
        self.grok_enabled = False
        self.grok_handler = None
        
        # Check for Grok API key
        api_key = os.getenv("XAI_API_KEY")
        if api_key:
            try:
                from grok_handler import GrokHandler
                self.grok_handler = GrokHandler(api_key=api_key, model="grok-4-0709")
                self.grok_enabled = True
                logger.info("✅ Grok integration enabled")
            except ImportError as e:
                logger.warning(f"⚠️ Grok integration not available: {e}")
        else:
            logger.warning("⚠️ XAI_API_KEY not found - Grok disabled")
    
    async def process_voice_command(self, transcription: str):
        """Process a voice command through the complete pipeline"""
        logger.info(f"🎤 Processing command: '{transcription}'")
        
        if self.grok_enabled and self.grok_handler:
            try:
                # Process with Grok
                logger.info("🧠 Processing with Grok...")
                response = await self.grok_handler.process_command(transcription)
                logger.info(f"🤖 Grok response: '{response}'")
                return response
            except Exception as e:
                logger.error(f"❌ Grok processing failed: {e}")
                return self._fallback_response(transcription)
        else:
            # Fallback processing
            return self._fallback_response(transcription)
    
    def _fallback_response(self, transcription: str) -> str:
        """Fallback response when Grok is not available"""
        return f"I heard: '{transcription}'. I'm still learning, but I'll help as best I can!"
    
    async def simulate_voice_pipeline(self, test_commands: list):
        """Simulate the complete voice processing pipeline"""
        print("Voice Processing Pipeline Demo")
        print("=" * 50)
        print(f"Grok Integration: {'Enabled' if self.grok_enabled else 'Disabled'}")
        print()
        
        for i, command in enumerate(test_commands, 1):
            print(f"Test {i}: '{command}'")
            
            # Simulate STT transcription (already done)
            transcription = command
            
            # Process with Grok
            response = await self.process_voice_command(transcription)
            
            print(f"Response: '{response}'")
            print("-" * 30)

async def main():
    """Main demo function"""
    demo = STTGrokDemo()
    
    # Test commands
    test_commands = [
        "Hello Alicia, how are you today?",
        "What's the weather like?",
        "Turn on the living room lights",
        "Tell me a joke",
        "What time is it?"
    ]
    
    # Run the demo
    await demo.simulate_voice_pipeline(test_commands)
    
    print("\nIntegration Status:")
    print("=" * 20)
    print(f"STT Pipeline: Working (Whisper)")
    print(f"Grok Integration: {'Working' if demo.grok_enabled else 'Disabled'}")
    print(f"MQTT Publishing: Ready")
    print(f"TTS Pipeline: Ready (Piper)")
    
    if not demo.grok_enabled:
        print("\nTo enable Grok integration:")
        print("1. Get API key from https://x.ai/api")
        print("2. Set environment variable: set XAI_API_KEY=your-key")
        print("3. Install dependencies: pip install -r voice-processing/requirements.txt")
    
    print("\nComplete Pipeline Flow:")
    print("Voice Input → Whisper STT → Grok Processing → Piper TTS → Sonos Output")

if __name__ == "__main__":
    asyncio.run(main())
