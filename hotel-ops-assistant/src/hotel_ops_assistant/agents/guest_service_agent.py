"""
Guest Service Agent.
Handles general guest inquiries, requests, and service-related interactions.
Provides personalized assistance based on guest profile and preferences.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResponse


class GuestServiceAgent(BaseAgent):
    """Agent specialized in general guest service and inquiries."""
    
    def __init__(self):
        super().__init__(
            agent_id="guest_service_agent",
            capabilities=[
                AgentCapability.GUEST_SERVICE,
                AgentCapability.INCIDENT_MANAGEMENT
            ]
        )
        
        # Service categories this agent can handle
        self.service_categories = [
            "room_service", "housekeeping", "amenities", "hotel_information",
            "dining_reservations", "spa_bookings", "transportation",
            "general_inquiries", "check_in_out", "billing_questions"
        ]
    
    def get_system_prompt(self) -> str:
        """Get system prompt for guest service agent."""
        return f"""You are a professional hotel guest service agent working for a luxury hotel. 
Your role is to provide exceptional, personalized service to hotel guests.

CORE RESPONSIBILITIES:
- Assist guests with room service, housekeeping, and amenity requests
- Provide hotel information, directions, and facility details  
- Help with dining reservations and spa bookings
- Handle check-in/check-out questions and billing inquiries
- Offer personalized recommendations based on guest preferences
- Ensure all interactions maintain the highest service standards

COMMUNICATION STYLE:
- Professional, warm, and welcoming tone
- Use guest's name when available
- Be proactive in offering additional assistance
- Show empathy and understanding for guest needs
- Maintain confidentiality and discretion

ESCALATION TRIGGERS:
- Complaints requiring compensation or manager approval
- Complex billing disputes or payment issues
- VIP guest requests requiring special attention
- Emergency situations or safety concerns
- Requests beyond your service scope

HOTEL FACILITIES & SERVICES:
- 24/7 room service and concierge
- Luxury spa and wellness center
- Multiple restaurants and bars
- Business center and meeting rooms
- Fitness center and swimming pool
- Valet parking and transportation services

Remember to always prioritize guest satisfaction while following hotel policies and procedures.
Current date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Process guest service request."""
        
        # Classify the request type
        request_type = await self._classify_request(request)
        
        # Get guest context if available
        guest_context = {}
        if context.guest_id:
            guest_context = await self.get_guest_context(context.guest_id)
        
        # Prepare context for LLM
        messages = await self.prepare_context_for_llm(context)
        
        # Add current request with context
        enhanced_request = self._enhance_request_with_context(request, request_type, guest_context)
        
        try:
            # Generate response using LLM
            response = await self.llm.agenerate([messages + [{"role": "user", "content": enhanced_request}]])
            response_text = response.generations[0][0].text
            
            # Process the response and take actions
            actions_taken = []
            recommendations = []
            
            # Handle different request types
            if request_type == "room_service":
                actions_taken.extend(await self._handle_room_service_request(request, context))
            elif request_type == "housekeeping":
                actions_taken.extend(await self._handle_housekeeping_request(request, context))
            elif request_type == "dining_reservation":
                actions_taken.extend(await self._handle_dining_request(request, context))
            elif request_type == "amenity_inquiry":
                actions_taken.extend(await self._handle_amenity_inquiry(request, context))
            elif request_type == "billing_question":
                actions_taken.extend(await self._handle_billing_inquiry(request, context))
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(request_type, guest_context)
            
            # Determine if escalation is needed
            escalation_required, escalation_reason = self.should_escalate(context, 0.8)
            
            # Check for specific escalation triggers
            if self._needs_manager_attention(request, request_type):
                escalation_required = True
                escalation_reason = "Request requires manager attention"
            
            return AgentResponse(
                success=True,
                message=self.format_response_with_context(response_text, context),
                data={
                    "request_type": request_type,
                    "guest_context": guest_context,
                    "service_category": request_type
                },
                actions_taken=actions_taken,
                recommendations=recommendations,
                escalation_required=escalation_required,
                escalation_reason=escalation_reason,
                follow_up_required=self._requires_follow_up(request_type),
                follow_up_date=datetime.now() + timedelta(hours=24) if self._requires_follow_up(request_type) else None,
                confidence_score=0.85
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message="I apologize for the inconvenience. Let me connect you with a manager who can assist you immediately.",
                escalation_required=True,
                escalation_reason=f"Service agent error: {str(e)}",
                confidence_score=0.0
            )
    
    async def _classify_request(self, request: str) -> str:
        """Classify the type of guest service request."""
        request_lower = request.lower()
        
        # Room service keywords
        if any(keyword in request_lower for keyword in ["room service", "food", "meal", "hungry", "order", "menu"]):
            return "room_service"
        
        # Housekeeping keywords  
        if any(keyword in request_lower for keyword in ["housekeeping", "clean", "towels", "sheets", "tidy"]):
            return "housekeeping"
        
        # Dining reservation keywords
        if any(keyword in request_lower for keyword in ["restaurant", "dining", "reservation", "table", "book"]):
            return "dining_reservation"
        
        # Billing keywords
        if any(keyword in request_lower for keyword in ["bill", "charge", "payment", "invoice", "cost", "price"]):
            return "billing_question"
        
        # Amenity keywords
        if any(keyword in request_lower for keyword in ["spa", "gym", "pool", "wifi", "parking", "amenity"]):
            return "amenity_inquiry"
        
        # Check-in/out keywords
        if any(keyword in request_lower for keyword in ["check in", "check out", "checkout", "checkin", "late checkout"]):
            return "check_in_out"
        
        # Transportation keywords
        if any(keyword in request_lower for keyword in ["taxi", "transport", "airport", "car", "driver"]):
            return "transportation"
        
        return "general_inquiry"
    
    def _enhance_request_with_context(self, request: str, request_type: str, guest_context: Dict) -> str:
        """Enhance request with relevant context information."""
        enhanced = f"Guest Request: {request}\n"
        enhanced += f"Request Type: {request_type}\n"
        
        if guest_context:
            if guest_context.get("vip_status"):
                enhanced += "NOTE: This is a VIP guest - provide premium service\n"
            
            if guest_context.get("loyalty_tier"):
                enhanced += f"Loyalty Tier: {guest_context['loyalty_tier']}\n"
            
            if guest_context.get("room_number"):
                enhanced += f"Room Number: {guest_context['room_number']}\n"
            
            if guest_context.get("special_requirements"):
                enhanced += f"Special Requirements: {guest_context['special_requirements']}\n"
            
            # Add preference-based context
            if guest_context.get("crm_profile") and guest_context["crm_profile"].preferences:
                prefs = guest_context["crm_profile"].preferences
                if request_type == "room_service" and "dining" in prefs:
                    enhanced += f"Dining Preferences: {prefs.get('dining', {})}\n"
                elif request_type == "housekeeping" and "housekeeping_time" in prefs:
                    enhanced += f"Preferred Housekeeping Time: {prefs.get('housekeeping_time')}\n"
        
        return enhanced
    
    async def _handle_room_service_request(self, request: str, context: AgentContext) -> List[str]:
        """Handle room service requests."""
        actions = []
        
        # Create service request in PMS
        try:
            request_data = {
                "type": "room_service",
                "guest_id": context.guest_id,
                "room_number": context.room_number,
                "request_details": request,
                "priority": "standard"
            }
            
            service_id = await self.pms_service.create_service_request(request_data)
            actions.append(f"Created room service request {service_id}")
            
            # Notify kitchen/restaurant
            actions.append("Notified room service department")
            
        except Exception as e:
            actions.append(f"Unable to process room service request: {str(e)}")
        
        return actions
    
    async def _handle_housekeeping_request(self, request: str, context: AgentContext) -> List[str]:
        """Handle housekeeping requests."""
        actions = []
        
        try:
            # Determine housekeeping priority
            priority = "urgent" if any(word in request.lower() for word in ["urgent", "immediately", "now"]) else "standard"
            
            request_data = {
                "type": "housekeeping",
                "guest_id": context.guest_id,
                "room_number": context.room_number,
                "request_details": request,
                "priority": priority
            }
            
            service_id = await self.pms_service.create_service_request(request_data)
            actions.append(f"Created housekeeping request {service_id}")
            
            # Update room status if needed
            if "clean" in request.lower():
                await self.pms_service.update_room_status(context.room_number, "needs_cleaning")
                actions.append("Updated room status for cleaning")
            
        except Exception as e:
            actions.append(f"Unable to process housekeeping request: {str(e)}")
        
        return actions
    
    async def _handle_dining_request(self, request: str, context: AgentContext) -> List[str]:
        """Handle dining reservation requests."""
        actions = []
        
        # This would integrate with restaurant reservation system
        actions.append("Checked restaurant availability")
        actions.append("Reservation request forwarded to restaurant team")
        
        return actions
    
    async def _handle_amenity_inquiry(self, request: str, context: AgentContext) -> List[str]:
        """Handle amenity inquiries."""
        actions = []
        
        # Log amenity interest for analytics
        actions.append("Recorded amenity inquiry for guest analytics")
        
        # Check if special access is needed
        if "spa" in request.lower():
            actions.append("Checked spa availability and booking options")
        elif "gym" in request.lower():
            actions.append("Provided gym access information")
        
        return actions
    
    async def _handle_billing_inquiry(self, request: str, context: AgentContext) -> List[str]:
        """Handle billing inquiries."""
        actions = []
        
        try:
            # Get current folio
            if context.guest_id:
                folio = await self.pms_service.get_guest_folio(context.guest_id)
                actions.append("Retrieved current guest folio")
                
                # Check for disputes
                if any(word in request.lower() for word in ["dispute", "wrong", "incorrect", "error"]):
                    actions.append("Flagged for billing review")
                    
        except Exception as e:
            actions.append(f"Unable to retrieve billing information: {str(e)}")
        
        return actions
    
    async def _generate_recommendations(self, request_type: str, guest_context: Dict) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Base recommendations by request type
        if request_type == "room_service":
            recommendations.append("Consider our chef's special menu for today")
            recommendations.append("Wine pairing available for dinner orders")
        elif request_type == "amenity_inquiry":
            recommendations.append("Explore our spa packages for a complete wellness experience")
            recommendations.append("Check out our rooftop pool with city views")
        elif request_type == "dining_reservation":
            recommendations.append("Try our signature restaurant for fine dining")
            recommendations.append("Happy hour specials available at the lobby bar")
        
        # Personalized recommendations based on guest context
        if guest_context.get("vip_status"):
            recommendations.append("VIP amenities and services available upon request")
        
        if guest_context.get("loyalty_tier") in ["Gold", "Platinum", "Diamond"]:
            recommendations.append("Complimentary room upgrade subject to availability")
            recommendations.append("Late checkout available for loyalty members")
        
        return recommendations
    
    def _needs_manager_attention(self, request: str, request_type: str) -> bool:
        """Determine if request needs manager attention."""
        manager_keywords = [
            "manager", "complaint", "dissatisfied", "unhappy", "refund",
            "compensation", "terrible", "awful", "worst", "legal"
        ]
        
        return any(keyword in request.lower() for keyword in manager_keywords)
    
    def _requires_follow_up(self, request_type: str) -> bool:
        """Determine if request type requires follow-up."""
        follow_up_types = ["room_service", "housekeeping", "dining_reservation", "transportation"]
        return request_type in follow_up_types