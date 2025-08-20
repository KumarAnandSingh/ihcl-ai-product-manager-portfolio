"""
Security Agent.
Handles security incidents, access management, and safety protocols.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResponse


class SecurityAgent(BaseAgent):
    """Agent specialized in security and safety management."""
    
    def __init__(self):
        super().__init__(
            agent_id="security_agent",
            capabilities=[
                AgentCapability.SECURITY_MONITORING,
                AgentCapability.INCIDENT_MANAGEMENT
            ]
        )
    
    def get_system_prompt(self) -> str:
        return f"""You are a hotel security specialist responsible for guest safety and property security.
Handle security incidents, access issues, and safety concerns with professionalism and urgency.
Always prioritize guest safety while maintaining security protocols.
Current date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Process security-related request."""
        
        # Classify security issue
        issue_type = self._classify_security_issue(request)
        severity = self._assess_security_severity(request)
        
        # Get security context
        security_context = await self._get_security_context(context)
        
        # Take immediate actions for high-severity issues
        actions_taken = []
        if severity in ["high", "critical"]:
            actions_taken = await self._execute_emergency_response(issue_type, context)
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(issue_type, severity)
        
        # Determine escalation
        escalation_required = severity in ["high", "critical"]
        
        return AgentResponse(
            success=True,
            message=f"Security assessment completed. Issue type: {issue_type}, Severity: {severity}. Appropriate protocols have been initiated.",
            data={
                "issue_type": issue_type,
                "severity": severity,
                "security_context": security_context
            },
            actions_taken=actions_taken,
            recommendations=recommendations,
            escalation_required=escalation_required,
            escalation_reason=f"Security incident - {severity} severity" if escalation_required else None,
            confidence_score=0.9
        )
    
    def _classify_security_issue(self, request: str) -> str:
        """Classify the type of security issue."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["emergency", "fire", "medical"]):
            return "emergency"
        elif any(word in request_lower for word in ["access", "key", "card", "locked"]):
            return "access_issue"
        elif any(word in request_lower for word in ["theft", "stolen", "missing"]):
            return "theft"
        elif any(word in request_lower for word in ["suspicious", "unauthorized", "stranger"]):
            return "suspicious_activity"
        elif any(word in request_lower for word in ["noise", "disturbance", "loud"]):
            return "disturbance"
        else:
            return "general_security"
    
    def _assess_security_severity(self, request: str) -> str:
        """Assess the severity of the security issue."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["emergency", "danger", "threat", "weapon"]):
            return "critical"
        elif any(word in request_lower for word in ["urgent", "immediate", "now", "help"]):
            return "high"
        elif any(word in request_lower for word in ["concerning", "worried", "suspicious"]):
            return "medium"
        else:
            return "low"
    
    async def _get_security_context(self, context: AgentContext) -> Dict:
        """Get relevant security context."""
        security_context = {}
        
        try:
            # Get recent security events
            recent_events = await self.security_service.get_recent_events(hours=24)
            security_context["recent_events"] = len(recent_events)
            
            # Get access logs if room specified
            if context.room_number:
                access_logs = await self.security_service.get_access_logs(context.room_number, days=1)
                security_context["access_logs"] = len(access_logs)
        except:
            pass
        
        return security_context
    
    async def _execute_emergency_response(self, issue_type: str, context: AgentContext) -> List[str]:
        """Execute emergency response protocols."""
        actions = []
        
        if issue_type == "emergency":
            actions.append("Emergency services contacted")
            actions.append("Hotel management notified immediately")
            actions.append("Emergency response team dispatched")
        
        elif issue_type == "theft":
            actions.append("Security team alerted")
            actions.append("Area secured and investigated")
            actions.append("Incident report initiated")
        
        elif issue_type == "suspicious_activity":
            actions.append("Security patrol dispatched to location")
            actions.append("Surveillance systems activated")
            actions.append("Staff in area notified")
        
        return actions
    
    def _generate_security_recommendations(self, issue_type: str, severity: str) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if severity in ["high", "critical"]:
            recommendations.append("Immediate management notification required")
            recommendations.append("Document all actions and evidence")
        
        if issue_type == "access_issue":
            recommendations.append("Review guest authorization")
            recommendations.append("Consider key card replacement")
        
        recommendations.append("Follow up with guest within 1 hour")
        recommendations.append("Update security protocols if needed")
        
        return recommendations