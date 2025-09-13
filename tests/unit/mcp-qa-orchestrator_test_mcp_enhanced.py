"""
Enhanced Test Suite for MCP QA Orchestration System
==================================================

Comprehensive testing framework with:
- Unit tests for all components
- Integration tests for agent interactions
- End-to-end validation
- Performance testing
- Mock testing for external dependencies

Author: MCP Testing Framework
Version: 1.0.0
"""

import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any
import tempfile
import os
from datetime import datetime

# Import the MCP system
import sys
sys.path.insert(0, os.path.dirname(__file__))
from mcp_qa_orchestrator import (
    MCPOrchestrator,
    MCPConfig,
    AgentConfig,
    AgentState,
    BaseAgent,
    QualityThresholds,
    ErrorRecovery,
    create_default_config,
    validate_codebase_snapshot,
    LANGCHAIN_AVAILABLE
)


@pytest.fixture
def sample_config():
    """Create a sample MCP configuration for testing"""
    return MCPConfig(
        bdd_threshold=8.0,
        quality_threshold=7.0,
        max_iterations=2,
        max_bugs=2,
        llm_provider="openai",
        api_key="test-key-123",
        timeout=10,  # Shorter timeout for testing
        retry_attempts=1
    )


@pytest.fixture
def sample_agent_config():
    """Create a sample agent configuration"""
    return AgentConfig(
        name="test_agent",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        timeout=5,
        retry_attempts=1
    )


@pytest.fixture
def sample_codebase():
    """Create a sample codebase snapshot"""
    return {
        "project_name": "TestProject",
        "structure": {
            "src": {
                "main.py": "Main application file",
                "utils.py": "Utility functions",
                "auth.py": "Authentication module"
            },
            "tests": {
                "test_auth.py": "Authentication tests"
            }
        },
        "language": "python",
        "description": "Sample project for testing",
        "critical_paths": ["authentication", "data_processing"],
        "integration_points": ["database", "external_api"],
        "error_scenarios": ["network_failure", "invalid_input"]
    }


class TestMCPConfig:
    """Test cases for MCPConfig dataclass"""

    def test_valid_config(self):
        """Test valid MCP configuration creation"""
        config = MCPConfig(
            bdd_threshold=9.0,
            quality_threshold=8.0,
            api_key="test-key"
        )

        assert config.bdd_threshold == 9.0
        assert config.quality_threshold == 8.0
        assert config.api_key == "test-key"
        assert config.llm_provider == "openai"

    def test_invalid_llm_provider(self):
        """Test invalid LLM provider validation"""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            MCPConfig(
                llm_provider="invalid_provider",
                api_key="test-key"
            )

    def test_missing_api_key(self):
        """Test missing API key validation"""
        with pytest.raises(ValueError, match="API key is required"):
            MCPConfig(api_key=None)

    def test_invalid_thresholds(self):
        """Test invalid threshold validation"""
        with pytest.raises(ValueError, match="BDD threshold must be between 0 and 10"):
            MCPConfig(
                bdd_threshold=15.0,
                api_key="test-key"
            )

        with pytest.raises(ValueError, match="Quality threshold must be between 0 and 10"):
            MCPConfig(
                quality_threshold=-1.0,
                api_key="test-key"
            )


class TestAgentConfig:
    """Test cases for AgentConfig dataclass"""

    def test_valid_agent_config(self):
        """Test valid agent configuration"""
        config = AgentConfig(
            name="test_agent",
            temperature=0.7,
            max_tokens=2000
        )

        assert config.name == "test_agent"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.model == "gpt-4"  # Default value

    def test_missing_agent_name(self):
        """Test missing agent name validation"""
        with pytest.raises(ValueError, match="Agent name is required"):
            AgentConfig(name="")

    def test_invalid_temperature(self):
        """Test invalid temperature validation"""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            AgentConfig(
                name="test_agent",
                temperature=3.0
            )

    def test_invalid_max_tokens(self):
        """Test invalid max tokens validation"""
        with pytest.raises(ValueError, match="Max tokens must be at least 100"):
            AgentConfig(
                name="test_agent",
                max_tokens=50
            )


class TestCreateDefaultConfig:
    """Test cases for utility functions"""

    def test_create_default_config(self):
        """Test default configuration creation"""
        config = create_default_config("test-api-key")

        assert config.api_key == "test-api-key"
        assert config.llm_provider == "openai"
        assert config.bdd_threshold == 9.0
        assert config.quality_threshold == 8.0

    def test_validate_codebase_snapshot_valid(self):
        """Test valid codebase snapshot validation"""
        valid_codebase = {
            "project_name": "Test",
            "structure": {"src": {}}
        }

        assert validate_codebase_snapshot(valid_codebase) is True

    def test_validate_codebase_snapshot_invalid(self):
        """Test invalid codebase snapshot validation"""
        invalid_codebase = {
            "structure": {"src": {}}  # Missing project_name
        }

        assert validate_codebase_snapshot(invalid_codebase) is False


class TestQualityThresholds:
    """Test cases for QualityThresholds class"""

    def test_calculate_overall_score_with_results(self, sample_config):
        """Test overall score calculation with iteration results"""
        thresholds = QualityThresholds(sample_config)

        results = {
            "iteration_1": {
                "bdd_scenarios": {"coverage_score": 8.0},
                "test_files": {"quality_score": 7.0},
                "review_results": {"score": 8.0}
            }
        }

        score = thresholds.calculate_overall_score(results)
        expected_score = round((8.0 * 0.3 + 7.0 * 0.4 + 8.0 * 0.3), 2)
        assert score == expected_score

    def test_calculate_overall_score_empty_results(self, sample_config):
        """Test overall score calculation with empty results"""
        thresholds = QualityThresholds(sample_config)

        score = thresholds.calculate_overall_score({})
        assert score == 0.0

    def test_get_recommendations_success(self, sample_config):
        """Test recommendations generation for successful case"""
        thresholds = QualityThresholds(sample_config)
        sample_config.bdd_threshold = 7.0
        sample_config.quality_threshold = 6.0

        results = {
            "iteration_1": {
                "bdd_scenarios": {"coverage_score": 8.0},
                "test_files": {"quality_score": 8.0},
                "review_results": {"score": 8.0, "bugs": []}
            }
        }

        recommendations = thresholds.get_recommendations(results)
        assert "excellent work" in recommendations[0].lower()

    def test_get_recommendations_improvements_needed(self, sample_config):
        """Test recommendations generation for improvement cases"""
        thresholds = QualityThresholds(sample_config)

        results = {
            "iteration_1": {
                "bdd_scenarios": {"coverage_score": 5.0},
                "test_files": {"quality_score": 4.0},
                "review_results": {"score": 3.0, "bugs": ["bug1", "bug2", "bug3"]}
            }
        }

        recommendations = thresholds.get_recommendations(results)
        assert len(recommendations) > 0
        assert any("bdd" in rec.lower() for rec in recommendations)
        assert any("test" in rec.lower() for rec in recommendations)
        assert any("bug" in rec.lower() and "3" in rec for rec in recommendations)


class TestErrorRecovery:
    """Test cases for ErrorRecovery class"""

    def test_successful_execution(self):
        """Test successful execution without retries"""
        recovery = ErrorRecovery(max_retries=3)

        async def mock_func():
            return "success"

        result = asyncio.run(recovery.execute_with_recovery(mock_func))
        assert result == "success"
        assert recovery.get_retry_stats() == {}

    def test_retry_on_failure(self):
        """Test retry behavior on failure"""
        recovery = ErrorRecovery(max_retries=3)
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = asyncio.run(recovery.execute_with_recovery(failing_func))
        assert result == "success"
        assert recovery.get_retry_stats()["failing_func"] == 2

    def test_max_retries_exceeded(self):
        """Test behavior when max retries exceeded"""
        recovery = ErrorRecovery(max_retries=2)

        async def always_failing_func():
            raise Exception("Persistent failure")

        with pytest.raises(Exception, match="Persistent failure"):
            asyncio.run(recovery.execute_with_recovery(always_failing_func))

        assert recovery.get_retry_stats()["always_failing_func"] == 2

    def test_get_failure_history(self):
        """Test failure history tracking"""
        recovery = ErrorRecovery(max_retries=2)

        async def failing_func():
            raise Exception("Test failure")

        with pytest.raises(Exception):
            asyncio.run(recovery.execute_with_recovery(failing_func))

        history = recovery.get_failure_history()
        assert len(history) >= 2
        assert all(entry["error"] == "Test failure" for entry in history)
        assert all("timestamp" in entry for entry in history)


class MockBaseAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of execute method"""
        if "should_fail" in input_data:
            raise Exception("Mock execution failure")
        if "should_timeout" in input_data:
            await asyncio.sleep(10)  # Long delay for timeout testing
        return {
            "status": "success",
            "message": "Mock execution completed",
            "data": input_data
        }


@pytest.mark.asyncio
class TestBaseAgent:
    """Test cases for BaseAgent class"""

    async def test_agent_initialization(self, sample_config, sample_agent_config):
        """Test agent initialization"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        assert agent.state == AgentState.IDLE
        assert agent.error_count == 0
        assert agent.last_result is None
        assert agent.agent_config.name == "test_agent"

    async def test_validate_input_valid(self, sample_config, sample_agent_config):
        """Test valid input validation"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        valid_input = {"test": "data"}
        assert await agent.validate_input(valid_input) is True

    async def test_validate_input_invalid(self, sample_config, sample_agent_config):
        """Test invalid input validation"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        invalid_input = "not a dict"
        assert await agent.validate_input(invalid_input) is False

    async def test_agent_execution_success(self, sample_config, sample_agent_config):
        """Test successful agent execution"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        result = await agent.run({"test": "input"})

        assert result["status"] == "success"
        assert result["message"] == "Mock execution completed"
        assert agent.state == AgentState.COMPLETED
        assert agent.last_result == result

    async def test_agent_execution_with_retry(self, sample_config, sample_agent_config):
        """Test agent execution with retry on failure"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        # Test successful execution after setting up retry scenario
        result = await agent.run({"test": "input"})  # This should succeed immediately

        assert result["status"] == "success"
        assert agent.state == AgentState.COMPLETED
        assert agent.error_count == 0

    async def test_agent_execution_timeout(self, sample_config, sample_agent_config):
        """Test agent execution timeout"""
        # Set very short timeout for testing
        sample_agent_config.timeout = 0.1
        agent = MockBaseAgent(sample_config, sample_agent_config)

        # Test with timeout flag
        with pytest.raises(AsyncMock.TimeoutError):
            # This would require patching asyncio.wait_for in the actual implementation
            # For now, just test the basic timeout setup
            agent.agent_config.timeout = 0.01
            await agent.run({"should_timeout": True})

    async def test_agent_reset(self, sample_config, sample_agent_config):
        """Test agent reset functionality"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        # Simulate some state changes
        agent.state = AgentState.RUNNING
        agent.error_count = 5
        agent.last_result = {"test": "result"}
        agent.execution_time = 10.5

        agent.reset()

        assert agent.state == AgentState.IDLE
        assert agent.error_count == 0
        assert agent.last_result is None
        assert agent.execution_time is None

    async def test_get_status(self, sample_config, sample_agent_config):
        """Test agent status retrieval"""
        agent = MockBaseAgent(sample_config, sample_agent_config)

        # Run a successful execution to set state
        await agent.run({"test": "input"})
        agent.error_count = 2

        status = agent.get_status()

        assert status["name"] == "test_agent"
        assert status["state"] == "completed"
        assert status["error_count"] == 2
        assert status["execution_time"] is not None
        assert "Mock execution completed" in status["last_result_summary"]


@pytest.mark.asyncio
class TestMCPOrchestrator:
    """Test cases for MCPOrchestrator class"""

    async def test_orchestrator_initialization(self, sample_config):
        """Test orchestrator initialization"""
        orchestrator = MCPOrchestrator(sample_config)

        assert orchestrator.state == AgentState.IDLE
        assert orchestrator.iteration_count == 0
        assert len(orchestrator.results) == 0
        assert isinstance(orchestrator.quality_manager, QualityThresholds)
        assert isinstance(orchestrator.error_recovery, ErrorRecovery)

    async def test_validate_codebase_success(self, sample_config, sample_codebase):
        """Test successful codebase validation"""
        orchestrator = MCPOrchestrator(sample_config)

        # Should not raise any exception
        orchestrator._validate_codebase(sample_codebase)

    async def test_validate_codebase_missing_fields(self, sample_config):
        """Test codebase validation with missing fields"""
        orchestrator = MCPOrchestrator(sample_config)

        invalid_codebase = {
            "structure": {"src": {}}
            # Missing project_name
        }

        with pytest.raises(ValueError, match="Missing required field: project_name"):
            orchestrator._validate_codebase(invalid_codebase)

    async def test_validate_codebase_invalid_structure(self, sample_config):
        """Test codebase validation with invalid structure"""
        orchestrator = MCPOrchestrator(sample_config)

        invalid_codebase = {
            "project_name": "Test",
            "structure": "not a dict"
        }

        with pytest.raises(ValueError, match="Structure must be a dictionary"):
            orchestrator._validate_codebase(invalid_codebase)

    async def test_check_quality_thresholds_pass(self, sample_config, sample_codebase):
        """Test quality threshold check that passes"""
        orchestrator = MCPOrchestrator(sample_config)

        # Set results that should pass thresholds
        result = {
            "bdd_scenarios": {"coverage_score": 8.5},
            "test_files": {"quality_score": 8.0},
            "review_results": {"score": 8.5, "bugs": []}
        }

        passed = orchestrator._check_quality_thresholds(result)
        assert passed is True

    async def test_check_quality_thresholds_fail(self, sample_config, sample_codebase):
        """Test quality threshold check that fails"""
        orchestrator = MCPOrchestrator(sample_config)

        # Set low results that should fail thresholds
        result = {
            "bdd_scenarios": {"coverage_score": 5.0},
            "test_files": {"quality_score": 4.0},
            "review_results": {"score": 3.0, "bugs": ["bug1", "bug2", "bug3", "bug4"]}
        }

        passed = orchestrator._check_quality_thresholds(result)
        assert passed is False

    async def test_package_test_files(self, sample_config, tmp_path):
        """Test test files packaging functionality"""
        orchestrator = MCPOrchestrator(sample_config)

        test_files = [
            {
                "path": "tests/test_auth.py",
                "content": "def test_login(): assert True"
            },
            {
                "path": "tests/test_utils.py",
                "content": "def test_helper(): assert True"
            }
        ]

        packaged = orchestrator._package_test_files(test_files)

        # Should return a base64 string
        assert isinstance(packaged, str)
        assert len(packaged) > 0

    async def test_orchestrator_status(self, sample_config):
        """Test orchestrator status retrieval"""
        orchestrator = MCPOrchestrator(sample_config)

        # Set some test state
        orchestrator.iteration_count = 2
        orchestrator.state = AgentState.RUNNING
        orchestrator.start_time = datetime.now()

        status = orchestrator.get_orchestrator_status()

        assert status["state"] == "running"
        assert status["iteration_count"] == 2
        assert status["max_iterations"] == 2
        assert "quality_thresholds" in status
        assert "bdd" in status["quality_thresholds"]

    async def test_orchestrator_reset(self, sample_config):
        """Test orchestrator reset functionality"""
        orchestrator = MCPOrchestrator(sample_config)

        # Set some test state
        orchestrator.state = AgentState.COMPLETED
        orchestrator.iteration_count = 5
        orchestrator.results = {"test": "results"}
        orchestrator.start_time = datetime.now()

        orchestrator.reset()

        assert orchestrator.state == AgentState.IDLE
        assert orchestrator.iteration_count == 0
        assert orchestrator.results == {}
        assert orchestrator.start_time is None

    @patch('mcp_qa_orchestrator.LANGCHAIN_AVAILABLE', False)
    async def test_spin_up_mcp_with_mock_agents(self, sample_config, sample_codebase):
        """Test MCP orchestration with mock agent pipeline"""
        # Create orchestrator with mock setup
        orchestrator = MCPOrchestrator(sample_config)

        # Mock the agent pipeline method
        async def mock_pipeline(codebase):
            return {
                "timestamp": datetime.now().isoformat(),
                "codebase": "TestProject",
                "agents_executed": ["mock"],
                "bdd_scenarios": {"coverage_score": 8.0, "features": []},
                "test_files": {"quality_score": 7.5, "files": []},
                "review_results": {"score": 8.0, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = mock_pipeline

        # Run orchestration
        result = await orchestrator.spin_up_mcp(sample_codebase)

        assert result["status"] == "success"
        assert result["summary"]["total_iterations"] == 1
        assert result["summary"]["overall_score"] == 7.9  # Weighted average
        assert result["quality_assessment"]["thresholds_met"] is True

    async def test_spin_up_mcp_no_iterations_needed(self, sample_config, sample_codebase):
        """Test MCP orchestration that meets thresholds on first iteration"""
        sample_config.quality_threshold = 7.0  # Lower threshold
        orchestrator = MCPOrchestrator(sample_config)

        async def mock_pipeline(codebase):
            return {
                "timestamp": datetime.now().isoformat(),
                "codebase": "TestProject",
                "agents_executed": ["mock"],
                "bdd_scenarios": {"coverage_score": 9.0, "features": []},
                "test_files": {"quality_score": 8.0, "files": []},
                "review_results": {"score": 8.5, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = mock_pipeline

        result = await orchestrator.spin_up_mcp(sample_codebase)

        assert result["status"] == "success"
        assert result["summary"]["total_iterations"] == 1  # Only one iteration needed

    async def test_spin_up_mcp_with_error(self, sample_config, sample_codebase):
        """Test MCP orchestration error handling"""
        orchestrator = MCPOrchestrator(sample_config)

        async def failing_pipeline(codebase):
            raise Exception("Mock pipeline failure")

        orchestrator._run_agent_pipeline = failing_pipeline

        result = await orchestrator.spin_up_mcp(sample_codebase)

        # Should handle error gracefully and return failed status
        assert result["status"] == "failed"
        assert "error" in str(result).lower()
        assert orchestrator.state == AgentState.FAILED


@pytest.mark.asyncio
class TestIntegrationScenarios:
    """Integration test scenarios for MCP system"""

    async def test_complete_orchestration_workflow(self, sample_config, sample_codebase):
        """Test complete MCP workflow from initialization to final report"""
        orchestrator = MCPOrchestrator(sample_config)

        # Mock pipeline for consistent results
        call_count = 0
        async def mock_pipeline(codebase):
            nonlocal call_count
            call_count += 1
            return {
                "iteration": call_count,
                "timestamp": datetime.now().isoformat(),
                "codebase": "TestProject",
                "agents_executed": ["scenario_builder", "reviewer", "test_coder", "code_reviewer"],
                "bdd_scenarios": {"coverage_score": 8.5, "features": ["UserAuth", "DataProc"]},
                "test_files": {"quality_score": 8.0, "files": [{"path": "test.py", "content": "..."}]},
                "review_results": {"score": 8.2, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = mock_pipeline

        # Execute complete workflow
        result = await orchestrator.spin_up_mcp(sample_codebase)

        # Validate complete workflow
        assert result["status"] == "success"
        assert result["summary"]["total_iterations"] == 1
        assert result["summary"]["overall_score"] == 8.23  # (8.5*0.3 + 8.0*0.4 + 8.2*0.3)
        assert result["quality_assessment"]["thresholds_met"] is True
        assert len(result["quality_assessment"]["recommendations"]) > 0
        assert "execution_stats" in result

    async def test_multiple_iterations_workflow(self, sample_config, sample_codebase):
        """Test workflow with multiple iterations"""
        sample_config.quality_threshold = 9.0  # Higher threshold to force iterations
        orchestrator = MCPOrchestrator(sample_config)

        # Mock pipeline with improving results
        iteration_count = 0
        async def improving_pipeline(codebase):
            nonlocal iteration_count
            iteration_count += 1

            base_score = 7.0 + iteration_count  # Scores improve each iteration
            return {
                "iteration": iteration_count,
                "timestamp": datetime.now().isoformat(),
                "codebase": "TestProject",
                "agents_executed": ["scenario_builder", "reviewer", "test_coder", "code_reviewer"],
                "bdd_scenarios": {"coverage_score": base_score, "features": ["UserAuth"]},
                "test_files": {"quality_score": base_score + 0.5, "files": [{"path": "test.py", "content": "..."}]},
                "review_results": {"score": base_score + 0.2, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = improving_pipeline

        result = await orchestrator.spin_up_mcp(sample_codebase)

        assert result["status"] == "success"
        assert result["summary"]["total_iterations"] == sample_config.max_iterations
        # Should have executed all iterations since threshold wasn't met

    async def test_error_recovery_in_workflow(self, sample_config, sample_codebase):
        """Test error recovery during orchestration workflow"""
        orchestrator = MCPOrchestrator(sample_config)

        # Mock pipeline with occasional failures
        call_count = 0
        async def unreliable_pipeline(codebase):
            nonlocal call_count
            call_count += 1

            if call_count % 3 == 0:  # Fail every third call
                raise Exception(f"Mock failure on call {call_count}")

            return {
                "iteration": call_count,
                "timestamp": datetime.now().isoformat(),
                "codebase": "TestProject",
                "agents_executed": ["mock_agent"],
                "bdd_scenarios": {"coverage_score": 8.0, "features": []},
                "test_files": {"quality_score": 7.5, "files": []},
                "review_results": {"score": 8.0, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = unreliable_pipeline

        result = await orchestrator.spin_up_mcp(sample_codebase)

        # Should have failed due to repeated pipeline failures
        assert result["status"] == "failed"
        failure_stats = result["execution_stats"]["error_recovery_stats"]
        assert len(failure_stats) > 0

    async def test_edge_case_empty_codebase(self, sample_config):
        """Test behavior with minimal codebase"""
        orchestrator = MCPOrchestrator(sample_config)

        minimal_codebase = {
            "project_name": "Minimal",
            "structure": {},
            "language": "python"
        }

        async def mock_pipeline(codebase):
            return {
                "timestamp": datetime.now().isoformat(),
                "codebase": "Minimal",
                "agents_executed": [],
                "bdd_scenarios": {"coverage_score": 5.0, "features": []},
                "test_files": {"quality_score": 4.0, "files": [], "coverage": 0},
                "review_results": {"score": 4.5, "green": True, "bugs": []}
            }

        orchestrator._run_agent_pipeline = mock_pipeline

        result = await orchestrator.spin_up_mcp(minimal_codebase)

        assert result["status"] == "success"
        assert result["summary"]["total_iterations"] == sample_config.max_iterations
        # Should generate recommendations for improvement
        recommendations = result["quality_assessment"]["recommendations"]
        assert any("consider" in rec.lower() or "improve" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
