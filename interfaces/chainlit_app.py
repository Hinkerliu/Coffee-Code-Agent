"""Chainlit web interface for the coffee multi-agent system."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import chainlit as cl
from typing import List, Any, cast
import asyncio
import yaml
from autogen_core.models import ChatCompletionClient
from autogen_core import CancellationToken
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage

from workflows.coffee_workflow import CoffeeWorkflowCoordinator, SimpleCoffeeWorkflow


@cl.set_starters  # type: ignore
async def set_starters() -> List[cl.Starter]:
    """Define starter messages for the web interface."""
    return [
        cl.Starter(
            label="Espresso Calculator",
            message="Generate Python code for espresso brewing ratio calculations with temperature control",
            icon="☕",
        ),
        cl.Starter(
            label="Pour-over Recipe",
            message="Create a complete pour-over coffee recipe calculator with scaling and timing",
            icon="🫖",
        ),
        cl.Starter(
            label="Cold Brew Timer",
            message="Build a cold brew coffee timer with ratio calculations and safety alerts",
            icon="🧊",
        ),
        cl.Starter(
            label="Coffee Shop Utilities",
            message="Generate coffee shop utilities for recipe scaling, inventory, and brewing guides",
            icon="🏪",
        ),
    ]


@cl.on_chat_start  # type: ignore
async def start_chat() -> None:
    """Initialize the chat session with coffee workflow."""
    try:
        # Check API key configuration first
        from config.settings import settings
        
        # Validate API keys
        has_valid_key = any([
            settings.model.openai_api_key,
            settings.model.azure_openai_api_key,
            settings.model.deepseek_api_key
        ])
        
        if not has_valid_key:
            await cl.Message(
                content="""
❌ **API Key Configuration Error**

No valid API keys found! Please configure at least one API key:

🔧 **Setup Instructions:**
1. Copy `.env.example` to `.env`
2. Get an API key from one of these providers:
   • **DeepSeek**: https://platform.deepseek.com/api_keys
   • **OpenAI**: https://platform.openai.com/api-keys
   • **Azure OpenAI**: https://portal.azure.com/
3. Replace the placeholder in `.env` with your actual API key
4. Restart the application

💡 **Tip:** Run `python setup_api_keys.py` to check your configuration.
                """,
                author="System"
            ).send()
            return
        
        # Check for placeholder values
        if (settings.model.deepseek_api_key and 
            settings.model.deepseek_api_key in ["your_actual_deepseek_api_key_here", "your_deepseek_api_key_here"]):
            await cl.Message(
                content="""
⚠️ **Invalid API Key Detected**

You're using a placeholder API key. Please:

1. Get a real API key from https://platform.deepseek.com/api_keys
2. Replace the placeholder in your `.env` file
3. Restart the application

💡 **Tip:** Run `python setup_api_keys.py` to validate your configuration.
                """,
                author="System"
            ).send()
            return
            
        # Load model configuration
        model_config_path = Path("model_config.yaml")
        if not model_config_path.exists():
            await cl.Message(
                content="❌ Error: model_config.yaml not found. Please configure your model settings.",
                author="System"
            ).send()
            return
            
        with open(model_config_path, "r") as f:
            model_config = yaml.safe_load(f)
        
        # Create model client
        model_client = ChatCompletionClient.load_component(model_config)
        
        # Create workflow coordinator
        workflow_coordinator = CoffeeWorkflowCoordinator(model_client)
        simple_workflow = SimpleCoffeeWorkflow(model_client)
        
        # Store in session
        cl.user_session.set("workflow_coordinator", workflow_coordinator)
        cl.user_session.set("simple_workflow", simple_workflow)
        cl.user_session.set("chat_history", [])
        
        # Welcome message
        welcome = """
☕ **Welcome to the Coffee Code Generator!**

I'm your AI-powered coffee code assistant. I can help you generate Python code for:

🎯 **Coffee Calculations**
- Coffee-to-water ratios
- Temperature conversions
- Recipe scaling
- Brewing timers

🔧 **Equipment Control**
- Temperature monitoring
- Timing alerts
- Safety checks

📊 **Recipe Management**
- Recipe databases
- Scaling functions
- Brewing guides

**How to use:**
1. Describe your coffee code requirement
2. Our agents will generate, analyze, and optimize the code
3. Review and approve the final result

**Try the starters above or type your own requirement!**
        """
        
        await cl.Message(content=welcome, author="CoffeeBot").send()
        
    except Exception as e:
        error_msg = str(e)
        
        # Check for specific API authentication errors
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            await cl.Message(
                content=f"""
❌ **API Authentication Error**

{error_msg}

🔧 **To fix this:**
1. Check your API key in the `.env` file
2. Ensure it's a valid, active API key
3. Verify you have sufficient credits/quota
4. Run `python setup_api_keys.py` to validate

💡 **Need help?** Check the documentation or get a new API key from your provider.
                """,
                author="System"
            ).send()
        else:
            await cl.Message(
                content=f"❌ Error initializing chat: {str(e)}",
                author="System"
            ).send()


@cl.on_message  # type: ignore
async def handle_message(message: cl.Message) -> None:
    """Handle incoming messages with coffee code generation."""
    
    try:
        # Get workflow coordinator from session
        workflow_coordinator = cl.user_session.get("workflow_coordinator")
        if not workflow_coordinator:
            await cl.Message(
                content="❌ Error: Workflow not initialized. Please restart the chat.",
                author="System"
            ).send()
            return
        
        # Add user message to history
        chat_history = cl.user_session.get("chat_history", [])
        chat_history.append({"role": "user", "content": message.content})
        cl.user_session.set("chat_history", chat_history)
        
        # Create progress message
        progress_msg = cl.Message(
            content="🔄 Starting coffee code generation workflow...",
            author="CoffeeBot"
        )
        await progress_msg.send()
        
        # Run streaming workflow
        updates = await workflow_coordinator.run_streaming_workflow(message.content)
        
        # Process updates
        for update in updates:
            await _handle_workflow_update(update)
            
    except Exception as e:
        await cl.Message(
            content=f"❌ Error processing request: {str(e)}",
            author="CoffeeBot"
        ).send()


async def _handle_workflow_update(update: dict[str, Any]) -> None:
    """Handle workflow updates and update the UI."""
    
    update_type = update.get("type", "")
    
    if update_type == "workflow_start":
        # Send a new message instead of updating
        await cl.Message(
            content=f"🚀 {update['message']}",
            author="CoffeeBot"
        ).send()
        
    elif update_type == "progress":
        # Send a new message instead of updating
        await cl.Message(
            content=f"⏳ {update['message']}",
            author="CoffeeBot"
        ).send()
        
    elif update_type == "result":
        step = update.get("step", "")
        data = update.get("data", {})
        
        if step == "generation":
            if data.get("success"):
                await cl.Message(
                    content="✅ **Code Generation Complete!**\n\nCoffeeCodeGeneratorAgent has created your code.",
                    author="CoffeeBot"
                ).send()
            else:
                error_msg = data.get('message', 'Unknown error')
                
                # Check for API authentication errors
                if "authentication" in error_msg.lower() or "api key" in error_msg.lower() or "401" in error_msg:
                    await cl.Message(
                        content=f"""
❌ **Generation Failed: API Authentication Error**

{error_msg}

🔧 **To fix this:**
1. Check your API key in the `.env` file
2. Ensure it's a valid, active API key
3. Verify you have sufficient credits/quota
4. Run `python setup_api_keys.py` to validate your configuration

💡 **Get API keys from:**
• DeepSeek: https://platform.deepseek.com/api_keys
• OpenAI: https://platform.openai.com/api-keys
• Azure OpenAI: https://portal.azure.com/

Please fix your API configuration and try again.
                        """,
                        author="CoffeeBot"
                    ).send()
                else:
                    await cl.Message(
                        content=f"❌ **Generation Failed:** {error_msg}",
                        author="CoffeeBot"
                    ).send()
                
        elif step == "analysis":
            if data.get("success"):
                quality_data = data.get("data", {})
                
                # Handle CodeQualityReport object or dict
                if hasattr(quality_data, 'score'):
                    # It's a CodeQualityReport object
                    score = quality_data.score
                    issues = quality_data.issues
                    coffee_validations = quality_data.coffee_domain_validations
                else:
                    # It's a dict (fallback)
                    score = quality_data.get("score", 0)
                    issues = quality_data.get("issues", [])
                    coffee_validations = quality_data.get("coffee_domain_validations", [])
                
                issues_count = len(issues)
                
                analysis_msg = f"""
📊 **Quality Analysis Complete!**

**CodeQualityAnalyzerAgent Results:**
- Quality Score: **{score}/100**
- Issues Found: **{issues_count}**
- Coffee Domain Validations: **{len(coffee_validations)}**

The agent has analyzed your code for:
- ✅ Syntax and style compliance
- ✅ Security vulnerabilities
- ✅ Coffee domain parameter validation
- ✅ Safety measures for equipment control

Moving to optimization phase...
                """
                await cl.Message(content=analysis_msg, author="CoffeeBot").send()
                
        elif step == "optimization":
            if data.get("success"):
                opt_data = data.get("data", {})
                
                # Handle OptimizationResult object or dict
                if hasattr(opt_data, 'improvements'):
                    # It's an OptimizationResult object
                    improvements = opt_data.improvements
                    performance_gains = opt_data.performance_gains
                else:
                    # It's a dict (fallback)
                    improvements = opt_data.get("improvements", [])
                    performance_gains = opt_data.get("performance_gains", {})
                
                opt_msg = f"""
⚡ **Optimization Complete!**

**CodeOptimizerAgent Applied:**
{chr(10).join(f"- {imp}" for imp in improvements[:5])}

**Performance Improvements:**
- Readability: +{performance_gains.get('readability_score', 0):.1f}%
- Maintainability: +{performance_gains.get('maintainability_score', 0):.1f}%
- Coffee Domain Accuracy: +{performance_gains.get('coffee_domain_accuracy', 0):.1f}%
                """
                await cl.Message(content=opt_msg, author="CoffeeBot").send()
                
        elif step == "approval":
            if data.get("success"):
                approved = data.get("data", {}).get("approved", False)
                
                if approved:
                    await cl.Message(
                        content="✅ **User Approved!** Workflow completed successfully.",
                        author="CoffeeBot"
                    ).send()
                else:
                    await cl.Message(
                        content="❌ **User Rejected!** Code generation stopped.",
                        author="CoffeeBot"
                    ).send()
                    
    elif update_type == "success":
        # Final success with code
        final_code = update.get("final_code", "")
        
        # Create final message
        final_msg = f"""
🎉 **Coffee Code Generation Complete!**

Your coffee-related Python code has been successfully generated, analyzed, optimized, and approved.

```python
{final_code}
```

**What you can do:**
- Copy the code above
- Save it to a Python file
- Run it in your coffee application
- Use it as a starting point for your project

**Features included:**
- ✅ Coffee brewing calculations
- ✅ Input validation
- ✅ Error handling
- ✅ Type hints
- ✅ Documentation
- ✅ Safety measures
        """
        
        await cl.Message(content=final_msg, author="CoffeeBot").send()
        
        # Save to session
        chat_history = cl.user_session.get("chat_history", [])
        chat_history.append({"role": "assistant", "content": final_code})
        cl.user_session.set("chat_history", chat_history)
        
    elif update_type == "rejected":
        await cl.Message(
            content=f"❌ {update['message']}",
            author="CoffeeBot"
        ).send()
        
    elif update_type == "error":
        await cl.Message(
            content=f"❌ **Error:** {update.get('message', 'Unknown error')}",
            author="CoffeeBot"
        ).send()


@cl.action_callback("approve_code")  # type: ignore
async def approve_code(action):
    """Handle code approval action."""
    
    await cl.Message(
        content="✅ **Code Approved!** Thank you for your feedback.",
        author="CoffeeBot"
    ).send()
    
    return "APPROVE"


@cl.action_callback("reject_code")  # type: ignore
async def reject_code(action):
    """Handle code rejection action."""
    
    await cl.Message(
        content="❌ **Code Rejected.** Would you like to try a different approach?",
        author="CoffeeBot"
    ).send()
    
    return "REJECT"


@cl.action_callback("suggest_improvements")  # type: ignore
async def suggest_improvements(action):
    """Handle improvement suggestions action."""
    
    res = await cl.AskUserMessage(
        content="💡 **What improvements would you like to suggest?**",
        author="CoffeeBot"
    ).send()
    
    if res:
        return f"SUGGEST: {res['output']}"
    
    return "NO_SUGGESTIONS"


@cl.on_stop  # type: ignore
async def on_stop():
    """Handle chat stop event."""
    
    print("🛑 Chat session ended")


# Utility functions for Chainlit
async def run_chainlit_app():
    """Run the Chainlit app (for development/testing)."""
    import os
    os.system("chainlit run interfaces/chainlit_app.py -w")


if __name__ == "__main__":
    # This is for development - normally run with: chainlit run interfaces/chainlit_app.py
    import asyncio
    asyncio.run(run_chainlit_app())