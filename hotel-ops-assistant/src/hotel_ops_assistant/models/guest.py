"""
Guest models for Hotel Operations Assistant.
Includes comprehensive guest profiles, preferences, history, and PII protection.
"""

import hashlib
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import (
    Column, String, Text, Integer, Boolean, Date, DateTime, Numeric,
    ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator, EmailStr

from .base import BaseModel as SQLBaseModel, BaseResponse, BaseRequest


class GuestTier(str, Enum):
    """Guest loyalty tier levels."""
    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class GuestStatus(str, Enum):
    """Guest account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    VIP = "vip"


class PreferenceCategory(str, Enum):
    """Guest preference categories."""
    ROOM = "room"
    DINING = "dining"
    SERVICE = "service"
    COMMUNICATION = "communication"
    ACCESSIBILITY = "accessibility"


class Guest(SQLBaseModel):
    """
    Guest profile model with PII protection and compliance features.
    Stores encrypted sensitive data with audit trail.
    """
    
    __tablename__ = "guests"
    
    # Basic Information (Some fields encrypted)
    guest_number = Column(String(20), unique=True, nullable=False, comment="Unique guest identifier")
    title = Column(String(10), comment="Guest title (Mr., Mrs., etc.)")
    first_name_encrypted = Column(Text, comment="Encrypted first name")
    last_name_encrypted = Column(Text, comment="Encrypted last name") 
    email_encrypted = Column(Text, comment="Encrypted email address")
    phone_encrypted = Column(Text, comment="Encrypted phone number")
    
    # Non-sensitive demographic data
    date_of_birth = Column(Date, comment="Date of birth")
    nationality = Column(String(3), comment="Nationality code (ISO 3166-1)")
    language_preference = Column(String(10), default="en", comment="Preferred language")
    
    # Loyalty and Status
    tier = Column(SQLEnum(GuestTier), default=GuestTier.STANDARD, nullable=False)
    status = Column(SQLEnum(GuestStatus), default=GuestStatus.ACTIVE, nullable=False)
    loyalty_points = Column(Integer, default=0, comment="Current loyalty points balance")
    lifetime_value = Column(Numeric(12, 2), default=0, comment="Total lifetime spend")
    
    # Risk and Compliance
    is_pii_protected = Column(Boolean, default=True, comment="PII protection enabled")
    data_retention_until = Column(DateTime, comment="Data retention expiry date")
    consent_marketing = Column(Boolean, default=False, comment="Marketing consent")
    consent_analytics = Column(Boolean, default=False, comment="Analytics consent")
    last_consent_update = Column(DateTime, comment="Last consent update")
    
    # Security
    password_hash = Column(String(255), comment="Hashed password for guest portal")
    failed_login_attempts = Column(Integer, default=0, comment="Failed login count")
    account_locked_until = Column(DateTime, comment="Account lockout expiry")
    two_factor_enabled = Column(Boolean, default=False, comment="2FA status")
    
    # Hotel-specific
    home_hotel_code = Column(String(10), comment="Primary hotel preference")
    vip_notes = Column(Text, comment="VIP guest notes")
    special_requirements = Column(Text, comment="Special accommodation needs")
    
    # Relationships
    preferences = relationship("GuestPreference", back_populates="guest", cascade="all, delete-orphan")
    history = relationship("GuestHistory", back_populates="guest", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="guest")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_guest_number', 'guest_number'),
        Index('idx_guest_email_hash', 'email_encrypted'),
        Index('idx_guest_tier_status', 'tier', 'status'),
        Index('idx_guest_home_hotel', 'home_hotel_code'),
    )
    
    def get_display_name(self, decrypt_func) -> str:
        """Get guest display name (requires decryption function)."""
        first_name = decrypt_func(self.first_name_encrypted) if self.first_name_encrypted else ""
        last_name = decrypt_func(self.last_name_encrypted) if self.last_name_encrypted else ""
        return f"{first_name} {last_name}".strip() or self.guest_number
    
    def get_email_hash(self) -> str:
        """Get hash of email for lookup purposes."""
        if self.email_encrypted:
            return hashlib.sha256(self.email_encrypted.encode()).hexdigest()[:16]
        return ""
    
    def is_vip(self) -> bool:
        """Check if guest is VIP status."""
        return self.status == GuestStatus.VIP or self.tier in [GuestTier.PLATINUM, GuestTier.DIAMOND]
    
    def calculate_age(self) -> Optional[int]:
        """Calculate guest age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class GuestPreference(SQLBaseModel):
    """Guest preferences and special requirements."""
    
    __tablename__ = "guest_preferences"
    
    guest_id = Column(PostgresUUID(as_uuid=True), ForeignKey("guests.id"), nullable=False)
    category = Column(SQLEnum(PreferenceCategory), nullable=False)
    preference_key = Column(String(100), nullable=False, comment="Preference identifier")
    preference_value = Column(Text, comment="Preference value")
    priority = Column(Integer, default=1, comment="Preference priority (1=highest)")
    is_active = Column(Boolean, default=True, comment="Preference active status")
    notes = Column(Text, comment="Additional notes about preference")
    
    # Relationships
    guest = relationship("Guest", back_populates="preferences")
    
    # Indexes
    __table_args__ = (
        Index('idx_guest_pref_guest_category', 'guest_id', 'category'),
        Index('idx_guest_pref_key', 'preference_key'),
    )


class GuestHistory(SQLBaseModel):
    """Guest interaction and stay history."""
    
    __tablename__ = "guest_history"
    
    guest_id = Column(PostgresUUID(as_uuid=True), ForeignKey("guests.id"), nullable=False)
    event_type = Column(String(50), nullable=False, comment="Type of event/interaction")
    event_date = Column(DateTime, nullable=False, comment="Event timestamp")
    hotel_code = Column(String(10), comment="Hotel where event occurred")
    room_number = Column(String(20), comment="Room number if applicable")
    
    # Event details
    description = Column(Text, comment="Event description")
    amount = Column(Numeric(12, 2), comment="Associated amount if applicable")
    currency = Column(String(3), comment="Currency code")
    service_rating = Column(Integer, comment="Guest service rating (1-5)")
    
    # System tracking
    source_system = Column(String(50), comment="System that recorded the event")
    reference_number = Column(String(100), comment="External reference number")
    
    # Additional data
    metadata_json = Column(JSON, comment="Additional event metadata")
    
    # Relationships
    guest = relationship("Guest", back_populates="history")
    
    # Indexes
    __table_args__ = (
        Index('idx_guest_hist_guest_date', 'guest_id', 'event_date'),
        Index('idx_guest_hist_type', 'event_type'),
        Index('idx_guest_hist_hotel', 'hotel_code'),
    )


# Pydantic models for API
class GuestCreateRequest(BaseRequest):
    """Request model for creating a new guest profile."""
    
    title: Optional[str] = Field(None, max_length=10)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=3)
    language_preference: str = Field(default="en", max_length=10)
    
    # Consent
    consent_marketing: bool = Field(default=False)
    consent_analytics: bool = Field(default=False)
    
    # Optional fields
    home_hotel_code: Optional[str] = Field(None, max_length=10)
    special_requirements: Optional[str] = None
    
    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Remove non-digit characters
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        return v
    
    @validator("nationality")
    def validate_nationality(cls, v):
        """Validate nationality code format."""
        if v and len(v) != 3:
            raise ValueError("Nationality code must be 3 characters (ISO 3166-1)")
        return v.upper() if v else v


class GuestUpdateRequest(BaseRequest):
    """Request model for updating guest profile."""
    
    title: Optional[str] = Field(None, max_length=10)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    language_preference: Optional[str] = Field(None, max_length=10)
    
    # Status updates (admin only)
    tier: Optional[GuestTier] = None
    status: Optional[GuestStatus] = None
    
    # Consent updates
    consent_marketing: Optional[bool] = None
    consent_analytics: Optional[bool] = None
    
    # Hotel-specific
    home_hotel_code: Optional[str] = Field(None, max_length=10)
    special_requirements: Optional[str] = None


class GuestPreferenceRequest(BaseRequest):
    """Request model for guest preferences."""
    
    category: PreferenceCategory
    preference_key: str = Field(..., min_length=1, max_length=100)
    preference_value: str = Field(..., min_length=1)
    priority: int = Field(default=1, ge=1, le=10)
    notes: Optional[str] = None


class GuestResponse(BaseResponse):
    """Response model for guest profile (with PII masking)."""
    
    guest_number: str
    title: Optional[str]
    first_name: str  # Will be masked if PII protection is enabled
    last_name: str   # Will be masked if PII protection is enabled
    email: str       # Will be masked if PII protection is enabled
    phone: str       # Will be masked if PII protection is enabled
    
    date_of_birth: Optional[date]
    nationality: Optional[str]
    language_preference: str
    
    tier: GuestTier
    status: GuestStatus
    loyalty_points: int
    lifetime_value: Decimal
    
    home_hotel_code: Optional[str]
    special_requirements: Optional[str]
    
    is_vip: bool
    age: Optional[int]
    
    @classmethod
    def from_orm_with_masking(cls, guest: Guest, mask_pii: bool = True, decrypt_func=None):
        """Create response from ORM object with PII masking."""
        data = guest.to_dict()
        
        if mask_pii and guest.is_pii_protected:
            # Mask PII fields
            data["first_name"] = "*****" if guest.first_name_encrypted else ""
            data["last_name"] = "*****" if guest.last_name_encrypted else ""
            data["email"] = "*****@*****.***" if guest.email_encrypted else ""
            data["phone"] = "*****" if guest.phone_encrypted else ""
        else:
            # Decrypt PII fields
            if decrypt_func:
                data["first_name"] = decrypt_func(guest.first_name_encrypted) if guest.first_name_encrypted else ""
                data["last_name"] = decrypt_func(guest.last_name_encrypted) if guest.last_name_encrypted else ""
                data["email"] = decrypt_func(guest.email_encrypted) if guest.email_encrypted else ""
                data["phone"] = decrypt_func(guest.phone_encrypted) if guest.phone_encrypted else ""
        
        # Add computed fields
        data["is_vip"] = guest.is_vip()
        data["age"] = guest.calculate_age()
        
        return cls(**data)


class GuestPreferenceResponse(BaseResponse):
    """Response model for guest preferences."""
    
    guest_id: UUID
    category: PreferenceCategory
    preference_key: str
    preference_value: str
    priority: int
    is_active: bool
    notes: Optional[str]


class GuestHistoryResponse(BaseResponse):
    """Response model for guest history."""
    
    guest_id: UUID
    event_type: str
    event_date: datetime
    hotel_code: Optional[str]
    room_number: Optional[str]
    description: Optional[str]
    amount: Optional[Decimal]
    currency: Optional[str]
    service_rating: Optional[int]
    source_system: Optional[str]
    reference_number: Optional[str]


class GuestSearchRequest(BaseRequest):
    """Request model for guest search."""
    
    query: Optional[str] = Field(None, description="Search query (name, email, phone, guest number)")
    guest_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    tier: Optional[GuestTier] = None
    status: Optional[GuestStatus] = None
    hotel_code: Optional[str] = Field(None, max_length=10)
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_stay_after: Optional[datetime] = None
    last_stay_before: Optional[datetime] = None
    
    # Advanced filters
    min_lifetime_value: Optional[Decimal] = Field(None, ge=0)
    max_lifetime_value: Optional[Decimal] = Field(None, ge=0)
    has_special_requirements: Optional[bool] = None
    vip_only: Optional[bool] = None


class GuestStatsResponse(BaseModel):
    """Response model for guest statistics."""
    
    total_guests: int
    active_guests: int
    vip_guests: int
    guests_by_tier: Dict[str, int]
    guests_by_status: Dict[str, int]
    average_lifetime_value: Decimal
    total_loyalty_points: int
    new_guests_this_month: int
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }