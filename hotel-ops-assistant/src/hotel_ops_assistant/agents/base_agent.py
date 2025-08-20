"""
Base Agent for Hotel Operations.
Provides common functionality and interfaces for all specialized agents.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..compliance.audit_logger import AuditLogger, AuditEventType
from ..services.hotel_systems import PMSService, POSService, CRMService, SecurityService, MaintenanceService


class AgentCapability(str, Enum):
    """Agent capabilities and specializations."""
    GUEST_SERVICE = "guest_service"
    COMPLAINT_HANDLING = "complaint_handling"
    SECURITY_MONITORING = "security_monitoring"
    FRAUD_DETECTION = "fraud_detection"
    MAINTENANCE_COORDINATION = "maintenance_coordination"
    CONCIERGE_SERVICES = "concierge_services"
    INCIDENT_MANAGEMENT = "incident_management"
    COMPLIANCE_MONITORING = "compliance_monitoring"


class AgentContext(BaseModel):
    """Context information for agent execution."""
    
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    guest_id: Optional[str] = None
    incident_id: Optional[str] = None
    hotel_code: Optional[str] = None
    room_number: Optional[str] = None
    language: str = "en"
    channel: str = "api"  # api, web, mobile, phone, email
    priority: str = "medium"  # low, medium, high, urgent
    
    # Additional context data
    context_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Conversation history
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Standardized agent response format."""
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    actions_taken: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    confidence_score: float = Field(ge=0, le=1, default=0.8)
    
    # System metadata
    agent_id: str
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None


class BaseAgent(ABC):
    """Abstract base class for all hotel operation agents."""
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.settings = get_settings()
        self.audit_logger = AuditLogger()
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize hotel system services
        self.pms_service = PMSService()
        self.pos_service = POSService()
        self.crm_service = CRMService()
        self.security_service = SecurityService()
        self.maintenance_service = MaintenanceService()
        
        # Agent-specific memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 interactions
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Performance tracking
        self._execution_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "escalations": 0
        }
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model for the agent."""
        llm_config = self.settings.get_llm_config()
        
        return ChatOpenAI(
            model_name=llm_config["model"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            openai_api_key=llm_config["api_keys"]["openai"]
        )
    
    @abstractmethod
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Process a request and return response."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    async def execute(self, request: str, context: AgentContext) -> AgentResponse:
        """Main execution method with monitoring and error handling."""
        start_time = datetime.now()
        
        try:
            # Log request
            self.audit_logger.log_event(
                event_type=AuditEventType.API_ACCESS,
                action=f"agent_request_{self.agent_id}",
                user_id=context.user_id,
                guest_id=context.guest_id,
                details={
                    "agent_id": self.agent_id,
                    "request_length": len(request),
                    "context": context.dict()
                }
            )
            
            # Update context
            context.last_updated = datetime.now()
            context.conversation_history.append({
                "role": "user",
                "content": request,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process request
            response = await self.process_request(request, context)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            response.processing_time_ms = int(processing_time)
            response.agent_id = self.agent_id
            
            # Update conversation history
            context.conversation_history.append({
                "role": "assistant",
                "content": response.message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update statistics
            self._update_stats(True, processing_time, response.escalation_required)
            
            # Log response
            self.audit_logger.log_event(
                event_type=AuditEventType.API_ACCESS,
                action=f"agent_response_{self.agent_id}",
                outcome="success",
                user_id=context.user_id,
                guest_id=context.guest_id,
                details={
                    "agent_id": self.agent_id,
                    "processing_time_ms": processing_time,
                    "escalation_required": response.escalation_required,
                    "confidence_score": response.confidence_score
                }
            )
            
            return response
            
        except Exception as e:
            # Handle errors
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_stats(False, processing_time, False)
            
            error_response = AgentResponse(
                success=False,
                message=f"I apologize, but I encountered an error while processing your request. Please try again or contact support if the issue persists.",
                agent_id=self.agent_id,
                processing_time_ms=int(processing_time),
                escalation_required=True,
                escalation_reason=f"Agent error: {str(e)}"
            )
            
            # Log error
            self.audit_logger.log_event(
                event_type=AuditEventType.API_ACCESS,
                action=f"agent_error_{self.agent_id}",
                outcome="failure",
                user_id=context.user_id,
                guest_id=context.guest_id,
                details={
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "processing_time_ms": processing_time
                }
            )
            
            return error_response
    
    def _update_stats(self, success: bool, processing_time: float, escalated: bool):
        """Update agent performance statistics."""
        self._execution_stats["total_requests"] += 1
        
        if success:
            self._execution_stats["successful_requests"] += 1
        else:
            self._execution_stats["failed_requests"] += 1
        
        if escalated:
            self._execution_stats["escalations"] += 1
        
        # Update average response time
        total_requests = self._execution_stats["total_requests"]
        current_avg = self._execution_stats["average_response_time"]
        self._execution_stats["average_response_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    async def get_guest_context(self, guest_id: str) -> Dict[str, Any]:
        """Get comprehensive guest context from various systems."""
        try:
            # Get data from multiple systems in parallel
            tasks = [
                self.pms_service.get_guest_reservation(guest_id),
                self.crm_service.get_guest_profile(guest_id),
                self.crm_service.get_guest_history(guest_id),
                self.pos_service.get_guest_transactions(guest_id, days=30)
            ]
            
            reservation, crm_profile, guest_history, recent_transactions = await asyncio.gather(*tasks, return_exceptions=True)
            
            context = {
                "guest_id": guest_id,
                "current_reservation": reservation if not isinstance(reservation, Exception) else None,
                "crm_profile": crm_profile if not isinstance(crm_profile, Exception) else None,
                "guest_history": guest_history if not isinstance(guest_history, Exception) else None,
                "recent_transactions": recent_transactions if not isinstance(recent_transactions, Exception) else [],
                "vip_status": False,
                "loyalty_tier": "Standard",
                "special_requirements": []
            }
            
            # Enhance context with computed fields
            if context["crm_profile"]:
                context["vip_status"] = context["crm_profile"].loyalty_tier in ["Platinum", "Diamond"]
                context["loyalty_tier"] = context["crm_profile"].loyalty_tier
            
            if context["current_reservation"]:
                context["room_number"] = context["current_reservation"].room_number
                context["check_out_date"] = context["current_reservation"].check_out
                context["special_requirements"] = context["current_reservation"].special_requests or []
            
            return context
            
        except Exception as e:
            self.audit_logger.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                action="guest_context_fetch_error",
                outcome="failure",
                guest_id=guest_id,
                details={"error": str(e)}
            )
            return {"guest_id": guest_id, "error": "Unable to fetch guest context"}
    
    async def create_incident(self, incident_data: Dict[str, Any], context: AgentContext) -> str:
        """Create an incident for issues that require tracking."""
        try:
            # This would integrate with the incident management system
            incident_id = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Log incident creation
            self.audit_logger.log_incident_event(
                incident_id=incident_id,
                action="create",
                user_id=context.user_id,
                guest_id=context.guest_id,
                after_state=incident_data
            )
            
            return incident_id
            
        except Exception as e:
            raise Exception(f"Failed to create incident: {str(e)}")
    
    def format_response_with_context(self, response: str, context: AgentContext) -> str:
        """Format response with appropriate context and personalization."""
        # Add personalization based on guest context
        if context.guest_id and "guest" not in response.lower():
            response = f"Dear valued guest, {response}"
        
        # Add language-specific formatting
        if context.language != "en":
            response += f"\n\n[Response language: {context.language}]"
        
        # Add urgency indicators
        if context.priority in ["high", "urgent"]:
            response = f"⚠️ {response}"
        
        return response
    
    def should_escalate(self, context: AgentContext, confidence: float) -> tuple[bool, str]:
        """Determine if the request should be escalated."""
        escalation_reasons = []
        
        # Low confidence
        if confidence < 0.6:
            escalation_reasons.append("Low confidence in response")
        
        # VIP guest
        if context.context_data.get("vip_status"):
            escalation_reasons.append("VIP guest request")
        
        # High priority
        if context.priority in ["urgent", "critical"]:
            escalation_reasons.append("High priority request")
        
        # Sensitive topics
        sensitive_keywords = ["complaint", "refund", "compensation", "legal", "emergency"]
        if any(keyword in context.context_data.get("request_text", "").lower() for keyword in sensitive_keywords):
            escalation_reasons.append("Sensitive topic detected")
        
        should_escalate = len(escalation_reasons) > 0
        escalation_reason = "; ".join(escalation_reasons) if escalation_reasons else None
        
        return should_escalate, escalation_reason
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        stats = self._execution_stats.copy()
        
        # Calculate derived metrics
        if stats["total_requests"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
            stats["escalation_rate"] = stats["escalations"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0.0
            stats["escalation_rate"] = 0.0
        
        return {
            "agent_id": self.agent_id,
            "capabilities": [cap.value for cap in self.capabilities],
            "performance_metrics": stats,
            "status": "active"
        }
    
    def can_handle(self, capability: AgentCapability) -> bool:
        """Check if agent can handle a specific capability."""
        return capability in self.capabilities
    
    async def prepare_context_for_llm(self, context: AgentContext) -> List[BaseMessage]:
        """Prepare context and conversation history for LLM."""
        messages = []
        
        # System prompt
        system_prompt = self.get_system_prompt()
        if context.guest_id:
            guest_context = await self.get_guest_context(context.guest_id)
            system_prompt += f"\n\nGuest Context: {guest_context}"
        
        messages.append(SystemMessage(content=system_prompt))
        
        # Add conversation history
        for msg in context.conversation_history[-10:]:  # Last 10 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages