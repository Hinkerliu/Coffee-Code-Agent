"""Pydantic models for the coffee multi-agent system."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class BrewMethod(str, Enum):
    """Supported coffee brewing methods."""
    ESPRESSO = "espresso"
    POUR_OVER = "pour_over"
    FRENCH_PRESS = "french_press"
    COLD_BREW = "cold_brew"
    AEROPRESS = "aeropress"
    TURKISH = "turkish"
    MOKA_POT = "moka_pot"
    SIPHON = "siphon"


class CoffeeRecipe(BaseModel):
    """Standard coffee recipe with validation."""
    
    name: str = Field(..., min_length=1, max_length=100)
    brew_method: BrewMethod
    coffee_weight: float = Field(..., gt=0, description="Coffee weight in grams")
    water_weight: float = Field(..., gt=0, description="Water weight in grams")
    water_temperature: float = Field(..., ge=175, le=212, description="Temperature in Fahrenheit")
    grind_size: str = Field(..., description="Grind size description")
    brew_time: float = Field(..., gt=0, description="Brew time in minutes")
    notes: Optional[str] = None
    
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
        """Calculate coffee-to-water ratio."""
        return self.water_weight / self.coffee_weight
    
    @property
    def ratio_str(self) -> str:
        """Return ratio as string (1:X format)."""
        return f"1:{self.ratio:.2f}"


class CodeGenerationRequest(BaseModel):
    """Request for coffee code generation."""
    
    requirement: str = Field(..., min_length=1, description="User's coffee code requirement")
    brew_method: Optional[BrewMethod] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    language: str = Field(default="python", description="Target programming language")
    complexity: str = Field(default="basic", description="Code complexity level")
    
    @validator('requirement')
    def validate_requirement(cls, v):
        # 更宽松的验证：允许短的中文输入，但确保不为空
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Requirement cannot be empty')
        return v


class CodeQualityReport(BaseModel):
    """Report on code quality analysis."""
    
    score: float = Field(..., ge=0, le=100, description="Overall quality score")
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    coffee_domain_validations: List[Dict[str, Any]] = Field(default_factory=list)
    security_issues: List[Dict[str, Any]] = Field(default_factory=list)
    performance_notes: List[str] = Field(default_factory=list)
    
    @property
    def is_acceptable(self) -> bool:
        """Check if code quality is acceptable."""
        return self.score >= 70 and not any(issue.get('severity') == 'error' for issue in self.issues)


class OptimizationResult(BaseModel):
    """Result of code optimization."""
    
    original_code: str
    optimized_code: str
    improvements: List[str] = Field(default_factory=list)
    performance_gains: Dict[str, float] = Field(default_factory=dict)
    quality_score_improvement: float = Field(default=0.0)
    optimizations_applied: List[str] = Field(default_factory=list)
    
    @property
    def improvement_percentage(self) -> float:
        """Calculate overall improvement percentage."""
        return sum(self.performance_gains.values()) / len(self.performance_gains) if self.performance_gains else 0.0


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    
    success: bool
    message: str
    data: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: __import__('time').time())


class UserFeedback(BaseModel):
    """User feedback for code approval."""
    
    approved: bool
    comments: Optional[str] = None
    suggestions: Optional[List[str]] = None
    priority: str = Field(default="medium", description="Feedback priority")


class WorkflowState(BaseModel):
    """State tracking for multi-agent workflow."""
    
    current_step: str
    completed_steps: List[str] = Field(default_factory=list)
    generated_code: Optional[str] = None
    quality_report: Optional[CodeQualityReport] = None
    optimization_result: Optional[OptimizationResult] = None
    user_feedback: Optional[UserFeedback] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return "user_approval" in self.completed_steps


class CoffeeCalculationRequest(BaseModel):
    """Request for coffee brewing calculations."""
    
    calculation_type: str = Field(..., description="Type of calculation needed")
    coffee_weight: Optional[float] = None
    water_weight: Optional[float] = None
    brew_method: Optional[BrewMethod] = None
    servings: Optional[int] = Field(default=1, ge=1)
    custom_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CoffeeCalculationResult(BaseModel):
    """Result of coffee brewing calculations."""
    
    calculation_type: str
    coffee_weight: float
    water_weight: float
    ratio: float
    water_temperature: float
    brew_time: float
    grind_size: str
    servings: int
    notes: List[str] = Field(default_factory=list)


class CodeExecutionResult(BaseModel):
    """Result of code execution."""
    
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    memory_usage: Optional[float] = None
    
    @property
    def has_error(self) -> bool:
        """Check if execution had errors."""
        return self.error is not None