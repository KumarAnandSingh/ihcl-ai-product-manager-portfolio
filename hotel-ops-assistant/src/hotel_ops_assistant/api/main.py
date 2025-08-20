"""
Main FastAPI application for Hotel Operations Assistant.
Provides comprehensive API endpoints for all hotel operations.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from ..core.config import get_settings
from ..agents.agent_coordinator import AgentCoordinator
from ..agents.base_agent import AgentContext, AgentResponse
from ..compliance.audit_logger import AuditLogger, AuditEventType
from ..services.compliance_service import ComplianceService
from .middleware import setup_middleware
from .routes import setup_routes


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Dict[str, any]]


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=2000)
    guest_id: Optional[str] = None
    room_number: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "en"
    channel: str = "api"
    priority: str = "medium"
    context_data: Dict[str, any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Chat response model."""
    success: bool
    message: str
    session_id: str
    agent_id: str
    data: Optional[Dict[str, any]] = None
    actions_taken: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    escalation_required: bool = False
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    confidence_score: float


class ComplianceCheckRequest(BaseModel):
    """Compliance check request model."""
    data: Dict[str, any]
    operation: str
    framework: str = "dpdp_act_2023"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    settings = get_settings()
    
    # Initialize core services
    app.state.agent_coordinator = AgentCoordinator()
    app.state.audit_logger = AuditLogger()
    app.state.compliance_service = ComplianceService()
    
    # Log application startup
    app.state.audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_CONFIGURATION,
        action="application_startup",
        outcome="success",
        details={
            "version": settings.app_version,
            "environment": settings.environment
        }
    )
    
    yield
    
    # Shutdown
    app.state.audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_CONFIGURATION,
        action="application_shutdown",
        outcome="success"
    )


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    settings = get_settings()
    
    app = FastAPI(
        title="Hotel Operations Assistant",
        description="AI-powered hotel operations management system with comprehensive guest services, compliance, and fraud detection capabilities.",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup routes
    setup_routes(app)
    
    return app


# Global exception handler
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    
    # Log the error
    if hasattr(request.app.state, 'audit_logger'):
        request.app.state.audit_logger.log_event(
            event_type=AuditEventType.API_ACCESS,
            action=f"error_{request.method}_{request.url.path}",
            outcome="failure",
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal error occurred. Please try again or contact support.",
            "error_id": str(datetime.now().timestamp())
        }
    )


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "hotel_ops_assistant.api.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        workers=1 if settings.debug else settings.api_workers,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )