"""
Configuration Management for Security Incident Triage Agent.

Provides comprehensive configuration management with environment-based
settings, validation, and hospitality industry defaults.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecurityTriageConfig(BaseSettings):
    """
    Comprehensive configuration for Security Incident Triage Agent.
    
    Provides environment-based configuration with validation,
    defaults optimized for hospitality security operations.
    """
    
    # === ENVIRONMENT SETTINGS ===
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Deployment environment"
    )
    
    debug_mode: bool = Field(
        default=True,
        description="Enable debug mode with verbose logging"
    )
    
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    
    # === DATABASE SETTINGS ===
    database_path: str = Field(
        default="data/security_incidents.db",
        description="Path to SQLite database file"
    )
    
    checkpoint_db_path: str = Field(
        default="data/workflow_checkpoints.db",
        description="Path to LangGraph checkpoint database"
    )
    
    data_retention_days: int = Field(
        default=365,
        description="Number of days to retain incident data"
    )
    
    # === REDIS SETTINGS ===
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for session management"
    )
    
    session_ttl_hours: int = Field(
        default=24,
        description="Session time-to-live in hours"
    )
    
    # === LLM SETTINGS ===
    llm_model: str = Field(
        default="gpt-4",
        description="Default LLM model to use"
    )
    
    llm_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="LLM temperature setting"
    )
    
    llm_max_tokens: int = Field(
        default=4000,
        description="Maximum tokens for LLM responses"
    )
    
    llm_timeout_seconds: int = Field(
        default=120,
        description="LLM request timeout in seconds"
    )
    
    # === API KEYS (from environment) ===
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    
    # === WORKFLOW SETTINGS ===
    max_workflow_steps: int = Field(
        default=20,
        description="Maximum number of workflow steps"
    )
    
    workflow_timeout_minutes: int = Field(
        default=30,
        description="Workflow execution timeout"
    )
    
    enable_checkpoints: bool = Field(
        default=True,
        description="Enable workflow checkpointing"
    )
    
    # === SAFETY AND COMPLIANCE SETTINGS ===
    enable_safety_guardrails: bool = Field(
        default=True,
        description="Enable safety guardrails"
    )
    
    enable_compliance_checks: bool = Field(
        default=True,
        description="Enable compliance checking"
    )
    
    enable_human_intervention: bool = Field(
        default=True,
        description="Enable human intervention gates"
    )
    
    max_hallucination_rate: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Maximum acceptable hallucination rate"
    )
    
    # === HOSPITALITY SETTINGS ===
    property_type: str = Field(
        default="business_hotel",
        description="Type of hospitality property (luxury_resort, business_hotel, boutique_hotel, budget_hotel)"
    )
    
    property_code: Optional[str] = Field(
        default=None,
        description="Unique property identifier"
    )
    
    guest_privacy_level: str = Field(
        default="high",
        description="Guest privacy protection level (low, medium, high, maximum)"
    )
    
    business_hours: Dict[str, str] = Field(
        default={
            "start": "06:00",
            "end": "23:00",
            "timezone": "UTC"
        },
        description="Business hours for escalation timing"
    )
    
    # === NOTIFICATION SETTINGS ===
    notification_channels: List[str] = Field(
        default=["email", "sms", "dashboard"],
        description="Available notification channels"
    )
    
    escalation_contacts: Dict[str, Dict[str, str]] = Field(
        default={
            "security_manager": {
                "email": "security.manager@hotel.com",
                "phone": "+1-555-0001",
                "escalation_delay_minutes": "15"
            },
            "general_manager": {
                "email": "gm@hotel.com", 
                "phone": "+1-555-0002",
                "escalation_delay_minutes": "30"
            },
            "legal_counsel": {
                "email": "legal@hotel.com",
                "escalation_delay_minutes": "60"
            }
        },
        description="Escalation contact information"
    )
    
    # === PERFORMANCE SETTINGS ===
    performance_targets: Dict[str, float] = Field(
        default={
            "critical_response_time_minutes": 15.0,
            "high_response_time_minutes": 60.0,
            "medium_response_time_minutes": 240.0,
            "automation_rate": 0.80,
            "quality_score_target": 0.90,
            "compliance_rate_target": 0.98
        },
        description="Performance targets and SLAs"
    )
    
    # === INTEGRATION SETTINGS ===
    webhook_urls: Dict[str, str] = Field(
        default={},
        description="Webhook URLs for external integrations"
    )
    
    api_rate_limits: Dict[str, int] = Field(
        default={
            "classification": 100,  # requests per minute
            "prioritization": 100,
            "response_generation": 50
        },
        description="API rate limits per tool"
    )
    
    # === MONITORING SETTINGS ===
    enable_metrics_collection: bool = Field(
        default=True,
        description="Enable comprehensive metrics collection"
    )
    
    metrics_export_interval_minutes: int = Field(
        default=5,
        description="Metrics export interval"
    )
    
    enable_performance_monitoring: bool = Field(
        default=True,
        description="Enable performance monitoring"
    )
    
    alert_thresholds: Dict[str, float] = Field(
        default={
            "response_time_critical_minutes": 30.0,
            "error_rate_percentage": 5.0,
            "quality_score_minimum": 0.7,
            "safety_violation_rate": 0.02
        },
        description="Alert thresholds for monitoring"
    )
    
    # === SECURITY SETTINGS ===
    enable_audit_logging: bool = Field(
        default=True,
        description="Enable comprehensive audit logging"
    )
    
    encrypt_sensitive_data: bool = Field(
        default=True,
        description="Encrypt sensitive data at rest"
    )
    
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "https://*.hotel.com"],
        description="Allowed origins for CORS"
    )
    
    # === FILE PATHS ===
    log_directory: str = Field(
        default="logs",
        description="Directory for log files"
    )
    
    data_directory: str = Field(
        default="data",
        description="Directory for data files"
    )
    
    config_directory: str = Field(
        default="config",
        description="Directory for configuration files"
    )
    
    class Config:
        env_prefix = "SECURITY_TRIAGE_"
        env_file = ".env"
        case_sensitive = False
        
        # Field aliases for environment variables
        fields = {
            "openai_api_key": {"env": "OPENAI_API_KEY"},
            "anthropic_api_key": {"env": "ANTHROPIC_API_KEY"},
        }
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        """Validate environment setting."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("log_level", pre=True)
    def validate_log_level(cls, v):
        """Validate log level setting."""
        if isinstance(v, str):
            return LogLevel(v.upper())
        return v
    
    @validator("property_type")
    def validate_property_type(cls, v):
        """Validate property type."""
        valid_types = ["luxury_resort", "business_hotel", "boutique_hotel", "budget_hotel"]
        if v not in valid_types:
            raise ValueError(f"Property type must be one of: {valid_types}")
        return v
    
    @validator("guest_privacy_level")
    def validate_privacy_level(cls, v):
        """Validate guest privacy level."""
        valid_levels = ["low", "medium", "high", "maximum"]
        if v not in valid_levels:
            raise ValueError(f"Privacy level must be one of: {valid_levels}")
        return v
    
    @validator("database_path", "checkpoint_db_path")
    def validate_database_paths(cls, v):
        """Ensure database directories exist."""
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @validator("log_directory", "data_directory", "config_directory")
    def create_directories(cls, v):
        """Create required directories."""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    def get_database_url(self) -> str:
        """Get SQLite database URL."""
        return f"sqlite:///{self.database_path}"
    
    def get_checkpoint_url(self) -> str:
        """Get checkpoint database URL."""
        return f"sqlite:///{self.checkpoint_db_path}"
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    def get_performance_target(self, metric_name: str) -> Optional[float]:
        """Get performance target for a specific metric."""
        return self.performance_targets.get(metric_name)
    
    def get_escalation_contact(self, role: str) -> Optional[Dict[str, str]]:
        """Get escalation contact information."""
        return self.escalation_contacts.get(role)
    
    def get_alert_threshold(self, metric_name: str) -> Optional[float]:
        """Get alert threshold for a specific metric."""
        return self.alert_thresholds.get(metric_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file."""
        import json
        
        config_dict = self.dict()
        # Remove sensitive information
        sensitive_keys = ["openai_api_key", "anthropic_api_key"]
        for key in sensitive_keys:
            if key in config_dict:
                config_dict[key] = "***REDACTED***"
        
        with open(file_path, "w") as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "SecurityTriageConfig":
        """Load configuration from JSON file."""
        import json
        
        with open(file_path, "r") as f:
            config_data = json.load(f)
        
        return cls(**config_data)