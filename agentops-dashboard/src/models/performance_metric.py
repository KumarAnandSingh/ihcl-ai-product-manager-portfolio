"""Performance metrics tracking model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class PerformanceMetric(BaseModel):
    """Track detailed performance metrics for agents and systems."""
    
    __tablename__ = "performance_metrics"
    
    # Primary identifier
    metric_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Link to agent execution
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    
    # Metric identification
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)  # latency, throughput, accuracy, availability
    metric_category: Mapped[str] = mapped_column(String(100), nullable=False)  # performance, quality, reliability, cost
    
    # Time dimensions
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    measurement_window: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # window size in seconds
    
    # System context
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Agent context
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    agent_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metric values
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # ms, %, count, usd, etc.
    
    # Statistical measures
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p95_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p99_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    std_dev: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # SLA tracking
    sla_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_met: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sla_breach_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # critical, major, minor
    
    # Threshold monitoring
    warning_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    critical_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Performance categories
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    throughput_rps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    availability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Resource utilization
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disk_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_io: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Quality metrics
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Business metrics
    user_satisfaction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    task_completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    conversion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Trend analysis
    trend_direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # improving, degrading, stable
    trend_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Comparative analysis
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    variance_from_baseline: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    previous_period_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    period_over_period_change: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Sample size and confidence
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence_interval: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    margin_of_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Alert status
    alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    alert_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Additional context
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    labels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<PerformanceMetric(id={self.metric_id}, name={self.metric_name}, value={self.value} {self.unit})>"