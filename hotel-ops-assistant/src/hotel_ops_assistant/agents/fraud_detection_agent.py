"""
Fraud Detection Agent.
Specialized agent for detecting and responding to fraudulent activities,
suspicious transactions, and security threats in hotel operations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import re

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResponse


class FraudDetectionAgent(BaseAgent):
    """Agent specialized in fraud detection and security threat assessment."""
    
    def __init__(self):
        super().__init__(
            agent_id="fraud_detection_agent",
            capabilities=[
                AgentCapability.FRAUD_DETECTION,
                AgentCapability.SECURITY_MONITORING,
                AgentCapability.COMPLIANCE_MONITORING
            ]
        )
        
        # Fraud detection patterns and thresholds
        self.fraud_patterns = {
            "payment_fraud": {
                "multiple_cards": {"threshold": 3, "timeframe_hours": 24},
                "high_amount": {"threshold": 50000, "single_transaction": True},
                "rapid_transactions": {"threshold": 5, "timeframe_minutes": 10},
                "foreign_card": {"risk_countries": ["XX", "YY"], "verification_required": True}
            },
            "identity_fraud": {
                "multiple_identities": {"threshold": 2, "same_contact": True},
                "document_inconsistency": {"validation_required": True},
                "age_mismatch": {"tolerance_years": 2}
            },
            "booking_fraud": {
                "no_show_pattern": {"threshold": 3, "timeframe_days": 30},
                "last_minute_cancellation": {"threshold": 5, "timeframe_days": 7},
                "bulk_bookings": {"threshold": 10, "same_user": True}
            },
            "access_fraud": {
                "unauthorized_access": {"failed_attempts": 5, "timeframe_minutes": 15},
                "location_anomaly": {"distance_km": 1000, "timeframe_hours": 2},
                "device_mismatch": {"new_device_suspicious": True}
            }
        }
        
        # Risk scoring weights
        self.risk_weights = {
            "transaction_amount": 0.3,
            "frequency_pattern": 0.25,
            "identity_verification": 0.2,
            "location_consistency": 0.15,
            "historical_behavior": 0.1
        }
        
        # Security response protocols
        self.response_protocols = {
            "low_risk": {"alert_level": 1, "auto_block": False, "investigation_required": False},
            "medium_risk": {"alert_level": 2, "auto_block": False, "investigation_required": True},
            "high_risk": {"alert_level": 3, "auto_block": True, "investigation_required": True},
            "critical_risk": {"alert_level": 4, "auto_block": True, "immediate_response": True}
        }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for fraud detection agent."""
        return f"""You are a senior fraud detection specialist and security analyst for a luxury hotel. 
Your expertise is in identifying, analyzing, and preventing fraudulent activities while maintaining excellent guest experience for legitimate customers.

CORE RESPONSIBILITIES:
- Analyze transactions, bookings, and access patterns for fraud indicators
- Assess identity verification and document authenticity  
- Monitor for suspicious payment activities and financial fraud
- Detect unauthorized access attempts and security breaches
- Coordinate with security teams and law enforcement when needed
- Balance fraud prevention with guest experience

FRAUD DETECTION FOCUS AREAS:
1. Payment Fraud: Multiple cards, high amounts, rapid transactions, foreign cards
2. Identity Fraud: False documents, multiple identities, age mismatches
3. Booking Fraud: No-show patterns, cancellation abuse, bulk booking fraud
4. Access Fraud: Unauthorized access, location anomalies, device inconsistencies
5. Account Takeover: Compromised accounts, unusual behavior patterns

ANALYTICAL APPROACH:
- Use data patterns and statistical analysis for risk assessment
- Consider transaction velocity, amounts, and timing
- Analyze guest behavior against historical norms
- Cross-reference with known fraud indicators and blacklists
- Validate identity documents and contact information

RESPONSE PROTOCOLS:
- Low Risk: Monitor and log for pattern analysis
- Medium Risk: Additional verification required before proceeding
- High Risk: Temporary hold, manual review required
- Critical Risk: Immediate block, security team notification

COMMUNICATION STYLE:
- Professional and discrete when discussing security matters
- Clear and factual in risk assessments
- Urgent when immediate action required
- Empathetic when legitimate guests are affected by security measures

Remember: Protect the hotel from fraud while ensuring legitimate guests receive seamless service.
Current date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        """Process fraud detection request and assess risk."""
        
        # Parse the fraud detection request
        fraud_context = await self._parse_fraud_context(request, context)
        
        # Analyze for fraud patterns
        fraud_analysis = await self._analyze_fraud_patterns(fraud_context, context)
        
        # Calculate risk score
        risk_assessment = await self._calculate_risk_score(fraud_analysis, context)
        
        # Get guest/transaction history for context
        historical_data = await self._get_historical_context(context)
        
        # Prepare enhanced context for LLM
        messages = await self.prepare_context_for_llm(context)
        
        enhanced_request = self._build_fraud_analysis_context(
            request, fraud_analysis, risk_assessment, historical_data
        )
        
        try:
            # Generate fraud assessment response
            response = await self.llm.agenerate([messages + [{"role": "user", "content": enhanced_request}]])
            response_text = response.generations[0][0].text
            
            # Execute security actions based on risk level
            security_actions = await self._execute_security_actions(
                risk_assessment, fraud_analysis, context
            )
            
            # Generate investigation recommendations
            investigation_steps = self._generate_investigation_recommendations(
                fraud_analysis, risk_assessment
            )
            
            # Create fraud incident if needed
            incident_id = None
            if risk_assessment["risk_level"] in ["high_risk", "critical_risk"]:
                incident_id = await self.create_incident({
                    "type": "fraud_alert",
                    "category": "security",
                    "severity": "high" if risk_assessment["risk_level"] == "high_risk" else "critical",
                    "description": request,
                    "fraud_indicators": fraud_analysis["indicators"],
                    "risk_score": risk_assessment["score"],
                    "guest_id": context.guest_id
                }, context)
            
            # Determine escalation requirements
            escalation_required = risk_assessment["risk_level"] in ["high_risk", "critical_risk"]
            escalation_reason = f"Fraud risk level: {risk_assessment['risk_level']}" if escalation_required else None
            
            return AgentResponse(
                success=True,
                message=self.format_response_with_context(response_text, context),
                data={
                    "fraud_analysis": fraud_analysis,
                    "risk_assessment": risk_assessment,
                    "incident_id": incident_id,
                    "security_actions_taken": security_actions,
                    "recommended_actions": investigation_steps
                },
                actions_taken=security_actions,
                recommendations=investigation_steps,
                escalation_required=escalation_required,
                escalation_reason=escalation_reason,
                follow_up_required=risk_assessment["risk_level"] != "low_risk",
                follow_up_date=datetime.now() + timedelta(hours=4) if escalation_required else None,
                confidence_score=risk_assessment["confidence"]
            )
            
        except Exception as e:
            # For fraud detection, always escalate errors as potential security issues
            return AgentResponse(
                success=False,
                message="Security analysis system temporarily unavailable. Implementing additional verification protocols.",
                escalation_required=True,
                escalation_reason=f"Fraud detection system error: {str(e)}",
                confidence_score=0.0
            )
    
    async def _parse_fraud_context(self, request: str, context: AgentContext) -> Dict[str, any]:
        """Parse request to extract fraud-relevant information."""
        
        request_lower = request.lower()
        
        # Determine fraud type being reported/analyzed
        fraud_type = "general"
        if any(word in request_lower for word in ["payment", "card", "transaction", "charge"]):
            fraud_type = "payment_fraud"
        elif any(word in request_lower for word in ["identity", "document", "fake", "false"]):
            fraud_type = "identity_fraud"
        elif any(word in request_lower for word in ["booking", "reservation", "no show"]):
            fraud_type = "booking_fraud"
        elif any(word in request_lower for word in ["access", "unauthorized", "login", "account"]):
            fraud_type = "access_fraud"
        
        # Extract transaction details if mentioned
        transaction_data = {}
        
        # Look for amounts
        amount_pattern = r'[₹$€]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, request)
        if amounts:
            transaction_data["amounts"] = [float(amount.replace(',', '')) for amount in amounts]
        
        # Look for card numbers (last 4 digits)
        card_pattern = r'\d{4}\s*$|ending\s+in\s+(\d{4})|last\s+four\s+(\d{4})'
        cards = re.findall(card_pattern, request)
        if cards:
            transaction_data["card_references"] = [card for card in cards if card]
        
        # Look for time references
        time_indicators = []
        if any(word in request_lower for word in ["multiple", "several", "many"]):
            time_indicators.append("multiple_occurrences")
        if any(word in request_lower for word in ["rapid", "quick", "fast", "immediately"]):
            time_indicators.append("rapid_frequency")
        if any(word in request_lower for word in ["foreign", "international", "overseas"]):
            time_indicators.append("foreign_origin")
        
        return {
            "fraud_type": fraud_type,
            "transaction_data": transaction_data,
            "time_indicators": time_indicators,
            "urgency_level": self._assess_urgency_from_request(request_lower),
            "specific_concerns": self._extract_specific_concerns(request_lower)
        }
    
    def _assess_urgency_from_request(self, request_lower: str) -> str:
        """Assess urgency level from request content."""
        if any(word in request_lower for word in ["emergency", "urgent", "immediate", "happening now"]):
            return "critical"
        elif any(word in request_lower for word in ["suspicious", "concerning", "unusual"]):
            return "high"
        elif any(word in request_lower for word in ["check", "verify", "review"]):
            return "medium"
        else:
            return "low"
    
    def _extract_specific_concerns(self, request_lower: str) -> List[str]:
        """Extract specific fraud concerns from request."""
        concerns = []
        
        concern_mapping = {
            "stolen card": ["stolen", "card"],
            "identity theft": ["identity", "theft", "stolen identity"],
            "account takeover": ["account", "takeover", "compromised"],
            "fake documents": ["fake", "forged", "document"],
            "money laundering": ["money", "laundering", "suspicious amount"],
            "chargeback fraud": ["chargeback", "dispute", "unauthorized"],
            "friendly fraud": ["friendly fraud", "legitimate dispute"],
            "unauthorized access": ["unauthorized", "access", "breach"]
        }
        
        for concern, keywords in concern_mapping.items():
            if all(keyword in request_lower for keyword in keywords):
                concerns.append(concern)
        
        return concerns
    
    async def _analyze_fraud_patterns(self, fraud_context: Dict, context: AgentContext) -> Dict[str, any]:
        """Analyze patterns for fraud indicators."""
        
        indicators = []
        pattern_matches = {}
        
        fraud_type = fraud_context["fraud_type"]
        
        try:
            if fraud_type == "payment_fraud":
                # Analyze payment patterns
                if context.guest_id:
                    recent_transactions = await self.pos_service.get_guest_transactions(context.guest_id, days=7)
                    
                    # Check for multiple card usage
                    unique_cards = len(set(txn.payment_method for txn in recent_transactions if "card" in txn.payment_method))
                    if unique_cards >= self.fraud_patterns["payment_fraud"]["multiple_cards"]["threshold"]:
                        indicators.append("multiple_cards_used")
                        pattern_matches["multiple_cards"] = unique_cards
                    
                    # Check for high amounts
                    high_amount_txns = [txn for txn in recent_transactions if txn.amount > self.fraud_patterns["payment_fraud"]["high_amount"]["threshold"]]
                    if high_amount_txns:
                        indicators.append("high_value_transactions")
                        pattern_matches["high_amounts"] = len(high_amount_txns)
                    
                    # Check transaction velocity
                    recent_hour_txns = [txn for txn in recent_transactions if 
                                      (datetime.now() - txn.timestamp).total_seconds() < 3600]
                    if len(recent_hour_txns) >= self.fraud_patterns["payment_fraud"]["rapid_transactions"]["threshold"]:
                        indicators.append("rapid_transaction_pattern")
                        pattern_matches["velocity"] = len(recent_hour_txns)
            
            elif fraud_type == "identity_fraud":
                # Check identity consistency
                if context.guest_id:
                    guest_context = await self.get_guest_context(context.guest_id)
                    if guest_context.get("crm_profile"):
                        # In real implementation, would check document consistency
                        indicators.append("identity_verification_required")
            
            elif fraud_type == "booking_fraud":
                # Analyze booking patterns
                if context.guest_id:
                    guest_history = await self.crm_service.get_guest_history(context.guest_id)
                    # Would analyze no-show patterns, cancellation behavior, etc.
                    pass
            
            elif fraud_type == "access_fraud":
                # Check access patterns
                if context.room_number:
                    access_logs = await self.security_service.get_access_logs(context.room_number, days=1)
                    
                    # Check for multiple failed attempts
                    failed_attempts = [log for log in access_logs if not log["successful"]]
                    if len(failed_attempts) >= self.fraud_patterns["access_fraud"]["unauthorized_access"]["failed_attempts"]:
                        indicators.append("multiple_failed_access")
                        pattern_matches["failed_attempts"] = len(failed_attempts)
        
        except Exception as e:
            indicators.append(f"analysis_error: {str(e)}")
        
        return {
            "fraud_type": fraud_type,
            "indicators": indicators,
            "pattern_matches": pattern_matches,
            "analysis_timestamp": datetime.now(),
            "data_sources": ["pos", "crm", "security", "pms"]
        }
    
    async def _calculate_risk_score(self, fraud_analysis: Dict, context: AgentContext) -> Dict[str, any]:
        """Calculate comprehensive risk score."""
        
        base_score = 0.0
        risk_factors = {}
        
        # Score based on fraud indicators
        indicator_scores = {
            "multiple_cards_used": 25,
            "high_value_transactions": 30,
            "rapid_transaction_pattern": 35,
            "multiple_failed_access": 40,
            "identity_verification_required": 20,
            "foreign_origin_suspicious": 15
        }
        
        for indicator in fraud_analysis["indicators"]:
            score = indicator_scores.get(indicator, 10)
            base_score += score
            risk_factors[indicator] = score
        
        # Adjust based on guest profile
        if context.guest_id:
            try:
                guest_context = await self.get_guest_context(context.guest_id)
                
                # Lower risk for established guests
                if guest_context.get("crm_profile"):
                    total_stays = guest_context["crm_profile"].total_stays
                    if total_stays > 5:
                        base_score *= 0.7  # Reduce risk for repeat guests
                        risk_factors["repeat_guest_adjustment"] = -30
                    
                    # VIP guests get special consideration but also scrutiny
                    if guest_context.get("vip_status"):
                        base_score *= 0.8  # Slight reduction but still monitored
                        risk_factors["vip_adjustment"] = -20
                
            except:
                # If we can't verify guest, increase risk slightly
                base_score += 10
                risk_factors["verification_unavailable"] = 10
        
        # Pattern-specific adjustments
        pattern_matches = fraud_analysis.get("pattern_matches", {})
        for pattern, value in pattern_matches.items():
            if pattern == "velocity" and value > 10:
                base_score += 25  # Very high velocity is concerning
            elif pattern == "high_amounts" and value > 3:
                base_score += 20  # Multiple high amounts
        
        # Cap the score at 100
        final_score = min(base_score, 100.0)
        
        # Determine risk level
        if final_score >= 80:
            risk_level = "critical_risk"
        elif final_score >= 60:
            risk_level = "high_risk"
        elif final_score >= 30:
            risk_level = "medium_risk"
        else:
            risk_level = "low_risk"
        
        # Calculate confidence based on data availability
        confidence = 0.9 if len(fraud_analysis["indicators"]) > 0 else 0.6
        
        return {
            "score": final_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "confidence": confidence,
            "assessment_timestamp": datetime.now(),
            "requires_manual_review": final_score >= 50
        }
    
    async def _get_historical_context(self, context: AgentContext) -> Dict[str, any]:
        """Get historical context for fraud analysis."""
        
        historical_data = {
            "transaction_history": [],
            "incident_history": [],
            "access_history": [],
            "profile_changes": []
        }
        
        if context.guest_id:
            try:
                # Get transaction history
                transactions = await self.pos_service.get_guest_transactions(context.guest_id, days=30)
                historical_data["transaction_history"] = [
                    {
                        "amount": float(txn.amount),
                        "timestamp": txn.timestamp,
                        "location": txn.location,
                        "payment_method": txn.payment_method
                    }
                    for txn in transactions
                ]
                
                # Get access history for room
                if context.room_number:
                    access_logs = await self.security_service.get_access_logs(context.room_number, days=7)
                    historical_data["access_history"] = access_logs
                
            except Exception as e:
                historical_data["error"] = str(e)
        
        return historical_data
    
    def _build_fraud_analysis_context(self, request: str, fraud_analysis: Dict, 
                                    risk_assessment: Dict, historical_data: Dict) -> str:
        """Build comprehensive fraud analysis context for LLM."""
        
        context = f"""FRAUD DETECTION ANALYSIS REQUEST:
Original Request: {request}

FRAUD ANALYSIS RESULTS:
- Fraud Type: {fraud_analysis['fraud_type']}
- Risk Score: {risk_assessment['score']}/100
- Risk Level: {risk_assessment['risk_level']}
- Confidence: {risk_assessment['confidence']*100:.1f}%

FRAUD INDICATORS DETECTED:
{chr(10).join(f"- {indicator}" for indicator in fraud_analysis['indicators'])}

RISK FACTORS:
{chr(10).join(f"- {factor}: {score}" for factor, score in risk_assessment['risk_factors'].items())}

PATTERN ANALYSIS:
{chr(10).join(f"- {pattern}: {value}" for pattern, value in fraud_analysis.get('pattern_matches', {}).items())}

HISTORICAL CONTEXT:
- Transaction History: {len(historical_data.get('transaction_history', []))} transactions
- Access History: {len(historical_data.get('access_history', []))} access events
- Previous Incidents: {len(historical_data.get('incident_history', []))} incidents

RESPONSE REQUIREMENT:
Based on the risk level ({risk_assessment['risk_level']}), provide:
1. Clear assessment of the fraud risk
2. Immediate actions that should be taken
3. Investigation steps required
4. Guest communication approach (if applicable)
5. Security measures to implement

Maintain professional tone while addressing security concerns appropriately.
"""
        
        return context
    
    async def _execute_security_actions(self, risk_assessment: Dict, fraud_analysis: Dict, 
                                      context: AgentContext) -> List[str]:
        """Execute security actions based on risk assessment."""
        
        actions = []
        risk_level = risk_assessment["risk_level"]
        protocol = self.response_protocols[risk_level]
        
        try:
            # Always log the fraud assessment
            self.audit_logger.log_security_event(
                action="fraud_risk_assessment",
                severity="high" if risk_level in ["high_risk", "critical_risk"] else "medium",
                details={
                    "risk_score": risk_assessment["score"],
                    "risk_level": risk_level,
                    "fraud_type": fraud_analysis["fraud_type"],
                    "indicators": fraud_analysis["indicators"]
                },
                user_id=context.user_id,
                guest_id=context.guest_id
            )
            actions.append("Logged fraud risk assessment")
            
            # Risk-level specific actions
            if risk_level == "low_risk":
                actions.append("Increased monitoring activated")
                
            elif risk_level == "medium_risk":
                actions.append("Enhanced verification protocols enabled")
                actions.append("Transaction monitoring increased")
                
            elif risk_level == "high_risk":
                # Temporary holds and additional verification
                actions.append("Temporary transaction hold implemented")
                actions.append("Identity verification required for next interaction")
                actions.append("Security team notified for investigation")
                
                # Block certain activities if specified
                if protocol.get("auto_block"):
                    actions.append("Automatic security block activated")
                
            elif risk_level == "critical_risk":
                # Immediate security response
                actions.append("Immediate security alert triggered")
                actions.append("Account frozen pending investigation")
                actions.append("Security manager notified immediately")
                actions.append("Law enforcement contact prepared")
                
                # Immediate response protocol
                if protocol.get("immediate_response"):
                    actions.append("Emergency security protocol activated")
            
            # Fraud-type specific actions
            fraud_type = fraud_analysis["fraud_type"]
            
            if fraud_type == "payment_fraud":
                actions.append("Payment processing flagged for manual review")
                if risk_level in ["high_risk", "critical_risk"]:
                    actions.append("Credit card authorization enhanced")
                    
            elif fraud_type == "identity_fraud":
                actions.append("Identity document verification required")
                actions.append("Additional identification requested")
                
            elif fraud_type == "access_fraud":
                actions.append("Access permissions review initiated")
                if context.room_number:
                    actions.append(f"Room {context.room_number} access logs analyzed")
                    
            elif fraud_type == "booking_fraud":
                actions.append("Booking pattern analysis completed")
                actions.append("Reservation verification enhanced")
            
            # Communication actions
            if context.guest_id and risk_level in ["medium_risk", "high_risk"]:
                actions.append("Guest notification prepared (security verification)")
                
        except Exception as e:
            actions.append(f"Error executing security actions: {str(e)}")
        
        return actions
    
    def _generate_investigation_recommendations(self, fraud_analysis: Dict, risk_assessment: Dict) -> List[str]:
        """Generate investigation recommendations based on analysis."""
        
        recommendations = []
        risk_level = risk_assessment["risk_level"]
        fraud_type = fraud_analysis["fraud_type"]
        
        # General investigation steps
        if risk_level != "low_risk":
            recommendations.append("Conduct comprehensive guest background verification")
            recommendations.append("Review all recent transactions and activities")
            recommendations.append("Cross-reference with known fraud databases")
        
        # Risk-level specific recommendations
        if risk_level in ["high_risk", "critical_risk"]:
            recommendations.append("Initiate formal fraud investigation")
            recommendations.append("Coordinate with hotel security and management")
            recommendations.append("Document all evidence and communications")
            recommendations.append("Prepare incident report for authorities if needed")
        
        # Fraud-type specific recommendations
        if fraud_type == "payment_fraud":
            recommendations.append("Verify payment method authenticity with bank")
            recommendations.append("Check for card presence and authorization validity")
            recommendations.append("Review PCI DSS compliance for transaction processing")
            
        elif fraud_type == "identity_fraud":
            recommendations.append("Validate identity documents with issuing authorities")
            recommendations.append("Perform biometric verification if available")
            recommendations.append("Check guest against identity theft databases")
            
        elif fraud_type == "access_fraud":
            recommendations.append("Review access control systems and logs")
            recommendations.append("Verify guest authorization for accessed areas")
            recommendations.append("Check for security system vulnerabilities")
            
        elif fraud_type == "booking_fraud":
            recommendations.append("Analyze booking patterns and payment methods")
            recommendations.append("Verify contact information and guest details")
            recommendations.append("Review cancellation and no-show history")
        
        # Follow-up recommendations
        recommendations.append("Schedule follow-up review in 24-48 hours")
        recommendations.append("Monitor guest activities for pattern changes")
        recommendations.append("Update fraud detection models with new patterns")
        
        return recommendations