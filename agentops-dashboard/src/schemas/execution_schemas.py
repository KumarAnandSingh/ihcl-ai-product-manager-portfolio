"""Pydantic schemas for agent execution data."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Agent execution status options."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionCreate(BaseModel):
    """Schema for creating a new agent execution."""
    execution_id: str = Field(..., description="Unique execution identifier")
    agent_name: str = Field(..., description="Name of the agent")
    agent_version: str = Field(..., description="Version of the agent")
    agent_type: str = Field(..., description="Type/category of the agent")
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    environment: str = Field(..., description="Environment (production, staging, dev)")
    task_id: str = Field(..., description="Task identifier")
    task_type: str = Field(..., description="Type of task being executed")
    task_description: Optional[str] = Field(None, description="Description of the task")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")
    start_time: datetime = Field(..., description="Execution start time")
    status: ExecutionStatus = Field(ExecutionStatus.RUNNING, description="Current status")
    
    # Optional fields that may be populated later
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    success: Optional[bool] = Field(None, description="Whether execution was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_type: Optional[str] = Field(None, description="Type of error")
    
    # Tool and model usage
    tools_used: Optional[Dict[str, Any]] = Field(None, description="Tools used during execution")
    tool_calls_count: int = Field(0, description="Number of tool calls made")
    tool_success_rate: Optional[float] = Field(None, description="Tool call success rate")
    model_name: Optional[str] = Field(None, description="LLM model used")
    model_provider: Optional[str] = Field(None, description="Model provider")
    input_tokens: Optional[int] = Field(None, description="Input tokens consumed")
    output_tokens: Optional[int] = Field(None, description="Output tokens generated")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    
    # Cost and quality metrics
    cost_usd: Optional[float] = Field(None, description="Cost in USD")
    cost_breakdown: Optional[Dict[str, Any]] = Field(None, description="Detailed cost breakdown")
    confidence_score: Optional[float] = Field(None, description="Confidence score", ge=0, le=1)
    accuracy_score: Optional[float] = Field(None, description="Accuracy score", ge=0, le=1)
    safety_score: Optional[float] = Field(None, description="Safety score", ge=0, le=1)
    
    # Data
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    # System metrics
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")


class ExecutionUpdate(BaseModel):
    """Schema for updating an agent execution."""
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Optional[ExecutionStatus] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    tools_used: Optional[Dict[str, Any]] = None
    tool_calls_count: Optional[int] = None
    tool_success_rate: Optional[float] = Field(None, ge=0, le=1)
    
    model_name: Optional[str] = None
    model_provider: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    cost_usd: Optional[float] = None
    cost_breakdown: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    accuracy_score: Optional[float] = Field(None, ge=0, le=1)
    safety_score: Optional[float] = Field(None, ge=0, le=1)
    
    output_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


class ExecutionResponse(BaseModel):
    """Schema for agent execution response."""
    execution_id: str
    agent_name: str
    agent_version: str
    agent_type: str
    session_id: str
    user_id: Optional[str]
    environment: str
    task_id: str
    task_type: str
    task_description: Optional[str]
    priority: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: str
    success: Optional[bool]
    error_message: Optional[str]
    error_type: Optional[str]
    
    tools_used: Optional[Dict[str, Any]]
    tool_calls_count: int
    tool_success_rate: Optional[float]
    model_name: Optional[str]
    model_provider: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    
    cost_usd: Optional[float]
    cost_breakdown: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    accuracy_score: Optional[float]
    safety_score: Optional[float]
    
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    
    memory_usage_mb: Optional[float]
    cpu_usage_percent: Optional[float]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExecutionSummary(BaseModel):
    """Summary statistics for executions."""
    total_executions: int
    successful_executions: int
    success_rate_percent: float
    average_duration_ms: float
    total_cost_usd: float
    error_distribution: Dict[str, int]
    time_window_hours: int


class ExecutionFilters(BaseModel):
    """Filters for querying executions."""
    agent_name: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    success: Optional[bool] = None
    task_type: Optional[str] = None