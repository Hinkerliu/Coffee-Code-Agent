"""Code optimization tools for improving coffee domain code performance and maintainability."""

import ast
import re
from typing import Dict, List, Any, Optional, Tuple
import textwrap
from dataclasses import dataclass


@dataclass
class OptimizationSuggestion:
    """Represents a code optimization suggestion."""
    
    category: str  # 'performance', 'readability', 'maintainability', 'coffee_domain'
    description: str
    original_code: str
    optimized_code: str
    benefit: str
    priority: str  # 'high', 'medium', 'low'
    line_range: Optional[Tuple[int, int]] = None


class CoffeeCodeOptimizer:
    """Optimizes coffee domain code for performance and accuracy."""
    
    @staticmethod
    def optimize_mathematical_calculations(code: str) -> List[OptimizationSuggestion]:
        """Optimize mathematical calculations for better performance."""
        suggestions = []
        
        # Look for repeated calculations
        patterns = [
            (r'(\d+\.?\d*)\s*\/\s*(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)', 'Division then multiplication'),
            (r'(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)\s*\/\s*(\d+\.?\d*)', 'Multiplication then division'),
            (r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)\s*\-\s*(\d+\.?\d*)', 'Addition then subtraction'),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                original = match.group()
                
                # Suggest using variables for repeated calculations
                optimized = f"""# Pre-calculate common values
ratio = {match.group(2)}
result = {match.group(1)} / ratio * {match.group(3)}"""
                
                suggestions.append(OptimizationSuggestion(
                    category='performance',
                    description=f'Optimize {description} calculation',
                    original_code=original,
                    optimized_code=optimized,
                    benefit='Improves readability and reduces calculation errors',
                    priority='medium'
                ))
        
        return suggestions
    
    @staticmethod
    def optimize_coffee_constants(code: str) -> List[OptimizationSuggestion]:
        """Optimize coffee-specific constants and calculations."""
        suggestions = []
        
        # Look for magic numbers that should be constants
        magic_numbers = [
            (r'(\d+\.?\d*)\s*#\s*.*(?:ratio|coffee|water)', 'Coffee ratio'),
            (r'(\d+\.?\d*)\s*#\s*.*(?:temperature|temp)', 'Temperature'),
            (r'(\d+\.?\d*)\s*#\s*.*(?:time|brew|minutes)', 'Brew time'),
        ]
        
        for pattern, description in magic_numbers:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                value = match.group(1)
                
                # Create named constants
                if 'ratio' in description.lower():
                    constant_name = 'COFFEE_RATIO'
                    optimized = f"""# Coffee brewing constants
{constant_name} = {value}  # Standard coffee-to-water ratio"""
                elif 'temperature' in description.lower():
                    constant_name = 'OPTIMAL_TEMP_F'
                    optimized = f"""# Coffee brewing constants
{constant_name} = {value}  # Optimal brewing temperature (°F)"""
                elif 'time' in description.lower():
                    constant_name = 'BREW_TIME_MINUTES'
                    optimized = f"""# Coffee brewing constants
{constant_name} = {value}  # Recommended brew time (minutes)"""
                else:
                    continue
                
                suggestions.append(OptimizationSuggestion(
                    category='maintainability',
                    description=f'Replace magic number with named constant for {description}',
                    original_code=value,
                    optimized_code=optimized,
                    benefit='Improves code maintainability and makes intent clearer',
                    priority='high'
                ))
        
        return suggestions
    
    @staticmethod
    def optimize_error_handling(code: str) -> List[OptimizationSuggestion]:
        """Optimize error handling for coffee calculations."""
        suggestions = []
        
        # Look for basic error handling patterns
        if 'try:' in code and 'except:' in code:
            # Suggest specific exception handling
            original = "try:\n    # calculation\nexcept:\n    pass"
            
            optimized = """try:
    # calculation
except ValueError as e:
    raise ValueError(f"Invalid coffee parameter: {e}")
except ZeroDivisionError:
    raise ValueError("Cannot calculate with zero weight")
except Exception as e:
    raise RuntimeError(f"Coffee calculation error: {e}")"""
            
            suggestions.append(OptimizationSuggestion(
                category='maintainability',
                description='Improve error handling specificity',
                original_code=original,
                optimized_code=optimized,
                benefit='Provides better error messages and debugging information',
                priority='high'
            ))
        
        return suggestions
    
    @staticmethod
    def optimize_input_validation(code: str) -> List[OptimizationSuggestion]:
        """Optimize input validation for coffee parameters."""
        suggestions = []
        
        # Look for basic input validation
        validation_patterns = [
            (r'if\s+(\w+)\s*\u003c\s*\d+', 'Basic validation'),
            (r'assert\s+(\w+)\s*\u003e\s*\d+', 'Assertion validation'),
        ]
        
        for pattern, description in validation_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                original = match.group()
                
                optimized = """def validate_coffee_parameters(coffee_g: float, water_g: float, temp_f: float) -> bool:
    \"\"\"Validate coffee brewing parameters.\"\"\"
    if coffee_g <= 0:
        raise ValueError("Coffee weight must be positive")
    if water_g <= 0:
        raise ValueError("Water weight must be positive")
    if temp_f < 195 or temp_f > 205:
        raise ValueError("Temperature must be between 195-205°F")
    return True"""
                
                suggestions.append(OptimizationSuggestion(
                    category='coffee_domain',
                    description=f'Add comprehensive coffee parameter validation',
                    original_code=original,
                    optimized_code=optimized,
                    benefit='Ensures coffee brewing parameters meet industry standards',
                    priority='high'
                ))
        
        return suggestions
    
    @staticmethod
    def optimize_performance(code: str) -> List[OptimizationSuggestion]:
        """Optimize code performance for coffee calculations."""
        suggestions = []
        
        # Look for repeated calculations
        if 'round(' in code:
            # Suggest using Decimal for precision
            original = "round(coffee_weight * ratio, 2)"
            
            optimized = """from decimal import Decimal, ROUND_HALF_UP

def precise_calculation(coffee_weight: float, ratio: float) -> float:
    \"\"\"Calculate with high precision for coffee ratios.\"\"\"
    result = Decimal(str(coffee_weight)) * Decimal(str(ratio))
    return float(result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))"""
            
            suggestions.append(OptimizationSuggestion(
                category='performance',
                description='Use Decimal for precise coffee calculations',
                original_code=original,
                optimized_code=optimized,
                benefit='Improves precision for coffee brewing calculations',
                priority='medium'
            ))
        
        return suggestions
    
    @staticmethod
    def optimize_documentation(code: str) -> List[OptimizationSuggestion]:
        """Optimize code documentation for coffee domain."""
        suggestions = []
        
        # Check for missing docstrings
        if 'def ' in code and '"""' not in code:
            original = "def calculate_ratio(coffee, water):"
            
            optimized = '''def calculate_ratio(coffee_weight: float, water_weight: float) -> float:
    """Calculate coffee-to-water ratio.
    
    Args:
        coffee_weight: Weight of coffee in grams
        water_weight: Weight of water in grams
        
    Returns:
        Coffee-to-water ratio (e.g., 16.67 for 1:16.67)
        
    Raises:
        ValueError: If either weight is not positive
        
    Example:
        >>> calculate_ratio(30, 500)
        16.67
    """'''
            
            suggestions.append(OptimizationSuggestion(
                category='readability',
                description='Add comprehensive docstrings for coffee functions',
                original_code=original,
                optimized_code=optimized,
                benefit='Improves code understanding and usage',
                priority='high'
            ))
        
        return suggestions
    
    @staticmethod
    def optimize_type_hints(code: str) -> List[OptimizationSuggestion]:
        """Add type hints for better code clarity."""
        suggestions = []
        
        # Look for function definitions without type hints
        function_pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(function_pattern, code)
        
        for match in matches:
            func_name = match.group(1)
            params = match.group(2)
            
            if ':' not in params and 'def' in code:
                # Add type hints
                original = f"def {func_name}({params}):"
                
                optimized = f"""def {func_name}(coffee_weight: float, water_weight: float, temperature: float = 200.0) -> float:
    \"\"\"Calculate coffee brewing parameters with type safety.\"\"\""""
                
                suggestions.append(OptimizationSuggestion(
                    category='maintainability',
                    description='Add type hints for better code clarity',
                    original_code=original,
                    optimized_code=optimized,
                    benefit='Improves IDE support and reduces runtime errors',
                    priority='medium'
                ))
        
        return suggestions
    
    @staticmethod
    def optimize_constants_usage(code: str) -> List[OptimizationSuggestion]:
        """Optimize the usage of coffee brewing constants."""
        suggestions = []
        
        # Look for repeated calculations
        if '16.67' in code or '15' in code:
            original = "water_needed = coffee_grams * 16.67"
            
            optimized = """# Coffee brewing constants
from enum import Enum

class BrewMethod(Enum):
    ESPRESSO = {"ratio": 2.0, "temp": 200, "time": 0.5}
    POUR_OVER = {"ratio": 16.67, "temp": 200, "time": 3.5}
    FRENCH_PRESS = {"ratio": 15.0, "temp": 200, "time": 4.0}

water_needed = coffee_grams * BrewMethod.POUR_OVER.value["ratio"]"""
            
            suggestions.append(OptimizationSuggestion(
                category='maintainability',
                description='Use Enum for coffee brewing constants',
                original_code=original,
                optimized_code=optimized,
                benefit='Centralizes configuration and improves maintainability',
                priority='medium'
            ))
        
        return suggestions


class CodeOptimizer:
    """Main code optimization engine."""
    
    @staticmethod
    def get_optimization_suggestions(code: str) -> List[OptimizationSuggestion]:
        """Get all optimization suggestions for the code."""
        suggestions = []
        
        # Collect all optimization suggestions
        suggestions.extend(CoffeeCodeOptimizer.optimize_mathematical_calculations(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_coffee_constants(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_error_handling(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_input_validation(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_performance(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_documentation(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_type_hints(code))
        suggestions.extend(CoffeeCodeOptimizer.optimize_constants_usage(code))
        
        # Remove duplicates based on original code
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion.original_code not in seen:
                seen.add(suggestion.original_code)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    @staticmethod
    def apply_optimizations(code: str, suggestions: List[OptimizationSuggestion]) -> str:
        """Apply optimization suggestions to code."""
        optimized_code = code
        
        # Apply suggestions in order of priority
        high_priority = [s for s in suggestions if s.priority == 'high']
        medium_priority = [s for s in suggestions if s.priority == 'medium']
        low_priority = [s for s in suggestions if s.priority == 'low']
        
        # Apply high priority optimizations
        for suggestion in high_priority:
            optimized_code = optimized_code.replace(suggestion.original_code, suggestion.optimized_code)
        
        return optimized_code
    
    @staticmethod
    def generate_optimization_report(code: str) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        suggestions = CodeOptimizer.get_optimization_suggestions(code)
        
        return {
            'total_suggestions': len(suggestions),
            'by_category': {
                'performance': len([s for s in suggestions if s.category == 'performance']),
                'readability': len([s for s in suggestions if s.category == 'readability']),
                'maintainability': len([s for s in suggestions if s.category == 'maintainability']),
                'coffee_domain': len([s for s in suggestions if s.category == 'coffee_domain']),
            },
            'by_priority': {
                'high': len([s for s in suggestions if s.priority == 'high']),
                'medium': len([s for s in suggestions if s.priority == 'medium']),
                'low': len([s for s in suggestions if s.priority == 'low']),
            },
            'suggestions': [
                {
                    'category': s.category,
                    'description': s.description,
                    'benefit': s.benefit,
                    'priority': s.priority,
                    'original_code': s.original_code,
                    'optimized_code': s.optimized_code
                }
                for s in suggestions
            ]
        }


# Async wrapper functions for agent tools
async def optimize_coffee_code(code: str) -> Dict[str, Any]:
    """Optimize coffee domain code for performance and maintainability."""
    return CodeOptimizer.generate_optimization_report(code)


async def apply_optimizations(code: str, suggestions: List[Dict]) -> str:
    """Apply specific optimizations to code."""
    suggestion_objects = [
        OptimizationSuggestion(
            category=s.get('category', 'general'),
            description=s.get('description', ''),
            original_code=s.get('original_code', ''),
            optimized_code=s.get('optimized_code', ''),
            benefit=s.get('benefit', ''),
            priority=s.get('priority', 'medium')
        )
        for s in suggestions
    ]
    
    return CodeOptimizer.apply_optimizations(code, suggestion_objects)


async def get_performance_improvements(code: str) -> Dict[str, float]:
    """Calculate potential performance improvements."""
    suggestions = CodeOptimizer.get_optimization_suggestions(code)
    
    improvements = {
        'readability_score': 0.0,
        'maintainability_score': 0.0,
        'performance_score': 0.0,
        'coffee_domain_accuracy': 0.0
    }
    
    for suggestion in suggestions:
        if suggestion.category == 'performance':
            improvements['performance_score'] += 10.0
        elif suggestion.category == 'readability':
            improvements['readability_score'] += 15.0
        elif suggestion.category == 'maintainability':
            improvements['maintainability_score'] += 20.0
        elif suggestion.category == 'coffee_domain':
            improvements['coffee_domain_accuracy'] += 25.0
    
    # Cap scores at 100%
    for key in improvements:
        improvements[key] = min(improvements[key], 100.0)
    
    return improvements