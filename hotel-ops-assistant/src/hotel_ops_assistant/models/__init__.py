"""
Data models for Hotel Operations Assistant.
Includes guest profiles, incidents, compliance records, and system entities.
"""

from .base import BaseModel, TimestampMixin
from .guest import Guest, GuestProfile, GuestPreference, GuestHistory
from .incident import Incident, IncidentType, IncidentPriority, IncidentStatus
from .compliance import ComplianceRecord, PIICategory, AuditLog
from .hotel import Room, RoomType, Department, Staff
from .analytics import PerformanceMetric, KPITarget, AlertRule

__all__ = [
    # Base models
    "BaseModel",
    "TimestampMixin",
    
    # Guest models
    "Guest",
    "GuestProfile", 
    "GuestPreference",
    "GuestHistory",
    
    # Incident models
    "Incident",
    "IncidentType",
    "IncidentPriority", 
    "IncidentStatus",
    
    # Compliance models
    "ComplianceRecord",
    "PIICategory",
    "AuditLog",
    
    # Hotel models
    "Room",
    "RoomType",
    "Department",
    "Staff",
    
    # Analytics models
    "PerformanceMetric",
    "KPITarget",
    "AlertRule",
]