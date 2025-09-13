#!/usr/bin/env python3
"""
MCP QA Orchestration System - Phase 2 Demo
===========================================

This demo script showcases the fully implemented LangChain agents:
1. ScenarioBuilderAgent - Generates BDD scenarios from codebase
2. ReviewerAgent - Reviews and improves BDD scenarios
3. TestCoderAgent - Creates Python test code from scenarios
4. CodeReviewerAgent - Reviews generated test code

Requirements:
- pip install -r requirements.txt
- Set OPENAI_API_KEY environment variable

Usage:
python demo.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Import the MCP system
sys.path.insert(0, os.path.dirname(__file__))
from mcp_qa_orchestrator import (
    MCPOrchestrator,
    MCPConfig,
    LANGCHAIN_AVAILABLE
)

# Ensure proper environment setup
def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment setup...")

    # Check LangChain availability
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain dependencies not available!")
        print("   Install with: pip install -r requirements.txt")
        return False

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable not set!")
        print("   Set with: export OPENAI_API_KEY=your-api-key-here")
        return False

    print("✅ Environment ready!")
    return True

def create_sample_codebase() -> Dict[str, Any]:
    """Create a comprehensive sample codebase for demonstration"""
    return {
        "project_name": "SmartHomeController",
        "language": "python",
        "architecture": "Microservices with MQTT messaging",
        "description": "A smart home automation controller with device management and voice control",
        "critical_paths": [
            "device_discovery",
            "voice_command_processing",
            "security_authentication",
            "device_state_management"
        ],
        "integration_points": [
            "mqtt_broker",
            "device_registry",
            "voice_stt_service",
            "voice_tts_service"
        ],
        "error_scenarios": [
            "network_disconnection",
            "invalid_device_commands",
            "authentication_failures",
            "voice_recognition_errors"
        ],
        "structure": {
            "src": {
                "controller": {
                    "main.py": "Main controller application",
                    "device_manager.py": "Device registry and management",
                    "voice_processor.py": "Voice command processing",
                    "security_manager.py": "Authentication and authorization",
                    "mqtt_client.py": "MQTT communication handler",
                    "config_manager.py": "Configuration management"
                },
                "services": {
                    "stt_service.py": "Speech-to-text service",
                    "tts_service.py": "Text-to-speech service",
                    "device_service.py": "Generic device control",
                    "automation_service.py": "Home automation rules"
                },
                "utils": {
                    "logger.py": "Centralized logging",
                    "validators.py": "Data validation utilities",
                    "exceptions.py": "Custom exception classes"
                }
            },
            "tests": {
                "unit": {
                    "test_device_manager.py": "Device manager unit tests",
                    "test_voice_processor.py": "Voice processing unit tests",
                    "test_security.py": "Security functionality tests"
                },
                "integration": {
                    "test_mqtt_integration.py": "MQTT integration tests",
                    "test_voice_pipeline.py": "Voice processing pipeline tests"
                },
                "e2e": {
                    "test_complete_workflow.py": "End-to-end test scenarios"
                }
            },
            "docs": {
                "api_reference.md": "API documentation",
                "setup_guide.md": "Installation and setup",
                "user_manual.md": "User guide"
            },
            "config": {
                "devices.json": "Device configuration",
                "mqtt_config.json": "MQTT broker settings",
                "security_config.json": "Security settings"
            }
        }
    }

async def run_demo():
    """Run the complete MCP QA orchestration demo"""
    print("\n🚀 MCP QA Orchestration System - Phase 2 Demo")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\n❌ Demo cannot run due to environment issues.")
        print("Please install dependencies and set API key, then try again.")
        return

    # Create sample codebase
    print("\n📊 Creating sample codebase...")
    codebase = create_sample_codebase()
    print(f"✅ Sample project: {codebase['project_name']}")
    print(f"📁 Files analyzed: {len(json.dumps(codebase['structure']))} chars of structure")

    # Create MCP configuration
    print("\n⚙️  Configuring MCP orchestrator...")
    config = MCPConfig(
        bdd_threshold=8.0,      # Require 80%+ BDD coverage
        quality_threshold=7.5,  # Require 75%+ test quality
        max_iterations=2,       # Allow up to 2 improvement iterations
        max_bugs=2,            # Maximum 2 bugs allowed
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=60,            # 60 second timeout per agent
        retry_attempts=2       # 2 retry attempts per agent
    )
    print(f"✅ Configuration: BDD≥{config.bdd_threshold}, Quality≥{config.quality_threshold}")

    # Initialize orchestrator
    print("\n🤖 Initializing LangChain agents...")
    orchestrator = MCPOrchestrator(config)

    try:
        # Display available agents
        print(f"🎯 Available agents: {list(orchestrator.agents.keys())}")

        # Start orchestration
        print("\n🎬 Starting MCP orchestration...")
        start_time = datetime.now()

        result = await orchestrator.spin_up_mcp(codebase)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Display results
        print(f"\n🎉 Orchestration completed in {duration:.1f} seconds!")
        print("=" * 60)

        # Summary
        status = result.get("summary", {})
        quality = result.get("quality_assessment", {})

        print(f"📊 Final Status: {result.get('status', 'unknown').upper()}")
        print("📈 Quality Scores:")
        print(f"   • BDD Coverage: {result.get('results', {}).get('bdd_scenarios', {}).get('coverage_score', 0):.1f}/10")
        print(f"   • Test Quality: {result.get('results', {}).get('test_files', {}).get('quality_score', 0):.1f}/10")
        print(f"   • Overall Score: {quality.get('overall_score', 0):.1f}/10")
        print(f"   • Thresholds Met: {quality.get('thresholds_met', False)}")
        print(f"   • Iterations: {status.get('total_iterations', 0)}")

        # Agents executed
        agents_executed = result.get("results", {}).get("agents_executed", [])
        print(f"🤖 Agents Executed: {len(agents_executed)}")
        for agent in agents_executed:
            print(f"   • {agent.replace('_', ' ').title()}")

        # Show sample BDD scenarios if available
        bdd_scenarios = result.get("results", {}).get("bdd_scenarios", {})
        if bdd_scenarios.get("features"):
            print("
🍅 Sample BDD Feature:"            feature = bdd_scenarios["features"][0]
            print(f"Feature: {feature['name']}")
            print(f"Description: {feature['description']}")
            if feature.get("scenarios"):
                scenario = feature["scenarios"][0]
                print(".1f")
                print("📝 Steps:")
                for step in scenario.get("steps", []):
                    print(f"   {step}")

        # Show test generation if available
        test_files = result.get("results", {}).get("test_files", {})
        if test_files.get("files"):
            print("
📝 Generated Test File:"            test_file = test_files["files"][0]
            lines = test_file.get("content", "").split("\n")[:10]  # First 10 lines
            print(f"Test File: {test_file.get('path', 'unknown')}")
            print("Content Preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")

        # Show recommendations
        recommendations = quality.get("recommendations", [])
        if recommendations:
            print("
💡 Recommendations:"            for rec in recommendations[:3]:  # Show first 3
                print(f"   • {rec}")

        print("\n🎯 System Features Demonstrated:")
        print("   ✅ LangChain LLM Integration")
        print("   ✅ Structured Output Processing")
        print("   ✅ BDD Scenario Generation")
        print("   ✅ Python Test Code Creation")
        print("   ✅ Code Quality Review")
        print("   ✅ Iterative Quality Improvement")
        print("   ✅ Error Recovery & Retry Logic")
        print("   ✅ Comprehensive Reporting")

    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("💡 This might be due to:")
        print("   • API key issues")
        print("   • Network connectivity")
        print("   • LangChain configuration")
        print("   • OpenAI API limits or errors")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is valid")
        print("   2. Verify internet connection")
        print("   3. Ensure LangChain dependencies are installed")
        print("   4. Check OpenAI account has sufficient credits")
        print("📈 Quality Scores:")
        print(f"   • BDD Coverage: {result.get('results', {}).get('bdd_scenarios', {}).get('coverage_score', 0):.1f}/10")
        print(f"   • Test Quality: {result.get('results', {}).get('test_files', {}).get('quality_score', 0):.1f}/10")
        print(f"   • Overall Score: {quality.get('overall_score', 0):.1f}/10")
        print(f"   • Thresholds Met: {quality.get('thresholds_met', False)}")
        print(f"   • Iterations: {status.get('total_iterations', 0)}")

        # Agents executed
        agents_executed = result.get("results", {}).get("agents_executed", [])
        print(f"🤖 Agents Executed: {len(agents_executed)}")
        for agent in agents_executed:
            print(f"   • {agent.replace('_', ' ').title()}")

        # Show sample BDD scenarios if available
        bdd_scenarios = result.get("results", {}).get("bdd_scenarios", {})
        if bdd_scenarios.get("features"):
            print("\n🍅 Sample BDD Feature:")
            feature = bdd_scenarios["features"][0]
            print(f"Feature: {feature['name']}")
            print(f"Description: {feature['description']}")
            if feature.get("scenarios"):
                scenario = feature["scenarios"][0]
                print(".1f")
                print("📝 Steps:")
                for step in scenario.get("steps", []):
                    print(f"   {step}")

        # Show test generation if available
        test_files = result.get("results", {}).get("test_files", {})
        if test_files.get("files"):
            print("\n📝 Generated Test File:")
            test_file = test_files["files"][0]
            lines = test_file.get("content", "").split("\n")[:10]  # First 10 lines
            print(f"Test File: {test_file.get('path', 'unknown')}")
            print("Content Preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")

        # Show recommendations
        recommendations = quality.get("recommendations", [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"   • {rec}")

        print("\n🎯 System Features Demonstrated:")
        print("   ✅ LangChain LLM Integration")
        print("   ✅ Structured Output Processing")
        print("   ✅ BDD Scenario Generation")
        print("   ✅ Python Test Code Creation")
        print("   ✅ Code Quality Review")
        print("   ✅ Iterative Quality Improvement")
        print("   ✅ Error Recovery & Retry Logic")
        print("   ✅ Comprehensive Reporting")

    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("💡 This might be due to:")
        print("   • API key issues")
        print("   • Network connectivity")
        print("   • LangChain configuration")
        print("   • OpenAI API limits or errors")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is valid")
        print("   2. Verify internet connection")
        print("   3. Ensure LangChain dependencies are installed")
        print("   4. Check OpenAI account has sufficient credits")
        print("\n🔄 Demo complete - check for any error messages above")
        print(f"   • Test Quality: {result.get('results', {}).get('test_files', {}).get('quality_score', 0):.1f}/10")
        print(f"   • Overall Score: {quality.get('overall_score', 0):.1f}/10")
        print(f"   • Thresholds Met: {quality.get('thresholds_met', False)}")
        print(f"   • Iterations: {status.get('total_iterations', 0)}")

        # Agents executed
        agents_executed = result.get("results", {}).get("agents_executed", [])
        print(f"🤖 Agents Executed: {len(agents_executed)}")
        for agent in agents_executed:
            print(f"   • {agent.replace('_', ' ').title()}")

        # Show sample BDD scenarios if available
        bdd_scenarios = result.get("results", {}).get("bdd_scenarios", {})
        if bdd_scenarios.get("features"):
            print("
🍅 Sample BDD Feature:"            feature = bdd_scenarios["features"][0]
            print(f"Feature: {feature['name']}")
            print(f"Description: {feature['description']}")
            if feature.get("scenarios"):
                scenario = feature["scenarios"][0]
                print(".1f")
                print("📝 Steps:")
                for step in scenario.get("steps", []):
                    print(f"   {step}")

        # Show test generation if available
        test_files = result.get("results", {}).get("test_files", {})
        if test_files.get("files"):
            print("
📝 Generated Test File:"            test_file = test_files["files"][0]
            lines = test_file.get("content", "").split("\n")[:10]  # First 10 lines
            print(f"Test File: {test_file.get('path', 'unknown')}")
            print("Content Preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")

        # Show recommendations
        recommendations = quality.get("recommendations", [])
        if recommendations:
            print("
💡 Recommendations:"            for rec in recommendations[:3]:  # Show first 3
                print(f"   • {rec}")

        print("\n🎯 System Features Demonstrated:")
        print("   ✅ LangChain LLM Integration")
        print("   ✅ Structured Output Processing")
        print("   ✅ BDD Scenario Generation")
        print("   ✅ Python Test Code Creation")
        print("   ✅ Code Quality Review")
        print("   ✅ Iterative Quality Improvement")
        print("   ✅ Error Recovery & Retry Logic")
        print("   ✅ Comprehensive Reporting")

    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("💡 This might be due to:")
        print("   • API key issues")
        print("   • Network connectivity")
        print("   • LangChain configuration")
        print("   • OpenAI API limits or errors")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is valid")
        print("   2. Verify internet connection")
        print("   3. Ensure LangChain dependencies are installed")
        print("   4. Check OpenAI account has sufficient credits")

if __name__ == "__main__":
    print("🤖 MCP QA Orchestration System - Phase 2 Demo\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python demo.py")
        print("\nRequirements:")
        print("• Python 3.8+")
        print("• LangChain dependencies (pip install -r requirements.txt)")
        print("• OpenAI API key (export OPENAI_API_KEY=your-key)")
        print("\nThis demo showcases:")
        print("• LangChain-powered AI agents")
        print("• BDD scenario generation")
        print("• Python test code creation")
        print("• Quality assessment and iteration")
        sys.exit(0)

    # Run the demo
    asyncio.run(run_demo())
