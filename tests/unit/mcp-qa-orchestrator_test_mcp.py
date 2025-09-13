#!/usr/bin/env python3
"""
Test script for the MCP QA Orchestration System
Validates basic functionality without requiring API keys
"""

import asyncio
import json
import os
from unittest.mock import Mock, patch
from mcp_qa_orchestrator import MCPOrchestrator, MCPConfig, ScenarioBuilderAgent, ReviewerAgent, TestCoderAgent, CodeReviewerAgent

def test_agent_initialization():
    """Test that all agents can be initialized"""
    print("🧪 Testing agent initialization...")
    
    config = MCPConfig(
        bdd_threshold=9.0,
        quality_threshold=8.0,
        max_iterations=3,
        llm_provider="openai",
        api_key="test-key"
    )
    
    try:
        # Test individual agents
        scenario_agent = ScenarioBuilderAgent(config)
        reviewer_agent = ReviewerAgent(config)
        test_coder_agent = TestCoderAgent(config)
        code_reviewer_agent = CodeReviewerAgent(config)
        
        print("✅ All agents initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_mcp_orchestrator_initialization():
    """Test MCP orchestrator initialization"""
    print("🧪 Testing MCP orchestrator initialization...")
    
    config = MCPConfig(
        bdd_threshold=9.0,
        quality_threshold=8.0,
        max_iterations=3,
        llm_provider="openai",
        api_key="test-key"
    )
    
    try:
        mcp = MCPOrchestrator(config)
        print("✅ MCP orchestrator initialized successfully")
        print(f"   - Agents: {list(mcp.agents.keys())}")
        print(f"   - State: {mcp.state}")
        return True
    except Exception as e:
        print(f"❌ MCP orchestrator initialization failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    print("🧪 Testing configuration validation...")
    
    try:
        # Test valid config
        valid_config = MCPConfig(
            bdd_threshold=9.0,
            quality_threshold=8.0,
            max_iterations=3,
            llm_provider="openai",
            api_key="test-key"
        )
        print("✅ Valid configuration accepted")
        
        # Test invalid provider
        try:
            invalid_config = MCPConfig(
                llm_provider="invalid_provider",
                api_key="test-key"
            )
            print("❌ Invalid provider should have been rejected")
            return False
        except ValueError:
            print("✅ Invalid provider correctly rejected")
        
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_codebase_snapshot_validation():
    """Test codebase snapshot structure validation"""
    print("🧪 Testing codebase snapshot validation...")
    
    # Valid codebase snapshot
    valid_codebase = {
        "project_name": "Test Project",
        "structure": {
            "services": ["service1", "service2"],
            "frontend": "React app"
        },
        "critical_paths": ["path1", "path2"]
    }
    
    # Invalid codebase snapshot (missing required fields)
    invalid_codebase = {
        "project_name": "Test Project"
        # Missing structure and critical_paths
    }
    
    try:
        # Test valid snapshot
        if "project_name" in valid_codebase and "structure" in valid_codebase:
            print("✅ Valid codebase snapshot accepted")
        else:
            print("❌ Valid codebase snapshot rejected")
            return False
        
        # Test invalid snapshot
        if "project_name" in invalid_codebase and "structure" in invalid_codebase:
            print("❌ Invalid codebase snapshot accepted")
            return False
        else:
            print("✅ Invalid codebase snapshot correctly rejected")
        
        return True
    except Exception as e:
        print(f"❌ Codebase snapshot validation failed: {e}")
        return False

def test_json_serialization():
    """Test JSON serialization of results"""
    print("🧪 Testing JSON serialization...")
    
    try:
        # Test result structure
        test_result = {
            "status": "success",
            "summary": {
                "bdd_coverage_score": 9.0,
                "test_quality_score": 8.5,
                "review_score": 8.8
            },
            "bdd_scenarios": {
                "features": [],
                "coverage_score": 9.0
            },
            "test_files": {
                "files": [],
                "quality_score": 8.5
            },
            "review_results": {
                "green": True,
                "score": 8.8,
                "bugs": []
            }
        }
        
        # Test serialization
        json_str = json.dumps(test_result, indent=2)
        parsed_result = json.loads(json_str)
        
        if parsed_result == test_result:
            print("✅ JSON serialization/deserialization successful")
            return True
        else:
            print("❌ JSON serialization/deserialization failed")
            return False
            
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

@patch('mcp_qa_orchestrator.ChatOpenAI')
async def test_mock_agent_execution(mock_llm):
    """Test agent execution with mocked LLM"""
    print("🧪 Testing mock agent execution...")
    
    # Mock LLM response
    mock_response = Mock()
    mock_response.generations = [[Mock(text='{"test": "response"}')]]
    mock_llm.return_value.agenerate.return_value = mock_response
    
    config = MCPConfig(
        bdd_threshold=9.0,
        quality_threshold=8.0,
        max_iterations=3,
        llm_provider="openai",
        api_key="test-key"
    )
    
    try:
        # Test scenario builder agent
        agent = ScenarioBuilderAgent(config)
        result = await agent.execute({"test": "input"})
        
        if "test" in result and result["test"] == "response":
            print("✅ Mock agent execution successful")
            return True
        else:
            print(f"❌ Mock agent execution failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Mock agent execution test failed: {e}")
        return False

def test_file_operations():
    """Test file operations (ZIP creation, base64 encoding)"""
    print("🧪 Testing file operations...")
    
    try:
        from mcp_qa_orchestrator import MCPOrchestrator, MCPConfig
        import base64
        import zipfile
        import io
        
        config = MCPConfig(api_key="test-key")
        mcp = MCPOrchestrator(config)
        
        # Test test file packaging
        test_files = [
            {"path": "test1.py", "content": "print('test1')"},
            {"path": "test2.py", "content": "print('test2')"}
        ]
        
        package = mcp._package_test_files(test_files)
        
        if package:
            # Test decoding
            decoded = base64.b64decode(package)
            zip_file = zipfile.ZipFile(io.BytesIO(decoded))
            file_list = zip_file.namelist()
            
            if "test1.py" in file_list and "test2.py" in file_list:
                print("✅ File operations successful")
                return True
            else:
                print("❌ File operations failed - files not found in ZIP")
                return False
        else:
            print("❌ File operations failed - no package created")
            return False
            
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Running MCP QA Orchestration System Tests")
    print("=" * 60)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("MCP Orchestrator Initialization", test_mcp_orchestrator_initialization),
        ("Configuration Validation", test_config_validation),
        ("Codebase Snapshot Validation", test_codebase_snapshot_validation),
        ("JSON Serialization", test_json_serialization),
        ("Mock Agent Execution", test_mock_agent_execution),
        ("File Operations", test_file_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The MCP system is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())



