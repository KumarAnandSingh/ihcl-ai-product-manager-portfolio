"""Alert and notification tracking model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class Alert(BaseModel):
    """Track alerts and notifications for system monitoring."""
    
    __tablename__ = "alerts"
    
    # Primary identifier
    alert_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Links to related entities
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("security_incidents.incident_id"),
        nullable=True
    )
    metric_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("performance_metrics.metric_id"),
        nullable=True
    )
    
    # Alert classification
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)  # performance, security, cost, quality
    alert_category: Mapped[str] = mapped_column(String(100), nullable=False)  # threshold, anomaly, trend, pattern
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low, info
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # p0, p1, p2, p3, p4
    
    # Alert details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")  # open, acknowledged, investigating, resolved, closed
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Assignment
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    team_assigned: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    
    # Source information
    source_system: Mapped[str] = mapped_column(String(255), nullable=False)
    source_component: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    detection_rule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Context
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    affected_systems: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    affected_users: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Trigger conditions
    trigger_condition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Impact assessment
    business_impact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # critical, high, medium, low, none
    user_impact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    financial_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # SLA impact
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    sla_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sla_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Notification tracking
    notifications_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_channels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # email, slack, pagerduty, etc.
    notification_recipients: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Auto-remediation
    auto_remediation_attempted: Mapped[bool] = mapped_column(Boolean, default=False)
    remediation_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    remediation_success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Correlation and grouping
    correlation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parent_alert_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    grouped_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Historical context
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    last_occurrence: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    frequency_pattern: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Resolution details
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    preventive_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Metrics and KPIs
    time_to_acknowledge: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # seconds
    time_to_resolve: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # seconds
    escalation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Feedback and learning
    false_positive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback_provided: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Additional context
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    labels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # External integrations
    external_ticket_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    external_system: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.alert_id}, type={self.alert_type}, severity={self.severity}, status={self.status})>"