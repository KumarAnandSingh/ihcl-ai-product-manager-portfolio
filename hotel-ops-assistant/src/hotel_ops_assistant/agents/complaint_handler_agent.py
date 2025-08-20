"""
Complaint Handler Agent.
Specialized agent for handling guest complaints, service issues, and resolution processes.
Focuses on de-escalation, compensation assessment, and service recovery.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResponse


class ComplaintHandlerAgent(BaseAgent):
    """Agent specialized in handling guest complaints and service recovery."""
    
    def __init__(self):
        super().__init__(
            agent_id="complaint_handler_agent",
            capabilities=[
                AgentCapability.COMPLAINT_HANDLING,
                AgentCapability.INCIDENT_MANAGEMENT
            ]
        )
        
        # Complaint categories and severity levels
        self.complaint_categories = {
            "room_issues": ["cleanliness", "maintenance", "amenities", "noise"],
            "service_issues": ["staff_behavior", "response_time", "quality"],
            "billing_issues": ["incorrect_charges", "unexpected_fees", "payment_problems"],
            "facility_issues": ["restaurant", "spa", "gym", "pool", "wifi"],
            "safety_security": ["safety_concerns", "security_issues", "access_problems"]
        }
        
        self.severity_indicators = {
            "low": ["minor", "small", "slight", "little"],
            "medium": ["noticeable", "concerning", "problematic"],
            "high": ["serious", "major", "significant", "terrible", "awful"],
            "critical": ["dangerous", "unsafe", "emergency", "urgent", "immediately"]
        }
        
        # Compensation guidelines
        self.compensation_matrix = {
            "low": {"max_amount": 1000, "types": ["amenity", "service_credit"]},
            "medium": {"max_amount": 5000, "types": ["room_credit", "dining_credit", "spa_credit"]},
            "high": {"max_amount": 15000, "types": ["room_upgrade", "complimentary_night", "partial_refund"]},
            "critical": {"max_amount": 50000, "types": ["full_refund", "complimentary_stay", "immediate_relocation"]}
        }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for complaint handler agent."""
        return f"""You are a senior guest relations specialist at a luxury hotel, specializing in complaint resolution and service recovery. Your expertise lies in turning negative experiences into positive outcomes.

CORE RESPONSIBILITIES:
- Listen empathetically to guest complaints and concerns
- Assess complaint severity and categorize issues appropriately
- Provide immediate resolution or escalation as needed
- Offer appropriate compensation within guidelines
- Follow up to ensure guest satisfaction
- Prevent negative reviews and maintain hotel reputation

COMPLAINT HANDLING APPROACH:
1. LISTEN: Allow guest to fully express their concerns without interruption
2. EMPATHIZE: Acknowledge their feelings and apologize sincerely
3. ASSESS: Determine severity, impact, and appropriate resolution
4. ACT: Take immediate corrective action or escalate as needed
5. FOLLOW UP: Ensure resolution meets guest expectations

COMMUNICATION PRINCIPLES:
- Use empathetic language and acknowledge guest frustration
- Take ownership and avoid making excuses
- Be solution-focused and offer concrete actions
- Maintain professional composure even with difficult guests
- Provide clear timelines for resolution
- Ensure guest feels heard and valued

ESCALATION TRIGGERS:
- Safety or security concerns
- Potential legal implications
- Requests exceeding compensation authority
- VIP guest complaints
- Repeat complaints from same guest
- Social media threats or public complaints

COMPENSATION AUTHORITY:
- Up to ₹15,000 in direct compensation
- Room upgrades and amenity credits
- Complimentary services and experiences
- Manager approval required for higher amounts

Remember: Every complaint is an opportunity to demonstrate exceptional service and build guest loyalty.
Current date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Process guest complaint and provide resolution."""
        
        # Analyze the complaint
        complaint_analysis = await self._analyze_complaint(request)
        
        # Get guest context for personalized handling
        guest_context = {}
        if context.guest_id:
            guest_context = await self.get_guest_context(context.guest_id)
        
        # Check complaint history
        complaint_history = await self._get_complaint_history(context.guest_id)
        
        # Prepare context for LLM
        messages = await self.prepare_context_for_llm(context)
        
        # Enhanced request with analysis
        enhanced_request = self._build_complaint_context(
            request, complaint_analysis, guest_context, complaint_history
        )
        
        try:
            # Generate empathetic response
            response = await self.llm.agenerate([messages + [{"role": "user", "content": enhanced_request}]])
            response_text = response.generations[0][0].text
            
            # Take resolution actions
            actions_taken = await self._execute_resolution_actions(
                complaint_analysis, context, guest_context
            )
            
            # Determine compensation if needed
            compensation = await self._assess_compensation(
                complaint_analysis, guest_context, complaint_history
            )
            
            # Create incident record
            incident_id = await self.create_incident({
                "type": "guest_complaint",
                "category": complaint_analysis["category"],
                "severity": complaint_analysis["severity"],
                "description": request,
                "compensation_offered": compensation,
                "guest_id": context.guest_id,
                "room_number": context.room_number
            }, context)
            
            # Determine escalation needs
            escalation_required = self._should_escalate_complaint(
                complaint_analysis, guest_context, compensation
            )
            
            escalation_reason = None
            if escalation_required:
                escalation_reason = self._get_escalation_reason(complaint_analysis, compensation)
            
            # Generate follow-up recommendations
            recommendations = self._generate_service_recovery_recommendations(
                complaint_analysis, guest_context
            )
            
            return AgentResponse(
                success=True,
                message=self.format_response_with_context(response_text, context),
                data={
                    "complaint_analysis": complaint_analysis,
                    "incident_id": incident_id,
                    "compensation_offered": compensation,
                    "resolution_timeline": self._get_resolution_timeline(complaint_analysis["severity"])
                },
                actions_taken=actions_taken,
                recommendations=recommendations,
                escalation_required=escalation_required,
                escalation_reason=escalation_reason,
                follow_up_required=True,
                follow_up_date=datetime.now() + timedelta(hours=24),
                confidence_score=0.9
            )
            
        except Exception as e:
            # For complaints, always escalate on errors
            return AgentResponse(
                success=False,
                message="I sincerely apologize for this issue. Let me immediately connect you with our Guest Relations Manager who will personally handle your concern.",
                escalation_required=True,
                escalation_reason=f"Complaint handling error: {str(e)}",
                confidence_score=0.0
            )
    
    async def _analyze_complaint(self, complaint_text: str) -> Dict[str, any]:
        """Analyze complaint to determine category, severity, and key issues."""
        
        complaint_lower = complaint_text.lower()
        
        # Determine category
        category = "general"
        for cat, keywords in self.complaint_categories.items():
            if any(keyword in complaint_lower for keyword in keywords):
                category = cat
                break
        
        # Determine severity
        severity = "medium"  # default
        for sev, indicators in self.severity_indicators.items():
            if any(indicator in complaint_lower for indicator in indicators):
                severity = sev
                break
        
        # Extract key issues
        key_issues = []
        if "dirty" in complaint_lower or "clean" in complaint_lower:
            key_issues.append("cleanliness")
        if "staff" in complaint_lower or "rude" in complaint_lower:
            key_issues.append("staff_behavior")
        if "wait" in complaint_lower or "slow" in complaint_lower:
            key_issues.append("response_time")
        if "charge" in complaint_lower or "bill" in complaint_lower:
            key_issues.append("billing")
        if "noise" in complaint_lower or "loud" in complaint_lower:
            key_issues.append("noise")
        
        # Detect emotional indicators
        emotional_indicators = []
        negative_emotions = ["angry", "frustrated", "disappointed", "upset", "furious"]
        for emotion in negative_emotions:
            if emotion in complaint_lower:
                emotional_indicators.append(emotion)
        
        # Check for specific demands
        demands = []
        if "refund" in complaint_lower:
            demands.append("refund")
        if "compensation" in complaint_lower:
            demands.append("compensation")
        if "manager" in complaint_lower:
            demands.append("manager")
        if "review" in complaint_lower or "social media" in complaint_lower:
            demands.append("public_complaint_threat")
        
        return {
            "category": category,
            "severity": severity,
            "key_issues": key_issues,
            "emotional_indicators": emotional_indicators,
            "specific_demands": demands,
            "urgency_level": self._assess_urgency(severity, demands),
            "resolution_complexity": self._assess_complexity(category, key_issues)
        }
    
    def _assess_urgency(self, severity: str, demands: List[str]) -> str:
        """Assess urgency level of complaint."""
        if severity == "critical" or "public_complaint_threat" in demands:
            return "immediate"
        elif severity == "high" or "manager" in demands:
            return "urgent"
        elif severity == "medium":
            return "priority"
        else:
            return "standard"
    
    def _assess_complexity(self, category: str, issues: List[str]) -> str:
        """Assess complexity of resolution required."""
        if category == "safety_security" or len(issues) > 3:
            return "complex"
        elif category in ["billing_issues", "service_issues"] or len(issues) > 1:
            return "moderate"
        else:
            return "simple"
    
    async def _get_complaint_history(self, guest_id: str) -> Dict[str, any]:
        """Get guest's complaint history."""
        if not guest_id:
            return {"total_complaints": 0, "recent_complaints": [], "repeat_guest": False}
        
        try:
            crm_profile = await self.crm_service.get_guest_profile(guest_id)
            if crm_profile:
                return {
                    "total_complaints": crm_profile.complaints_count,
                    "recent_complaints": [],  # Would query incident system
                    "repeat_guest": crm_profile.total_stays > 1,
                    "loyalty_tier": crm_profile.loyalty_tier,
                    "total_stays": crm_profile.total_stays
                }
        except:
            pass
        
        return {"total_complaints": 0, "recent_complaints": [], "repeat_guest": False}
    
    def _build_complaint_context(self, complaint: str, analysis: Dict, guest_context: Dict, history: Dict) -> str:
        """Build comprehensive context for complaint handling."""
        
        context = f"""GUEST COMPLAINT ANALYSIS:
Complaint: {complaint}

Analysis:
- Category: {analysis['category']}
- Severity: {analysis['severity']}
- Urgency: {analysis['urgency_level']}
- Key Issues: {', '.join(analysis['key_issues'])}
- Emotional State: {', '.join(analysis['emotional_indicators'])}
- Specific Demands: {', '.join(analysis['specific_demands'])}

Guest Profile:
"""
        
        if guest_context.get("vip_status"):
            context += "- VIP Guest (Requires Premium Service Recovery)\n"
        
        if guest_context.get("loyalty_tier"):
            context += f"- Loyalty Tier: {guest_context['loyalty_tier']}\n"
        
        if history.get("repeat_guest"):
            context += f"- Repeat Guest ({history.get('total_stays', 0)} stays)\n"
        
        if history.get("total_complaints", 0) > 0:
            context += f"- Previous Complaints: {history['total_complaints']}\n"
        
        context += f"""
RESOLUTION APPROACH REQUIRED:
1. Provide sincere, empathetic apology
2. Take immediate ownership of the issue
3. Offer specific resolution steps
4. Provide appropriate compensation if warranted
5. Ensure follow-up for satisfaction confirmation

Please craft a response that addresses all concerns professionally and offers a concrete resolution path.
"""
        
        return context
    
    async def _execute_resolution_actions(self, analysis: Dict, context: AgentContext, guest_context: Dict) -> List[str]:
        """Execute immediate resolution actions."""
        actions = []
        
        category = analysis["category"]
        severity = analysis["severity"]
        
        try:
            # Room-related issues
            if category == "room_issues":
                if context.room_number:
                    # Create maintenance request if needed
                    if "maintenance" in analysis["key_issues"]:
                        work_order_data = {
                            "room_number": context.room_number,
                            "issue_type": "general",
                            "priority": "urgent" if severity in ["high", "critical"] else "medium",
                            "description": f"Guest complaint: {analysis['key_issues']}",
                            "reported_by": "guest_relations"
                        }
                        wo_id = await self.maintenance_service.create_work_order(work_order_data)
                        actions.append(f"Created urgent maintenance request {wo_id}")
                    
                    # Request immediate housekeeping if cleanliness issue
                    if "cleanliness" in analysis["key_issues"]:
                        hk_request = {
                            "type": "immediate_cleaning",
                            "room_number": context.room_number,
                            "priority": "urgent",
                            "details": "Guest complaint - immediate attention required"
                        }
                        hk_id = await self.pms_service.create_service_request(hk_request)
                        actions.append(f"Dispatched immediate housekeeping team {hk_id}")
            
            # Service-related issues
            elif category == "service_issues":
                if "staff_behavior" in analysis["key_issues"]:
                    actions.append("Notified department manager for staff coaching")
                
                if "response_time" in analysis["key_issues"]:
                    actions.append("Escalated to operations for process review")
            
            # Billing issues
            elif category == "billing_issues":
                if context.guest_id:
                    folio = await self.pms_service.get_guest_folio(context.guest_id)
                    actions.append("Retrieved guest folio for review")
                    actions.append("Flagged account for billing department review")
            
            # Facility issues
            elif category == "facility_issues":
                actions.append("Notified facility management for immediate inspection")
                if severity in ["high", "critical"]:
                    actions.append("Created high-priority facility maintenance request")
            
            # Safety/security issues
            elif category == "safety_security":
                actions.append("Immediately notified security team")
                if severity == "critical":
                    actions.append("Initiated emergency response protocol")
            
            # VIP guest special handling
            if guest_context.get("vip_status"):
                actions.append("Notified Guest Relations Manager (VIP Protocol)")
                actions.append("Assigned dedicated concierge for resolution")
            
        except Exception as e:
            actions.append(f"Error executing resolution actions: {str(e)}")
        
        return actions
    
    async def _assess_compensation(self, analysis: Dict, guest_context: Dict, history: Dict) -> Dict[str, any]:
        """Assess and determine appropriate compensation."""
        
        severity = analysis["severity"]
        category = analysis["category"]
        
        # Get compensation guidelines for severity level
        comp_guide = self.compensation_matrix.get(severity, self.compensation_matrix["medium"])
        
        compensation = {
            "recommended": True,
            "type": "service_credit",
            "amount": 0,
            "currency": "INR",
            "description": "",
            "requires_approval": False
        }
        
        # Calculate base compensation amount
        if severity == "low":
            base_amount = 1000
            compensation["type"] = "amenity_credit"
            compensation["description"] = "Complimentary amenity access"
        elif severity == "medium":
            base_amount = 3000
            compensation["type"] = "dining_credit"
            compensation["description"] = "Dining credit for inconvenience"
        elif severity == "high":
            base_amount = 8000
            compensation["type"] = "room_credit"
            compensation["description"] = "Room charge adjustment"
        else:  # critical
            base_amount = 20000
            compensation["type"] = "significant_compensation"
            compensation["description"] = "Substantial compensation for serious issue"
            compensation["requires_approval"] = True
        
        # Adjust for guest status
        if guest_context.get("vip_status"):
            base_amount *= 2
            compensation["description"] += " (VIP Enhancement)"
        elif guest_context.get("loyalty_tier") in ["Gold", "Platinum", "Diamond"]:
            base_amount *= 1.5
            compensation["description"] += " (Loyalty Member)"
        
        # Adjust for repeat complaints
        if history.get("total_complaints", 0) > 2:
            base_amount *= 1.3
            compensation["description"] += " (Service Recovery)"
        
        compensation["amount"] = min(base_amount, comp_guide["max_amount"])
        
        # Check if requires manager approval
        if compensation["amount"] > 10000 or severity == "critical":
            compensation["requires_approval"] = True
        
        return compensation
    
    def _should_escalate_complaint(self, analysis: Dict, guest_context: Dict, compensation: Dict) -> bool:
        """Determine if complaint should be escalated."""
        
        # Always escalate critical issues
        if analysis["severity"] == "critical":
            return True
        
        # Escalate safety/security issues
        if analysis["category"] == "safety_security":
            return True
        
        # Escalate VIP complaints
        if guest_context.get("vip_status"):
            return True
        
        # Escalate if compensation requires approval
        if compensation.get("requires_approval"):
            return True
        
        # Escalate public complaint threats
        if "public_complaint_threat" in analysis.get("specific_demands", []):
            return True
        
        # Escalate high severity with multiple issues
        if analysis["severity"] == "high" and len(analysis["key_issues"]) > 2:
            return True
        
        return False
    
    def _get_escalation_reason(self, analysis: Dict, compensation: Dict) -> str:
        """Get specific reason for escalation."""
        reasons = []
        
        if analysis["severity"] == "critical":
            reasons.append("Critical severity complaint")
        
        if analysis["category"] == "safety_security":
            reasons.append("Safety/security concern")
        
        if compensation.get("requires_approval"):
            reasons.append("Compensation exceeds agent authority")
        
        if "public_complaint_threat" in analysis.get("specific_demands", []):
            reasons.append("Threat of public complaint/review")
        
        return "; ".join(reasons) if reasons else "Complex complaint requiring management attention"
    
    def _generate_service_recovery_recommendations(self, analysis: Dict, guest_context: Dict) -> List[str]:
        """Generate service recovery recommendations."""
        recommendations = []
        
        # Category-specific recommendations
        if analysis["category"] == "room_issues":
            recommendations.append("Consider room upgrade for remainder of stay")
            recommendations.append("Provide complimentary minibar or room service")
        elif analysis["category"] == "service_issues":
            recommendations.append("Assign dedicated concierge for remainder of stay")
            recommendations.append("Schedule staff retraining session")
        elif analysis["category"] == "facility_issues":
            recommendations.append("Offer alternative facility access or external arrangements")
            recommendations.append("Provide facility improvement timeline to guest")
        
        # Guest-specific recommendations
        if guest_context.get("vip_status"):
            recommendations.append("Implement VIP service recovery protocol")
            recommendations.append("Consider complimentary future stay invitation")
        
        # General service recovery
        recommendations.append("Schedule follow-up call within 24 hours")
        recommendations.append("Send personalized apology letter from management")
        recommendations.append("Update guest profile with preferences to prevent future issues")
        
        return recommendations
    
    def _get_resolution_timeline(self, severity: str) -> Dict[str, str]:
        """Get expected resolution timeline based on severity."""
        timelines = {
            "low": {"immediate": "2 hours", "complete": "24 hours"},
            "medium": {"immediate": "1 hour", "complete": "12 hours"},
            "high": {"immediate": "30 minutes", "complete": "4 hours"},
            "critical": {"immediate": "15 minutes", "complete": "2 hours"}
        }
        
        return timelines.get(severity, timelines["medium"])