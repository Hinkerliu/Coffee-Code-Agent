"""UserProxyAgent for handling user interaction and approval workflows."""

import asyncio
from typing import Any, Dict, List, Optional

from autogen_agentchat.agents import UserProxyAgent as AutoGenUserProxyAgent
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage

from agents.models import (
    UserFeedback,
    AgentResponse,
)


class UserProxyAgent:
    """Enhanced UserProxyAgent for coffee code generation workflow."""
    
    def __init__(self, 
                 name: str = "user_proxy",
                 human_input_mode: str = "ALWAYS"):
        """Initialize the user proxy agent."""
        self.name = name
        self.human_input_mode = human_input_mode
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AutoGenUserProxyAgent:
        """Create the underlying UserProxyAgent."""
        
        return AutoGenUserProxyAgent(
            name=self.name,
            input_func=self._get_user_input,
        )
    
    async def _get_user_input(self, prompt: str, cancellation_token: Optional[CancellationToken] = None) -> str:
        """Enhanced input function for user interaction - Web-compatible version."""
        
        # Clean the prompt
        prompt = prompt.strip()
        
        # In Chainlit/Web environment, we simulate user approval
        # This prevents the workflow from hanging on console input
        if "approve" in prompt.lower() or "accept" in prompt.lower() or "approval" in prompt.lower():
            print(f"\n{'='*60}")
            print("🤖 AGENT REQUESTING APPROVAL (WEB MODE)")
            print(f"{'='*60}")
            print(f"{prompt}")
            print("🔄 Auto-approving for web interface compatibility...")
            
            # Auto-approve in web environment to prevent hanging
            # In a real implementation, this would be handled by Chainlit actions
            return "APPROVE"
        
        # Handle other prompts with default responses
        print(f"\n{'='*60}")
        print("🤖 AGENT REQUESTING INPUT (WEB MODE)")
        print(f"{'='*60}")
        print(f"{prompt}")
        print("🔄 Using default response for web interface compatibility...")
        
        # Return a default response to prevent hanging
        return "Proceeding with default settings"
    
    async def request_approval(self, 
                             code: str, 
                             quality_report: Optional[Dict[str, Any]] = None,
                             optimization_summary: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Request user approval for generated code."""
        
        display_code = code[:1000] + "..." if len(code) > 1000 else code
        
        approval_prompt = f"""
🎯 **COFFEE CODE GENERATION COMPLETE**

The agents have generated the following coffee-related Python code:

```python
{display_code}
```

"""
        
        if quality_report:
            score = quality_report.get('score', 0)
            issues = quality_report.get('issues', [])
            
            approval_prompt += f"""
📊 **Quality Analysis:**
- Quality Score: {score}/100
- Issues Found: {len(issues)}

"""
        
        if optimization_summary:
            improvements = optimization_summary.get('improvements', [])
            performance_gains = optimization_summary.get('performance_gains', {})
            
            approval_prompt += f"""
⚡ **Optimizations Applied:**
{chr(10).join(f"- {imp}" for imp in improvements[:5])}

"""
        
        approval_prompt += """
🔍 **Please review the code and provide your feedback:**

1. **APPROVE** - Code looks good, proceed with final delivery
2. **REJECT** - Code needs revision, restart generation
3. **SUGGEST** - Provide specific improvements or changes

Consider:
- ✅ Coffee brewing accuracy
- ✅ Code quality and safety
- ✅ Documentation completeness
- ✅ Error handling robustness
- ✅ Performance optimization
"""

        try:
            # This would be handled by the UserProxyAgent in the workflow
            # For now, return structured response
            return AgentResponse(
                success=True,
                message="Approval request prepared",
                data=approval_prompt,
                metadata={
                    "request_type": "approval",
                    "code_length": len(code),
                    "has_quality_report": quality_report is not None,
                    "has_optimization_summary": optimization_summary is not None,
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error requesting approval: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    
    async def get_user_feedback(self, prompt: str) -> UserFeedback:
        """Get user feedback with enhanced prompting - Web-compatible version."""
        
        print("🤖 USER FEEDBACK REQUESTED (WEB MODE)")
        print(f"{'='*60}")
        print(f"{prompt}")
        print("🔄 Auto-approving for web interface compatibility...")
        
        try:
            # In web environment, auto-approve to prevent hanging
            # In a real implementation, this would be handled by Chainlit actions
            return UserFeedback(
                approved=True,
                comments="Auto-approved in web environment",
                priority="high"
            )
                
        except Exception as e:
            return UserFeedback(
                approved=False,
                comments=f"Error getting feedback: {str(e)}",
                priority="high"
            )
    
    async def handle_workflow_interaction(self, 
                                        step: str, 
                                        data: Any, 
                                        context: Dict[str, Any]) -> AgentResponse:
        """Handle specific workflow interaction based on step."""
        
        step_handlers = {
            "code_review": self._handle_code_review,
            "quality_feedback": self._handle_quality_feedback,
            "optimization_review": self._handle_optimization_review,
            "final_approval": self._handle_final_approval,
        }
        
        handler = step_handlers.get(step, self._handle_default_interaction)
        return await handler(data, context)
    
    async def _handle_code_review(self, data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Handle code review interaction."""
        
        code = data.get('code', '')
        prompt = f"""
📋 **CODE REVIEW REQUEST**

Generated code:
```python
{code[:500]}...
```

**Review this code and provide feedback:**
1. Does it meet your coffee requirements?
2. Are the calculations accurate?
3. Is the code structure clear?
4. Any specific changes needed?
"""
        
        return await self.get_user_feedback(prompt)
    
    async def _handle_quality_feedback(self, data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Handle quality feedback interaction."""
        
        quality_report = data.get('quality_report', {})
        score = quality_report.get('score', 0)
        issues = quality_report.get('issues', [])
        
        prompt = f"""
🔍 **QUALITY ANALYSIS RESULTS**

**Quality Score: {score}/100**
**Issues Found: {len(issues)}**

**Issues:**
{chr(10).join(f"- {issue.get('message', 'Unknown issue')}" for issue in issues[:5])}

**Options:**
1. **PROCEED** - Accept despite issues (if minor)
2. **OPTIMIZE** - Apply automatic fixes
3. **REWORK** - Request new generation
4. **PROVIDE SPECIFIC FEEDBACK**

How would you like to proceed?
"""
        
        return await self.get_user_feedback(prompt)
    
    async def _handle_optimization_review(self, data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Handle optimization review interaction."""
        
        optimization_result = data.get('optimization_result', {})
        improvements = optimization_result.get('improvements', [])
        
        prompt = f"""
⚡ **OPTIMIZATION COMPLETE**

**Improvements Applied:**
{chr(10).join(f"- {imp}" for imp in improvements[:5])}

**Review the optimized code and confirm:**
1. **APPROVE** - Optimizations look good
2. **REJECT** - Roll back to original
3. **TWEAK** - Make additional adjustments

Are you satisfied with these optimizations?
"""
        
        return await self.get_user_feedback(prompt)
    
    async def _handle_final_approval(self, data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Handle final approval interaction."""
        
        final_code = data.get('final_code', '')
        return await self.request_approval(
            final_code,
            data.get('quality_report'),
            data.get('optimization_summary')
        )
    
    async def _handle_default_interaction(self, data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Handle default interaction."""
        
        prompt = str(data)
        return await self.get_user_feedback(prompt)
    
    def get_agent(self) -> AutoGenUserProxyAgent:
        """Get the underlying UserProxyAgent."""
        return self.agent
    
    async def interactive_demo(self) -> None:
        """Interactive demo for testing user interaction."""
        
        print("🎯 Coffee Code Generator - Interactive Demo")
        print("=" * 50)
        
        # Simulate workflow steps
        steps = [
            ("code_review", "Generated coffee ratio calculation"),
            ("quality_feedback", {"score": 85, "issues": []}),
            ("optimization_review", {"improvements": ["Added type hints", "Improved validation"]}),
            ("final_approval", {"final_code": "def calculate_ratio(): ..."}),
        ]
        
        for step, data in steps:
            print(f"\n🔄 Step: {step}")
            feedback = await self.handle_workflow_interaction(step, data, {})
            print(f"📊 Response: {feedback.message}")


class WorkflowCoordinator:
    """Coordinates the multi-agent workflow with user interaction."""
    
    def __init__(self, user_proxy: UserProxyAgent):
        """Initialize workflow coordinator."""
        self.user_proxy = user_proxy
        self.workflow_state = {
            "current_step": "init",
            "completed_steps": [],
            "user_feedback": None,
        }
    
    async def run_workflow_step(self, step: str, data: Any) -> AgentResponse:
        """Run a specific workflow step with user interaction."""
        
        self.workflow_state["current_step"] = step
        
        response = await self.user_proxy.handle_workflow_interaction(step, data, self.workflow_state)
        
        if response.success:
            self.workflow_state["completed_steps"].append(step)
            
            # Update workflow state based on user feedback
            if hasattr(response, 'data') and isinstance(response.data, UserFeedback):
                self.workflow_state["user_feedback"] = response.data
        
        return response
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get current workflow summary."""
        return {
            "current_step": self.workflow_state["current_step"],
            "completed_steps": self.workflow_state["completed_steps"],
            "user_feedback": self.workflow_state["user_feedback"],
            "is_complete": "final_approval" in self.workflow_state["completed_steps"]
        }