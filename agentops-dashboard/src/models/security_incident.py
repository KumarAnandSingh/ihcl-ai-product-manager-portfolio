"""Security incident tracking model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class SecurityIncident(BaseModel):
    """Track security incidents and violations."""
    
    __tablename__ = "security_incidents"
    
    # Primary identifier
    incident_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Link to agent execution
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    
    # Incident classification
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False)  # prompt_injection, pii_exposure, unauthorized_access, etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # security, privacy, compliance, safety
    
    # Detection information
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detected_by: Mapped[str] = mapped_column(String(255), nullable=False)  # system component that detected
    detection_method: Mapped[str] = mapped_column(String(100), nullable=False)  # automated, manual, alert
    
    # Incident details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_systems: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")  # open, investigating, resolved, closed
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolution_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Risk assessment
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    likelihood: Mapped[str] = mapped_column(String(20), nullable=False)  # very_high, high, medium, low, very_low
    
    # Compliance impact
    compliance_violation: Mapped[bool] = mapped_column(Boolean, default=False)
    regulations_affected: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # GDPR, CCPA, SOX, etc.
    data_classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # public, internal, confidential, restricted
    
    # PII/Sensitive data exposure
    pii_exposed: Mapped[bool] = mapped_column(Boolean, default=False)
    pii_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # email, phone, ssn, etc.
    records_affected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Technical details
    attack_vector: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vulnerability_exploited: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    indicators_of_compromise: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Evidence and artifacts
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    logs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    screenshots: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Response actions
    immediate_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    mitigation_steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    preventive_measures: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Business impact
    business_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    financial_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reputation_impact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Notification and communication
    notifications_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_recipients: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    external_reporting_required: Mapped[bool] = mapped_column(Boolean, default=False)
    reported_to_authorities: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Resolution details
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    incident_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<SecurityIncident(id={self.incident_id}, type={self.incident_type}, severity={self.severity})>"