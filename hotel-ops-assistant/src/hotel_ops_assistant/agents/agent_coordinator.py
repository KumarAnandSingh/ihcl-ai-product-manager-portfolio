"""
Agent Coordinator.
Routes requests to appropriate specialized agents and coordinates multi-agent workflows.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResponse
from .guest_service_agent import GuestServiceAgent
from .complaint_handler_agent import ComplaintHandlerAgent
from .security_agent import SecurityAgent
from .fraud_detection_agent import FraudDetectionAgent


class AgentCoordinator:
    """Coordinates and routes requests to appropriate specialized agents."""
    
    def __init__(self):
        # Initialize all specialized agents
        self.agents = {
            "guest_service": GuestServiceAgent(),
            "complaint_handler": ComplaintHandlerAgent(),
            "security": SecurityAgent(),
            "fraud_detection": FraudDetectionAgent()
        }
        
        # Request routing patterns
        self.routing_patterns = {
            "complaint": {
                "keywords": ["complaint", "dissatisfied", "unhappy", "problem", "issue", "wrong"],
                "agent": "complaint_handler",
                "priority": "high"
            },
            "security": {
                "keywords": ["security", "safety", "emergency", "theft", "suspicious", "access"],
                "agent": "security",
                "priority": "urgent"
            },
            "fraud": {
                "keywords": ["fraud", "suspicious transaction", "unauthorized", "stolen card", "fake"],
                "agent": "fraud_detection",
                "priority": "urgent"
            },
            "guest_service": {
                "keywords": ["service", "help", "assistance", "request", "booking", "room"],
                "agent": "guest_service",
                "priority": "medium"
            }
        }
    
    async def route_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Route request to appropriate agent and return response."""
        
        # Determine the best agent for this request
        agent_id, confidence = self._determine_best_agent(request, context)
        
        # Get the agent
        agent = self.agents.get(agent_id)
        if not agent:
            return self._create_error_response("Agent not available", context)
        
        try:
            # Process the request
            response = await agent.execute(request, context)
            
            # Add routing metadata
            response.data = response.data or {}
            response.data.update({
                "routed_to_agent": agent_id,
                "routing_confidence": confidence,
                "routing_timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            return self._create_error_response(f"Agent processing error: {str(e)}", context)
    
    def _determine_best_agent(self, request: str, context: AgentContext) -> Tuple[str, float]:
        """Determine the best agent to handle the request."""
        
        request_lower = request.lower()
        scores = {}
        
        # Score each agent based on keyword matches
        for category, config in self.routing_patterns.items():
            score = 0
            keyword_matches = 0
            
            for keyword in config["keywords"]:
                if keyword in request_lower:
                    keyword_matches += 1
                    # Give higher weight to exact matches
                    if keyword == request_lower.strip():
                        score += 10
                    else:
                        score += 5
            
            # Bonus for multiple keyword matches
            if keyword_matches > 1:
                score += keyword_matches * 2
            
            # Priority-based scoring
            priority_scores = {"urgent": 3, "high": 2, "medium": 1}
            score += priority_scores.get(config["priority"], 0)
            
            if score > 0:
                scores[config["agent"]] = score
        
        # Context-based adjustments
        if context.priority in ["urgent", "high"]:
            # Prefer complaint handler for high priority issues
            if "complaint_handler" in scores:
                scores["complaint_handler"] += 5
            
            # Prefer security for urgent matters with safety keywords
            if any(word in request_lower for word in ["emergency", "safety", "help"]):
                scores["security"] = scores.get("security", 0) + 5
        
        # VIP guest handling
        if context.context_data.get("vip_status"):
            # VIP guests should get specialized handling
            if "complaint_handler" in scores:
                scores["complaint_handler"] += 3
            if "guest_service" in scores:
                scores["guest_service"] += 2
        
        # Default to guest service if no clear match
        if not scores:
            scores["guest_service"] = 1
        
        # Get the agent with highest score
        best_agent = max(scores.items(), key=lambda x: x[1])
        agent_id = best_agent[0]
        
        # Calculate confidence (normalize score to 0-1 range)
        max_possible_score = 20  # Rough estimate of max possible score
        confidence = min(best_agent[1] / max_possible_score, 1.0)
        
        return agent_id, confidence
    
    def _create_error_response(self, error_message: str, context: AgentContext) -> AgentResponse:
        """Create a standardized error response."""
        return AgentResponse(
            success=False,
            message="I apologize, but I'm having difficulty processing your request right now. Please contact our front desk directly for immediate assistance.",
            escalation_required=True,
            escalation_reason=error_message,
            agent_id="coordinator",
            confidence_score=0.0
        )
    
    async def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all available agents."""
        capabilities = {}
        
        for agent_id, agent in self.agents.items():
            capabilities[agent_id] = [cap.value for cap in agent.capabilities]
        
        return capabilities
    
    async def get_system_health(self) -> Dict[str, any]:
        """Get health status of all agents."""
        health_status = {
            "coordinator_status": "healthy",
            "agents": {},
            "total_agents": len(self.agents),
            "healthy_agents": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        for agent_id, agent in self.agents.items():
            try:
                # Get agent performance metrics
                performance = agent.get_agent_performance()
                health_status["agents"][agent_id] = {
                    "status": "healthy",
                    "performance": performance
                }
                health_status["healthy_agents"] += 1
                
            except Exception as e:
                health_status["agents"][agent_id] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        health_status["system_health"] = "healthy" if health_status["healthy_agents"] == health_status["total_agents"] else "degraded"
        
        return health_status
    
    async def process_multi_agent_workflow(self, workflow_type: str, request: str, context: AgentContext) -> List[AgentResponse]:
        """Process workflows that require multiple agents."""
        
        responses = []
        
        if workflow_type == "complaint_with_fraud_check":
            # First check for fraud indicators
            fraud_response = await self.agents["fraud_detection"].execute(
                f"Analyze for fraud indicators: {request}", context
            )
            responses.append(fraud_response)
            
            # Then handle as complaint
            complaint_response = await self.agents["complaint_handler"].execute(request, context)
            responses.append(complaint_response)
            
        elif workflow_type == "security_incident_escalation":
            # Security assessment first
            security_response = await self.agents["security"].execute(request, context)
            responses.append(security_response)
            
            # If escalation required, also notify guest services
            if security_response.escalation_required:
                service_response = await self.agents["guest_service"].execute(
                    "Provide guest support for security incident", context
                )
                responses.append(service_response)
        
        return responses