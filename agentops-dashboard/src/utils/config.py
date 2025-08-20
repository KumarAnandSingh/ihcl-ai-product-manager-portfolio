"""Configuration management for AgentOps Dashboard."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    database_url: str = "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops_dashboard"
    redis_url: str = "redis://localhost:6379/0"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Dashboard settings
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8501
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Security
    secret_key: str = "your-secret-key-here"
    
    # External integrations
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # Alerting
    slack_webhook_url: Optional[str] = None
    pagerduty_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings