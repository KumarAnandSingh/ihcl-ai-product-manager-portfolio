"""
API routes setup and configuration.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..agents.base_agent import AgentContext
from ..compliance.audit_logger import AuditEventType


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    guest_id: Optional[str] = None
    room_number: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "en"
    channel: str = "api"
    priority: str = "medium"
    context_data: Dict[str, any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
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
    data: Dict[str, any]
    operation: str
    framework: str = "dpdp_act_2023"


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Dict[str, any]]


def setup_routes(app: FastAPI) -> None:
    """Setup all API routes."""
    
    settings = get_settings()
    
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Hotel Operations Assistant API",
            "version": settings.app_version,
            "environment": settings.environment,
            "status": "operational",
            "docs_url": "/docs" if not settings.is_production else "Contact administrator for documentation"
        }
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check(request: Request):
        """Comprehensive health check endpoint."""
        
        try:
            # Check agent coordinator health
            agent_health = await request.app.state.agent_coordinator.get_system_health()
            
            # Check compliance service
            compliance_dashboard = request.app.state.compliance_service.get_compliance_dashboard()
            
            services_health = {
                "agents": {
                    "status": agent_health.get("system_health", "unknown"),
                    "details": agent_health
                },
                "compliance": {
                    "status": "healthy" if compliance_dashboard.get("overall_compliance_score", 0) > 70 else "warning",
                    "details": {
                        "compliance_score": compliance_dashboard.get("overall_compliance_score", 0),
                        "pii_protection": compliance_dashboard.get("pii_protection_enabled", False)
                    }
                },
                "audit_logging": {
                    "status": "healthy" if settings.enable_audit_logging else "disabled",
                    "details": {"enabled": settings.enable_audit_logging}
                }
            }
            
            # Determine overall status
            overall_status = "healthy"
            for service_status in services_health.values():
                if service_status["status"] in ["unhealthy", "error"]:
                    overall_status = "unhealthy"
                    break
                elif service_status["status"] == "warning":
                    overall_status = "warning"
            
            return HealthResponse(
                status=overall_status,
                timestamp=datetime.now(),
                version=settings.app_version,
                environment=settings.environment,
                services=services_health
            )
            
        except Exception as e:
            return HealthResponse(
                status="error",
                timestamp=datetime.now(),
                version=settings.app_version,
                environment=settings.environment,
                services={"error": {"status": "error", "details": str(e)}}
            )
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest,
        background_tasks: BackgroundTasks,
        http_request: Request
    ):
        """Main chat endpoint for guest interactions."""
        
        try:
            # Create agent context
            context = AgentContext(
                session_id=request.session_id or str(uuid.uuid4()),
                user_id=request.guest_id,  # For audit purposes
                guest_id=request.guest_id,
                room_number=request.room_number,
                language=request.language,
                channel=request.channel,
                priority=request.priority,
                context_data=request.context_data
            )
            
            # Route request to appropriate agent
            response = await http_request.app.state.agent_coordinator.route_request(
                request.message, context
            )
            
            # Convert to API response format
            api_response = ChatResponse(
                success=response.success,
                message=response.message,
                session_id=context.session_id,
                agent_id=response.agent_id,
                data=response.data,
                actions_taken=response.actions_taken,
                recommendations=response.recommendations,
                escalation_required=response.escalation_required,
                follow_up_required=response.follow_up_required,
                follow_up_date=response.follow_up_date,
                processing_time_ms=response.processing_time_ms,
                confidence_score=response.confidence_score
            )
            
            # Background compliance check
            if request.guest_id and request.context_data:
                background_tasks.add_task(
                    perform_compliance_check,
                    http_request.app.state.compliance_service,
                    request.context_data,
                    "chat_interaction"
                )
            
            return api_response
            
        except Exception as e:
            # Log error
            http_request.app.state.audit_logger.log_event(
                event_type=AuditEventType.API_ACCESS,
                action="chat_error",
                outcome="failure",
                details={"error": str(e)},
                guest_id=request.guest_id
            )
            
            raise HTTPException(
                status_code=500,
                detail="Unable to process your request at this time. Please contact front desk for assistance."
            )
    
    @app.post("/compliance/check")
    async def compliance_check(
        request: ComplianceCheckRequest,
        http_request: Request
    ):
        """Endpoint for compliance checking."""
        
        try:
            compliance_service = http_request.app.state.compliance_service
            
            if request.framework == "dpdp_act_2023":
                result = await compliance_service.check_dpdp_compliance(
                    request.data, request.operation
                )
            elif request.framework == "gdpr":
                result = await compliance_service.check_gdpr_compliance(
                    request.data, request.operation
                )
            elif request.framework == "pci_dss":
                result = await compliance_service.check_pci_dss_compliance(request.data)
            else:
                raise HTTPException(status_code=400, detail="Unsupported compliance framework")
            
            return {
                "check_id": result.check_id,
                "framework": result.framework.value,
                "status": result.status.value,
                "score": result.score,
                "recommendations": result.recommendations,
                "checked_at": result.checked_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")
    
    @app.get("/compliance/dashboard")
    async def compliance_dashboard(http_request: Request):
        """Get compliance dashboard data."""
        
        try:
            dashboard = http_request.app.state.compliance_service.get_compliance_dashboard()
            return dashboard
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to fetch compliance dashboard: {str(e)}")
    
    @app.get("/agents/capabilities")
    async def get_agent_capabilities(http_request: Request):
        """Get capabilities of all available agents."""
        
        try:
            capabilities = await http_request.app.state.agent_coordinator.get_agent_capabilities()
            return {"capabilities": capabilities}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to fetch agent capabilities: {str(e)}")
    
    @app.get("/audit/events")
    async def get_audit_events(
        http_request: Request,
        hours: int = 24,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ):
        """Get audit events with filtering."""
        
        try:
            from datetime import timedelta
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Convert string event_type to enum if provided
            event_type_enum = None
            if event_type:
                try:
                    event_type_enum = AuditEventType(event_type)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid event type")
            
            events = http_request.app.state.audit_logger.get_events(
                start_time=start_time,
                event_type=event_type_enum,
                user_id=user_id,
                limit=limit
            )
            
            # Convert events to dict format
            events_data = [event.to_dict() for event in events]
            
            return {
                "events": events_data,
                "total": len(events_data),
                "period_hours": hours,
                "filters": {
                    "event_type": event_type,
                    "user_id": user_id
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to fetch audit events: {str(e)}")
    
    @app.get("/audit/statistics")
    async def get_audit_statistics(
        http_request: Request,
        hours: int = 24
    ):
        """Get audit statistics."""
        
        try:
            stats = http_request.app.state.audit_logger.get_audit_statistics(hours=hours)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to fetch audit statistics: {str(e)}")
    
    @app.post("/data-subject-request")
    async def submit_data_subject_request(
        request_type: str,
        subject_id: str,
        subject_email: str,
        description: Optional[str] = None,
        http_request: Request = None
    ):
        """Submit data subject rights request."""
        
        try:
            from ..services.compliance_service import DataSubjectRequest, DataSubjectRights
            
            # Validate request type
            try:
                request_type_enum = DataSubjectRights(request_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid request type")
            
            # Create request
            data_request = DataSubjectRequest(
                request_id=f"DSR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                request_type=request_type_enum,
                subject_id=subject_id,
                subject_email=subject_email,
                requested_at=datetime.now(),
                description=description
            )
            
            # Process request
            response = await http_request.app.state.compliance_service.handle_data_subject_request(data_request)
            
            return {
                "request_id": data_request.request_id,
                "status": "submitted",
                "estimated_completion": "30 days",
                "response": response
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unable to process data subject request: {str(e)}")
    
    # Demo and testing endpoints
    @app.get("/demo/scenarios")
    async def get_demo_scenarios():
        """Get predefined demo scenarios for testing."""
        
        scenarios = {
            "guest_service": [
                "I need room service for dinner",
                "Can you help me book a spa appointment?",
                "What time does the gym close?",
                "I'd like a late checkout please"
            ],
            "complaints": [
                "My room is very dirty and hasn't been cleaned",
                "The staff at the restaurant was very rude to me",
                "I'm being charged for services I didn't use",
                "The noise from the construction is unbearable"
            ],
            "security": [
                "I can't access my room, my key card isn't working",
                "There's suspicious activity in the hallway",
                "I think someone has been in my room",
                "I lost my wallet in the lobby"
            ],
            "fraud_detection": [
                "Multiple credit cards used for same guest in one hour",
                "High-value transaction from foreign credit card",
                "Guest identity documents appear inconsistent",
                "Unusual access pattern detected for room 304"
            ]
        }
        
        return {"scenarios": scenarios}


async def perform_compliance_check(compliance_service, data: Dict, operation: str):
    """Background task for compliance checking."""
    try:
        await compliance_service.check_dpdp_compliance(data, operation)
    except Exception as e:
        # Log error but don't raise - this is a background task
        print(f"Background compliance check failed: {e}")