#!/usr/bin/env python3
"""
Debug Wyoming Protocol Connection
Test the Wyoming client connection directly to identify issues
"""

import asyncio
import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wyoming.client import AsyncTcpClient
    from wyoming.tts import Synthesize
    from wyoming.asr import Transcribe
    from wyoming.audio import AudioStart, AudioStop, AudioChunk
    print("✅ Wyoming client library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Wyoming client: {e}")
    print("Please install dependencies: pip install wyoming")
    sys.exit(1)

class WyomingConnectionDebugger:
    def __init__(self):
        # Use the same URLs as the assistant
        self.whisper_url = "tcp://alicia_wyoming_whisper:10300"
        self.piper_url = "tcp://alicia_wyoming_piper:10200"

        # Parse URLs for AsyncTcpClient (expects host, port separately)
        self.whisper_host, self.whisper_port = self._parse_wyoming_url(self.whisper_url)
        self.piper_host, self.piper_port = self._parse_wyoming_url(self.piper_url)

    def _parse_wyoming_url(self, url: str) -> tuple[str, int]:
        """Parse Wyoming URL into host and port for AsyncTcpClient"""
        # Remove tcp:// prefix if present
        if url.startswith("tcp://"):
            url = url[6:]

        # Split host and port
        if ":" in url:
            host, port_str = url.rsplit(":", 1)
            port = int(port_str)
        else:
            # Default port if not specified
            host = url
            port = 10300 if "whisper" in url else 10200

        return host, port

    async def debug_whisper_connection(self):
        """Debug Whisper connection step by step"""
        print("\n🔍 Debugging Wyoming Whisper Connection...")
        print(f"Target URL: {self.whisper_url}")

        try:
            print("1. Attempting to create AsyncTcpClient...")
            client = AsyncTcpClient(self.whisper_host, self.whisper_port)
            print("✅ AsyncTcpClient created successfully")

            print("2. Attempting to establish connection...")
            async with client:
                print("✅ Connection established successfully")

                print("3. Testing basic communication...")
                # Try to send a simple message
                test_message = Transcribe(name="test", language="en")
                print(f"   Sending: {test_message}")

                await client.write_event(test_message.event())
                print("✅ Message sent successfully")

                print("4. Waiting for response...")
                try:
                    event = await asyncio.wait_for(client.read_event(), timeout=5.0)
                    print(f"✅ Response received: {event.type}")
                    if hasattr(event, 'data'):
                        print(f"   Data: {event.data}")
                    return True
                except asyncio.TimeoutError:
                    print("❌ Timeout waiting for response")
                    return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False

    async def debug_piper_connection(self):
        """Debug Piper connection step by step"""
        print("\n🔍 Debugging Wyoming Piper Connection...")
        print(f"Target URL: {self.piper_url}")

        try:
            print("1. Attempting to create AsyncTcpClient...")
            client = AsyncTcpClient(self.piper_host, self.piper_port)
            print("✅ AsyncTcpClient created successfully")

            print("2. Attempting to establish connection...")
            async with client:
                print("✅ Connection established successfully")

                print("3. Testing basic communication...")
                # Try to send a simple synthesis request
                from wyoming.tts import SynthesizeVoice
                test_text = "Test"
                test_voice = SynthesizeVoice(name="en_US-lessac-medium")
                test_message = Synthesize(text=test_text, voice=test_voice)
                print(f"   Sending synthesis request: '{test_text}'")

                await client.write_event(test_message.event())
                print("✅ Synthesis request sent successfully")

                print("4. Waiting for response...")
                try:
                    event = await asyncio.wait_for(client.read_event(), timeout=5.0)
                    print(f"✅ Response received: {event.type}")
                    if hasattr(event, 'data'):
                        print(f"   Data: {event.data}")
                    return True
                except asyncio.TimeoutError:
                    print("❌ Timeout waiting for response")
                    return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False

    async def test_basic_tcp_connection(self):
        """Test basic TCP connectivity without Wyoming protocol"""
        print("\n🔍 Testing Basic TCP Connectivity...")

        import socket
        import asyncio

        async def test_port(host, port):
            try:
                reader, writer = await asyncio.open_connection(host, port)
                print(f"✅ Basic TCP connection to {host}:{port} successful")
                writer.close()
                await writer.wait_closed()
                return True
            except Exception as e:
                print(f"❌ Basic TCP connection to {host}:{port} failed: {e}")
                return False

        # Test both services
        whisper_ok = await test_port("alicia_wyoming_whisper", 10300)
        piper_ok = await test_port("alicia_wyoming_piper", 10200)

        return whisper_ok, piper_ok

    async def run_debug_tests(self):
        """Run all debug tests"""
        print("🚀 Starting Wyoming Connection Debug Tests")
        print("=" * 60)

        # Test basic TCP connectivity first
        whisper_tcp, piper_tcp = await self.test_basic_tcp_connection()

        if not (whisper_tcp and piper_tcp):
            print("\n❌ Basic TCP connectivity failed. Wyoming services may not be running properly.")
            return False

        # Test Wyoming protocol connections
        print("\n🧪 Testing Wyoming Protocol Connections...")

        whisper_test = await self.debug_whisper_connection()
        piper_test = await self.debug_piper_connection()

        # Summary
        print("\n" + "=" * 60)
        print("📊 DEBUG TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Basic TCP Whisper (10300): {'✅ PASS' if whisper_tcp else '❌ FAIL'}")
        print(f"Basic TCP Piper (10200): {'✅ PASS' if piper_tcp else '❌ FAIL'}")
        print(f"Wyoming Protocol Whisper: {'✅ PASS' if whisper_test else '❌ FAIL'}")
        print(f"Wyoming Protocol Piper: {'✅ PASS' if piper_test else '❌ FAIL'}")

        success = whisper_test and piper_test
        print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")

        if success:
            print("\n🎉 Wyoming Protocol connections are working correctly!")
            print("The assistant should be able to connect now.")
        else:
            print("\n❌ Wyoming Protocol connections are failing.")
            print("This indicates an issue with the Wyoming client library or service configuration.")

        return success

async def main():
    """Main debug function"""
    debugger = WyomingConnectionDebugger()
    success = await debugger.run_debug_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
