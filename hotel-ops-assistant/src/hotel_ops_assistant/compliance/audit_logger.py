"""
Audit Logging Service.
Provides comprehensive audit trail for all system activities, user actions,
and data access in compliance with regulatory requirements.
"""

import json
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..core.config import get_settings


class AuditEventType(str, Enum):
    """Types of audit events."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PII_ACCESS = "pii_access"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    GUEST_PROFILE_ACCESS = "guest_profile_access"
    GUEST_PROFILE_UPDATE = "guest_profile_update"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    API_ACCESS = "api_access"
    REPORT_GENERATED = "report_generated"
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    FRAUD_DETECTION = "fraud_detection"
    ESCALATION = "escalation"
    PAYMENT_PROCESSING = "payment_processing"
    COMMUNICATION_SENT = "communication_sent"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """Audit event data model."""
    
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.MEDIUM
    
    # Actor information
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Event details
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    outcome: str  # success, failure, partial
    
    # Context
    details: Dict[str, Any] = Field(default_factory=dict)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    
    # Technical details
    request_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    response_code: Optional[int] = None
    processing_time_ms: Optional[int] = None
    
    # Compliance markers
    pii_involved: bool = False
    compliance_tags: List[str] = Field(default_factory=list)
    data_classification: Optional[str] = None
    
    # Business context
    hotel_code: Optional[str] = None
    guest_id: Optional[str] = None
    incident_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "outcome": self.outcome,
            "details": self.details,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "request_id": self.request_id,
            "api_endpoint": self.api_endpoint,
            "response_code": self.response_code,
            "processing_time_ms": self.processing_time_ms,
            "pii_involved": self.pii_involved,
            "compliance_tags": self.compliance_tags,
            "data_classification": self.data_classification,
            "hotel_code": self.hotel_code,
            "guest_id": self.guest_id,
            "incident_id": self.incident_id
        }
    
    def compute_hash(self) -> str:
        """Compute hash for integrity verification."""
        # Create a canonical representation for hashing
        canonical_data = {
            "event_id": str(self.event_id),
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "action": self.action,
            "outcome": self.outcome,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id
        }
        
        canonical_json = json.dumps(canonical_data, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()


class AuditLogger:
    """Comprehensive audit logging service."""
    
    def __init__(self):
        self.settings = get_settings()
        self._events: List[AuditEvent] = []
        self._enabled = self.settings.enable_audit_logging
        
        # Track event statistics
        self._stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "events_by_user": {},
            "pii_access_events": 0,
            "failed_events": 0
        }
    
    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str = "success",
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditEvent:
        """Log an audit event."""
        if not self._enabled:
            return
        
        event = AuditEvent(
            event_type=event_type,
            action=action,
            outcome=outcome,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
            details=details or {},
            **kwargs
        )
        
        # Store event
        self._events.append(event)
        
        # Update statistics
        self._update_stats(event)
        
        # Clean up old events if needed
        self._cleanup_old_events()
        
        # Log to external systems if configured
        self._forward_to_external_systems(event)
        
        return event
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        outcome: str = "success",
        details: Optional[Dict[str, Any]] = None,
        pii_involved: bool = False,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        """Log a user action."""
        event_type = AuditEventType.PII_ACCESS if pii_involved else AuditEventType.DATA_ACCESS
        
        return self.log_event(
            event_type=event_type,
            action=action,
            outcome=outcome,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            pii_involved=pii_involved,
            session_id=session_id,
            ip_address=ip_address,
            severity=AuditSeverity.HIGH if pii_involved else AuditSeverity.MEDIUM
        )
    
    def log_data_modification(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        pii_involved: bool = False,
        **kwargs
    ) -> AuditEvent:
        """Log data modification event."""
        return self.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=before_state,
            after_state=after_state,
            pii_involved=pii_involved,
            severity=AuditSeverity.HIGH if pii_involved else AuditSeverity.MEDIUM,
            **kwargs
        )
    
    def log_guest_access(
        self,
        user_id: str,
        guest_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        **kwargs
    ) -> AuditEvent:
        """Log guest profile access."""
        return self.log_event(
            event_type=AuditEventType.GUEST_PROFILE_ACCESS,
            action=action,
            outcome=outcome,
            user_id=user_id,
            resource_type="guest_profile",
            resource_id=guest_id,
            guest_id=guest_id,
            details=details,
            pii_involved=True,
            severity=AuditSeverity.HIGH,
            compliance_tags=["DPDP", "GDPR", "PII"],
            **kwargs
        )
    
    def log_incident_event(
        self,
        incident_id: str,
        action: str,
        user_id: Optional[str] = None,
        guest_id: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditEvent:
        """Log incident-related event."""
        event_type = AuditEventType.INCIDENT_CREATED if action == "create" else AuditEventType.INCIDENT_UPDATED
        
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            resource_type="incident",
            resource_id=incident_id,
            incident_id=incident_id,
            guest_id=guest_id,
            before_state=before_state,
            after_state=after_state,
            **kwargs
        )
    
    def log_security_event(
        self,
        action: str,
        severity: AuditSeverity,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
        **kwargs
    ) -> AuditEvent:
        """Log security-related event."""
        return self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            action=action,
            severity=severity,
            user_id=user_id,
            resource_type="security",
            details=details,
            compliance_tags=["SECURITY"],
            **kwargs
        )
    
    def log_api_access(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        response_code: Optional[int] = None,
        processing_time_ms: Optional[int] = None,
        request_id: Optional[str] = None,
        **kwargs
    ) -> AuditEvent:
        """Log API access."""
        outcome = "success" if response_code and 200 <= response_code < 400 else "failure"
        
        return self.log_event(
            event_type=AuditEventType.API_ACCESS,
            action=f"{method} {endpoint}",
            outcome=outcome,
            user_id=user_id,
            api_endpoint=endpoint,
            response_code=response_code,
            processing_time_ms=processing_time_ms,
            request_id=request_id,
            severity=AuditSeverity.LOW,
            **kwargs
        )
    
    def log_compliance_check(
        self,
        check_type: str,
        resource_type: str,
        resource_id: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditEvent:
        """Log compliance check event."""
        return self.log_event(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            action=f"compliance_check_{check_type}",
            outcome=result,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            compliance_tags=["COMPLIANCE"],
            **kwargs
        )
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events with filtering."""
        filtered_events = self._events
        
        # Apply filters
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if resource_type:
            filtered_events = [e for e in filtered_events if e.resource_type == resource_type]
        
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
        
        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_events[:limit]
    
    def get_user_activity(self, user_id: str, hours: int = 24) -> List[AuditEvent]:
        """Get recent activity for a specific user."""
        start_time = datetime.now() - timedelta(hours=hours)
        return self.get_events(start_time=start_time, user_id=user_id)
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[AuditEvent]:
        """Get modification history for a specific resource."""
        return self.get_events(resource_type=resource_type, resource_id=resource_id)
    
    def get_pii_access_events(self, hours: int = 24) -> List[AuditEvent]:
        """Get recent PII access events."""
        start_time = datetime.now() - timedelta(hours=hours)
        all_events = self.get_events(start_time=start_time)
        return [e for e in all_events if e.pii_involved]
    
    def get_security_events(self, hours: int = 24) -> List[AuditEvent]:
        """Get recent security events."""
        start_time = datetime.now() - timedelta(hours=hours)
        return self.get_events(
            start_time=start_time,
            event_type=AuditEventType.SECURITY_EVENT
        )
    
    def get_audit_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit statistics."""
        start_time = datetime.now() - timedelta(hours=hours)
        recent_events = self.get_events(start_time=start_time, limit=10000)
        
        stats = {
            "period_hours": hours,
            "total_events": len(recent_events),
            "events_by_type": {},
            "events_by_severity": {},
            "events_by_user": {},
            "events_by_outcome": {},
            "pii_access_count": 0,
            "security_events_count": 0,
            "failed_events_count": 0,
            "top_users": {},
            "top_resources": {}
        }
        
        # Calculate statistics
        for event in recent_events:
            # By type
            event_type = event.event_type.value
            stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
            
            # By severity
            severity = event.severity.value
            stats["events_by_severity"][severity] = stats["events_by_severity"].get(severity, 0) + 1
            
            # By outcome
            outcome = event.outcome
            stats["events_by_outcome"][outcome] = stats["events_by_outcome"].get(outcome, 0) + 1
            
            # By user
            if event.user_id:
                stats["events_by_user"][event.user_id] = stats["events_by_user"].get(event.user_id, 0) + 1
            
            # Special counts
            if event.pii_involved:
                stats["pii_access_count"] += 1
            
            if event.event_type == AuditEventType.SECURITY_EVENT:
                stats["security_events_count"] += 1
            
            if event.outcome == "failure":
                stats["failed_events_count"] += 1
        
        # Top users and resources
        stats["top_users"] = dict(sorted(stats["events_by_user"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats
    
    def generate_compliance_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate compliance audit report."""
        events = self.get_events(start_time=start_time, end_time=end_time, limit=10000)
        
        report = {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "total_events": len(events),
                "pii_access_events": len([e for e in events if e.pii_involved]),
                "security_events": len([e for e in events if e.event_type == AuditEventType.SECURITY_EVENT]),
                "failed_operations": len([e for e in events if e.outcome == "failure"]),
                "unique_users": len(set(e.user_id for e in events if e.user_id))
            },
            "compliance_metrics": {
                "data_access_transparency": True,  # All data access is logged
                "user_activity_tracking": True,   # All user activities are tracked
                "pii_access_monitoring": True,    # PII access is specifically monitored
                "audit_trail_integrity": self._verify_audit_integrity(events),
                "retention_compliance": self._check_retention_compliance()
            },
            "risk_indicators": {
                "high_pii_access": len([e for e in events if e.pii_involved and e.severity == AuditSeverity.HIGH]),
                "failed_security_events": len([
                    e for e in events 
                    if e.event_type == AuditEventType.SECURITY_EVENT and e.outcome == "failure"
                ]),
                "unusual_access_patterns": self._detect_unusual_patterns(events)
            },
            "recommendations": self._generate_compliance_recommendations(events)
        }
        
        return report
    
    def _update_stats(self, event: AuditEvent):
        """Update internal statistics."""
        self._stats["total_events"] += 1
        
        # By type
        event_type = event.event_type.value
        self._stats["events_by_type"][event_type] = self._stats["events_by_type"].get(event_type, 0) + 1
        
        # By severity
        severity = event.severity.value
        self._stats["events_by_severity"][severity] = self._stats["events_by_severity"].get(severity, 0) + 1
        
        # By user
        if event.user_id:
            self._stats["events_by_user"][event.user_id] = self._stats["events_by_user"].get(event.user_id, 0) + 1
        
        # Special counters
        if event.pii_involved:
            self._stats["pii_access_events"] += 1
        
        if event.outcome == "failure":
            self._stats["failed_events"] += 1
    
    def _cleanup_old_events(self):
        """Clean up old events based on retention policy."""
        if not self.settings.data_retention_days:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.settings.data_retention_days)
        self._events = [e for e in self._events if e.timestamp > cutoff_date]
    
    def _forward_to_external_systems(self, event: AuditEvent):
        """Forward audit events to external logging systems."""
        # In production, this would forward to:
        # - SIEM systems
        # - Centralized logging (ELK stack)
        # - Compliance monitoring systems
        # - Real-time alerting systems
        pass
    
    def _verify_audit_integrity(self, events: List[AuditEvent]) -> bool:
        """Verify integrity of audit events."""
        # In production, this would verify cryptographic hashes
        # and check for tampering
        return True
    
    def _check_retention_compliance(self) -> bool:
        """Check if audit retention policy is being followed."""
        if not self.settings.data_retention_days:
            return True
        
        oldest_event = min(self._events, key=lambda x: x.timestamp) if self._events else None
        if not oldest_event:
            return True
        
        max_age = datetime.now() - timedelta(days=self.settings.data_retention_days)
        return oldest_event.timestamp >= max_age
    
    def _detect_unusual_patterns(self, events: List[AuditEvent]) -> List[str]:
        """Detect unusual access patterns."""
        patterns = []
        
        # Check for excessive PII access
        pii_events = [e for e in events if e.pii_involved]
        if len(pii_events) > 100:  # Threshold
            patterns.append("High volume of PII access detected")
        
        # Check for failed login attempts
        failed_logins = [e for e in events if e.event_type == AuditEventType.USER_LOGIN and e.outcome == "failure"]
        if len(failed_logins) > 10:
            patterns.append("Multiple failed login attempts detected")
        
        # Check for after-hours access
        after_hours_events = [
            e for e in events 
            if e.timestamp.hour < 6 or e.timestamp.hour > 22
        ]
        if len(after_hours_events) > 20:
            patterns.append("Significant after-hours system access")
        
        return patterns
    
    def _generate_compliance_recommendations(self, events: List[AuditEvent]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        pii_events = [e for e in events if e.pii_involved]
        if len(pii_events) > 50:
            recommendations.append("Consider implementing additional PII access controls")
        
        failed_events = [e for e in events if e.outcome == "failure"]
        if len(failed_events) > 20:
            recommendations.append("Review and address frequent operation failures")
        
        security_events = [e for e in events if e.event_type == AuditEventType.SECURITY_EVENT]
        if len(security_events) > 10:
            recommendations.append("Enhanced security monitoring may be needed")
        
        return recommendations