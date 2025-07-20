"""Coffee brewing calculation tools for the multi-agent system."""

import math
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field, validator

from config.settings import settings


class CoffeeRecipe(BaseModel):
    """Standard coffee recipe with validation."""
    
    name: str = Field(..., min_length=1, max_length=100)
    brew_method: str = Field(..., description="Brewing method (espresso, pour_over, etc.)")
    coffee_weight: float = Field(..., gt=0, description="Coffee weight in grams")
    water_weight: float = Field(..., gt=0, description="Water weight in grams")
    water_temperature: float = Field(..., ge=175, le=212, description="Temperature in Fahrenheit")
    grind_size: str = Field(..., description="Grind size description")
    brew_time: float = Field(..., gt=0, description="Brew time in minutes")
    
    @validator('water_temperature')
    def validate_temperature(cls, v):
        if v < settings.coffee.safety_temp_min or v > settings.coffee.safety_temp_max:
            raise ValueError(
                f'Water temperature should be between {settings.coffee.safety_temp_min}-{settings.coffee.safety_temp_max}°F'
            )
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


class BrewParameters(BaseModel):
    """Coffee brewing parameters for calculations."""
    
    coffee_weight: float = Field(..., gt=0)
    water_weight: float = Field(..., gt=0)
    water_temperature: float = Field(..., ge=175, le=212)
    grind_size: str = Field(default="medium")
    brew_method: str = Field(default="pour_over")


class CoffeeCalculator:
    """Calculator for coffee brewing parameters."""
    
    # Industry standard ratios by brew method
    STANDARD_RATIOS = {
        "espresso": 2.0,
        "pour_over": 16.67,
        "french_press": 15.0,
        "cold_brew": 8.0,
        "aeropress": 15.0,
        "turkish": 12.0
    }
    
    # Grind size recommendations by brew method
    GRIND_SIZES = {
        "espresso": "fine",
        "pour_over": "medium-fine",
        "french_press": "coarse",
        "cold_brew": "extra coarse",
        "aeropress": "medium",
        "turkish": "extra fine"
    }
    
    # Brew time recommendations by method (minutes)
    BREW_TIMES = {
        "espresso": 0.5,
        "pour_over": 3.5,
        "french_press": 4.0,
        "cold_brew": 60 * 12,  # 12 hours
        "aeropress": 2.5,
        "turkish": 5.0
    }

    @staticmethod
    def calculate_water_needed(coffee_grams: float, ratio: Optional[float] = None, method: str = "pour_over") -> float:
        """Calculate water needed based on coffee weight and ratio."""
        if coffee_grams <= 0:
            raise ValueError("Coffee weight must be positive")
        
        if ratio is None:
            ratio = CoffeeCalculator.STANDARD_RATIOS.get(method, settings.coffee.default_ratio)
        
        if ratio < 1 or ratio > 50:
            raise ValueError("Ratio must be between 1:1 and 1:50")
        
        return round(coffee_grams * ratio, 2)

    @staticmethod
    def calculate_coffee_needed(water_grams: float, ratio: Optional[float] = None, method: str = "pour_over") -> float:
        """Calculate coffee needed based on water weight and ratio."""
        if water_grams <= 0:
            raise ValueError("Water weight must be positive")
        
        if ratio is None:
            ratio = CoffeeCalculator.STANDARD_RATIOS.get(method, settings.coffee.default_ratio)
        
        if ratio < 1 or ratio > 50:
            raise ValueError("Ratio must be between 1:1 and 1:50")
        
        return round(water_grams / ratio, 2)

    @staticmethod
    def convert_temperature(temp: float, from_unit: str = "fahrenheit", to_unit: str = "celsius") -> float:
        """Convert temperature between Fahrenheit and Celsius."""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit == to_unit:
            return round(temp, 2)
        
        if from_unit == "fahrenheit" and to_unit == "celsius":
            return round((temp - 32) * 5/9, 2)
        elif from_unit == "celsius" and to_unit == "fahrenheit":
            return round(temp * 9/5 + 32, 2)
        else:
            raise ValueError("Unsupported temperature units")

    @staticmethod
    def recommend_grind_size(method: str) -> str:
        """Recommend grind size based on brew method."""
        return CoffeeCalculator.GRIND_SIZES.get(method.lower(), "medium")

    @staticmethod
    def recommend_brew_time(method: str) -> float:
        """Recommend brew time based on method."""
        return CoffeeCalculator.BREW_TIMES.get(method.lower(), 3.5)

    @staticmethod
    def scale_recipe(recipe: CoffeeRecipe, servings: float) -> CoffeeRecipe:
        """Scale a recipe for different number of servings."""
        if servings <= 0:
            raise ValueError("Servings must be positive")
        
        scale_factor = servings
        
        return CoffeeRecipe(
            name=f"{recipe.name} (scaled for {servings})",
            brew_method=recipe.brew_method,
            coffee_weight=round(recipe.coffee_weight * scale_factor, 2),
            water_weight=round(recipe.water_weight * scale_factor, 2),
            water_temperature=recipe.water_temperature,
            grind_size=recipe.grind_size,
            brew_time=recipe.brew_time
        )

    @staticmethod
    def calculate_extraction_yield(dose: float, tds: float, beverage_weight: float) -> float:
        """Calculate extraction yield percentage."""
        if dose <= 0:
            raise ValueError("Dose must be positive")
        
        return round((tds * beverage_weight) / dose * 100, 2)

    @staticmethod
    def validate_coffee_parameters(params: Dict) -> Dict[str, List[str]]:
        """Validate coffee parameters against industry standards."""
        issues = []
        warnings = []
        
        # Temperature validation
        temp = params.get('water_temperature')
        if temp:
            if temp < settings.coffee.safety_temp_min:
                issues.append(f"Water temperature {temp}°F below safety minimum {settings.coffee.safety_temp_min}°F")
            elif temp < 195:
                warnings.append(f"Water temperature {temp}°F below optimal range (195-205°F)")
            elif temp > settings.coffee.safety_temp_max:
                issues.append(f"Water temperature {temp}°F above safety maximum {settings.coffee.safety_temp_max}°F")
            elif temp > 205:
                warnings.append(f"Water temperature {temp}°F above optimal range (195-205°F)")
        
        # Ratio validation
        coffee_weight = params.get('coffee_weight')
        water_weight = params.get('water_weight')
        if coffee_weight and water_weight:
            ratio = water_weight / coffee_weight
            if ratio < 10:
                issues.append(f"Coffee-to-water ratio 1:{ratio:.1f} too strong (minimum 1:10)")
            elif ratio < 15:
                warnings.append(f"Coffee-to-water ratio 1:{ratio:.1f} stronger than standard (1:15-1:17)")
            elif ratio > 20:
                warnings.append(f"Coffee-to-water ratio 1:{ratio:.1f} weaker than standard (1:15-1:17)")
            elif ratio > 25:
                issues.append(f"Coffee-to-water ratio 1:{ratio:.1f} too weak (maximum 1:25)")
        
        return {"issues": issues, "warnings": warnings}


# Async wrapper functions for agent tools
async def calculate_coffee_ratio(coffee_grams: float, method: str = "pour_over") -> float:
    """Calculate water needed for given coffee amount."""
    return CoffeeCalculator.calculate_water_needed(coffee_grams, method=method)


async def calculate_coffee_amount(water_grams: float, method: str = "pour_over") -> float:
    """Calculate coffee needed for given water amount."""
    return CoffeeCalculator.calculate_coffee_needed(water_grams, method=method)


async def convert_temperature(temp: float, from_unit: str = "fahrenheit", to_unit: str = "celsius") -> float:
    """Convert temperature between units."""
    return CoffeeCalculator.convert_temperature(temp, from_unit, to_unit)


async def get_grind_recommendation(method: str) -> str:
    """Get grind size recommendation."""
    return CoffeeCalculator.recommend_grind_size(method)


async def get_brew_time_recommendation(method: str) -> float:
    """Get brew time recommendation."""
    return CoffeeCalculator.recommend_brew_time(method)


async def validate_brewing_params(coffee_weight: float, water_weight: float, water_temp: float) -> Dict:
    """Validate brewing parameters."""
    params = {
        'coffee_weight': coffee_weight,
        'water_weight': water_weight,
        'water_temperature': water_temp
    }
    return CoffeeCalculator.validate_coffee_parameters(params)