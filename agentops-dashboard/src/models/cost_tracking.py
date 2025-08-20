"""Cost tracking and optimization model."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class CostTracking(BaseModel):
    """Track costs and optimization opportunities for AI operations."""
    
    __tablename__ = "cost_tracking"
    
    # Primary identifier
    cost_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Link to agent execution
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    
    # Time dimensions
    billing_date: Mapped[date] = mapped_column(Date, nullable=False)
    billing_hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    
    # Service identification
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)  # llm_api, embedding, vector_db, etc.
    provider: Mapped[str] = mapped_column(String(100), nullable=False)  # openai, anthropic, aws, etc.
    
    # Model details
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # gpt-4, gpt-3.5, claude-3, etc.
    
    # Usage metrics
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Cost breakdown
    base_cost: Mapped[float] = mapped_column(Float, nullable=False)
    input_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    output_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    processing_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    storage_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Pricing details
    input_price_per_token: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    output_price_per_token: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    request_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Cost allocation
    project_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    team_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Agent context
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    task_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Performance correlation
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Optimization opportunities
    optimization_potential: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # % cost reduction possible
    recommended_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    caching_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Budget tracking
    budget_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    budget_allocation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_remaining: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Cost efficiency metrics
    cost_per_task: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_per_user: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_per_successful_outcome: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Comparative analysis
    baseline_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_variance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_trend: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # increasing, decreasing, stable
    
    # Additional context
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ROI calculation
    business_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    roi_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payback_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CostTracking(id={self.cost_id}, service={self.service_name}, cost=${self.total_cost:.4f})>"