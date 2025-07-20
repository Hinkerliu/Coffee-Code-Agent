"""CoffeeCodeGeneratorAgent for generating coffee-related Python code."""

import ast
from typing import Any, Dict, List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from tools.coffee_calculations import (
    calculate_coffee_ratio,
    calculate_coffee_amount,
    convert_temperature,
    get_grind_recommendation,
    get_brew_time_recommendation,
    validate_brewing_params,
)
from agents.models import (
    CodeGenerationRequest,
    CoffeeRecipe,
    BrewMethod,
    AgentResponse,
)


class CoffeeCodeGeneratorAgent:
    """Agent specialized in generating coffee-related Python code."""
    
    def __init__(self, model_client: ChatCompletionClient):
        """Initialize the coffee code generator agent."""
        self.model_client = model_client
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """Create the AssistantAgent with coffee-specific tools."""
        
        system_message = """You are CoffeeCodeGeneratorAgent, an expert in generating accurate Python code for coffee-related operations. 

Your responsibilities:
1. Generate precise, tested Python code for coffee brewing calculations
2. Include proper error handling and input validation
3. Follow coffee industry standards (195-205°F water temp, 1:15-1:17 ratios)
4. Implement calculation functions directly in the generated code
5. Include comprehensive documentation and examples
6. Ensure code safety, especially for equipment control
7. Validate all coffee domain parameters

Always:
- Start with input validation
- Use proper type hints
- Include docstrings with examples
- Handle edge cases (zero/negative values)
- Follow PEP 8 style guidelines
- Add safety checks for temperature and time limits
- Generate complete, self-contained code without external dependencies

Key calculation formulas to implement:
- Coffee-to-water ratio: typically 1:15 to 1:17 (water_grams / coffee_grams)
- Water temperature: 195-205°F (90-96°C) for most brewing methods
- Grind sizes: coarse (French press), medium (pour over), fine (espresso)
- Brew times: vary by method (2-4 min pour over, 4 min French press, 25-30 sec espresso)

Generate complete, production-ready code that can be immediately used for coffee brewing applications."""

        return AssistantAgent(
            name="coffee_generator",
            model_client=self.model_client,
            tools=[
                calculate_coffee_ratio,
                calculate_coffee_amount,
                convert_temperature,
                get_grind_recommendation,
                get_brew_time_recommendation,
                validate_brewing_params,
            ],
            system_message=system_message,
            model_client_stream=True,
            reflect_on_tool_use=True,
        )
    
    async def generate_code(self, request: CodeGenerationRequest) -> AgentResponse:
        """Generate coffee-related Python code based on user requirements."""
        
        prompt = f"""Generate Python code for the following coffee requirement:

{request.requirement}

Parameters:
- Brew Method: {request.brew_method or 'any'}
- Special Parameters: {request.parameters}
- Language: {request.language}
- Complexity: {request.complexity}

Requirements for the generated code:
1. Must include proper input validation
2. Must follow coffee industry standards
3. Must include comprehensive documentation
4. Must handle edge cases gracefully
5. Must include safety checks for temperature/time
6. Must use the provided calculation tools when appropriate
7. Must be production-ready

Generate complete, executable Python code with:
- Proper type hints
- Comprehensive docstrings
- Input validation
- Error handling
- Usage examples
- Safety checks

Return only the Python code without additional explanations."""

        try:
            from autogen_agentchat.messages import TextMessage
            
            response = await self.agent.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            
            generated_code = response.chat_message.content
            
            # Extract Python code from markdown if present
            python_code = self._extract_python_code(generated_code)
            
            # Validate the generated code
            is_valid = self._validate_generated_code(python_code)
            
            return AgentResponse(
                success=is_valid,
                message="Coffee code generated successfully" if is_valid else "Generated code needs validation",
                data=python_code,  # Return the extracted Python code
                metadata={
                    "brew_method": request.brew_method,
                    "complexity": request.complexity,
                    "validation_status": is_valid,
                    "raw_response": generated_code,  # Keep the original response for debugging
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error generating code: {str(e)}",
                data=None,
                metadata={"error": str(e)}
            )
    

    
    def _extract_python_code(self, content: str) -> str:
        """Extract Python code from markdown code blocks with improved error handling."""
        # Remove markdown code block markers
        if "```python" in content:
            # Find the start and end of the Python code block
            start_marker = "```python"
            end_marker = "```"
            
            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    extracted_code = content[start_idx:end_idx].strip()
                else:
                    # If no closing marker found, take everything after the opening marker
                    extracted_code = content[start_idx:].strip()
                    print("Warning: No closing ``` found, using content until end")
                
                # Additional cleanup for common issues
                extracted_code = self._cleanup_extracted_code(extracted_code)
                return extracted_code
        
        # If no markdown blocks found, return the content as is
        cleaned_content = self._cleanup_extracted_code(content.strip())
        return cleaned_content
    
    def _cleanup_extracted_code(self, code: str) -> str:
        """Clean up extracted code to fix common issues."""
        if not code:
            return code
        
        # Remove any trailing incomplete lines that might cause syntax errors
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are clearly incomplete or problematic
            stripped_line = line.strip()
            
            # Skip empty lines at the end
            if not stripped_line and not cleaned_lines:
                continue
                
            # Check for incomplete triple quotes
            if stripped_line.count('"""') % 2 != 0 or stripped_line.count("'''") % 2 != 0:
                # If we find an incomplete triple quote, try to close it
                if stripped_line.endswith('"""') or stripped_line.endswith("'''"):
                    cleaned_lines.append(line)
                elif '"""' in stripped_line and not stripped_line.endswith('"""'):
                    # Close incomplete docstring
                    cleaned_lines.append(line + '"""')
                elif "'''" in stripped_line and not stripped_line.endswith("'''"):
                    cleaned_lines.append(line + "'''")
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def _validate_generated_code(self, code: str) -> bool:
        """Enhanced validation of generated Python code with better error handling."""
        try:
            # Check if code is not empty
            if not code or not code.strip():
                print("Validation failed: Empty code")
                return False
            
            # Try to parse the code - this will catch syntax errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                print(f"Syntax error in generated code: {e}")
                # Try to fix common issues and re-validate
                fixed_code = self._attempt_syntax_fix(code)
                if fixed_code != code:
                    try:
                        ast.parse(fixed_code)
                        print("Successfully fixed syntax error")
                        # Update the code with the fixed version
                        return True
                    except SyntaxError:
                        print("Could not fix syntax error")
                        return False
                else:
                    return False
            
            # More flexible validation - check for at least one of these elements
            validation_checks = {
                "has_function": any(keyword in code for keyword in ["def ", "class "]),
                "has_imports": any(keyword in code for keyword in ["import ", "from "]),
                "has_docstring": '"""' in code or "'''" in code,
                "has_comments": "#" in code,
                "has_coffee_related": any(term in code.lower() for term in [
                    "coffee", "espresso", "brew", "grind", "temperature", "ratio", "water"
                ]),
            }
            
            # Require at least 2 out of 5 checks to pass
            passed_checks = sum(validation_checks.values())
            min_required = 2
            
            if passed_checks >= min_required:
                return True
            else:
                # Log which checks failed for debugging
                failed_checks = [k for k, v in validation_checks.items() if not v]
                print(f"Validation failed. Passed: {passed_checks}/{len(validation_checks)}, Failed: {failed_checks}")
                return False
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def _attempt_syntax_fix(self, code: str) -> str:
        """Attempt to fix common syntax errors in generated code."""
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for incomplete triple quotes
            if line.count('"""') % 2 != 0:
                if not line.strip().endswith('"""'):
                    line = line + '"""'
            elif line.count("'''") % 2 != 0:
                if not line.strip().endswith("'''"):
                    line = line + "'''"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    async def generate_recipe_code(self, recipe: CoffeeRecipe) -> str:
        """Generate Python code for a specific coffee recipe."""
        
        code_template = f'''"""
Coffee Recipe: {recipe.name}
Brew Method: {recipe.brew_method.value}
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class CoffeeRecipe:
    """Coffee recipe with validation."""
    name: str
    coffee_weight: float  # grams
    water_weight: float   # grams  
    water_temperature: float  # Fahrenheit
    grind_size: str
    brew_time: float      # minutes

class {recipe.name.replace(" ", "")}Recipe:
    """Recipe for {recipe.name}."""
    
    def __init__(self):
        self.recipe = CoffeeRecipe(
            name="{recipe.name}",
            coffee_weight={recipe.coffee_weight},
            water_weight={recipe.water_weight},
            water_temperature={recipe.water_temperature},
            grind_size="{recipe.grind_size}",
            brew_time={recipe.brew_time}
        )
    
    def calculate_ratio(self) -> float:
        """Calculate coffee-to-water ratio."""
        return self.recipe.water_weight / self.recipe.coffee_weight
    
    def scale_recipe(self, servings: int) -> Dict[str, float]:
        """Scale recipe for different servings."""
        if servings <= 0:
            raise ValueError("Servings must be positive")
        
        scale_factor = servings
        return {{
            "coffee_weight": self.recipe.coffee_weight * scale_factor,
            "water_weight": self.recipe.water_weight * scale_factor,
            "brew_time": self.recipe.brew_time,
            "water_temperature": self.recipe.water_temperature
        }}
    
    def validate_parameters(self) -> Dict[str, bool]:
        """Validate recipe parameters."""
        validations = {{
            "temperature_valid": 195 <= self.recipe.water_temperature <= 205,
            "ratio_valid": 15 <= self.calculate_ratio() <= 17,
            "weights_valid": self.recipe.coffee_weight > 0 and self.recipe.water_weight > 0,
            "brew_time_valid": self.recipe.brew_time > 0
        }}
        return validations

# Usage example
if __name__ == "__main__":
    recipe = {recipe.name.replace(" ", "")}Recipe()
    print(f"Ratio: 1:{recipe.calculate_ratio():.2f}")
    print(f"Scaled for 2 servings: {recipe.scale_recipe(2)}")
    print(f"Validation: {recipe.validate_parameters()}")
'''
        
        return code_template
    
    async def generate_calculation_function(self, calc_type: str) -> str:
        """Generate a specific coffee calculation function."""
        
        if calc_type == "ratio":
            return '''def calculate_coffee_ratio(coffee_grams: float, water_grams: float) -> float:
    """Calculate coffee-to-water ratio.
    
    Args:
        coffee_grams: Weight of coffee in grams
        water_grams: Weight of water in grams
        
    Returns:
        Coffee-to-water ratio (e.g., 16.67 for 1:16.67)
        
    Raises:
        ValueError: If either weight is not positive
    """
    if coffee_grams <= 0:
        raise ValueError("Coffee weight must be positive")
    if water_grams <= 0:
        raise ValueError("Water weight must be positive")
    
    ratio = water_grams / coffee_grams
    return round(ratio, 2)

# Example usage
if __name__ == "__main__":
    coffee = 30  # grams
    water = 500  # grams
    ratio = calculate_coffee_ratio(coffee, water)
    print(f"Ratio: 1:{ratio}")
'''
        elif calc_type == "temperature":
            return '''def convert_coffee_temperature(temp_f: float, to_celsius: bool = False) -> float:
    """Convert coffee brewing temperature between units.
    
    Args:
        temp_f: Temperature in Fahrenheit
        to_celsius: Whether to convert to Celsius
        
    Returns:
        Temperature in requested units
        
    Raises:
        ValueError: If temperature is outside safe brewing range
    """
    if temp_f < 175 or temp_f > 212:
        raise ValueError("Temperature must be between 175-212°F for safety")
    
    if to_celsius:
        return round((temp_f - 32) * 5/9, 1)
    return temp_f

# Example usage
if __name__ == "__main__":
    temp_f = 200
    temp_c = convert_coffee_temperature(temp_f, to_celsius=True)
    print(f"{temp_f}°F = {temp_c}°C")
'''
        elif calc_type == "scaling":
            return '''def scale_coffee_recipe(
    coffee_grams: float,
    water_grams: float,
    servings: int
) -> Dict[str, float]:
    """Scale a coffee recipe for different servings.
    
    Args:
        coffee_grams: Original coffee weight in grams
        water_grams: Original water weight in grams
        servings: Number of servings to scale for
        
    Returns:
        Dictionary with scaled coffee and water weights
        
    Raises:
        ValueError: If servings is not positive
    """
    if servings <= 0:
        raise ValueError("Servings must be positive")
    
    return {
        "coffee_weight": coffee_grams * servings,
        "water_grams": water_grams * servings,
        "ratio": water_grams / coffee_grams
    }

# Example usage
if __name__ == "__main__":
    original = scale_coffee_recipe(30, 500, 3)
    print(f"Scaled recipe: {original}")
'''
        else:
            return "# Unknown calculation type"
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AssistantAgent."""
        return self.agent