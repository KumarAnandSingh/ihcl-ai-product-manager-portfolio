"""
Incident management models for Hotel Operations Assistant.
Handles complaints, security issues, maintenance requests, and operational incidents.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, Numeric,
    ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator

from .base import BaseModel as SQLBaseModel, BaseResponse, BaseRequest


class IncidentType(str, Enum):
    """Types of incidents that can occur in hotel operations."""
    GUEST_COMPLAINT = "guest_complaint"
    SECURITY_INCIDENT = "security_incident"
    MAINTENANCE_REQUEST = "maintenance_request"
    ACCESS_ISSUE = "access_issue"
    FRAUD_ALERT = "fraud_alert"
    SYSTEM_FAILURE = "system_failure"
    STAFF_ISSUE = "staff_issue"
    VENDOR_ISSUE = "vendor_issue"
    HEALTH_SAFETY = "health_safety"
    HOUSEKEEPING_ISSUE = "housekeeping_issue"
    CONCIERGE_REQUEST = "concierge_request"
    BILLING_DISPUTE = "billing_dispute"
    LOST_FOUND = "lost_found"
    NOISE_COMPLAINT = "noise_complaint"
    AMENITY_ISSUE = "amenity_issue"


class IncidentPriority(str, Enum):
    """Incident priority levels for escalation and response."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_GUEST = "pending_guest"
    PENDING_VENDOR = "pending_vendor"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class IncidentCategory(str, Enum):
    """Broad categories for incident classification."""
    GUEST_SERVICES = "guest_services"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    OPERATIONS = "operations"
    TECHNOLOGY = "technology"
    COMPLIANCE = "compliance"
    FINANCE = "finance"


class EscalationReason(str, Enum):
    """Reasons for incident escalation."""
    TIME_EXCEEDED = "time_exceeded"
    VIP_GUEST = "vip_guest"
    HIGH_SEVERITY = "high_severity"
    REPEAT_INCIDENT = "repeat_incident"
    MANUAL_ESCALATION = "manual_escalation"
    SYSTEM_TRIGGERED = "system_triggered"
    COMPLIANCE_REQUIRED = "compliance_required"


class Incident(SQLBaseModel):
    """
    Core incident model for tracking all types of hotel operational issues.
    Includes automated escalation, SLA tracking, and compliance features.
    """
    
    __tablename__ = "incidents"
    
    # Basic Information
    incident_number = Column(String(20), unique=True, nullable=False, comment="Unique incident identifier")
    title = Column(String(200), nullable=False, comment="Incident title/summary")
    description = Column(Text, comment="Detailed incident description")
    
    # Classification
    incident_type = Column(SQLEnum(IncidentType), nullable=False)
    category = Column(SQLEnum(IncidentCategory), nullable=False)
    priority = Column(SQLEnum(IncidentPriority), default=IncidentPriority.MEDIUM, nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    
    # Guest and Location
    guest_id = Column(PostgresUUID(as_uuid=True), ForeignKey("guests.id"), nullable=True)
    room_number = Column(String(20), comment="Room number if applicable")
    location = Column(String(100), comment="Incident location")
    hotel_code = Column(String(10), comment="Hotel code")
    department = Column(String(50), comment="Responsible department")
    
    # Timing and SLA
    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, comment="When incident was acknowledged")
    first_response_at = Column(DateTime, comment="First response timestamp")
    resolved_at = Column(DateTime, comment="Resolution timestamp")
    closed_at = Column(DateTime, comment="Closure timestamp")
    
    sla_target_minutes = Column(Integer, comment="SLA target in minutes")
    sla_breached = Column(Boolean, default=False, comment="SLA breach flag")
    sla_breach_time = Column(DateTime, comment="When SLA was breached")
    
    # Assignment and Responsibility
    assigned_to = Column(String(100), comment="Assigned staff member")
    assigned_team = Column(String(50), comment="Assigned team/department")
    reporter_name = Column(String(100), comment="Who reported the incident")
    reporter_contact = Column(String(100), comment="Reporter contact information")
    
    # Resolution
    resolution_summary = Column(Text, comment="How the incident was resolved")
    resolution_category = Column(String(50), comment="Type of resolution")
    guest_satisfaction = Column(Integer, comment="Guest satisfaction rating (1-5)")
    follow_up_required = Column(Boolean, default=False, comment="Follow-up required flag")
    follow_up_date = Column(DateTime, comment="Scheduled follow-up date")
    
    # Financial Impact
    estimated_cost = Column(Numeric(12, 2), comment="Estimated cost of incident")
    actual_cost = Column(Numeric(12, 2), comment="Actual cost incurred")
    compensation_amount = Column(Numeric(12, 2), comment="Guest compensation amount")
    currency = Column(String(3), default="INR", comment="Currency code")
    
    # Escalation
    escalation_level = Column(Integer, default=0, comment="Current escalation level")
    escalation_reason = Column(SQLEnum(EscalationReason), comment="Reason for escalation")
    escalated_to = Column(String(100), comment="Escalated to whom")
    escalated_at = Column(DateTime, comment="Escalation timestamp")
    
    # Additional Data
    tags = Column(String(500), comment="Comma-separated tags")
    external_reference = Column(String(100), comment="External system reference")
    attachments = Column(JSON, comment="List of attachment references")
    communication_log = Column(JSON, comment="Communication history")
    
    # System Fields
    source_system = Column(String(50), comment="System that created the incident")
    ai_classification_confidence = Column(Numeric(3, 2), comment="AI classification confidence")
    automated_actions = Column(JSON, comment="Automated actions taken")
    
    # Relationships
    guest = relationship("Guest", back_populates="incidents")
    escalations = relationship("IncidentEscalation", back_populates="incident", cascade="all, delete-orphan")
    updates = relationship("IncidentUpdate", back_populates="incident", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_incident_number', 'incident_number'),
        Index('idx_incident_guest_id', 'guest_id'),
        Index('idx_incident_status_priority', 'status', 'priority'),
        Index('idx_incident_type_category', 'incident_type', 'category'),
        Index('idx_incident_reported_at', 'reported_at'),
        Index('idx_incident_assigned', 'assigned_to', 'assigned_team'),
        Index('idx_incident_hotel_room', 'hotel_code', 'room_number'),
        Index('idx_incident_sla', 'sla_breached', 'sla_target_minutes'),
    )
    
    def calculate_response_time(self) -> Optional[timedelta]:
        """Calculate response time from report to first response."""
        if self.first_response_at:
            return self.first_response_at - self.reported_at
        return None
    
    def calculate_resolution_time(self) -> Optional[timedelta]:
        """Calculate total resolution time."""
        if self.resolved_at:
            return self.resolved_at - self.reported_at
        return None
    
    def is_sla_at_risk(self, warning_threshold: float = 0.8) -> bool:
        """Check if incident is at risk of SLA breach."""
        if not self.sla_target_minutes or self.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            return False
        
        elapsed = datetime.utcnow() - self.reported_at
        elapsed_minutes = elapsed.total_seconds() / 60
        threshold_minutes = self.sla_target_minutes * warning_threshold
        
        return elapsed_minutes >= threshold_minutes
    
    def should_escalate(self) -> bool:
        """Determine if incident should be escalated."""
        # Check time-based escalation
        if self.sla_breached:
            return True
        
        # Check priority-based escalation
        if self.priority == IncidentPriority.CRITICAL and self.escalation_level == 0:
            return True
        
        # Check VIP guest escalation
        if self.guest and self.guest.is_vip() and self.escalation_level == 0:
            return True
        
        return False
    
    def get_escalation_target(self) -> Optional[str]:
        """Get the next escalation target."""
        escalation_matrix = {
            0: "team_lead",
            1: "department_manager", 
            2: "general_manager",
            3: "regional_manager"
        }
        return escalation_matrix.get(self.escalation_level + 1)


class IncidentEscalation(SQLBaseModel):
    """Incident escalation tracking."""
    
    __tablename__ = "incident_escalations"
    
    incident_id = Column(PostgresUUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    escalation_level = Column(Integer, nullable=False, comment="Escalation level")
    reason = Column(SQLEnum(EscalationReason), nullable=False)
    escalated_from = Column(String(100), comment="Who escalated")
    escalated_to = Column(String(100), comment="Escalated to whom")
    escalated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, comment="Escalation notes")
    
    # Relationships
    incident = relationship("Incident", back_populates="escalations")
    
    # Indexes
    __table_args__ = (
        Index('idx_escalation_incident', 'incident_id'),
        Index('idx_escalation_level', 'escalation_level'),
    )


class IncidentUpdate(SQLBaseModel):
    """Incident status updates and communication log."""
    
    __tablename__ = "incident_updates"
    
    incident_id = Column(PostgresUUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    update_type = Column(String(50), nullable=False, comment="Type of update")
    update_text = Column(Text, comment="Update content")
    updated_by = Column(String(100), comment="Who made the update")
    is_guest_visible = Column(Boolean, default=False, comment="Visible to guest")
    is_internal = Column(Boolean, default=True, comment="Internal update")
    
    # Status changes
    old_status = Column(SQLEnum(IncidentStatus), comment="Previous status")
    new_status = Column(SQLEnum(IncidentStatus), comment="New status")
    old_priority = Column(SQLEnum(IncidentPriority), comment="Previous priority")
    new_priority = Column(SQLEnum(IncidentPriority), comment="New priority")
    
    # Additional data
    attachments = Column(JSON, comment="Update attachments")
    metadata_json = Column(JSON, comment="Additional metadata")
    
    # Relationships
    incident = relationship("Incident", back_populates="updates")
    
    # Indexes
    __table_args__ = (
        Index('idx_update_incident', 'incident_id'),
        Index('idx_update_type', 'update_type'),
        Index('idx_update_guest_visible', 'is_guest_visible'),
    )


# Pydantic models for API
class IncidentCreateRequest(BaseRequest):
    """Request model for creating a new incident."""
    
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    incident_type: IncidentType
    priority: IncidentPriority = IncidentPriority.MEDIUM
    
    # Guest and location
    guest_id: Optional[UUID] = None
    room_number: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    
    # Reporter information
    reporter_name: str = Field(..., max_length=100)
    reporter_contact: Optional[str] = Field(None, max_length=100)
    
    # Optional fields
    tags: Optional[str] = Field(None, max_length=500)
    external_reference: Optional[str] = Field(None, max_length=100)
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    
    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags format."""
        if v:
            tags = [tag.strip() for tag in v.split(",")]
            if len(tags) > 10:
                raise ValueError("Maximum 10 tags allowed")
            for tag in tags:
                if len(tag) > 50:
                    raise ValueError("Each tag must be 50 characters or less")
        return v


class IncidentUpdateRequest(BaseRequest):
    """Request model for updating an incident."""
    
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    
    # Assignment
    assigned_to: Optional[str] = Field(None, max_length=100)
    assigned_team: Optional[str] = Field(None, max_length=50)
    
    # Resolution
    resolution_summary: Optional[str] = None
    resolution_category: Optional[str] = Field(None, max_length=50)
    guest_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    
    # Financial
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    compensation_amount: Optional[Decimal] = Field(None, ge=0)
    
    # Additional
    tags: Optional[str] = Field(None, max_length=500)
    
    # Update information
    update_text: Optional[str] = None
    is_guest_visible: bool = False


class IncidentEscalateRequest(BaseRequest):
    """Request model for escalating an incident."""
    
    reason: EscalationReason
    escalated_to: str = Field(..., max_length=100)
    notes: Optional[str] = None


class IncidentResponse(BaseResponse):
    """Response model for incident details."""
    
    incident_number: str
    title: str
    description: str
    incident_type: IncidentType
    category: IncidentCategory
    priority: IncidentPriority
    status: IncidentStatus
    
    # Guest and location
    guest_id: Optional[UUID]
    room_number: Optional[str]
    location: Optional[str]
    hotel_code: Optional[str]
    department: Optional[str]
    
    # Timing
    reported_at: datetime
    acknowledged_at: Optional[datetime]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    # SLA
    sla_target_minutes: Optional[int]
    sla_breached: bool
    sla_breach_time: Optional[datetime]
    
    # Assignment
    assigned_to: Optional[str]
    assigned_team: Optional[str]
    reporter_name: Optional[str]
    
    # Resolution
    resolution_summary: Optional[str]
    guest_satisfaction: Optional[int]
    follow_up_required: bool
    follow_up_date: Optional[datetime]
    
    # Financial
    estimated_cost: Optional[Decimal]
    actual_cost: Optional[Decimal]
    compensation_amount: Optional[Decimal]
    currency: Optional[str]
    
    # Escalation
    escalation_level: int
    escalation_reason: Optional[EscalationReason]
    escalated_to: Optional[str]
    escalated_at: Optional[datetime]
    
    # Computed fields
    response_time_minutes: Optional[int]
    resolution_time_minutes: Optional[int]
    is_sla_at_risk: bool
    should_escalate: bool
    
    @classmethod
    def from_orm_with_computed(cls, incident: Incident):
        """Create response from ORM object with computed fields."""
        data = incident.to_dict()
        
        # Add computed fields
        response_time = incident.calculate_response_time()
        resolution_time = incident.calculate_resolution_time()
        
        data.update({
            "response_time_minutes": int(response_time.total_seconds() / 60) if response_time else None,
            "resolution_time_minutes": int(resolution_time.total_seconds() / 60) if resolution_time else None,
            "is_sla_at_risk": incident.is_sla_at_risk(),
            "should_escalate": incident.should_escalate(),
        })
        
        return cls(**data)


class IncidentSearchRequest(BaseRequest):
    """Request model for incident search."""
    
    query: Optional[str] = Field(None, description="Search query")
    incident_number: Optional[str] = Field(None, max_length=20)
    incident_type: Optional[IncidentType] = None
    category: Optional[IncidentCategory] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    
    # Guest and location filters
    guest_id: Optional[UUID] = None
    room_number: Optional[str] = Field(None, max_length=20)
    hotel_code: Optional[str] = Field(None, max_length=10)
    department: Optional[str] = Field(None, max_length=50)
    
    # Assignment filters
    assigned_to: Optional[str] = Field(None, max_length=100)
    assigned_team: Optional[str] = Field(None, max_length=50)
    
    # Date filters
    reported_after: Optional[datetime] = None
    reported_before: Optional[datetime] = None
    resolved_after: Optional[datetime] = None
    resolved_before: Optional[datetime] = None
    
    # SLA and escalation filters
    sla_breached: Optional[bool] = None
    escalation_level: Optional[int] = Field(None, ge=0)
    needs_escalation: Optional[bool] = None
    
    # Additional filters
    has_guest_satisfaction: Optional[bool] = None
    follow_up_required: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=500)


class IncidentStatsResponse(BaseModel):
    """Response model for incident statistics."""
    
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    average_resolution_time_hours: float
    sla_compliance_rate: float
    
    incidents_by_type: Dict[str, int]
    incidents_by_priority: Dict[str, int]
    incidents_by_status: Dict[str, int]
    incidents_by_department: Dict[str, int]
    
    top_incident_locations: List[Dict[str, Any]]
    escalation_trends: Dict[str, int]
    guest_satisfaction_average: Optional[float]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }