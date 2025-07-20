"""CodeQualityAnalyzerAgent for analyzing coffee domain code quality and safety."""

import json
from typing import Any, Dict, List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from tools.code_analysis import (
    analyze_code_quality,
    validate_coffee_parameters,
    check_code_safety,
)
from agents.models import (
    CodeQualityReport,
    AgentResponse,
)


class CodeQualityAnalyzerAgent:
    """Agent specialized in analyzing coffee domain code quality and safety."""
    
    def __init__(self, model_client: ChatCompletionClient):
        """Initialize the code quality analyzer agent."""
        self.model_client = model_client
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """Create the AssistantAgent with code analysis tools."""
        
        system_message = """You are CodeQualityAnalyzerAgent, an expert in analyzing Python code for coffee-related applications.

Your responsibilities:
1. Perform comprehensive code quality analysis
2. Validate coffee domain parameters against industry standards
3. Identify security vulnerabilities and safety issues
4. Check for proper error handling and input validation
5. Ensure code follows Python best practices
6. Provide actionable recommendations for improvements
7. Validate coffee-specific calculations and parameters

Analysis areas:
- Syntax and style compliance
- Security vulnerabilities
- Coffee domain parameter validation (temperature, ratios, timing)
- Safety measures for equipment control
- Performance optimization opportunities
- Documentation completeness
- Error handling robustness

Coffee industry standards to validate:
- Water temperature: 195-205°F (90-96°C)
- Coffee-to-water ratios: 1:15 to 1:17 by weight
- Brew times appropriate for method
- Safety limits for equipment control
- Input validation for user parameters

Always provide:
- Clear severity levels (error, warning, info)
- Specific line references when possible
- Actionable recommendations
- Coffee domain-specific insights
- Safety considerations

Available tools:
- analyze_code_quality: Comprehensive static analysis
- validate_coffee_parameters: Coffee domain validation
- check_code_safety: Safety analysis for equipment control

Provide detailed analysis with specific recommendations for improvement."""

        return AssistantAgent(
            name="quality_analyzer",
            model_client=self.model_client,
            tools=[
                analyze_code_quality,
                validate_coffee_parameters,
                check_code_safety,
            ],
            system_message=system_message,
            model_client_stream=True,
            reflect_on_tool_use=True,
        )
    
    async def analyze_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Analyze code quality and provide comprehensive report."""
        
        prompt = f"""Analyze the following Python code for coffee domain quality and safety:

```python
{code}
```

Provide a comprehensive analysis covering:
1. Syntax and style compliance
2. Security vulnerabilities
3. Coffee domain parameter validation
4. Safety measures for equipment control
5. Performance considerations
6. Documentation completeness
7. Error handling robustness

Focus specifically on:
- Coffee brewing parameter validation (temperature, ratios, timing)
- Safety checks for temperature limits
- Input validation for user parameters
- Best practices for coffee calculation code

Provide specific recommendations with severity levels and actionable fixes."""

        try:
            from autogen_agentchat.messages import TextMessage
            
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            analysis_result = response.chat_message.content
            
            # Parse the analysis result
            quality_report = self._parse_analysis_result(analysis_result, code)
            
            return AgentResponse(
                success=True,
                message="Code quality analysis completed",
                data=quality_report,
                metadata={
                    "analysis_summary": {
                        "total_issues": len(quality_report.issues),
                        "coffee_validations": len(quality_report.coffee_domain_validations),
                        "security_issues": len(quality_report.security_issues),
                        "score": quality_report.score,
                    }
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error analyzing code: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    def _parse_analysis_result(self, analysis_text: str, code: str) -> CodeQualityReport:
        """Parse analysis result into structured report."""
        
        # Default structure
        issues = []
        suggestions = []
        coffee_validations = []
        security_issues = []
        performance_notes = []
        
        # Parse analysis text for structured data
        lines = analysis_text.split('\n')
        
        # Extract issues and suggestions
        for line in lines:
            line = line.strip()
            
            # Severity-based parsing
            if line.startswith('ERROR:') or 'error' in line.lower():
                issues.append({
                    "severity": "error",
                    "message": line,
                    "line_number": None,
                    "code_snippet": None
                })
            elif line.startswith('WARNING:') or 'warning' in line.lower():
                issues.append({
                    "severity": "warning",
                    "message": line,
                    "line_number": None,
                    "code_snippet": None
                })
            elif line.startswith('INFO:') or 'suggestion' in line.lower():
                suggestions.append(line)
            elif 'coffee' in line.lower() and any(word in line.lower() for word in ['temperature', 'ratio', 'time']):
                coffee_validations.append({
                    "parameter": "coffee_domain",
                    "value": None,
                    "valid": "valid" in line.lower(),
                    "message": line,
                    "recommendation": None
                })
        
        # Calculate quality score based on issues
        score = max(0, 100 - (len(issues) * 10))
        
        return CodeQualityReport(
            score=score,
            issues=issues,
            suggestions=suggestions,
            coffee_domain_validations=coffee_validations,
            security_issues=security_issues,
            performance_notes=performance_notes
        )
    
    async def validate_coffee_domain(self, code: str) -> AgentResponse:
        """Specifically validate coffee domain parameters."""
        
        prompt = f"""Focus on coffee domain validation for this code:

```python
{code}
```

Validate specifically:
1. Water temperature ranges (195-205°F)
2. Coffee-to-water ratios (1:15 to 1:17)
3. Brew times appropriate for method
4. Grind size recommendations
5. Safety limits for equipment
6. Input validation for coffee parameters

Provide detailed coffee domain validation results with specific parameter checks.
"""

        try:
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            return AgentResponse(
                success=True,
                message="Coffee domain validation completed",
                data=response.chat_message.content,
                metadata={"validation_type": "coffee_domain"}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error validating coffee domain: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    async def check_safety(self, code: str) -> AgentResponse:
        """Check safety aspects for equipment control code."""
        
        prompt = f"""Perform safety analysis for this coffee equipment control code:

```python
{code}
```

Check for:
1. Temperature safety limits
2. Time-based safety checks
3. Input validation for equipment control
4. Error handling for safety-critical operations
5. Emergency stop mechanisms
6. Maximum value limits
7. Safe defaults

Provide specific safety recommendations with risk levels.
"""

        try:
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            return AgentResponse(
                success=True,
                message="Safety analysis completed",
                data=response.chat_message.content,
                metadata={"analysis_type": "safety"}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error in safety analysis: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    def generate_quality_summary(self, report: CodeQualityReport) -> str:
        """Generate human-readable quality summary."""
        
        summary_parts = []
        
        # Overall score
        summary_parts.append(f"Quality Score: {report.score:.1f}/100")
        
        # Issues summary
        if report.issues:
            error_count = sum(1 for issue in report.issues if issue.get('severity') == 'error')
            warning_count = sum(1 for issue in report.issues if issue.get('severity') == 'warning')
            
            summary_parts.append(f"Issues Found: {error_count} errors, {warning_count} warnings")
        
        # Coffee domain validations
        if report.coffee_domain_validations:
            valid_count = sum(1 for v in report.coffee_domain_validations if v.get('valid', False))
            total_count = len(report.coffee_domain_validations)
            summary_parts.append(f"Coffee Domain Validations: {valid_count}/{total_count} passed")
        
        # Recommendations
        if report.suggestions:
            summary_parts.append(f"Recommendations: {len(report.suggestions)} suggestions")
        
        return "\n".join(summary_parts)
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AssistantAgent."""
        return self.agent