# Cline Phase 2 Implementation Prompt

## 🎯 Task: Implement LangChain Agent System

**Agent**: Cline (grok-code-fast-1 model)  
**Phase**: 2 of 4  
**Priority**: Core Functionality  
**Dependencies**: Phase 1 completed  

## 📋 Implementation Requirements

### File to Extend: `mcp_qa_orchestrator.py`

**Location**: `mcp-qa-orchestrator/mcp_qa_orchestrator.py`

### LangChain Integration

Add the following imports and dependencies to the existing file:

```python
# Add these imports to the existing file
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks import AsyncCallbackHandler
from langchain.schema.output import LLMResult
import openai
from pydantic import BaseModel, Field
```

### 1. LLM Configuration Class

```python
class LLMConfig(BaseModel):
    """LLM configuration for agents"""
    provider: str = Field(default="openai", description="LLM provider")
    model: str = Field(default="gpt-4", description="Model name")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: int = Field(default=2000, description="Maximum tokens to generate")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Base URL for API")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
    class Config:
        extra = "forbid"
```

### 2. LLM Manager Class

```python
class LLMManager:
    """Manages LLM instances and configurations"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = self._create_llm()
        self.logger = logging.getLogger("llm_manager")
    
    def _create_llm(self) -> ChatOpenAI:
        """Create LLM instance based on configuration"""
        try:
            if self.config.provider == "openai":
                return ChatOpenAI(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    openai_api_key=self.config.api_key,
                    openai_api_base=self.config.base_url,
                    request_timeout=self.config.timeout
                )
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
        except Exception as e:
            self.logger.error(f"Failed to create LLM: {str(e)}")
            raise
    
    async def generate_response(self, messages: List[Union[HumanMessage, SystemMessage]]) -> str:
        """Generate response from LLM"""
        try:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    async def generate_structured_response(self, messages: List[Union[HumanMessage, SystemMessage]], 
                                        output_schema: BaseModel) -> Dict[str, Any]:
        """Generate structured response using Pydantic schema"""
        try:
            # Add instruction for JSON output
            json_instruction = HumanMessage(content="Please respond with valid JSON that matches the expected schema.")
            messages.append(json_instruction)
            
            response = await self.generate_response(messages)
            
            # Parse JSON response
            import json
            parsed_response = json.loads(response)
            
            # Validate against schema
            validated_response = output_schema(**parsed_response)
            return validated_response.dict()
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Structured response generation failed: {str(e)}")
            raise
```

### 3. Output Schema Classes

```python
class BDDScenario(BaseModel):
    """BDD scenario structure"""
    name: str = Field(..., description="Scenario name")
    steps: List[str] = Field(..., description="Gherkin steps")
    tags: List[str] = Field(default=[], description="Scenario tags")
    priority: str = Field(default="medium", description="Scenario priority")

class BDDFeature(BaseModel):
    """BDD feature structure"""
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    scenarios: List[BDDScenario] = Field(..., description="Feature scenarios")
    background: Optional[str] = Field(default=None, description="Background steps")

class BDDOutput(BaseModel):
    """BDD generation output"""
    features: List[BDDFeature] = Field(..., description="Generated features")
    coverage_score: float = Field(..., description="Coverage score (0-10)")
    recommendations: List[str] = Field(default=[], description="Improvement recommendations")

class TestFile(BaseModel):
    """Test file structure"""
    path: str = Field(..., description="File path")
    content: str = Field(..., description="File content")
    test_count: int = Field(..., description="Number of test cases")
    coverage_estimate: float = Field(..., description="Estimated coverage")

class TestOutput(BaseModel):
    """Test generation output"""
    files: List[TestFile] = Field(..., description="Generated test files")
    quality_score: float = Field(..., description="Quality score (0-10)")
    recommendations: List[str] = Field(default=[], description="Improvement recommendations")

class BugReport(BaseModel):
    """Bug report structure"""
    issue: str = Field(..., description="Issue description")
    severity: str = Field(..., description="Severity level")
    location: str = Field(..., description="File/line location")
    suggestion: str = Field(..., description="Fix suggestion")

class ReviewOutput(BaseModel):
    """Code review output"""
    score: float = Field(..., description="Review score (0-10)")
    green: bool = Field(..., description="Whether tests pass")
    bugs: List[BugReport] = Field(default=[], description="Identified bugs")
    false_positives: List[str] = Field(default=[], description="False positive issues")
    recommendations: List[str] = Field(default=[], description="Improvement recommendations")
```

### 4. Scenario Builder Agent

```python
class ScenarioBuilderAgent(BaseAgent):
    """Agent for generating BDD scenarios"""
    
    def __init__(self, config: MCPConfig):
        agent_config = AgentConfig(
            name="scenario_builder",
            model="gpt-4",
            temperature=0.7,
            max_tokens=3000,
            prompt_template=self._get_prompt_template()
        )
        super().__init__(config, agent_config)
        
        # Create LLM manager
        llm_config = LLMConfig(
            provider=config.llm_provider,
            model="gpt-4",
            temperature=0.7,
            max_tokens=3000,
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.llm_manager = LLMManager(llm_config)
    
    def _get_prompt_template(self) -> str:
        """Get the prompt template for scenario building"""
        return """
You are an expert BDD scenario builder. Your task is to analyze a codebase and generate comprehensive BDD scenarios in Gherkin format.

Codebase Information:
- Project: {project_name}
- Architecture: {architecture}
- Structure: {structure}
- Critical Paths: {critical_paths}
- Integration Points: {integration_points}
- Error Scenarios: {error_scenarios}

Requirements:
1. Generate BDD scenarios for all critical paths
2. Cover happy path, edge cases, and error scenarios
3. Use proper Gherkin syntax (Given/When/Then)
4. Include appropriate tags and priorities
5. Ensure scenarios are testable and specific
6. Consider integration points and external dependencies

Output Format:
- Return valid JSON matching the BDDOutput schema
- Include coverage score (0-10) based on completeness
- Provide recommendations for improvement

Focus on:
- User authentication and authorization
- Data validation and processing
- Error handling and edge cases
- Integration with external services
- Performance and scalability scenarios
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scenario building"""
        try:
            # Prepare input data
            codebase = input_data.get("codebase", {})
            
            # Create messages
            system_message = SystemMessage(content=self._get_prompt_template())
            human_message = HumanMessage(content=f"""
Please analyze this codebase and generate BDD scenarios:

Project: {codebase.get('project_name', 'Unknown')}
Architecture: {codebase.get('architecture', 'Not specified')}
Structure: {json.dumps(codebase.get('structure', {}), indent=2)}
Critical Paths: {codebase.get('critical_paths', [])}
Integration Points: {codebase.get('integration_points', [])}
Error Scenarios: {codebase.get('error_scenarios', [])}
""")
            
            # Generate response
            result = await self.llm_manager.generate_structured_response(
                [system_message, human_message],
                BDDOutput
            )
            
            self.logger.info(f"Generated {len(result['features'])} BDD features")
            return result
            
        except Exception as e:
            self.logger.error(f"Scenario building failed: {str(e)}")
            raise
```

### 5. Reviewer Agent

```python
class ReviewerAgent(BaseAgent):
    """Agent for reviewing BDD scenarios"""
    
    def __init__(self, config: MCPConfig):
        agent_config = AgentConfig(
            name="reviewer",
            model="gpt-4",
            temperature=0.3,
            max_tokens=2000,
            prompt_template=self._get_prompt_template()
        )
        super().__init__(config, agent_config)
        
        # Create LLM manager
        llm_config = LLMConfig(
            provider=config.llm_provider,
            model="gpt-4",
            temperature=0.3,
            max_tokens=2000,
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.llm_manager = LLMManager(llm_config)
    
    def _get_prompt_template(self) -> str:
        """Get the prompt template for scenario review"""
        return """
You are an expert BDD scenario reviewer. Your task is to review BDD scenarios for quality, completeness, and testability.

Review Criteria:
1. Scenario clarity and specificity
2. Proper Gherkin syntax and structure
3. Testability and automation potential
4. Coverage of critical paths
5. Edge cases and error scenarios
6. Integration point coverage
7. Business value and user focus

Quality Standards:
- Scenarios should be clear and unambiguous
- Steps should be atomic and testable
- Background steps should be properly used
- Tags should be meaningful and consistent
- Scenarios should cover both happy and error paths

Output Format:
- Return valid JSON matching the BDDOutput schema
- Provide quality score (0-10) based on review
- Include specific recommendations for improvement
- Identify missing scenarios or coverage gaps
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scenario review"""
        try:
            # Get BDD scenarios from input
            bdd_data = input_data.get("bdd_scenarios", {})
            
            # Create messages
            system_message = SystemMessage(content=self._get_prompt_template())
            human_message = HumanMessage(content=f"""
Please review these BDD scenarios:

{json.dumps(bdd_data, indent=2)}

Focus on:
- Quality and clarity of scenarios
- Completeness of coverage
- Testability and automation potential
- Business value and user focus
""")
            
            # Generate response
            result = await self.llm_manager.generate_structured_response(
                [system_message, human_message],
                BDDOutput
            )
            
            self.logger.info(f"Reviewed BDD scenarios with score: {result['coverage_score']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Scenario review failed: {str(e)}")
            raise
```

### 6. Test-Coder Agent

```python
class TestCoderAgent(BaseAgent):
    """Agent for generating Python test code"""
    
    def __init__(self, config: MCPConfig):
        agent_config = AgentConfig(
            name="test_coder",
            model="gpt-4",
            temperature=0.5,
            max_tokens=4000,
            prompt_template=self._get_prompt_template()
        )
        super().__init__(config, agent_config)
        
        # Create LLM manager
        llm_config = LLMConfig(
            provider=config.llm_provider,
            model="gpt-4",
            temperature=0.5,
            max_tokens=4000,
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.llm_manager = LLMManager(llm_config)
    
    def _get_prompt_template(self) -> str:
        """Get the prompt template for test coding"""
        return """
You are an expert Python test developer. Your task is to generate comprehensive test code based on BDD scenarios and codebase structure.

Requirements:
1. Generate pytest-compatible test files
2. Use proper test structure and organization
3. Include fixtures and test data
4. Implement proper assertions and validations
5. Handle edge cases and error scenarios
6. Use appropriate mocking for external dependencies
7. Follow Python testing best practices

Code Standards:
- Use descriptive test names and docstrings
- Implement proper setup and teardown
- Use parametrized tests for multiple scenarios
- Include proper error handling and validation
- Use appropriate assertions (assert, pytest.raises, etc.)
- Follow PEP 8 style guidelines

Output Format:
- Return valid JSON matching the TestOutput schema
- Include file paths and content for each test file
- Provide quality score (0-10) based on code quality
- Include recommendations for improvement

Focus on:
- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for complete workflows
- Error handling and edge case testing
- Performance and load testing where appropriate
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test code generation"""
        try:
            # Get BDD scenarios and codebase info
            bdd_data = input_data.get("bdd_scenarios", {})
            codebase = input_data.get("codebase", {})
            
            # Create messages
            system_message = SystemMessage(content=self._get_prompt_template())
            human_message = HumanMessage(content=f"""
Please generate Python test code based on these BDD scenarios and codebase:

BDD Scenarios:
{json.dumps(bdd_data, indent=2)}

Codebase Structure:
{json.dumps(codebase.get('structure', {}), indent=2)}

Critical Paths:
{codebase.get('critical_paths', [])}

Integration Points:
{codebase.get('integration_points', [])}
""")
            
            # Generate response
            result = await self.llm_manager.generate_structured_response(
                [system_message, human_message],
                TestOutput
            )
            
            self.logger.info(f"Generated {len(result['files'])} test files")
            return result
            
        except Exception as e:
            self.logger.error(f"Test code generation failed: {str(e)}")
            raise
```

### 7. Code-Reviewer Agent

```python
class CodeReviewerAgent(BaseAgent):
    """Agent for reviewing generated test code"""
    
    def __init__(self, config: MCPConfig):
        agent_config = AgentConfig(
            name="code_reviewer",
            model="gpt-4",
            temperature=0.2,
            max_tokens=3000,
            prompt_template=self._get_prompt_template()
        )
        super().__init__(config, agent_config)
        
        # Create LLM manager
        llm_config = LLMConfig(
            provider=config.llm_provider,
            model="gpt-4",
            temperature=0.2,
            max_tokens=3000,
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.llm_manager = LLMManager(llm_config)
    
    def _get_prompt_template(self) -> str:
        """Get the prompt template for code review"""
        return """
You are an expert Python code reviewer specializing in test code. Your task is to review generated test code for quality, correctness, and adherence to best practices.

Review Criteria:
1. Code quality and readability
2. Test structure and organization
3. Proper use of pytest features
4. Assertion quality and coverage
5. Error handling and edge cases
6. Mocking and test isolation
7. Performance and efficiency
8. Adherence to BDD scenarios
9. Integration with codebase
10. Maintainability and extensibility

Quality Standards:
- Tests should be clear and maintainable
- Proper use of fixtures and parametrization
- Appropriate mocking of external dependencies
- Comprehensive assertion coverage
- Proper error handling and validation
- Follow Python and pytest best practices

Output Format:
- Return valid JSON matching the ReviewOutput schema
- Provide quality score (0-10) based on review
- Identify specific bugs and issues
- Include recommendations for improvement
- Flag false positives or unnecessary complexity
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code review"""
        try:
            # Get test files and BDD scenarios
            test_data = input_data.get("test_files", {})
            bdd_data = input_data.get("bdd_scenarios", {})
            codebase = input_data.get("codebase", {})
            
            # Create messages
            system_message = SystemMessage(content=self._get_prompt_template())
            human_message = HumanMessage(content=f"""
Please review these test files against the BDD scenarios and codebase:

Test Files:
{json.dumps(test_data, indent=2)}

BDD Scenarios:
{json.dumps(bdd_data, indent=2)}

Codebase Structure:
{json.dumps(codebase.get('structure', {}), indent=2)}

Focus on:
- Code quality and test effectiveness
- Adherence to BDD scenarios
- Proper testing practices
- Integration with codebase
""")
            
            # Generate response
            result = await self.llm_manager.generate_structured_response(
                [system_message, human_message],
                ReviewOutput
            )
            
            self.logger.info(f"Reviewed test code with score: {result['score']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Code review failed: {str(e)}")
            raise
```

### 8. Update MCP Orchestrator

Update the `_initialize_agents` method in the MCPOrchestrator class:

```python
def _initialize_agents(self):
    """Initialize all agents"""
    try:
        # Create LLM configuration
        llm_config = LLMConfig(
            provider=self.config.llm_provider,
            model="gpt-4",
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        
        # Initialize agents
        self.agents = {
            "scenario_builder": ScenarioBuilderAgent(self.config),
            "reviewer": ReviewerAgent(self.config),
            "test_coder": TestCoderAgent(self.config),
            "code_reviewer": CodeReviewerAgent(self.config)
        }
        
        self.logger.info(f"Initialized {len(self.agents)} agents")
        
    except Exception as e:
        self.logger.error(f"Failed to initialize agents: {str(e)}")
        raise
```

Update the `_run_agent_pipeline` method:

```python
async def _run_agent_pipeline(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
    """Run the complete agent pipeline"""
    try:
        # Step 1: Generate BDD scenarios
        self.logger.info("Running scenario builder agent")
        bdd_result = await self.agents["scenario_builder"].run({
            "codebase": codebase
        })
        
        # Step 2: Review BDD scenarios
        self.logger.info("Running reviewer agent")
        review_result = await self.agents["reviewer"].run({
            "bdd_scenarios": bdd_result
        })
        
        # Step 3: Generate test code
        self.logger.info("Running test coder agent")
        test_result = await self.agents["test_coder"].run({
            "bdd_scenarios": bdd_result,
            "codebase": codebase
        })
        
        # Step 4: Review test code
        self.logger.info("Running code reviewer agent")
        code_review_result = await self.agents["code_reviewer"].run({
            "test_files": test_result,
            "bdd_scenarios": bdd_result,
            "codebase": codebase
        })
        
        # Package test files
        test_files = test_result.get("files", [])
        packaged_files = self._package_test_files(test_files)
        
        # Combine results
        result = {
            "bdd_scenarios": bdd_result,
            "test_files": {
                **test_result,
                "packaged_files": packaged_files
            },
            "review_results": code_review_result,
            "iteration": self.iteration_count,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store results
        self.results[f"iteration_{self.iteration_count}"] = result
        
        return result
        
    except Exception as e:
        self.logger.error(f"Agent pipeline failed: {str(e)}")
        raise
```

## 🧪 Testing Requirements

### Unit Tests
Create comprehensive unit tests for:
- Each agent's execute method
- LLM manager functionality
- Output schema validation
- Error handling and retry logic

### Integration Tests
Test the complete agent pipeline with:
- Mock LLM responses
- Real API calls (with test API keys)
- Error scenarios and recovery
- Performance and timeout testing

## ✅ Success Criteria

1. **Agent Implementation**:
   - [ ] All four agents properly implemented
   - [ ] LangChain integration working
   - [ ] Structured output generation working
   - [ ] Error handling comprehensive

2. **Pipeline Integration**:
   - [ ] Agent pipeline working end-to-end
   - [ ] Results properly combined
   - [ ] File packaging working
   - [ ] Quality scoring accurate

3. **Testing**:
   - [ ] Unit tests for all agents
   - [ ] Integration tests for pipeline
   - [ ] Mock testing working
   - [ ] Error scenario testing

4. **Performance**:
   - [ ] Agent execution under 30 seconds
   - [ ] Proper async/await usage
   - [ ] Memory usage optimized
   - [ ] Timeout handling working

## 🚀 Implementation Notes

- **LangChain Integration**: Use proper LangChain patterns and error handling
- **Structured Output**: Use Pydantic schemas for reliable JSON output
- **Error Resilience**: Implement proper retry and recovery logic
- **Performance**: Optimize for speed and memory usage
- **Testing**: Comprehensive test coverage with mocking

## 🔗 Integration Points

This Phase 2 implementation should integrate with:
- **Phase 1**: Core orchestrator and base classes
- **Phase 3**: Configuration and documentation
- **Phase 4**: Testing and validation

The system should be fully functional after Phase 2, with all agents working and the complete pipeline operational.

---

**Ready for Cline to implement!** 🚀
