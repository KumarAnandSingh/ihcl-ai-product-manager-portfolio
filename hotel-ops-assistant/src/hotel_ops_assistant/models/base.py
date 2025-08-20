"""
Base models and mixins for Hotel Operations Assistant.
Provides common functionality for timestamps, UUIDs, and database operations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel, Field


# SQLAlchemy Base
Base = declarative_base()


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )


class UUIDMixin:
    """Mixin for adding UUID primary key to models."""
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the record"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )


class AuditMixin:
    """Mixin for audit trail functionality."""
    
    created_by = Column(
        String(255),
        nullable=True,
        comment="User who created the record"
    )
    
    updated_by = Column(
        String(255), 
        nullable=True,
        comment="User who last updated the record"
    )
    
    version = Column(
        String(50),
        default="1.0",
        nullable=False,
        comment="Record version for optimistic locking"
    )


class MetadataMixin:
    """Mixin for storing additional metadata."""
    
    metadata_json = Column(
        Text,
        nullable=True,
        comment="Additional metadata in JSON format"
    )
    
    tags = Column(
        String(1000),
        nullable=True,
        comment="Comma-separated tags for categorization"
    )


class BaseModel(Base, UUIDMixin, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """
    Abstract base model with common functionality.
    Includes UUID, timestamps, audit trail, and soft delete.
    """
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model."""
        return cls.__tablename__


# Pydantic models for API serialization
class BaseResponse(PydanticBaseModel):
    """Base response model with common fields."""
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


class BaseRequest(PydanticBaseModel):
    """Base request model with common validation."""
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True


class PaginationParams(PydanticBaseModel):
    """Standard pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(PydanticBaseModel):
    """Standard paginated response wrapper."""
    
    items: list = Field(description="List of items for current page")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")
    
    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse":
        """Create paginated response from query results."""
        total_pages = (total + page_size - 1) // page_size
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class HealthCheck(PydanticBaseModel):
    """Health check response model."""
    
    status: str = Field(description="Overall system status")
    timestamp: datetime = Field(description="Health check timestamp")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment name")
    services: Dict[str, Dict[str, Any]] = Field(description="Individual service statuses")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }