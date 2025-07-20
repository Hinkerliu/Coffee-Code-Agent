name: "AutoGen Coffee Multi-Agent System - Code Generation, Quality Analysis, and Optimization"
description: |

## Purpose
Build a complete AutoGen v0.4 multi-agent system for coffee domain code generation, featuring specialized agents for coffee recipe calculations, code quality analysis, optimization, and user interaction with both CLI and web interfaces.

## Core Principles
1. **Context is King**: Include ALL AutoGen v0.4 patterns, coffee domain knowledge, and validation mechanisms
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix iteratively
3. **Information Dense**: Use established codebase patterns and coffee industry standards
4. **Progressive Success**: Start with core agents, validate, then enhance with optimization
5. **Coffee Domain Expertise**: Embed coffee brewing knowledge, equipment specs, and industry standards

---

## Goal
Create a production-ready AutoGen v0.4 multi-agent system where users can request coffee-related Python code (brewing calculations, equipment control, recipe management) and receive validated, optimized code through a collaborative agent workflow.

## Why
- **Business value**: Automates coffee-related software development for cafes, roasters, and equipment manufacturers
- **Integration**: Demonstrates advanced AutoGen v0.4 multi-agent patterns with real-world domain expertise
- **Problems solved**: Reduces time-to-market for coffee tech applications, ensures code quality and safety standards

## What
A comprehensive system with:
- **CoffeeCodeGeneratorAgent**: Generates coffee-specific Python code based on user requirements
- **CodeQualityAnalyzerAgent**: Analyzes code for quality, security, and coffee domain validation
- **CodeOptimizerAgent**: Optimizes and fixes code based on quality analysis
- **UserProxyAgent**: Handles user interaction, approval workflows, and final delivery
- **CLI Interface**: Command-line interaction with streaming responses
- **Chainlit Web UI**: Real-time web interface with agent visibility

### Success Criteria
- [ ] CoffeeCodeGeneratorAgent generates accurate brewing calculations (ratios, temperatures, timing)
- [ ] CodeQualityAnalyzerAgent validates coffee domain parameters (195-205°F water temp, 1:15-1:17 ratios)
- [ ] CodeOptimizerAgent improves performance and maintainability
- [ ] UserProxyAgent handles approval workflows and user interaction
- [ ] CLI provides streaming responses with agent visibility
- [ ] Chainlit UI displays real-time agent conversations
- [ ] All tests pass with 80%+ coverage
- [ ] Code meets coffee industry safety and accuracy standards

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/
  why: Core AutoGen v0.4 patterns and agent creation
  
- url: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html
  why: AssistantAgent, UserProxyAgent implementation patterns
  
- url: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html
  why: RoundRobinGroupChat and team coordination patterns
  
- url: https://docs.chainlit.io/
  why: Streaming UI implementation and agent visibility
  
- file: examples/app_agent.py
  why: Single agent pattern with streaming and Chainlit integration
  
- file: examples/app_team.py
  why: Multi-agent team pattern with RoundRobinGroupChat
  
- file: examples/app_team_user_proxy.py
  why: UserProxyAgent implementation for approval workflows
  
- doc: Coffee brewing standards and parameters
  content: |
    Water temperature: 195-205°F (90-96°C)
    Coffee-to-water ratios: 1:15 to 1:17 by weight
    Espresso ratios: 1:2 (dose:yield)
    Grind sizes: Extra coarse (cold brew) to extra fine (Turkish)
    Brew times: 2-4 min pour-over, 25-30 sec espresso, 12-24 hr cold brew
    Equipment safety: Never exceed 212°F (100°C) for safety
    
- url: https://sca.coffee/research/coffee-standards
  why: Specialty Coffee Association standards for validation
```

### Current Codebase tree
```bash
.
├── CLAUDE.md                    # Project guidelines and patterns
├── INITIAL.md                   # Feature requirements
├── examples/
│   ├── README.md               # AutoGen setup instructions
│   ├── app_agent.py            # Single agent example
│   ├── app_team.py             # Multi-agent team example
│   ├── app_team_user_proxy.py  # User approval workflow
│   ├── model_config.yaml       # Model configuration template
│   └── model_config_template.yaml
├── PRPs/
│   ├── templates/
│   │   └── prp_base.md         # Template patterns
│   └── EXAMPLE_multi_agent_prp.md
├── README.md                   # Project documentation
└── requirements.txt            # Dependencies
```

### Desired Codebase tree with files to be added
```bash
.
├── agents/
│   ├── __init__.py                    # Package initialization
│   ├── coffee_generator.py           # CoffeeCodeGeneratorAgent implementation
│   ├── quality_analyzer.py           # CodeQualityAnalyzerAgent implementation
│   ├── optimizer.py                  # CodeOptimizerAgent implementation
│   ├── user_proxy.py                 # UserProxyAgent implementation
│   └── models.py                     # Pydantic models for coffee domain
├── tools/
│   ├── __init__.py                    # Package initialization
│   ├── coffee_calculations.py        # Coffee brewing calculation tools
│   ├── code_analysis.py              # Code quality analysis tools
│   └── code_optimization.py          # Code optimization tools
├── prompts/
│   ├── __init__.py                    # Package initialization
│   ├── coffee_generator_prompt.txt   # System prompt for generator
│   ├── quality_analyzer_prompt.txt   # System prompt for analyzer
│   ├── optimizer_prompt.txt          # System prompt for optimizer
│   └── user_proxy_prompt.txt         # System prompt for user proxy
├── workflows/
│   ├── __init__.py                    # Package initialization
│   ├── coffee_workflow.py            # Multi-agent workflow coordination
│   └── cli_workflow.py               # CLI interaction workflow
├── interfaces/
│   ├── __init__.py                    # Package initialization
│   ├── cli.py                        # Command-line interface
│   └── chainlit_app.py               # Chainlit web interface
├── tests/
│   ├── __init__.py                    # Package initialization
│   ├── test_coffee_generator.py      # Generator agent tests
│   ├── test_quality_analyzer.py      # Analyzer agent tests
│   ├── test_optimizer.py             # Optimizer agent tests
│   ├── test_user_proxy.py            # User proxy tests
│   ├── test_coffee_calculations.py   # Coffee calculation tests
│   └── test_workflows.py             # Workflow integration tests
├── config/
│   ├── __init__.py                    # Package initialization
│   ├── settings.py                   # Configuration management
│   └── model_config.yaml             # Model configuration
├── .env.example                      # Environment variables template
├── requirements.txt                  # Updated dependencies
├── README.md                        # Comprehensive documentation
└── docker-compose.yml               # Docker deployment configuration
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: AutoGen v0.4 requires Python 3.10+ and async/await throughout
# CRITICAL: Chainlit requires proper async handling for streaming
# CRITICAL: Coffee calculations must handle floating point precision for ratios
# CRITICAL: Temperature conversions must be accurate (Celsius/Fahrenheit)
# CRITICAL: Equipment control code must include safety checks
# CRITICAL: Never hardcode API keys - use environment variables
# CRITICAL: Use Pydantic models for all data validation
# CRITICAL: Implement proper error handling for agent failures
# CRITICAL: Follow PEP8 and use type hints everywhere
# CRITICAL: Test edge cases like zero/negative values in calculations
```

## Implementation Blueprint

### Data models and structure

```python
# agents/models.py - Core coffee domain data structures
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class BrewMethod(str, Enum):
    ESPRESSO = "espresso"
    POUR_OVER = "pour_over"
    FRENCH_PRESS = "french_press"
    COLD_BREW = "cold_brew"
    AEROPRESS = "aeropress"
    TURKISH = "turkish"

class CoffeeRecipe(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    brew_method: BrewMethod
    coffee_weight: float = Field(..., gt=0, description="Coffee weight in grams")
    water_weight: float = Field(..., gt=0, description="Water weight in grams")
    water_temperature: float = Field(..., ge=175, le=212, description="Temperature in Fahrenheit")
    grind_size: str = Field(..., description="Grind size description")
    brew_time: float = Field(..., gt=0, description="Brew time in minutes")
    
    @validator('water_temperature')
    def validate_temperature(cls, v):
        if v < 195 or v > 205:
            raise ValueError('Water temperature should be between 195-205°F for optimal extraction')
        return v
    
    @validator('coffee_weight', 'water_weight')
    def validate_weights(cls, v):
        if v <= 0:
            raise ValueError('Weights must be positive')
        return v
    
    @property
    def ratio(self) -> float:
        return self.water_weight / self.coffee_weight

class CodeGenerationRequest(BaseModel):
    requirement: str = Field(..., min_length=10, description="User's coffee code requirement")
    brew_method: Optional[BrewMethod] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class CodeQualityReport(BaseModel):
    score: float = Field(..., ge=0, le=100)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    coffee_domain_validations: List[str] = Field(default_factory=list)
    
class OptimizationResult(BaseModel):
    original_code: str
    optimized_code: str
    improvements: List[str] = Field(default_factory=list)
    performance_gains: Dict[str, float] = Field(default_factory=dict)
```

### List of tasks to be completed

```yaml
Task 1: Setup Environment and Configuration
CREATE config/settings.py:
  - PATTERN: Use pydantic-settings for environment variable management
  - Include model configurations, API keys, and coffee domain constants
  - Validate required environment variables on startup

CREATE .env.example:
  - Include all required environment variables with descriptions
  - Follow pattern from examples/README.md
  - Add coffee-specific configuration options

Task 2: Implement Coffee Calculation Tools
CREATE tools/coffee_calculations.py:
  - PATTERN: Async functions like examples/app_agent.py tools
  - Implement coffee-to-water ratio calculations
  - Temperature conversion utilities (C/F)
  - Grind size recommendations by brew method
  - Brew time calculations based on method and volume

Task 3: Implement Code Analysis Tools
CREATE tools/code_analysis.py:
  - PATTERN: Static analysis tools for code quality
  - Coffee domain validation (temperature ranges, ratios)
  - Security analysis for equipment control code
  - Performance analysis for calculation-heavy code

Task 4: Implement Code Optimization Tools
CREATE tools/code_optimization.py:
  - PATTERN: Code refactoring and optimization utilities
  - Performance optimization for mathematical calculations
  - Memory optimization for large datasets
  - Best practices enforcement for coffee domain code

Task 5: Create CoffeeCodeGeneratorAgent
CREATE agents/coffee_generator.py:
  - PATTERN: Follow examples/app_agent.py structure
  - Use AssistantAgent with coffee calculation tools
  - Generate Python code for coffee operations
  - Validate generated code against coffee standards

Task 6: Create CodeQualityAnalyzerAgent
CREATE agents/quality_analyzer.py:
  - PATTERN: AssistantAgent with code analysis tools
  - Analyze generated code for quality and safety
  - Validate coffee domain parameters
  - Provide detailed quality reports

Task 7: Create CodeOptimizerAgent
CREATE agents/optimizer.py:
  - PATTERN: AssistantAgent with optimization tools
  - Optimize code based on quality analysis
  - Improve performance and maintainability
  - Ensure coffee domain accuracy is preserved

Task 8: Create UserProxyAgent
CREATE agents/user_proxy.py:
  - PATTERN: Follow examples/app_team_user_proxy.py
  - Handle user approval workflows
  - Provide clear feedback and interaction
  - Manage conversation flow and termination

Task 9: Create Multi-Agent Workflow
CREATE workflows/coffee_workflow.py:
  - PATTERN: RoundRobinGroupChat from examples/app_team.py
  - Coordinate generator → analyzer → optimizer → user proxy flow
  - Implement proper termination conditions
  - Handle error cases and retries

Task 10: Create CLI Interface
CREATE interfaces/cli.py:
  - PATTERN: Command-line interface with streaming
  - Accept user coffee code requirements
  - Display agent interactions and progress
  - Handle configuration and setup

Task 11: Create Chainlit Web Interface
CREATE interfaces/chainlit_app.py:
  - PATTERN: Follow examples/app_team.py with streaming
  - Real-time web interface for agent interactions
  - Display tool usage and agent conversations
  - Support file uploads for complex requirements

Task 12: Add Comprehensive Testing
CREATE tests/:
  - PATTERN: Mirror existing test structure
  - Unit tests for each agent and tool
  - Integration tests for complete workflows
  - Coffee domain validation tests
  - Performance and edge case tests

Task 13: Create Documentation and Deployment
CREATE README.md:
  - Comprehensive setup and usage instructions
  - Coffee domain examples and use cases
  - API documentation and configuration
  - Docker deployment instructions

CREATE docker-compose.yml:
  - Multi-service deployment with Chainlit
  - Environment configuration
  - Volume mounts for configuration
```

### Per task pseudocode

```python
# Task 2: Coffee Calculation Tools
async def calculate_coffee_ratio(coffee_grams: float, ratio: float = 16.67) -> float:
    """Calculate water needed based on coffee weight and ratio."""
    # PATTERN: Input validation like examples
    if coffee_grams <= 0:
        raise ValueError("Coffee weight must be positive")
    if ratio < 15 or ratio > 17:
        raise ValueError("Ratio must be between 15:1 and 17:1")
    
    water_grams = coffee_grams * ratio
    return round(water_grams, 2)

async def validate_coffee_parameters(temp_f: float, coffee_g: float, water_g: float) -> dict:
    """Validate coffee brewing parameters against industry standards."""
    # CRITICAL: Industry standard validations
    issues = []
    if temp_f < 195 or temp_f > 205:
        issues.append("Water temperature outside optimal range (195-205°F)")
    
    ratio = water_g / coffee_g
    if ratio < 15 or ratio > 17:
        issues.append("Coffee-to-water ratio outside recommended range (1:15 to 1:17)")
    
    return {"valid": len(issues) == 0, "issues": issues}

# Task 5: CoffeeCodeGeneratorAgent
class CoffeeCodeGeneratorAgent:
    def __init__(self, model_client):
        self.agent = AssistantAgent(
            name="coffee_generator",
            model_client=model_client,
            tools=[calculate_coffee_ratio, validate_coffee_parameters],
            system_message="""You are a coffee code generation expert. Generate accurate Python code for coffee operations based on user requirements. Always validate coffee domain parameters against industry standards.""",
            model_client_stream=True
        )

# Task 9: Multi-Agent Workflow
coffee_workflow = RoundRobinGroupChat(
    agents=[generator_agent, analyzer_agent, optimizer_agent, user_proxy_agent],
    termination_condition=TextMentionTermination("APPROVE")
)

# Task 10: CLI Interface
async def run_coffee_cli():
    """Run coffee code generation via CLI."""
    # PATTERN: Async CLI like examples
    workflow = create_coffee_workflow()
    
    while True:
        user_input = input("\nEnter your coffee code requirement: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        async for msg in workflow.run_stream([TextMessage(content=user_input, source="user")]):
            if isinstance(msg, ModelClientStreamingChunkEvent):
                print(msg.content, end="", flush=True)
            elif isinstance(msg, TaskResult):
                print(f"\nWorkflow completed: {msg.stop_reason}")
```

### Integration Points
```yaml
ENVIRONMENT:
  - add to: .env
  - vars: |
      # Model Configuration
      OPENAI_API_KEY=sk-...
      AZURE_OPENAI_API_KEY=...
      AZURE_OPENAI_ENDPOINT=...
      
      # Coffee Domain Settings
      DEFAULT_WATER_TEMP=200
      DEFAULT_RATIO=16.67
      SAFETY_TEMP_MAX=212
      
CONFIG:
  - model_config.yaml: Update with coffee-specific model settings
  - settings.py: Include coffee domain constants and validation rules
  
DEPENDENCIES:
  - Update requirements.txt with:
    - autogen-agentchat>=0.4.0
    - chainlit>=1.0.0
    - pydantic>=2.0.0
    - pytest>=7.0.0
    - pytest-asyncio>=0.21.0
    - black>=23.0.0
    - mypy>=1.0.0
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check agents/ tools/ workflows/ interfaces/ --fix
black agents/ tools/ workflows/ interfaces/
mypy agents/ tools/ workflows/ interfaces/

# Expected: No errors. If errors, READ and fix.
```

### Level 2: Unit Tests
```python
# tests/test_coffee_calculations.py
async def test_coffee_ratio_calculation():
    """Test accurate coffee-to-water ratio calculation."""
    result = await calculate_coffee_ratio(30.0, 16.67)
    assert result == 500.1
    assert isinstance(result, float)

async def test_temperature_validation():
    """Test coffee parameter validation."""
    result = await validate_coffee_parameters(200, 30, 500)
    assert result["valid"] is True
    assert len(result["issues"]) == 0

# tests/test_agents.py
async def test_coffee_generator_agent():
    """Test coffee code generation agent."""
    agent = create_coffee_generator_agent()
    result = await agent.run("Generate code for espresso ratio calculation")
    assert "def calculate_espresso" in result.messages[-1].content.lower()

# Run tests iteratively until passing:
pytest tests/ -v --cov=agents --cov=tools --cov-report=term-missing
```

### Level 3: Integration Test
```bash
# Test CLI interaction
python -m interfaces.cli

# Expected interaction:
# > Enter your coffee code requirement: Create a function to calculate pour-over coffee ratios
# 🤖 Coffee Generator: [Generates ratio calculation function]
# 🔍 Quality Analyzer: [Analyzes code quality and coffee parameters]
# ⚡ Optimizer: [Suggests performance improvements]
# 👤 User Proxy: [Presents final code for approval]

# Test Chainlit web interface
chainlit run interfaces/chainlit_app.py -w
# Visit http://localhost:8000 and test coffee code generation
```

## Final Validation Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check .`
- [ ] No type errors: `mypy .`
- [ ] CLI works for coffee code generation
- [ ] Chainlit UI streams agent conversations
- [ ] Coffee domain validations work correctly
- [ ] Error cases handled gracefully
- [ ] All coffee parameters validated against industry standards
- [ ] Documentation includes clear setup and usage instructions
- [ ] Docker deployment works correctly

## Anti-Patterns to Avoid
- ❌ Don't generate code with hardcoded values - use parameters and validation
- ❌ Don't skip coffee domain validation - temperature and ratios must be accurate
- ❌ Don't use sync functions in async agent context
- ❌ Don't ignore safety checks for equipment control code
- ❌ Don't skip error handling for invalid user inputs
- ❌ Don't commit API keys or sensitive configuration
- ❌ Don't create agents without proper system messages
- ❌ Don't skip unit tests for coffee domain calculations

## Confidence Score: 9/10

High confidence due to:
- Clear AutoGen v0.4 patterns from existing codebase
- Comprehensive coffee domain knowledge embedded
- Established multi-agent workflow patterns
- Complete validation and testing strategy
- Detailed implementation blueprint with pseudocode
- Extensive documentation and error handling

Minor uncertainty on complex coffee equipment integrations, but core calculations and code generation patterns are well-established.