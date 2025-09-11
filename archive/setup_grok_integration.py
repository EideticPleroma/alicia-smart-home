#!/usr/bin/env python3
"""
Setup script for Grok integration with Alicia Voice Assistant
Automates the setup process and validates configuration
"""

import os
import sys
import subprocess
import json
import asyncio
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'openai>=1.0.0',
        'aiohttp>=3.8.0',
        'httpx>=0.25.2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.split('>=')[0].replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("✅ All packages installed")
    else:
        print("✅ All required packages are installed")

def check_api_key():
    """Check if Grok API key is set"""
    print("\n🔑 Checking API key...")
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY environment variable not set")
        print("\nTo set your API key:")
        print("1. Get your API key from https://x.ai/api")
        print("2. Set the environment variable:")
        print("   export XAI_API_KEY='your-api-key-here'")
        print("3. Or add it to your .env file")
        return False
    else:
        print(f"✅ API key found: {api_key[:8]}...")
        return True

def validate_config():
    """Validate configuration files"""
    print("\n⚙️ Validating configuration...")
    
    config_path = Path("voice-processing/config/assistant_config.yaml")
    if not config_path.exists():
        print("❌ Configuration file not found")
        return False
    
    # Check if Grok configuration exists
    with open(config_path, 'r') as f:
        content = f.read()
        if "provider: grok" in content:
            print("✅ Grok configuration found")
            return True
        else:
            print("❌ Grok configuration not found in assistant_config.yaml")
            return False

def test_integration():
    """Test the Grok integration"""
    print("\n🧪 Testing Grok integration...")
    
    try:
        # Import the handler
        sys.path.append('./voice-processing')
        from grok_handler import create_grok_handler
        
        # Test basic functionality
        async def run_test():
            handler = create_grok_handler()
            response = await handler.process_command("Hello, this is a test")
            return response is not None and len(response) > 0
        
        result = asyncio.run(run_test())
        if result:
            print("✅ Grok integration test passed")
            return True
        else:
            print("❌ Grok integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Grok integration test failed: {e}")
        return False

def create_env_template():
    """Create .env template file"""
    print("\n📝 Creating .env template...")
    
    env_content = """# Alicia Voice Assistant Environment Variables

# Grok API Configuration
XAI_API_KEY=your-grok-api-key-here

# MQTT Configuration
MQTT_BROKER=alicia_mqtt
MQTT_PORT=1883
MQTT_USERNAME=voice_assistant
MQTT_PASSWORD=alicia_ha_mqtt_2024

# Voice Processing
WHISPER_URL=tcp://alicia_wyoming_whisper:10300
PIPER_URL=tcp://alicia_unified_tts:10200

# LLM Settings
LLM_ENABLED=true
LLM_PROVIDER=grok
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.template file")
    print("   Copy to .env and update with your values")

def main():
    """Main setup function"""
    print("🚀 Setting up Grok integration for Alicia Voice Assistant")
    print("=" * 60)
    
    # Check requirements
    check_requirements()
    
    # Check API key
    api_key_ok = check_api_key()
    
    # Validate configuration
    config_ok = validate_config()
    
    # Create environment template
    create_env_template()
    
    # Test integration if API key is available
    if api_key_ok:
        test_ok = test_integration()
    else:
        test_ok = False
        print("\n⚠️ Skipping integration test - API key not set")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    print(f"Requirements: {'✅' if True else '❌'}")
    print(f"API Key: {'✅' if api_key_ok else '❌'}")
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"Integration Test: {'✅' if test_ok else '❌'}")
    
    if all([api_key_ok, config_ok, test_ok]):
        print("\n🎉 Setup complete! Grok integration is ready to use.")
        print("\nNext steps:")
        print("1. Start your voice assistant: docker-compose up -d")
        print("2. Test voice commands with Grok enabled")
        print("3. Monitor logs for any issues")
    else:
        print("\n⚠️ Setup incomplete. Please address the issues above.")
        print("\nFor help, see GROK_INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    main()
