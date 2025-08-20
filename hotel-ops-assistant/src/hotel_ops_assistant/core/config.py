"""
Configuration management for Hotel Operations Assistant.
Handles environment variables, settings validation, and configuration across environments.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings with validation and environment variable support."""
    
    # Application Configuration
    app_name: str = Field(default="Hotel Operations Assistant", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    
    # Database Configuration
    database_url: str = Field(env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # AI/LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field(default="gpt-4-turbo-preview", env="DEFAULT_MODEL")
    backup_model: str = Field(default="gpt-3.5-turbo", env="BACKUP_MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    
    # Hotel System Integrations (Mock APIs)
    pms_api_url: AnyHttpUrl = Field(default="http://localhost:8001", env="PMS_API_URL")
    pos_api_url: AnyHttpUrl = Field(default="http://localhost:8002", env="POS_API_URL")
    crm_api_url: AnyHttpUrl = Field(default="http://localhost:8003", env="CRM_API_URL")
    security_api_url: AnyHttpUrl = Field(default="http://localhost:8004", env="SECURITY_API_URL")
    maintenance_api_url: AnyHttpUrl = Field(default="http://localhost:8005", env="MAINTENANCE_API_URL")
    
    # Compliance and Privacy
    enable_pii_protection: bool = Field(default=True, env="ENABLE_PII_PROTECTION")
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")
    enable_gdpr_compliance: bool = Field(default=True, env="ENABLE_GDPR_COMPLIANCE")
    enable_dpdp_compliance: bool = Field(default=True, env="ENABLE_DPDP_COMPLIANCE")
    enable_pci_dss_compliance: bool = Field(default=True, env="ENABLE_PCI_DSS_COMPLIANCE")
    
    # Monitoring and Analytics
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    jaeger_endpoint: Optional[AnyHttpUrl] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # Performance Configuration
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")
    session_timeout_minutes: int = Field(default=30, env="SESSION_TIMEOUT_MINUTES")
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    
    # Hotel Configuration
    hotel_brand: str = Field(default="IHCL", env="HOTEL_BRAND")
    hotel_type: str = Field(default="luxury", env="HOTEL_TYPE")
    hotel_rooms: int = Field(default=450, env="HOTEL_ROOMS")
    hotel_timezone: str = Field(default="Asia/Kolkata", env="HOTEL_TIMEZONE")
    hotel_currency: str = Field(default="INR", env="HOTEL_CURRENCY")
    hotel_languages: str = Field(default="en,hi,ta,te,bn", env="HOTEL_LANGUAGES")
    
    # Emergency Contacts
    security_team_email: str = Field(default="security@hotel.com", env="SECURITY_TEAM_EMAIL")
    management_email: str = Field(default="management@hotel.com", env="MANAGEMENT_EMAIL")
    it_support_email: str = Field(default="it@hotel.com", env="IT_SUPPORT_EMAIL")
    escalation_phone: str = Field(default="+91-11-12345678", env="ESCALATION_PHONE")
    
    @validator("hotel_type")
    def validate_hotel_type(cls, v):
        """Validate hotel type is one of the supported types."""
        valid_types = ["luxury", "business", "boutique"]
        if v not in valid_types:
            raise ValueError(f"hotel_type must be one of {valid_types}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is supported."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("default_llm_provider")
    def validate_llm_provider(cls, v):
        """Validate LLM provider is supported."""
        valid_providers = ["openai", "anthropic"]
        if v not in valid_providers:
            raise ValueError(f"default_llm_provider must be one of {valid_providers}")
        return v
    
    @property
    def hotel_languages_list(self) -> List[str]:
        """Get hotel languages as a list."""
        return [lang.strip() for lang in self.hotel_languages.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"http://{self.api_host}:{self.api_port}"
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for SQLAlchemy."""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.database_echo and not self.is_production,
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return {
            "url": self.redis_url,
            "password": self.redis_password,
            "db": self.redis_db,
            "max_connections": self.redis_max_connections,
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "provider": self.default_llm_provider,
            "model": self.default_model,
            "backup_model": self.backup_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_keys": {
                "openai": self.openai_api_key,
                "anthropic": self.anthropic_api_key,
            }
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Hotel-specific configurations for different property types
HOTEL_TYPE_CONFIGS = {
    "luxury": {
        "service_levels": ["premium", "concierge", "butler", "vip"],
        "amenities": ["spa", "fine_dining", "business_center", "gym", "pool", "golf"],
        "room_categories": ["deluxe", "executive", "suite", "presidential"],
        "response_time_sla": {
            "complaints": 15,  # minutes
            "maintenance": 30,
            "security": 5,
            "concierge": 10
        },
        "escalation_thresholds": {
            "vip_guest_complaint": 1,
            "security_incident": 1,
            "fraud_alert": 0,
            "system_failure": 2
        }
    },
    "business": {
        "service_levels": ["standard", "business", "premium"],
        "amenities": ["business_center", "gym", "restaurant", "meeting_rooms"],
        "room_categories": ["standard", "business", "suite"],
        "response_time_sla": {
            "complaints": 30,
            "maintenance": 60,
            "security": 10,
            "concierge": 20
        },
        "escalation_thresholds": {
            "vip_guest_complaint": 2,
            "security_incident": 1,
            "fraud_alert": 1,
            "system_failure": 3
        }
    },
    "boutique": {
        "service_levels": ["personalized", "premium"],
        "amenities": ["restaurant", "bar", "gym", "spa"],
        "room_categories": ["standard", "deluxe", "suite"],
        "response_time_sla": {
            "complaints": 20,
            "maintenance": 45,
            "security": 8,
            "concierge": 15
        },
        "escalation_thresholds": {
            "vip_guest_complaint": 1,
            "security_incident": 1,
            "fraud_alert": 1,
            "system_failure": 2
        }
    }
}


def get_hotel_config(hotel_type: str) -> Dict[str, Any]:
    """Get hotel-specific configuration based on property type."""
    return HOTEL_TYPE_CONFIGS.get(hotel_type, HOTEL_TYPE_CONFIGS["luxury"])