"""Code analysis tools for validating coffee domain code quality and safety."""

import ast
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import tempfile
import os

from config.settings import settings


@dataclass
class CodeQualityIssue:
    """Represents a code quality issue."""
    
    severity: str  # 'error', 'warning', 'info'
    message: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class CoffeeDomainValidation:
    """Represents coffee domain specific validation."""
    
    parameter: str
    value: Any
    valid: bool
    message: str
    recommendation: Optional[str] = None


class CoffeeDomainValidator:
    """Validates coffee-specific parameters in generated code."""
    
    # Coffee brewing standards
    TEMP_MIN = settings.coffee.safety_temp_min
    TEMP_MAX = settings.coffee.safety_temp_max
    TEMP_OPTIMAL_MIN = 195
    TEMP_OPTIMAL_MAX = 205
    
    RATIO_MIN = 15
    RATIO_MAX = 17
    
    SAFETY_CHECKS = [
        'temperature',
        'pressure',
        'time',
        'weight',
        'volume'
    ]
    
    @staticmethod
    def extract_numeric_constants(code: str) -> Dict[str, List[float]]:
        """Extract numeric constants from code for validation."""
        try:
            tree = ast.parse(code)
            constants = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Num):
                    constants.append(node.n)
                elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    constants.append(float(node.value))
            
            return {'numeric_constants': constants}
        except Exception:
            return {'numeric_constants': []}
    
    @staticmethod
    def validate_temperature_constants(code: str) -> List[CoffeeDomainValidation]:
        """Validate temperature constants in the code."""
        validations = []
        
        # Look for temperature patterns
        temp_patterns = [
            r'(?:temperature|temp)\s*=\s*(\d+(?:\.\d+)?)',
            r'(?:water_temp|brew_temp)\s*=\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*°?F',
            r'(\d+(?:\.\d+)?)\s*°?C'
        ]
        
        for pattern in temp_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                try:
                    temp = float(match.group(1))
                    
                    # Check if it's likely Fahrenheit (90-250 range)
                    if 90 <= temp <= 250:
                        valid = CoffeeDomainValidator.TEMP_MIN <= temp <= CoffeeDomainValidator.TEMP_MAX
                        message = f"Temperature {temp}°F"
                        
                        if temp < CoffeeDomainValidator.TEMP_OPTIMAL_MIN:
                            recommendation = f"Consider increasing to {CoffeeDomainValidator.TEMP_OPTIMAL_MIN}-{CoffeeDomainValidator.TEMP_OPTIMAL_MAX}°F for optimal extraction"
                        elif temp > CoffeeDomainValidator.TEMP_OPTIMAL_MAX:
                            recommendation = f"Consider decreasing to {CoffeeDomainValidator.TEMP_OPTIMAL_MIN}-{CoffeeDomainValidator.TEMP_OPTIMAL_MAX}°F"
                        else:
                            recommendation = None
                            
                        validations.append(CoffeeDomainValidation(
                            parameter="temperature",
                            value=temp,
                            valid=valid,
                            message=message,
                            recommendation=recommendation
                        ))
                        
                except ValueError:
                    continue
        
        return validations
    
    @staticmethod
    def validate_ratio_constants(code: str) -> List[CoffeeDomainValidation]:
        """Validate coffee-to-water ratios in the code."""
        validations = []
        
        # Look for ratio patterns
        ratio_patterns = [
            r'(?:ratio|coffee_ratio)\s*=\s*(\d+(?:\.\d+)?)',
            r'(?:coffee|water)_weight.*?(\d+(?:\.\d+)?)',
            r'(?:water|coffee)_weight.*?(\d+(?:\.\d+)?)',
            r'1\s*:\s*(\d+(?:\.\d+)?)'
        ]
        
        # Extract pairs of coffee/water weights
        coffee_weights = []
        water_weights = []
        
        for pattern in ratio_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    if "coffee" in pattern.lower():
                        coffee_weights.append(value)
                    elif "water" in pattern.lower():
                        water_weights.append(value)
                    elif "ratio" in pattern.lower():
                        valid = CoffeeDomainValidator.RATIO_MIN <= value <= CoffeeDomainValidator.RATIO_MAX
                        validations.append(CoffeeDomainValidation(
                            parameter="ratio",
                            value=value,
                            valid=valid,
                            message=f"Coffee-to-water ratio 1:{value}",
                            recommendation=f"Recommended range: 1:{CoffeeDomainValidator.RATIO_MIN}-{CoffeeDomainValidator.RATIO_MAX}"
                        ))
                except ValueError:
                    continue
        
        # Calculate ratios from weight pairs
        if coffee_weights and water_weights and len(coffee_weights) == len(water_weights):
            for coffee, water in zip(coffee_weights, water_weights):
                if coffee > 0:
                    ratio = water / coffee
                    valid = CoffeeDomainValidator.RATIO_MIN <= ratio <= CoffeeDomainValidator.RATIO_MAX
                    validations.append(CoffeeDomainValidation(
                        parameter="ratio",
                        value=ratio,
                        valid=valid,
                        message=f"Calculated ratio 1:{ratio:.2f}",
                        recommendation=f"Recommended range: 1:{CoffeeDomainValidator.RATIO_MIN}-{CoffeeDomainValidator.RATIO_MAX}"
                    ))
        
        return validations
    
    @staticmethod
    def check_safety_measures(code: str) -> List[CodeQualityIssue]:
        """Check for safety measures in equipment control code."""
        issues = []
        
        # Check for temperature safety
        if any(word in code.lower() for word in ['temperature', 'temp', 'heat', 'boil']):
            if 'safety' not in code.lower() and 'limit' not in code.lower():
                issues.append(CodeQualityIssue(
                    severity='warning',
                    message='Code involving temperature/heating should include safety limits',
                    rule_id='SAFETY_TEMP'
                ))
        
        # Check for time safety
        if any(word in code.lower() for word in ['time', 'duration', 'timer']):
            if 'max' not in code.lower() and 'limit' not in code.lower():
                issues.append(CodeQualityIssue(
                    severity='warning',
                    message='Code involving timing should include maximum duration limits',
                    rule_id='SAFETY_TIME'
                ))
        
        # Check for input validation
        if 'input(' in code or 'raw_input(' in code:
            if 'float(' not in code and 'int(' not in code:
                issues.append(CodeQualityIssue(
                    severity='error',
                    message='User input should be properly validated and converted',
                    rule_id='INPUT_VALIDATION'
                ))
        
        return issues


class CodeAnalyzer:
    """Analyzes code quality and provides comprehensive reports."""
    
    @staticmethod
    def analyze_syntax(code: str) -> List[CodeQualityIssue]:
        """Check code syntax using AST parsing."""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(CodeQualityIssue(
                severity='error',
                message=f'Syntax error: {e.msg}',
                line_number=e.lineno,
                code_snippet=e.text
            ))
        except Exception as e:
            issues.append(CodeQualityIssue(
                severity='error',
                message=f'Parse error: {str(e)}'
            ))
        
        return issues
    
    @staticmethod
    def analyze_style(code: str) -> List[CodeQualityIssue]:
        """Perform basic style analysis."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            
            # Check for trailing whitespace
            if line != line.rstrip():
                issues.append(CodeQualityIssue(
                    severity='warning',
                    message='Trailing whitespace',
                    line_number=i,
                    code_snippet=line
                ))
            
            # Check for very long lines
            if len(line) > 100:
                issues.append(CodeQualityIssue(
                    severity='warning',
                    message='Line too long (should be <= 100 characters)',
                    line_number=i,
                    code_snippet=line[:50] + '...'
                ))
            
            # Check for missing docstrings in functions
            if line.strip().startswith('def '):
                # Look for docstring in next few lines
                found_docstring = False
                for j in range(i, min(i+5, len(lines))):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        found_docstring = True
                        break
                
                if not found_docstring:
                    issues.append(CodeQualityIssue(
                        severity='warning',
                        message='Function missing docstring',
                        line_number=i,
                        code_snippet=line
                    ))
        
        return issues
    
    @staticmethod
    def analyze_security(code: str) -> List[CodeQualityIssue]:
        """Perform basic security analysis."""
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']*["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']*["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']*["\']', 'Hardcoded secret'),
            (r'["\']sk-[a-zA-Z0-9]+["\']', 'OpenAI API key'),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                issues.append(CodeQualityIssue(
                    severity='error',
                    message=message,
                    code_snippet=match.group()
                ))
        
        # Check for unsafe operations
        unsafe_patterns = [
            'eval(',
            'exec(',
            '__import__',
            'subprocess.call',
            'os.system'
        ]
        
        for pattern in unsafe_patterns:
            if pattern in code:
                issues.append(CodeQualityIssue(
                    severity='error',
                    message=f'Potentially unsafe operation: {pattern}',
                    rule_id='SECURITY_UNSAFE'
                ))
        
        return issues
    
    @staticmethod
    def run_static_analysis(code: str) -> Dict[str, List[CodeQualityIssue]]:
        """Run comprehensive static analysis on code."""
        return {
            'syntax': CodeAnalyzer.analyze_syntax(code),
            'style': CodeAnalyzer.analyze_style(code),
            'security': CodeAnalyzer.analyze_security(code),
            'coffee_domain': [
                CodeQualityIssue(
                    severity=validation.valid and 'info' or 'error',
                    message=f"{validation.parameter}: {validation.message}",
                    rule_id=f'COFFEE_{validation.parameter.upper()}'
                )
                for validation in CoffeeDomainValidator.validate_temperature_constants(code) +
                               CoffeeDomainValidator.validate_ratio_constants(code)
            ],
            'safety': CoffeeDomainValidator.check_safety_measures(code)
        }


# Async wrapper functions for agent tools
async def analyze_code_quality(code: str) -> Dict[str, List[Dict]]:
    """Analyze code quality and return structured results."""
    analysis = CodeAnalyzer.run_static_analysis(code)
    
    # Convert to serializable format
    return {
        category: [
            {
                'severity': issue.severity,
                'message': issue.message,
                'line_number': issue.line_number,
                'code_snippet': issue.code_snippet,
                'rule_id': issue.rule_id
            }
            for issue in issues
        ]
        for category, issues in analysis.items()
    }


async def validate_coffee_parameters(code: str) -> Dict[str, List[Dict]]:
    """Validate coffee-specific parameters in code."""
    validations = []
    
    temp_validations = CoffeeDomainValidator.validate_temperature_constants(code)
    ratio_validations = CoffeeDomainValidator.validate_ratio_constants(code)
    
    for validation in temp_validations + ratio_validations:
        validations.append({
            'parameter': validation.parameter,
            'value': validation.value,
            'valid': validation.valid,
            'message': validation.message,
            'recommendation': validation.recommendation
        })
    
    return {'coffee_validations': validations}


async def check_code_safety(code: str) -> Dict[str, List[str]]:
    """Check for safety issues in equipment control code."""
    safety_issues = CoffeeDomainValidator.check_safety_measures(code)
    
    return {
        'safety_warnings': [issue.message for issue in safety_issues],
        'safety_rules': [issue.rule_id for issue in safety_issues if issue.rule_id]
    }