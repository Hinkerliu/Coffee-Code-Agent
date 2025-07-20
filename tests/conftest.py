"""Pytest configuration and fixtures for coffee multi-agent system tests."""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock

from autogen_core.models import ChatCompletionClient

from agents.models import CodeGenerationRequest, CodeQualityReport, OptimizationResult
from tools.coffee_calculations import CoffeeCalculator


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_model_client() -> Mock:
    """Mock model client for testing."""
    client = Mock(spec=ChatCompletionClient)
    
    # Mock create method
    async def mock_create(*args, **kwargs):
        mock_response = Mock()
        mock_response.content = '''
def calculate_espresso_ratio(coffee_grams: float) -> dict:
    ""Calculate espresso coffee-to-water ratio.""
    water_ml = coffee_grams * 2
    return {"coffee_grams": coffee_grams, "water_ml": water_ml, "ratio": "1:2"}
'''
        return mock_response
    
    client.create = AsyncMock(side_effect=mock_create)
    return client


@pytest.fixture
def sample_code_request() -> CodeGenerationRequest:
    """Sample coffee code request for testing."""
    return CodeGenerationRequest(
        requirement="Create a function to calculate espresso coffee-to-water ratios",
        brew_method="espresso",
        parameters={"coffee_grams": 18, "water_ml": 36}
    )


@pytest.fixture
def sample_code_report() -> CodeQualityReport:
    """Sample quality analysis result for testing."""
    return CodeQualityReport(
        score=85,
        issues=[],
        coffee_domain_validations=[{"type": "ratio", "status": "valid"}],
        security_issues=[],
        suggestions=["Add type hints", "Add docstring"]
    )


@pytest.fixture
def sample_optimization_result() -> OptimizationResult:
    """Sample optimization result for testing."""
    return OptimizationResult(
        original_code="def calc(a, b): return b/a",
        optimized_code="def calculate_ratio(coffee_grams: float, water_ml: float) -> float:\n    return water_ml / coffee_grams",
        improvements=["Added type hints", "Improved variable names"],
        performance_gains={"readability": 25.0, "maintainability": 30.0},
        quality_score_improvement=20.0,
        optimizations_applied=["Type hints", "Documentation"]
    )


@pytest.fixture
def coffee_calculator() -> CoffeeCalculator:
    """Coffee calculator instance for testing."""
    return CoffeeCalculator()


@pytest.fixture
def valid_coffee_params() -> dict:
    """Valid coffee parameters for testing."""
    return {
        "coffee_grams": 18,
        "water_ml": 360,
        "temperature_celsius": 93,
        "brew_time_minutes": 4
    }


@pytest.fixture
def invalid_coffee_params() -> dict:
    """Invalid coffee parameters for testing."""
    return {
        "coffee_grams": -5,  # Invalid negative weight
        "water_ml": 50,      # Too little water
        "temperature_celsius": 150,  # Too hot
        "brew_time_minutes": -1      # Invalid time
    }