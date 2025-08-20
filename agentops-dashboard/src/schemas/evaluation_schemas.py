"""Pydantic schemas for evaluation result data."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EvaluationType(str, Enum):
    """Evaluation type options."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    BENCHMARK = "benchmark"


class EvaluationResultCreate(BaseModel):
    """Schema for creating an evaluation result."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    execution_id: Optional[str] = Field(None, description="Related execution ID")
    
    evaluation_type: EvaluationType = Field(..., description="Type of evaluation")
    evaluator_name: str = Field(..., description="Name of evaluator")
    evaluator_version: str = Field(..., description="Version of evaluator")
    
    test_suite: str = Field(..., description="Test suite name")
    test_case: str = Field(..., description="Test case name")
    test_description: Optional[str] = Field(None, description="Test description")
    
    evaluation_time: datetime = Field(..., description="When evaluation was performed")
    evaluation_duration_ms: Optional[int] = Field(None, description="Evaluation duration")
    
    overall_score: float = Field(..., description="Overall score", ge=0, le=1)
    passed: bool = Field(..., description="Whether evaluation passed")
    grade: Optional[str] = Field(None, description="Letter grade")
    
    accuracy_score: Optional[float] = Field(None, description="Accuracy score", ge=0, le=1)
    relevance_score: Optional[float] = Field(None, description="Relevance score", ge=0, le=1)
    safety_score: Optional[float] = Field(None, description="Safety score", ge=0, le=1)
    coherence_score: Optional[float] = Field(None, description="Coherence score", ge=0, le=1)
    completeness_score: Optional[float] = Field(None, description="Completeness score", ge=0, le=1)
    efficiency_score: Optional[float] = Field(None, description="Efficiency score", ge=0, le=1)
    
    hallucination_detected: Optional[bool] = Field(None, description="Hallucination detected")
    hallucination_score: Optional[float] = Field(None, description="Hallucination score", ge=0, le=1)
    pii_exposure_detected: Optional[bool] = Field(None, description="PII exposure detected")
    bias_detected: Optional[bool] = Field(None, description="Bias detected")
    toxicity_score: Optional[float] = Field(None, description="Toxicity score", ge=0, le=1)
    
    task_completion_rate: Optional[float] = Field(None, description="Task completion rate", ge=0, le=1)
    tool_usage_accuracy: Optional[float] = Field(None, description="Tool usage accuracy", ge=0, le=1)
    response_appropriateness: Optional[float] = Field(None, description="Response appropriateness", ge=0, le=1)
    
    baseline_score: Optional[float] = Field(None, description="Baseline score", ge=0, le=1)
    improvement_percentage: Optional[float] = Field(None, description="Improvement percentage")
    statistical_significance: Optional[float] = Field(None, description="Statistical significance", ge=0, le=1)
    
    expected_output: Optional[Dict[str, Any]] = Field(None, description="Expected output")
    actual_output: Optional[Dict[str, Any]] = Field(None, description="Actual output")
    ground_truth: Optional[Dict[str, Any]] = Field(None, description="Ground truth")
    
    human_feedback: Optional[str] = Field(None, description="Human feedback")
    human_rating: Optional[int] = Field(None, description="Human rating (1-5)", ge=1, le=5)
    evaluator_comments: Optional[str] = Field(None, description="Evaluator comments")
    
    error_categories: Optional[Dict[str, Any]] = Field(None, description="Error categories")
    failure_modes: Optional[Dict[str, Any]] = Field(None, description="Failure modes")
    
    metrics_breakdown: Optional[Dict[str, Any]] = Field(None, description="Detailed metrics")
    evaluation_metadata: Optional[Dict[str, Any]] = Field(None, description="Evaluation metadata")
    
    environment: str = Field(..., description="Environment")
    model_version: Optional[str] = Field(None, description="Model version")
    configuration_hash: Optional[str] = Field(None, description="Configuration hash")


class EvaluationResultResponse(BaseModel):
    """Schema for evaluation result response."""
    evaluation_id: str
    execution_id: Optional[str]
    
    evaluation_type: str
    evaluator_name: str
    evaluator_version: str
    
    test_suite: str
    test_case: str
    test_description: Optional[str]
    
    evaluation_time: datetime
    evaluation_duration_ms: Optional[int]
    
    overall_score: float
    passed: bool
    grade: Optional[str]
    
    accuracy_score: Optional[float]
    relevance_score: Optional[float]
    safety_score: Optional[float]
    coherence_score: Optional[float]
    completeness_score: Optional[float]
    efficiency_score: Optional[float]
    
    hallucination_detected: Optional[bool]
    hallucination_score: Optional[float]
    pii_exposure_detected: Optional[bool]
    bias_detected: Optional[bool]
    toxicity_score: Optional[float]
    
    task_completion_rate: Optional[float]
    tool_usage_accuracy: Optional[float]
    response_appropriateness: Optional[float]
    
    baseline_score: Optional[float]
    improvement_percentage: Optional[float]
    statistical_significance: Optional[float]
    
    expected_output: Optional[Dict[str, Any]]
    actual_output: Optional[Dict[str, Any]]
    ground_truth: Optional[Dict[str, Any]]
    
    human_feedback: Optional[str]
    human_rating: Optional[int]
    evaluator_comments: Optional[str]
    
    error_categories: Optional[Dict[str, Any]]
    failure_modes: Optional[Dict[str, Any]]
    
    metrics_breakdown: Optional[Dict[str, Any]]
    evaluation_metadata: Optional[Dict[str, Any]]
    
    environment: str
    model_version: Optional[str]
    configuration_hash: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True