"""Core type definitions for the evaluation framework."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    """Status of an evaluation."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(str, Enum):
    """Types of evaluation metrics."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST = "cost"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    HALLUCINATION = "hallucination"
    TOOL_PRECISION = "tool_precision"
    BUSINESS_IMPACT = "business_impact"


class TaskType(str, Enum):
    """Types of tasks for evaluation."""
    SECURITY_TRIAGE = "security_triage"
    INCIDENT_CLASSIFICATION = "incident_classification"
    THREAT_DETECTION = "threat_detection"
    COMPLIANCE_CHECK = "compliance_check"
    GUEST_SERVICE = "guest_service"
    FRAUD_DETECTION = "fraud_detection"
    EMERGENCY_RESPONSE = "emergency_response"
    DATA_PROTECTION = "data_protection"


class Severity(str, Enum):
    """Severity levels for incidents and issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class TestCase:
    """Represents a single test case."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.SECURITY_TRIAGE
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    severity: Severity = Severity.MEDIUM
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "metadata": self.metadata,
            "severity": self.severity.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MetricResult:
    """Results for a specific metric."""
    metric_type: MetricType
    value: float
    unit: str = ""
    confidence_interval: Optional[tuple[float, float]] = None
    threshold: Optional[float] = None
    passed: Optional[bool] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.threshold is not None:
            self.passed = self.value >= self.threshold


@dataclass
class EvaluationResult:
    """Complete evaluation results for a test case."""
    test_case_id: str
    agent_name: str
    status: EvaluationStatus
    metrics: List[MetricResult] = field(default_factory=list)
    execution_time: Optional[float] = None
    actual_output: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_metric(self, metric_type: MetricType) -> Optional[MetricResult]:
        """Get a specific metric result."""
        for metric in self.metrics:
            if metric.metric_type == metric_type:
                return metric
        return None
    
    def get_overall_score(self) -> float:
        """Calculate overall evaluation score."""
        if not self.metrics:
            return 0.0
        
        weights = {
            MetricType.ACCURACY: 0.25,
            MetricType.SAFETY: 0.20,
            MetricType.COMPLIANCE: 0.20,
            MetricType.LATENCY: 0.15,
            MetricType.BUSINESS_IMPACT: 0.20,
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric in self.metrics:
            if metric.metric_type in weights:
                weight = weights[metric.metric_type]
                weighted_sum += metric.value * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0


class AgentConfig(BaseModel):
    """Configuration for an agent under evaluation."""
    name: str = Field(..., description="Agent name")
    endpoint: str = Field(..., description="Agent API endpoint")
    model: str = Field(default="gpt-4", description="LLM model used")
    temperature: float = Field(default=0.0, description="Model temperature")
    max_tokens: int = Field(default=1000, description="Maximum tokens")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    api_key: Optional[str] = Field(default=None, description="API key")
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers")
    
    class Config:
        extra = "allow"


class EvaluationConfig(BaseModel):
    """Configuration for evaluation runs."""
    name: str = Field(..., description="Evaluation run name")
    description: str = Field(default="", description="Evaluation description")
    agents: List[AgentConfig] = Field(..., description="Agents to evaluate")
    test_suite: str = Field(..., description="Test suite identifier")
    metrics: List[MetricType] = Field(default_factory=list, description="Metrics to compute")
    parallel_execution: bool = Field(default=True, description="Enable parallel execution")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    timeout: int = Field(default=300, description="Evaluation timeout")
    retry_attempts: int = Field(default=3, description="Retry attempts for failed tests")
    random_seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")
    
    class Config:
        extra = "allow"


class ComplianceRequirement(BaseModel):
    """Represents a compliance requirement."""
    id: str = Field(..., description="Requirement ID")
    name: str = Field(..., description="Requirement name")
    regulation: str = Field(..., description="Source regulation (GDPR, PCI DSS, etc.)")
    description: str = Field(..., description="Requirement description")
    validation_rules: List[str] = Field(..., description="Validation rules")
    severity: Severity = Field(default=Severity.MEDIUM, description="Requirement severity")
    
    class Config:
        extra = "allow"


class SecurityThreat(BaseModel):
    """Represents a security threat or incident."""
    id: str = Field(..., description="Threat ID")
    type: str = Field(..., description="Threat type")
    severity: Severity = Field(..., description="Threat severity")
    description: str = Field(..., description="Threat description")
    indicators: List[str] = Field(default_factory=list, description="Threat indicators")
    mitigation_steps: List[str] = Field(default_factory=list, description="Mitigation steps")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems")
    
    class Config:
        extra = "allow"


class HospitalityContext(BaseModel):
    """Context specific to hospitality domain."""
    property_type: str = Field(..., description="Property type (hotel, resort, etc.)")
    location: str = Field(..., description="Property location")
    guest_count: int = Field(default=0, description="Current guest count")
    staff_count: int = Field(default=0, description="Current staff count")
    occupancy_rate: float = Field(default=0.0, description="Current occupancy rate")
    special_events: List[str] = Field(default_factory=list, description="Special events")
    vip_guests: bool = Field(default=False, description="VIP guests present")
    
    class Config:
        extra = "allow"