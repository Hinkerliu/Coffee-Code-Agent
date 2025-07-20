"""CLI interface for the coffee multi-agent workflow."""

import asyncio
import argparse
import sys
from typing import Any, Dict, Optional

from autogen_core.models import ChatCompletionClient
import yaml

from workflows.coffee_workflow import (
    CoffeeWorkflowCoordinator,
    SimpleCoffeeWorkflow,
)


class CoffeeCLI:
    """Command-line interface for coffee code generation."""
    
    def __init__(self):
        """Initialize CLI with model configuration."""
        self.model_client = None
        self.workflow_coordinator = None
        self.simple_workflow = None
    
    async def initialize(self) -> bool:
        """Initialize CLI with model configuration."""
        try:
            with open("model_config.yaml", "r") as f:
                model_config = yaml.safe_load(f)
            
            self.model_client = ChatCompletionClient.load_component(model_config)
            self.workflow_coordinator = CoffeeWorkflowCoordinator(self.model_client)
            self.simple_workflow = SimpleCoffeeWorkflow(self.model_client)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {str(e)}")
            return False
    
    async def run_interactive(self) -> None:
        """Run interactive CLI session."""
        
        if not await self.initialize():
            return
        
        print("☕ Coffee Code Generator CLI")
        print("=" * 50)
        print("Welcome! I'll help you generate coffee-related Python code.")
        print("Our agents will:")
        print("  1. Generate code based on your requirements")
        print("  2. Analyze quality and safety")
        print("  3. Optimize for performance")
        print("  4. Get your final approval")
        print("\nType 'help' for commands or 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("\n🎯 coffee-cli> ").strip()
                
                if not user_input or user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye! Enjoy your perfectly brewed coffee code! ☕")
                    break
                
                if user_input.lower() == "help":
                    self._show_help()
                    continue
                
                if user_input.lower() in ["clear", "cls"]:
                    print("\033[2J\033[1;1H", end="")  # Clear screen
                    continue
                
                # Process the requirement
                await self._process_requirement(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting... Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def _process_requirement(self, requirement: str) -> None:
        """Process a coffee code generation requirement."""
        
        print(f"\n🔄 Processing: {requirement}")
        print("-" * 50)
        
        try:
            # Run streaming workflow
            updates = await self.workflow_coordinator.run_streaming_workflow(requirement)
            
            for update in updates:
                await self._handle_update(update)
                
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
    
    async def _handle_update(self, update: Dict[str, Any]) -> None:
        """Handle workflow update."""
        
        update_type = update.get("type", "")
        
        if update_type == "workflow_start":
            print(f"🚀 {update['message']}")
            
        elif update_type == "progress":
            print(f"⏳ {update['message']}")
            
        elif update_type == "result":
            step = update.get("step", "")
            data = update.get("data", {})
            
            if step == "generation":
                if data.get("success"):
                    print("✅ Code generation completed")
                else:
                    print(f"❌ Generation failed: {data.get('message', 'Unknown error')}")
                    
            elif step == "analysis":
                if data.get("success"):
                    quality_data = data.get("data", {})
                    score = quality_data.get("score", 0)
                    print(f"📊 Quality analysis: {score}/100")
                    
            elif step == "optimization":
                if data.get("success"):
                    opt_data = data.get("data", {})
                    improvements = opt_data.get("improvements", [])
                    print(f"⚡ Applied {len(improvements)} optimizations")
                    
            elif step == "approval":
                if data.get("success"):
                    approved = data.get("data", {}).get("approved", False)
                    if approved:
                        print("✅ User approved the final code")
                    else:
                        print("❌ User rejected the code")
                        
        elif update_type == "success":
            print(f"\n🎉 {update['message']}")
            if "final_code" in update:
                print(f"\n{'='*60}")
                print("📄 FINAL GENERATED CODE")
                print(f"{'='*60}")
                print(update["final_code"])
                
                # Save to file
                await self._save_code(update["final_code"], requirement="generated")
                
        elif update_type == "rejected":
            print(f"\n❌ {update['message']}")
            
        elif update_type == "error":
            print(f"\n❌ Error: {update.get('message', 'Unknown error')}")
    
    async def _save_code(self, code: str, requirement: str) -> None:
        """Save generated code to file."""
        
        import re
        import os
        from datetime import datetime
        
        # Create filename from requirement
        filename = re.sub(r'[^\w\s-]', '', requirement.lower())
        filename = re.sub(r'[-\s]+', '_', filename)
        filename = f"coffee_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        filepath = os.path.join("output", filename)
        
        try:
            with open(filepath, "w") as f:
                f.write(f'# Generated by Coffee Code Generator\n')
                f.write(f'# Requirement: {requirement}\n')
                f.write(f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                f.write(code)
            
            print(f"💾 Code saved to: {filepath}")
            
        except Exception as e:
            print(f"⚠️  Could not save file: {str(e)}")
    
    def _show_help(self) -> None:
        """Show CLI help."""
        
        help_text = """
☕ Coffee Code Generator CLI - Help

**Commands:**
- help                - Show this help message
- quit/exit/q         - Exit the application
- clear/cls           - Clear the screen

**Usage:**
Simply describe what coffee-related code you need:
- "Generate code for espresso ratio calculations"
- "Create a coffee recipe scaling function"
- "Build temperature conversion utilities"
- "Make a complete pour-over brewing calculator"

**Examples:**
- "Generate Python code for calculating coffee-to-water ratios"
- "Create a function to scale cold brew recipes"
- "Build espresso extraction yield calculator"
- "Make a complete coffee brewing timer with temperature alerts"

The agents will:
1. Generate code based on your requirements
2. Analyze quality and safety
3. Optimize for performance
4. Get your final approval
        """
        print(help_text)
    
    async def run_batch(self, requirements_file: str) -> None:
        """Run batch processing from file."""
        
        if not await self.initialize():
            return
        
        try:
            with open(requirements_file, "r") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            print(f"📁 Processing {len(requirements)} requirements from {requirements_file}")
            
            for i, requirement in enumerate(requirements, 1):
                print(f"\n🔢 Processing requirement {i}/{len(requirements)}: {requirement}")
                
                try:
                    result = await self.workflow_coordinator.run_complete_workflow(requirement)
                    
                    if result["workflow_success"]:
                        print(f"✅ Successfully processed: {requirement}")
                        await self._save_code(result["final_code"], requirement)
                    else:
                        print(f"❌ Failed to process: {requirement}")
                        
                except Exception as e:
                    print(f"❌ Error processing requirement {i}: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Batch processing failed: {str(e)}")
    
    async def run_single(self, requirement: str) -> None:
        """Run single requirement processing."""
        
        if not await self.initialize():
            return
        
        print(f"🎯 Processing: {requirement}")
        
        try:
            result = await self.workflow_coordinator.run_complete_workflow(requirement)
            
            if result["workflow_success"]:
                print("\n🎉 Successfully generated coffee code!")
                print(self.workflow_coordinator.get_workflow_summary(result))
                await self._save_code(result["final_code"], requirement)
            else:
                print("\n❌ Code generation was not completed")
                
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="Coffee Code Generator CLI - Generate coffee-related Python code with AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  coffee-cli                    # Start interactive mode
  coffee-cli -r "Generate espresso ratio calculator"  # Single requirement
  coffee-cli -f requirements.txt  # Batch processing from file
  coffee-cli -i                 # Interactive mode (default)
        """
    )
    
    parser.add_argument(
        "-r", "--requirement",
        type=str,
        help="Single coffee code requirement to process"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="File containing requirements (one per line)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode (default)"
    )
    
    args = parser.parse_args()
    
    cli = CoffeeCLI()
    
    async def run():
        if args.requirement:
            await cli.run_single(args.requirement)
        elif args.file:
            await cli.run_batch(args.file)
        else:
            await cli.run_interactive()
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()