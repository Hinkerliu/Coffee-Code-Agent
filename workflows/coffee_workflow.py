"""Coffee multi-agent workflow coordination using AutoGen v0.4 patterns."""

import asyncio
from typing import Any, Dict, List, Optional, Tuple
import yaml

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ChatCompletionClient
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage

from agents.coffee_generator import CoffeeCodeGeneratorAgent
from agents.quality_analyzer import CodeQualityAnalyzerAgent
from agents.optimizer import CodeOptimizerAgent
from agents.user_proxy import UserProxyAgent
from agents.models import (
    CodeGenerationRequest,
    CodeQualityReport,
    OptimizationResult,
    AgentResponse,
)


class CoffeeWorkflowCoordinator:
    """Coordinates the complete coffee code generation workflow."""
    
    def __init__(self, model_client: ChatCompletionClient):
        """Initialize workflow coordinator with all agents."""
        self.model_client = model_client
        self.agents = self._create_agents()
        self.workflow_steps = []
        self.current_step = "init"
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create all workflow agents."""
        return {
            "generator": CoffeeCodeGeneratorAgent(self.model_client),
            "analyzer": CodeQualityAnalyzerAgent(self.model_client),
            "optimizer": CodeOptimizerAgent(self.model_client),
            "user_proxy": UserProxyAgent(),
        }
    
    async def run_complete_workflow(self, user_requirement: str) -> Dict[str, Any]:
        """Run the complete coffee code generation workflow."""
        
        workflow_result = {
            "user_requirement": user_requirement,
            "steps": [],
            "final_code": None,
            "quality_score": 0,
            "optimization_summary": {},
            "user_approval": False,
            "workflow_success": False,
        }
        
        try:
            # Step 1: Generate initial code
            print("🎯 Step 1: Generating coffee code...")
            generation_result = await self._step_generate_code(user_requirement)
            workflow_result["steps"].append(generation_result)
            
            if not generation_result["success"]:
                return workflow_result
            
            generated_code = generation_result["data"]
            
            # Step 2: Analyze code quality
            print("🔍 Step 2: Analyzing code quality...")
            analysis_result = await self._step_analyze_quality(generated_code)
            workflow_result["steps"].append(analysis_result)
            
            quality_report = analysis_result["data"]
            workflow_result["quality_score"] = quality_report.score
            
            # Step 3: Optimize code
            print("⚡ Step 3: Optimizing code...")
            optimization_result = await self._step_optimize_code(generated_code, quality_report)
            workflow_result["steps"].append(optimization_result)
            
            optimized_code = optimization_result["data"].optimized_code
            workflow_result["optimization_summary"] = {
                "improvements": optimization_result["data"].improvements,
                "performance_gains": optimization_result["data"].performance_gains,
            }
            
            # Step 4: User approval
            print("👤 Step 4: Requesting user approval...")
            approval_result = await self._step_user_approval(
                optimized_code, 
                quality_report, 
                optimization_result["data"]
            )
            workflow_result["steps"].append(approval_result)
            
            workflow_result["user_approval"] = approval_result["data"]["approved"]
            workflow_result["final_code"] = optimized_code if workflow_result["user_approval"] else None
            workflow_result["workflow_success"] = workflow_result["user_approval"]
            
            return workflow_result
            
        except Exception as e:
            workflow_result["error"] = str(e)
            return workflow_result
    
    async def _step_generate_code(self, requirement: str) -> Dict[str, Any]:
        """Generate coffee code based on user requirement."""
        
        try:
            request = CodeGenerationRequest(requirement=requirement)
            response = await self.agents["generator"].generate_code(request)
            
            return {
                "step": "code_generation",
                "success": response.success,
                "data": response.data,
                "message": response.message,
                "metadata": response.metadata,
            }
            
        except Exception as e:
            return {
                "step": "code_generation",
                "success": False,
                "data": None,
                "message": f"Generation failed: {str(e)}",
                "metadata": {"error": str(e)},
            }
    
    async def _step_analyze_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality and safety."""
        
        try:
            response = await self.agents["analyzer"].analyze_code(code)
            
            return {
                "step": "quality_analysis",
                "success": response.success,
                "data": response.data,
                "message": response.message,
                "metadata": response.metadata,
            }
            
        except Exception as e:
            return {
                "step": "quality_analysis",
                "success": False,
                "data": None,
                "message": f"Analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
            }
    
    async def _step_optimize_code(self, code: str, quality_report: CodeQualityReport) -> Dict[str, Any]:
        """Optimize code based on quality analysis."""
        
        try:
            response = await self.agents["optimizer"].optimize_code(code)
            
            return {
                "step": "code_optimization",
                "success": response.success,
                "data": response.data,
                "message": response.message,
                "metadata": response.metadata,
            }
            
        except Exception as e:
            return {
                "step": "code_optimization",
                "success": False,
                "data": None,
                "message": f"Optimization failed: {str(e)}",
                "metadata": {"error": str(e)},
            }
    
    async def _step_user_approval(self, 
                                code: str, 
                                quality_report: CodeQualityReport,
                                optimization_result: OptimizationResult) -> Dict[str, Any]:
        """Get final user approval for the generated code."""
        
        try:
            # Create comprehensive approval prompt
            approval_prompt = self._create_approval_prompt(code, quality_report, optimization_result)
            
            # Get user feedback
            feedback = await self.agents["user_proxy"].get_user_feedback(approval_prompt)
            
            return {
                "step": "user_approval",
                "success": True,
                "data": {
                    "approved": feedback.approved,
                    "comments": feedback.comments,
                    "suggestions": feedback.suggestions,
                },
                "message": "User approval obtained",
                "metadata": {
                    "approval_status": feedback.approved,
                    "has_suggestions": bool(feedback.suggestions),
                },
            }
            
        except Exception as e:
            return {
                "step": "user_approval",
                "success": False,
                "data": {"approved": False, "comments": str(e)},
                "message": f"Approval process failed: {str(e)}",
                "metadata": {"error": str(e)},
            }
    
    def _create_approval_prompt(self, 
                              code: str, 
                              quality_report: CodeQualityReport,
                              optimization_result: OptimizationResult) -> str:
        """Create comprehensive approval prompt."""
        
        code_preview = code[:800] + "..." if len(code) > 800 else code
        
        prompt = f"""
☕ **COFFEE CODE GENERATION COMPLETE**

📊 **Quality Report:**
- Quality Score: {quality_report.score}/100
- Coffee Domain Validations: {len([v for v in quality_report.coffee_domain_validations if v.get('valid', False)])}/{len(quality_report.coffee_domain_validations)}
- Issues: {len([i for i in quality_report.issues if i.get('severity') == 'error'])} errors, {len([i for i in quality_report.issues if i.get('severity') == 'warning'])} warnings

⚡ **Optimizations Applied:**
{chr(10).join(f"- {imp}" for imp in optimization_result.improvements[:5])}

📈 **Performance Improvements:**
- Readability: +{optimization_result.performance_gains.get('readability_score', 0):.1f}%
- Maintainability: +{optimization_result.performance_gains.get('maintainability_score', 0):.1f}%
- Coffee Domain Accuracy: +{optimization_result.performance_gains.get('coffee_domain_accuracy', 0):.1f}%

📄 **Generated Code:**
```python
{code_preview}
```

**FINAL APPROVAL REQUIRED**

Please review the complete code and confirm:

1. **APPROVE** ✅ - Code meets your requirements and is ready for use
2. **REJECT** ❌ - Needs complete rework (restart workflow)
3. **SUGGEST** 💡 - Provide specific feedback for minor adjustments

Consider:
- ✅ Coffee brewing calculations accuracy
- ✅ Safety measures for equipment control
- ✅ Code quality and maintainability
- ✅ Documentation completeness
- ✅ Error handling robustness

Your decision: """
        
        return prompt
    
    async def run_streaming_workflow(self, user_requirement: str) -> List[Dict[str, Any]]:
        """Run workflow with streaming progress updates."""
        
        updates = []
        
        try:
            # Start workflow
            updates.append({
                "type": "workflow_start",
                "message": "Starting coffee code generation workflow...",
                "step": "init",
            })
            
            # Generate code
            updates.append({
                "type": "progress",
                "message": "CoffeeCodeGeneratorAgent: Analyzing requirements and generating code...",
                "step": "generation",
            })
            
            generation_result = await self._step_generate_code(user_requirement)
            updates.append({
                "type": "result",
                "step": "generation",
                "data": generation_result,
            })
            
            if not generation_result["success"]:
                updates.append({
                    "type": "error",
                    "message": "Code generation failed",
                    "data": generation_result,
                })
                return updates
            
            # Analyze quality
            updates.append({
                "type": "progress",
                "message": "CodeQualityAnalyzerAgent: Performing comprehensive quality analysis...",
                "step": "analysis",
            })
            
            analysis_result = await self._step_analyze_quality(generation_result["data"])
            updates.append({
                "type": "result",
                "step": "analysis",
                "data": analysis_result,
            })
            
            # Optimize code
            updates.append({
                "type": "progress",
                "message": "CodeOptimizerAgent: Applying performance and maintainability optimizations...",
                "step": "optimization",
            })
            
            optimization_result = await self._step_optimize_code(
                generation_result["data"], 
                analysis_result["data"]
            )
            updates.append({
                "type": "result",
                "step": "optimization",
                "data": optimization_result,
            })
            
            # User approval
            updates.append({
                "type": "progress",
                "message": "Awaiting user approval for final code...",
                "step": "approval",
            })
            
            approval_result = await self._step_user_approval(
                optimization_result["data"].optimized_code,
                analysis_result["data"],
                optimization_result["data"]
            )
            updates.append({
                "type": "result",
                "step": "approval",
                "data": approval_result,
            })
            
            if approval_result["data"]["approved"]:
                updates.append({
                    "type": "success",
                    "message": "Workflow completed successfully! Coffee code approved and ready.",
                    "final_code": optimization_result["data"].optimized_code,
                })
            else:
                updates.append({
                    "type": "rejected",
                    "message": "Workflow rejected by user. Process stopped.",
                })
            
            return updates
            
        except Exception as e:
            updates.append({
                "type": "error",
                "message": f"Workflow error: {str(e)}",
                "error": str(e),
            })
            return updates
    
    def get_workflow_summary(self, workflow_result: Dict[str, Any]) -> str:
        """Generate human-readable workflow summary."""
        
        summary = f"""
☕ **COFFEE CODE GENERATION WORKFLOW SUMMARY**

📋 **Requirements:** {workflow_result["user_requirement"][:100]}...

🔄 **Workflow Steps Completed:** {len(workflow_result["steps"])}

📊 **Final Quality Score:** {workflow_result.get("quality_score", 0)}/100

✅ **User Approval:** {"APPROVED" if workflow_result["user_approval"] else "REJECTED"}

📄 **Final Code Status:** {"Generated and approved" if workflow_result["workflow_success"] else "Not completed"}

**Detailed Steps:**
"""
        
        for step in workflow_result["steps"]:
            status = "✅" if step["success"] else "❌"
            summary += f"{status} {step["step"]}: {step["message"]}\n"
        
        return summary


class SimpleCoffeeWorkflow:
    """Simplified workflow for quick coffee code generation."""
    
    def __init__(self, model_client: ChatCompletionClient):
        """Initialize simple workflow."""
        self.coordinator = CoffeeWorkflowCoordinator(model_client)
    
    async def generate_coffee_code(self, requirement: str) -> str:
        """Simple interface to generate coffee code."""
        
        result = await self.coordinator.run_complete_workflow(requirement)
        
        if result["workflow_success"]:
            return result["final_code"]
        else:
            raise ValueError("Code generation failed or was rejected")
    
    async def interactive_session(self) -> None:
        """Run interactive coffee code generation session."""
        
        print("☕ Coffee Code Generator - Interactive Session")
        print("=" * 50)
        print("Enter your coffee code requirements and let our agents work!")
        print("Example: 'Generate code for espresso brewing calculations'")
        print("Type 'quit' to exit\n")
        
        while True:
            user_input = input("\n💬 Your coffee requirement: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                print("\n🔄 Starting workflow...")
                updates = await self.coordinator.run_streaming_workflow(user_input)
                
                for update in updates:
                    if update["type"] == "success":
                        print(f"\n✅ {update['message']}")
                        if "final_code" in update:
                            print("\n📄 Final Generated Code:")
                            print("-" * 40)
                            print(update["final_code"])
                    elif update["type"] == "error":
                        print(f"❌ {update['message']}")
                    elif update["type"] == "progress":
                        print(f"⏳ {update['message']}")
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")


# Example usage function
async def run_coffee_workflow_example():
    """Example usage of the coffee workflow."""
    
    # This would be called from CLI or Chainlit
    from autogen_core.models import ChatCompletionClient
    
    # Load model configuration
    with open("model_config.yaml", "r") as f:
        model_config = yaml.safe_load(f)
    
    model_client = ChatCompletionClient.load_component(model_config)
    
    # Create workflow
    workflow = CoffeeWorkflowCoordinator(model_client)
    
    # Run example workflow
    result = await workflow.run_complete_workflow(
        "Generate Python code for calculating optimal coffee-to-water ratios for pour-over brewing"
    )
    
    print(workflow.get_workflow_summary(result))
    
    return result


if __name__ == "__main__":
    asyncio.run(run_coffee_workflow_example())