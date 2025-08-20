"""Evaluation result tracking model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class EvaluationResult(BaseModel):
    """Track evaluation results for agent performance assessment."""
    
    __tablename__ = "evaluation_results"
    
    # Primary identifier
    evaluation_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Link to agent execution
    execution_id: Mapped[Optional[str]] = mapped_column(
        String(255), 
        ForeignKey("agent_executions.execution_id"),
        nullable=True
    )
    
    # Evaluation metadata
    evaluation_type: Mapped[str] = mapped_column(String(100), nullable=False)  # automatic, manual, benchmark
    evaluator_name: Mapped[str] = mapped_column(String(255), nullable=False)
    evaluator_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Test information
    test_suite: Mapped[str] = mapped_column(String(255), nullable=False)
    test_case: Mapped[str] = mapped_column(String(255), nullable=False)
    test_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Evaluation timing
    evaluation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evaluation_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Overall results
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # A+, A, B, C, D, F
    
    # Detailed scores
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    safety_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coherence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    efficiency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Specific evaluation metrics
    hallucination_detected: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    hallucination_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pii_exposure_detected: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    bias_detected: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    toxicity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Task-specific metrics
    task_completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tool_usage_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_appropriateness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Comparison metrics (for A/B testing)
    baseline_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    improvement_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    statistical_significance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Expected vs actual
    expected_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actual_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ground_truth: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Feedback and comments
    human_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    human_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 scale
    evaluator_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Error analysis
    error_categories: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    failure_modes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Detailed metrics
    metrics_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evaluation_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Environment context
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    configuration_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<EvaluationResult(id={self.evaluation_id}, score={self.overall_score}, passed={self.passed})>"