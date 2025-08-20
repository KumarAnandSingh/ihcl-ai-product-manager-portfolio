"""Audit log tracking model for compliance and debugging."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class AuditLog(BaseModel):
    """Track all system activities for compliance and debugging."""
    
    __tablename__ = "audit_logs"
    
    # Primary identifier
    log_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Links to related entities
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Event classification
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # access, modification, execution, error
    event_category: Mapped[str] = mapped_column(String(100), nullable=False)  # authentication, authorization, data_access, system
    action: Mapped[str] = mapped_column(String(255), nullable=False)  # login, create, read, update, delete, execute
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Actor information
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, system, agent, api
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Target/Resource information
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # agent, model, data, configuration
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resource_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Context
    source_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_system: Mapped[str] = mapped_column(String(255), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Event details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)  # success, failure, partial, error
    
    # Before/After states (for data changes)
    before_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    changes_made: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Security context
    authentication_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    authorization_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permissions_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Data sensitivity
    data_classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # public, internal, confidential, restricted
    pii_involved: Mapped[bool] = mapped_column(Boolean, default=False)
    sensitive_data_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Compliance tracking
    compliance_relevant: Mapped[bool] = mapped_column(Boolean, default=False)
    regulations_applicable: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # GDPR, CCPA, SOX, HIPAA, etc.
    retention_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Risk assessment
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")  # critical, high, medium, low
    risk_factors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Error and exception details
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Performance impact
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bytes_processed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    records_affected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Business context
    business_process: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    business_impact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cost_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Request/Response details
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    request_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Geolocation (if applicable)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Alert correlation
    alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Investigation support
    investigation_priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Chain of custody
    hash_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    digital_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    integrity_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Additional context
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    labels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # External references
    external_reference_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    external_system: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.log_id}, action={self.action}, actor={self.actor_id}, outcome={self.outcome})>"