"""
State management for the Security Incident Triage Agent.

Defines the state schema and data structures used throughout the
LangGraph workflow for incident processing.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class IncidentPriority(str, Enum):
    """Incident priority levels based on hospitality security standards."""
    CRITICAL = "critical"      # Immediate threat to safety/security
    HIGH = "high"             # Significant security concern
    MEDIUM = "medium"         # Moderate security issue
    LOW = "low"               # Minor security matter
    INFORMATIONAL = "info"    # Security-related information


class IncidentCategory(str, Enum):
    """Hospitality-specific incident categories."""
    GUEST_ACCESS = "guest_access"           # Unauthorized guest access
    PAYMENT_FRAUD = "payment_fraud"         # Payment/billing fraud
    PII_BREACH = "pii_breach"              # Personal data breach
    OPERATIONAL_SECURITY = "ops_security"   # Operational security violations
    VENDOR_ACCESS = "vendor_access"         # Vendor/contractor access issues
    PHYSICAL_SECURITY = "physical_security" # Physical security breaches
    CYBER_SECURITY = "cyber_security"       # Cybersecurity incidents
    COMPLIANCE_VIOLATION = "compliance"     # Regulatory compliance issues


class ComplianceFramework(str, Enum):
    """Relevant compliance frameworks for hospitality."""
    DPDP = "dpdp"              # Data Protection and Digital Privacy Act (India)
    PCI_DSS = "pci_dss"        # Payment Card Industry Data Security Standard
    GDPR = "gdpr"              # General Data Protection Regulation
    CCPA = "ccpa"              # California Consumer Privacy Act
    SOX = "sox"                # Sarbanes-Oxley Act
    HIPAA = "hipaa"            # Health Insurance Portability and Accountability Act


class ActionRequirement(BaseModel):
    """Requirements for specific actions in incident response."""
    requires_human_approval: bool = Field(default=False)
    requires_compliance_check: bool = Field(default=False)
    requires_legal_review: bool = Field(default=False)
    requires_documentation: bool = Field(default=True)
    timeout_minutes: Optional[int] = Field(default=None)


class SecurityPlaybook(BaseModel):
    """Security response playbook definition."""
    playbook_id: str
    name: str
    description: str
    applicable_categories: List[IncidentCategory]
    required_actions: List[str]
    action_requirements: Dict[str, ActionRequirement]
    escalation_criteria: Dict[str, Any]
    compliance_frameworks: List[ComplianceFramework]


class IncidentMetadata(BaseModel):
    """Metadata about the security incident."""
    reported_by: Optional[str] = None
    reporting_system: Optional[str] = None
    affected_systems: List[str] = Field(default_factory=list)
    affected_guests: List[str] = Field(default_factory=list)
    affected_employees: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    property_code: Optional[str] = None
    business_impact: Optional[str] = None
    estimated_cost: Optional[float] = None


class RiskAssessment(BaseModel):
    """Risk assessment for the incident."""
    risk_score: float = Field(ge=0.0, le=10.0)
    risk_factors: List[str] = Field(default_factory=list)
    mitigation_urgency: IncidentPriority
    potential_impact: str
    likelihood_score: float = Field(ge=0.0, le=10.0)
    confidence_score: float = Field(ge=0.0, le=1.0)


class HumanInterventionRequest(BaseModel):
    """Request for human intervention in the workflow."""
    intervention_type: str
    reason: str
    requested_at: datetime
    urgency: IncidentPriority
    context: Dict[str, Any]
    approver_role: str
    timeout_minutes: Optional[int] = None


class IncidentResponse(BaseModel):
    """Structured incident response information."""
    immediate_actions: List[str] = Field(default_factory=list)
    investigation_steps: List[str] = Field(default_factory=list)
    containment_measures: List[str] = Field(default_factory=list)
    notification_requirements: List[str] = Field(default_factory=list)
    documentation_requirements: List[str] = Field(default_factory=list)
    follow_up_actions: List[str] = Field(default_factory=list)


class IncidentState(BaseModel):
    """
    Main state object for the Security Incident Triage workflow.
    
    This state is passed between all nodes in the LangGraph workflow
    and contains all information about the incident being processed.
    """
    
    # Core incident information
    incident_id: str
    title: str
    description: str
    severity: Optional[IncidentPriority] = None
    category: Optional[IncidentCategory] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Messages for conversation history
    messages: List[BaseMessage] = Field(default_factory=list)
    
    # Analysis results
    classification_confidence: Optional[float] = None
    risk_assessment: Optional[RiskAssessment] = None
    applicable_playbooks: List[SecurityPlaybook] = Field(default_factory=list)
    selected_playbook: Optional[SecurityPlaybook] = None
    
    # Incident details
    metadata: IncidentMetadata = Field(default_factory=IncidentMetadata)
    
    # Response planning
    incident_response: Optional[IncidentResponse] = None
    
    # Human intervention
    pending_approvals: List[HumanInterventionRequest] = Field(default_factory=list)
    approval_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Workflow control
    current_step: str = "initial"
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    requires_human_intervention: bool = False
    workflow_paused: bool = False
    
    # Compliance and safety
    compliance_checks: Dict[ComplianceFramework, bool] = Field(default_factory=dict)
    safety_guardrails_passed: bool = True
    
    # Tool execution results
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Evaluation and metrics
    processing_metrics: Dict[str, Any] = Field(default_factory=dict)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Memory and context
    session_context: Dict[str, Any] = Field(default_factory=dict)
    historical_context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the conversation history."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def update_step(self, step: str) -> None:
        """Update the current workflow step."""
        if self.current_step not in self.completed_steps:
            self.completed_steps.append(self.current_step)
        self.current_step = step
        self.updated_at = datetime.utcnow()
    
    def mark_step_failed(self, step: str, reason: str) -> None:
        """Mark a workflow step as failed."""
        self.failed_steps.append(step)
        self.tool_results[f"{step}_failure"] = reason
        self.updated_at = datetime.utcnow()
    
    def request_human_intervention(
        self, 
        intervention_type: str, 
        reason: str, 
        urgency: IncidentPriority = IncidentPriority.MEDIUM,
        approver_role: str = "security_analyst",
        timeout_minutes: Optional[int] = None
    ) -> None:
        """Request human intervention in the workflow."""
        request = HumanInterventionRequest(
            intervention_type=intervention_type,
            reason=reason,
            requested_at=datetime.utcnow(),
            urgency=urgency,
            context={"current_step": self.current_step, "incident_id": self.incident_id},
            approver_role=approver_role,
            timeout_minutes=timeout_minutes
        )
        self.pending_approvals.append(request)
        self.requires_human_intervention = True
        self.workflow_paused = True
        self.updated_at = datetime.utcnow()
    
    def approve_intervention(self, intervention_type: str, approver: str, decision: bool, notes: str = "") -> None:
        """Process human approval for intervention request."""
        # Find and remove the pending approval
        for i, approval in enumerate(self.pending_approvals):
            if approval.intervention_type == intervention_type:
                # Record the approval
                self.approval_history.append({
                    "intervention_type": intervention_type,
                    "approver": approver,
                    "decision": decision,
                    "notes": notes,
                    "approved_at": datetime.utcnow(),
                    "original_request": approval.dict()
                })
                
                # Remove from pending
                self.pending_approvals.pop(i)
                break
        
        # If no more pending approvals, resume workflow
        if not self.pending_approvals:
            self.requires_human_intervention = False
            self.workflow_paused = False
        
        self.updated_at = datetime.utcnow()
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """Add a tool execution result."""
        self.tool_results[tool_name] = result
        self.updated_at = datetime.utcnow()
    
    def update_metrics(self, metric_name: str, value: Any) -> None:
        """Update processing metrics."""
        self.processing_metrics[metric_name] = value
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncidentState":
        """Create state from dictionary."""
        return cls.parse_obj(data)


# LangGraph reducer function for messages
def reduce_messages(existing: List[BaseMessage], new: List[BaseMessage]) -> List[BaseMessage]:
    """Reducer function for managing message history in LangGraph state."""
    return add_messages(existing, new)