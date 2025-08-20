"""Pydantic schemas for security incident data."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class IncidentSeverity(str, Enum):
    """Security incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    """Security incident status options."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentType(str, Enum):
    """Security incident types."""
    PROMPT_INJECTION = "prompt_injection"
    PII_EXPOSURE = "pii_exposure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    COMPLIANCE_VIOLATION = "compliance_violation"
    DATA_BREACH = "data_breach"
    MALICIOUS_INPUT = "malicious_input"
    SAFETY_VIOLATION = "safety_violation"


class SecurityIncidentCreate(BaseModel):
    """Schema for creating a security incident."""
    incident_id: str = Field(..., description="Unique incident identifier")
    execution_id: Optional[str] = Field(None, description="Related execution ID")
    incident_type: IncidentType = Field(..., description="Type of security incident")
    severity: IncidentSeverity = Field(..., description="Incident severity")
    category: str = Field(..., description="Incident category")
    
    detected_at: datetime = Field(..., description="When incident was detected")
    detected_by: str = Field(..., description="Component that detected the incident")
    detection_method: str = Field(..., description="How incident was detected")
    
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Detailed description")
    affected_systems: Optional[List[str]] = Field(None, description="Affected systems")
    
    status: IncidentStatus = Field(IncidentStatus.OPEN, description="Current status")
    risk_score: float = Field(..., description="Risk score", ge=0, le=10)
    impact_level: str = Field(..., description="Impact level")
    likelihood: str = Field(..., description="Likelihood")
    
    compliance_violation: bool = Field(False, description="Is compliance violation")
    regulations_affected: Optional[List[str]] = Field(None, description="Affected regulations")
    data_classification: Optional[str] = Field(None, description="Data classification")
    
    pii_exposed: bool = Field(False, description="PII exposure occurred")
    pii_types: Optional[List[str]] = Field(None, description="Types of PII exposed")
    records_affected: Optional[int] = Field(None, description="Number of records affected")
    
    attack_vector: Optional[str] = Field(None, description="Attack vector used")
    vulnerability_exploited: Optional[str] = Field(None, description="Vulnerability exploited")
    indicators_of_compromise: Optional[Dict[str, Any]] = Field(None, description="IOCs")
    
    evidence: Optional[Dict[str, Any]] = Field(None, description="Evidence collected")
    logs: Optional[Dict[str, Any]] = Field(None, description="Relevant logs")
    
    immediate_actions: Optional[List[str]] = Field(None, description="Immediate actions taken")
    mitigation_steps: Optional[List[str]] = Field(None, description="Mitigation steps")
    
    business_impact: Optional[str] = Field(None, description="Business impact description")
    financial_impact: Optional[float] = Field(None, description="Financial impact")
    
    environment: str = Field(..., description="Environment where incident occurred")
    source_system: Optional[str] = Field(None, description="Source system")
    incident_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SecurityIncidentUpdate(BaseModel):
    """Schema for updating a security incident."""
    status: Optional[IncidentStatus] = None
    assigned_to: Optional[str] = None
    resolution_time: Optional[datetime] = None
    
    immediate_actions: Optional[List[str]] = None
    mitigation_steps: Optional[List[str]] = None
    preventive_actions: Optional[List[str]] = None
    
    notifications_sent: Optional[bool] = None
    notification_recipients: Optional[List[str]] = None
    external_reporting_required: Optional[bool] = None
    reported_to_authorities: Optional[bool] = None
    
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    lessons_learned: Optional[str] = None
    
    incident_metadata: Optional[Dict[str, Any]] = None


class SecurityIncidentResponse(BaseModel):
    """Schema for security incident response."""
    incident_id: str
    execution_id: Optional[str]
    incident_type: str
    severity: str
    category: str
    
    detected_at: datetime
    detected_by: str
    detection_method: str
    
    title: str
    description: str
    affected_systems: Optional[List[str]]
    
    status: str
    assigned_to: Optional[str]
    resolution_time: Optional[datetime]
    
    risk_score: float
    impact_level: str
    likelihood: str
    
    compliance_violation: bool
    regulations_affected: Optional[List[str]]
    data_classification: Optional[str]
    
    pii_exposed: bool
    pii_types: Optional[List[str]]
    records_affected: Optional[int]
    
    attack_vector: Optional[str]
    vulnerability_exploited: Optional[str]
    indicators_of_compromise: Optional[Dict[str, Any]]
    
    evidence: Optional[Dict[str, Any]]
    logs: Optional[Dict[str, Any]]
    
    immediate_actions: Optional[List[str]]
    mitigation_steps: Optional[List[str]]
    preventive_actions: Optional[List[str]]
    
    business_impact: Optional[str]
    financial_impact: Optional[float]
    
    notifications_sent: bool
    notification_recipients: Optional[List[str]]
    external_reporting_required: bool
    reported_to_authorities: bool
    
    root_cause: Optional[str]
    resolution_summary: Optional[str]
    lessons_learned: Optional[str]
    
    environment: str
    source_system: Optional[str]
    incident_metadata: Optional[Dict[str, Any]]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True