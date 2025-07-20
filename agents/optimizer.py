"""CodeOptimizerAgent for optimizing coffee domain code performance and maintainability."""

import json
from typing import Any, Dict, List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from tools.code_optimization import (
    optimize_coffee_code,
    apply_optimizations,
    get_performance_improvements,
)
from agents.models import (
    OptimizationResult,
    AgentResponse,
)


class CodeOptimizerAgent:
    """Agent specialized in optimizing coffee domain code for performance and maintainability."""
    
    def __init__(self, model_client: ChatCompletionClient):
        """Initialize the code optimizer agent."""
        self.model_client = model_client
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """Create the AssistantAgent with optimization tools."""
        
        system_message = """You are CodeOptimizerAgent, an expert in optimizing Python code for coffee-related applications.

Your responsibilities:
1. Optimize code performance for coffee calculations
2. Improve code maintainability and readability
3. Enhance coffee domain parameter handling
4. Apply best practices for mathematical precision
5. Optimize for equipment control safety
6. Improve documentation and type safety
7. Reduce memory usage and execution time

Optimization focus areas:
- Mathematical calculation performance
- Coffee constant management
- Input validation efficiency
- Error handling optimization
- Documentation quality
- Type hint usage
- Safety measure efficiency
- Memory usage optimization

Coffee-specific optimizations:
- Precise decimal calculations for ratios
- Efficient temperature conversions
- Optimized recipe scaling
- Fast brewing parameter validation
- Memory-efficient recipe storage

Always provide:
- Specific optimization suggestions
- Performance improvement metrics
- Before/after code comparisons
- Safety considerations
- Maintainability improvements

Available tools:
- optimize_coffee_code: Generate optimization report
- apply_optimizations: Apply specific optimizations
- get_performance_improvements: Calculate performance gains

Provide optimized code that maintains accuracy while improving performance and maintainability."""

        return AssistantAgent(
            name="code_optimizer",
            model_client=self.model_client,
            tools=[
                optimize_coffee_code,
                apply_optimizations,
                get_performance_improvements,
            ],
            system_message=system_message,
            model_client_stream=True,
            reflect_on_tool_use=True,
        )
    
    async def optimize_code(self, original_code: str, optimization_focus: Optional[List[str]] = None) -> AgentResponse:
        """Optimize coffee domain code based on analysis results."""
        
        focus_areas = optimization_focus or ["performance", "maintainability", "coffee_domain"]
        
        prompt = f"""Optimize the following coffee domain Python code focusing on: {', '.join(focus_areas)}

Original code:
```python
{original_code}
```

Provide comprehensive optimization including:
1. Performance improvements for calculations
2. Better constant management
3. Enhanced input validation
4. Improved error handling
5. Better documentation
6. Type safety improvements
7. Safety optimization

Return the optimized code with a summary of improvements made.

Optimization requirements:
- Maintain coffee domain accuracy
- Preserve all functionality
- Improve readability
- Enhance maintainability
- Add safety measures
- Optimize performance where possible

Provide the complete optimized code with inline comments explaining key optimizations."""

        try:
            from autogen_agentchat.messages import TextMessage
            
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            optimization_result = response.chat_message.content
            
            # Extract optimized code and improvements
            optimized_code, improvements = self._parse_optimization_result(optimization_result, original_code)
            
            # Calculate performance improvements
            improvements_dict = await get_performance_improvements(optimized_code)
            
            result = OptimizationResult(
                original_code=original_code,
                optimized_code=optimized_code,
                improvements=improvements,
                performance_gains=improvements_dict,
                quality_score_improvement=improvements_dict.get('maintainability_score', 0),
                optimizations_applied=self._identify_optimizations_applied(original_code, optimized_code)
            )
            
            return AgentResponse(
                success=True,
                message="Code optimization completed successfully",
                data=result,
                metadata={
                    "focus_areas": focus_areas,
                    "improvements_count": len(improvements),
                    "performance_gains": improvements_dict,
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error optimizing code: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    def _parse_optimization_result(self, result: str, original_code: str) -> tuple[str, List[str]]:
        """Parse optimization result to extract optimized code and improvements."""
        
        # Simple parsing - in real implementation, use structured output
        lines = result.split('\n')
        
        # Look for code blocks
        code_start = None
        code_end = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```python'):
                code_start = i + 1
            elif line.strip() == '```' and code_start is not None:
                code_end = i
                break
        
        if code_start is not None and code_end is not None:
            optimized_code = '\n'.join(lines[code_start:code_end])
        else:
            # Fallback: use the entire response as optimized code
            optimized_code = result
        
        # Extract improvements from comments
        improvements = []
        for line in lines:
            if '# OPTIMIZATION:' in line.upper() or '# IMPROVEMENT:' in line.upper():
                improvement = line.replace('#', '').strip()
                improvements.append(improvement)
        
        return optimized_code, improvements
    
    def _identify_optimizations_applied(self, original: str, optimized: str) -> List[str]:
        """Identify which optimizations were applied."""
        optimizations = []
        
        # Check for specific optimization patterns
        if 'from typing import' not in original and 'from typing import' in optimized:
            optimizations.append("Added type hints")
        
        if '"""' not in original and '"""' in optimized:
            optimizations.append("Enhanced documentation")
        
        if 'def validate_' not in original and 'def validate_' in optimized:
            optimizations.append("Added input validation")
        
        if 'try:' not in original and 'try:' in optimized:
            optimizations.append("Improved error handling")
        
        if 'Decimal' not in original and 'Decimal' in optimized:
            optimizations.append("Enhanced precision with Decimal")
        
        if 'CONSTANT' not in original and any(word.isupper() for word in optimized.split()):
            optimizations.append("Added named constants")
        
        return optimizations
    
    async def apply_specific_optimizations(self, code: str, optimizations: List[Dict[str, Any]]) -> AgentResponse:
        """Apply specific optimizations based on requirements."""
        
        prompt = f"""Apply the following specific optimizations to the coffee domain code:

Code to optimize:
```python
{code}
```

Optimizations to apply:
{json.dumps(optimizations, indent=2)}

Apply these optimizations while maintaining:
1. Coffee domain accuracy
2. All original functionality
3. Safety considerations
4. Readability

Return the optimized code with comments indicating each optimization applied."""

        try:
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            optimized_code = response.chat_message.content
            
            return AgentResponse(
                success=True,
                message="Specific optimizations applied successfully",
                data=optimized_code,
                metadata={"optimations_applied": len(optimizations)}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error applying optimizations: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    async def generate_optimization_report(self, optimization_result: OptimizationResult) -> str:
        """Generate detailed optimization report."""
        
        report = f"""# Code Optimization Report

## Summary
- Original code: {len(optimization_result.original_code.split())} words
- Optimized code: {len(optimization_result.optimized_code.split())} words
- Improvements: {len(optimization_result.improvements)}
- Quality score improvement: +{optimization_result.quality_score_improvement:.1f}%

## Optimizations Applied
{chr(10).join(f"- {opt}" for opt in optimization_result.optimizations_applied)}

## Performance Improvements
"""
        
        for metric, improvement in optimization_result.performance_gains.items():
            report += f"- {metric.replace('_', ' ').title()}: +{improvement:.1f}%\n"
        
        if optimization_result.improvements:
            report += "\n## Key Improvements\n"
            report += f"{chr(10).join(f"- {imp}" for imp in optimization_result.improvements)}"
        
        return report
    
    async def compare_performance(self, original_code: str, optimized_code: str) -> Dict[str, Any]:
        """Compare performance metrics between original and optimized code."""
        
        improvements = await get_performance_improvements(optimized_code)
        
        return {
            "readability_improvement": improvements.get("readability_score", 0),
            "maintainability_improvement": improvements.get("maintainability_score", 0),
            "performance_improvement": improvements.get("performance_score", 0),
            "coffee_domain_accuracy": improvements.get("coffee_domain_accuracy", 0),
            "code_length_reduction": max(0, (len(original_code) - len(optimized_code)) / len(original_code) * 100),
        }
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AssistantAgent."""
        return self.agent