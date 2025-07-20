"""Configuration management for the coffee multi-agent system."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class CoffeeSettings(BaseSettings):
    """Coffee domain specific settings."""
    
    default_water_temp: float = Field(default=200.0, ge=195, le=205)
    default_ratio: float = Field(default=16.67, ge=15, le=17)
    safety_temp_max: float = Field(default=212.0)
    safety_temp_min: float = Field(default=195.0)
    
    class Config:
        env_prefix = "COFFEE_"


class ModelSettings(BaseSettings):
    """Model configuration settings."""
    
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-01"
    
    # DeepSeek API Configuration
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"  # Official base_url
    
    max_tokens: int = Field(default=4000, gt=0)
    temperature: float = Field(default=0.7, ge=0, le=2)
    top_p: float = Field(default=1.0, ge=0, le=1)
    
    class Config:
        env_prefix = ""
        extra = "ignore"  # Allow extra fields to be ignored


class AgentSettings(BaseSettings):
    """Agent behavior settings."""
    
    max_iterations: int = Field(default=10, gt=0)
    timeout_seconds: int = Field(default=60, gt=0)
    
    class Config:
        env_prefix = "AGENT_"


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/coffee_agents.log")
    
    class Config:
        env_prefix = "LOG_"


class ChainlitSettings(BaseSettings):
    """Chainlit UI settings."""
    
    port: int = Field(default=8000, gt=0, lt=65536)
    host: str = Field(default="0.0.0.0")
    
    class Config:
        env_prefix = "CHAINLIT_"


class Settings(BaseSettings):
    """Global application settings."""
    
    coffee: CoffeeSettings = Field(default_factory=CoffeeSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    chainlit: ChainlitSettings = Field(default_factory=ChainlitSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra fields to be ignored


# Global settings instance
settings = Settings()


def validate_required_settings() -> None:
    """Validate that required settings are present."""
    
    # Check for at least one model provider
    if not any([
        settings.model.openai_api_key,
        settings.model.azure_openai_api_key,
        settings.model.deepseek_api_key
    ]):
        raise ValueError(
            "At least one API key must be provided: OPENAI_API_KEY, AZURE_OPENAI_API_KEY, or DEEPSEEK_API_KEY"
        )
    
    # Validate coffee settings
    if settings.coffee.default_water_temp < settings.coffee.safety_temp_min:
        raise ValueError("Default water temperature below safety minimum")
    
    if settings.coffee.default_water_temp > settings.coffee.safety_temp_max:
        raise ValueError("Default water temperature above safety maximum")


# Validate on import
try:
    validate_required_settings()
except ValueError as e:
    import warnings
    warnings.warn(f"Configuration validation warning: {e}")