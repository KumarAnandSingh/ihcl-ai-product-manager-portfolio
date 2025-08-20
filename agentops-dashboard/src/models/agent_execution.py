"""Agent execution tracking model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class AgentExecution(BaseModel):
    """Track individual agent execution runs."""
    
    __tablename__ = "agent_executions"
    
    # Primary identifier
    execution_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Agent identification
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_version: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)  # security, guest_service, etc.
    
    # Execution context
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)  # production, staging, dev
    
    # Task information
    task_id: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    task_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    
    # Execution details
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status and results
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # running, completed, failed, timeout
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Tool usage
    tools_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_calls_count: Mapped[int] = mapped_column(Integer, default=0)
    tool_success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Model usage
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Cost tracking
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Quality metrics
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    safety_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Input/Output data
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # System metrics
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AgentExecution(id={self.execution_id}, agent={self.agent_name}, status={self.status})>"