# Cline Phase 1 Implementation Prompt

## 🎯 Task: Implement Core MCP Orchestrator

**Agent**: Cline (grok-code-fast-1 model)  
**Phase**: 1 of 4  
**Priority**: Critical Foundation  

## 📋 Implementation Requirements

### File to Create: `mcp_qa_orchestrator.py`

**Location**: `mcp-qa-orchestrator/mcp_qa_orchestrator.py`

### Core Architecture

Implement a complete MCP (Master Control Program) orchestration system with the following structure:

```python
# Required imports and dependencies
import asyncio
import json
import base64
import zipfile
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 1. Data Structures

#### AgentState Enum
```python
class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
```

#### MCPConfig Dataclass
```python
@dataclass
class MCPConfig:
    """Master Control Program configuration"""
    bdd_threshold: float = 9.0
    quality_threshold: float = 8.0
    max_iterations: int = 3
    max_bugs: int = 3
    llm_provider: str = "openai"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.llm_provider not in ["openai", "grok"]:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        if not self.api_key:
            raise ValueError("API key is required")
```

#### AgentConfig Dataclass
```python
@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    model: str
    temperature: float
    max_tokens: int
    prompt_template: str
    timeout: int = 30
    retry_attempts: int = 3
```

### 2. Base Agent Class

```python
class BaseAgent(ABC):
    """Abstract base class for all MCP agents"""
    
    def __init__(self, config: MCPConfig, agent_config: AgentConfig):
        self.config = config
        self.agent_config = agent_config
        self.state = AgentState.IDLE
        self.last_result: Optional[Dict[str, Any]] = None
        self.error_count = 0
        self.logger = logging.getLogger(f"agent.{agent_config.name}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic"""
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with error handling and retry logic"""
        self.state = AgentState.RUNNING
        self.logger.info(f"Starting {self.agent_config.name} agent")
        
        for attempt in range(self.agent_config.retry_attempts):
            try:
                result = await asyncio.wait_for(
                    self.execute(input_data),
                    timeout=self.agent_config.timeout
                )
                self.state = AgentState.COMPLETED
                self.last_result = result
                self.logger.info(f"{self.agent_config.name} completed successfully")
                return result
                
            except asyncio.TimeoutError:
                self.logger.error(f"{self.agent_config.name} timed out (attempt {attempt + 1})")
                self.error_count += 1
                
            except Exception as e:
                self.logger.error(f"{self.agent_config.name} failed: {str(e)} (attempt {attempt + 1})")
                self.error_count += 1
                
            if attempt < self.agent_config.retry_attempts - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.state = AgentState.FAILED
        self.logger.error(f"{self.agent_config.name} failed after {self.agent_config.retry_attempts} attempts")
        raise Exception(f"Agent {self.agent_config.name} failed after {self.agent_config.retry_attempts} attempts")
    
    def reset(self):
        """Reset agent state"""
        self.state = AgentState.IDLE
        self.last_result = None
        self.error_count = 0
```

### 3. MCP Orchestrator Class

```python
class MCPOrchestrator:
    """Master Control Program orchestrator"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.state = AgentState.IDLE
        self.iteration_count = 0
        self.results: Dict[str, Any] = {}
        self.logger = logging.getLogger("mcp_orchestrator")
        
        # Initialize agents (will be implemented in Phase 2)
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents (placeholder for Phase 2)"""
        # This will be implemented in Phase 2
        pass
    
    async def spin_up_mcp(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration method"""
        self.logger.info("Starting MCP orchestration")
        self.state = AgentState.RUNNING
        
        try:
            # Validate codebase snapshot
            self._validate_codebase(codebase)
            
            # Run orchestration loop
            while self.iteration_count < self.config.max_iterations:
                self.iteration_count += 1
                self.logger.info(f"Starting iteration {self.iteration_count}")
                
                # Run agent pipeline
                iteration_result = await self._run_agent_pipeline(codebase)
                
                # Check quality thresholds
                if self._check_quality_thresholds(iteration_result):
                    self.logger.info("Quality thresholds met, stopping iteration")
                    break
                
                # Check if we should continue
                if self.iteration_count >= self.config.max_iterations:
                    self.logger.warning("Maximum iterations reached")
                    break
            
            # Generate final report
            final_result = self._generate_final_report()
            self.state = AgentState.COMPLETED
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"MCP orchestration failed: {str(e)}")
            self.state = AgentState.FAILED
            raise
    
    def _validate_codebase(self, codebase: Dict[str, Any]):
        """Validate codebase snapshot structure"""
        required_fields = ["project_name", "structure"]
        for field in required_fields:
            if field not in codebase:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(codebase["structure"], dict):
            raise ValueError("Structure must be a dictionary")
        
        self.logger.info(f"Codebase validated for project: {codebase['project_name']}")
    
    async def _run_agent_pipeline(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete agent pipeline"""
        # This will be implemented in Phase 2
        # For now, return a placeholder result
        return {
            "bdd_scenarios": {"coverage_score": 8.5, "features": []},
            "test_files": {"quality_score": 8.0, "files": []},
            "review_results": {"score": 8.2, "green": True, "bugs": []}
        }
    
    def _check_quality_thresholds(self, result: Dict[str, Any]) -> bool:
        """Check if quality thresholds are met"""
        bdd_score = result.get("bdd_scenarios", {}).get("coverage_score", 0)
        test_score = result.get("test_files", {}).get("quality_score", 0)
        review_score = result.get("review_results", {}).get("score", 0)
        bugs_count = len(result.get("review_results", {}).get("bugs", []))
        
        bdd_passes = bdd_score >= self.config.bdd_threshold
        quality_passes = test_score >= self.config.quality_threshold
        review_passes = (review_score >= self.config.quality_threshold and 
                        bugs_count <= self.config.max_bugs)
        
        return bdd_passes and quality_passes and review_passes
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final orchestration report"""
        return {
            "status": "success" if self.state == AgentState.COMPLETED else "failed",
            "summary": {
                "total_iterations": self.iteration_count,
                "final_state": self.state.value,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.results
        }
    
    def _package_test_files(self, test_files: List[Dict[str, str]]) -> str:
        """Package test files into base64-encoded ZIP"""
        if not test_files:
            return ""
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for test_file in test_files:
                zip_file.writestr(test_file["path"], test_file["content"])
        
        zip_buffer.seek(0)
        return base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {name: agent.state.value for name, agent in self.agents.items()}
    
    def reset(self):
        """Reset orchestrator state"""
        self.state = AgentState.IDLE
        self.iteration_count = 0
        self.results = {}
        for agent in self.agents.values():
            agent.reset()
```

### 4. Quality Threshold Management

```python
class QualityThresholds:
    """Quality threshold management"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
    
    def calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        bdd_score = results.get("bdd_scenarios", {}).get("coverage_score", 0)
        test_score = results.get("test_files", {}).get("quality_score", 0)
        review_score = results.get("review_results", {}).get("score", 0)
        
        # Weighted average
        return (bdd_score * 0.3 + test_score * 0.4 + review_score * 0.3)
    
    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        bdd_score = results.get("bdd_scenarios", {}).get("coverage_score", 0)
        test_score = results.get("test_files", {}).get("quality_score", 0)
        review_score = results.get("review_results", {}).get("score", 0)
        bugs = results.get("review_results", {}).get("bugs", [])
        
        if bdd_score < self.config.bdd_threshold:
            recommendations.append(f"Improve BDD coverage (current: {bdd_score:.1f}, target: {self.config.bdd_threshold})")
        
        if test_score < self.config.quality_threshold:
            recommendations.append(f"Improve test quality (current: {test_score:.1f}, target: {self.config.quality_threshold})")
        
        if review_score < self.config.quality_threshold:
            recommendations.append(f"Address review issues (current: {review_score:.1f}, target: {self.config.quality_threshold})")
        
        if len(bugs) > self.config.max_bugs:
            recommendations.append(f"Fix identified bugs (current: {len(bugs)}, max: {self.config.max_bugs})")
        
        return recommendations
```

### 5. Error Recovery System

```python
class ErrorRecovery:
    """Error recovery and retry management"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}
    
    async def execute_with_recovery(self, func, *args, **kwargs):
        """Execute function with automatic retry and recovery"""
        func_name = func.__name__
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.retry_counts[func_name] = self.retry_counts.get(func_name, 0) + 1
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise e
    
    def get_retry_stats(self) -> Dict[str, int]:
        """Get retry statistics"""
        return self.retry_counts.copy()
```

## 🧪 Testing Requirements

### Unit Tests
Create comprehensive unit tests for:
- MCPConfig validation
- BaseAgent error handling
- MCPOrchestrator state management
- QualityThresholds calculations
- ErrorRecovery retry logic

### Integration Tests
Test the complete orchestration flow with:
- Valid codebase snapshots
- Invalid codebase snapshots
- Error scenarios
- Timeout scenarios

## ✅ Success Criteria

1. **Code Quality**:
   - [ ] All classes properly defined with type hints
   - [ ] Comprehensive error handling
   - [ ] Async/await pattern throughout
   - [ ] Proper logging implementation

2. **Functionality**:
   - [ ] MCPConfig validation working
   - [ ] BaseAgent abstract class implemented
   - [ ] MCPOrchestrator state machine working
   - [ ] Quality threshold checking working
   - [ ] File packaging working

3. **Testing**:
   - [ ] Unit tests for all classes
   - [ ] Integration tests for orchestration
   - [ ] Error scenario testing
   - [ ] Performance testing

4. **Documentation**:
   - [ ] Comprehensive docstrings
   - [ ] Type hints for all methods
   - [ ] Usage examples in comments

## 🚀 Implementation Notes

- **Follow Alicia's patterns**: Use similar error handling and logging patterns
- **Async-first**: All operations should be async/await
- **Type safety**: Use comprehensive type hints
- **Error resilience**: Implement proper retry and recovery logic
- **Performance**: Optimize for speed and memory usage
- **Maintainability**: Clear separation of concerns

## 🔗 Integration Points

This Phase 1 implementation should be ready to integrate with:
- **Phase 2**: LangChain agent implementations
- **Phase 3**: Configuration and documentation
- **Phase 4**: Testing and validation

The system should be fully functional after Phase 1, with subsequent phases adding the actual agent implementations and polish.

---

**Ready for Cline to implement!** 🚀
