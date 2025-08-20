"""
Safety Guardrails Tool for Security Triage Agent.

Provides comprehensive safety checks and content validation to ensure
secure and appropriate incident processing with hospitality industry focus.
"""

import re
import json
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import IncidentCategory, IncidentPriority


class SafetyViolation(BaseModel):
    """Individual safety violation detected."""
    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    detected_content: Optional[str] = None
    recommendation: str


class SafetyCheckResult(BaseModel):
    """Result of safety guardrails check."""
    passed: bool
    overall_risk_level: str  # "low", "medium", "high", "critical"
    violations: List[SafetyViolation] = Field(default_factory=list)
    content_flags: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    review_reason: str = ""
    sanitized_content: Optional[Dict[str, str]] = None
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class SafetyGuardrails(BaseTool):
    """
    Comprehensive safety guardrails for hospitality security incident processing.
    
    Implements multiple layers of safety checks including content validation,
    PII detection, threat assessment, and hospitality-specific safety measures.
    """
    
    name: str = "safety_guardrails"
    description: str = "Perform safety and security validation for incident processing"
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        model_name: str = "gpt-4",
        temperature: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if llm is None:
            if "gpt" in model_name.lower():
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    model_kwargs={"response_format": {"type": "json_object"}}
                )
            else:
                self.llm = ChatAnthropic(
                    model=model_name,
                    temperature=temperature
                )
        else:
            self.llm = llm
        
        self.pii_patterns = self._initialize_pii_patterns()
        self.threat_indicators = self._initialize_threat_indicators()
        self.hospitality_safeguards = self._initialize_hospitality_safeguards()
        self.safety_prompt = self._create_safety_prompt()
    
    def _initialize_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize PII detection patterns."""
        
        patterns = {}
        
        # Credit card patterns
        patterns["credit_card"] = re.compile(
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'
        )
        
        # Email patterns
        patterns["email"] = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone patterns (international)
        patterns["phone"] = re.compile(
            r'(\+?[1-9]\d{1,14}|\(\d{3}\)\s?\d{3}-?\d{4}|\d{3}-?\d{3}-?\d{4})'
        )
        
        # Indian Aadhaar number pattern
        patterns["aadhaar"] = re.compile(
            r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'
        )
        
        # Indian PAN number pattern
        patterns["pan"] = re.compile(
            r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        )
        
        # Passport patterns
        patterns["passport"] = re.compile(
            r'\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b[A-Z]{1,2}[0-9]{6,9}\b'
        )
        
        # IP address patterns
        patterns["ip_address"] = re.compile(
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        )
        
        # Room number patterns (hotel specific)
        patterns["room_number"] = re.compile(
            r'\broom\s*[#:]?\s*(\d{3,4}[a-z]?)\b|\b\d{3,4}[a-z]?\s*room\b',
            re.IGNORECASE
        )
        
        return patterns
    
    def _initialize_threat_indicators(self) -> Dict[str, List[str]]:
        """Initialize threat indicator keywords and patterns."""
        
        indicators = {}
        
        # Violence indicators
        indicators["violence"] = [
            "attack", "assault", "violence", "threat", "weapon", "harm", "injury",
            "blood", "fight", "aggression", "danger", "emergency"
        ]
        
        # Security breach indicators
        indicators["security_breach"] = [
            "unauthorized", "breach", "compromise", "infiltration", "intrusion",
            "hack", "malware", "ransomware", "phishing", "exploit"
        ]
        
        # Fraud indicators
        indicators["fraud"] = [
            "fraud", "scam", "deception", "fake", "counterfeit", "forgery",
            "identity theft", "credit card fraud", "billing fraud"
        ]
        
        # Privacy violation indicators
        indicators["privacy_violation"] = [
            "data leak", "exposure", "unauthorized access", "privacy breach",
            "personal information", "confidential", "sensitive data"
        ]
        
        # Hospitality-specific threats
        indicators["hospitality_threats"] = [
            "guest safety", "property damage", "theft", "burglary", "trespassing",
            "vandalism", "disruption", "evacuation", "lockdown"
        ]
        
        return indicators
    
    def _initialize_hospitality_safeguards(self) -> Dict[str, Any]:
        """Initialize hospitality-specific safety measures."""
        
        safeguards = {
            "guest_privacy_protection": {
                "pii_fields": ["guest_name", "room_number", "contact_info", "payment_details"],
                "redaction_required": True,
                "retention_limits": "30_days_post_checkout"
            },
            "operational_safety": {
                "restricted_areas": ["server_room", "cash_office", "key_storage", "security_office"],
                "emergency_protocols": ["fire", "medical", "security", "evacuation"],
                "guest_impact_assessment": True
            },
            "brand_protection": {
                "reputation_risks": ["media_exposure", "social_media", "public_incident"],
                "escalation_required": True,
                "communication_approval": "required"
            },
            "regulatory_compliance": {
                "data_protection": ["DPDP", "GDPR", "CCPA"],
                "payment_compliance": ["PCI_DSS"],
                "industry_standards": ["ISO_27001", "hospitality_guidelines"]
            }
        }
        
        return safeguards
    
    def _create_safety_prompt(self) -> ChatPromptTemplate:
        """Create the safety assessment prompt."""
        
        system_message = """You are an expert security safety analyst specializing in hospitality industry safety protocols. Your role is to assess security incidents for safety risks, content violations, and appropriate handling measures.

SAFETY ASSESSMENT FRAMEWORK:

1. CONTENT SAFETY CHECKS:
   - PII and sensitive data exposure
   - Inappropriate or harmful content
   - Threat language or violent content
   - Discriminatory or offensive material
   - Privacy violations

2. HOSPITALITY-SPECIFIC SAFETY:
   - Guest safety and privacy protection
   - Employee safety considerations
   - Property and asset security
   - Brand reputation protection
   - Operational continuity

3. SECURITY THREAT ASSESSMENT:
   - Active security threats
   - Cyber security risks
   - Physical security concerns
   - Fraud indicators
   - Compliance violations

4. RISK LEVEL CLASSIFICATION:
   - CRITICAL: Immediate safety threat, active attack, severe breach
   - HIGH: Significant safety concern, major security incident
   - MEDIUM: Moderate safety issue, potential risk
   - LOW: Minor safety consideration, routine handling

SAFETY VIOLATIONS:
- Exposure of guest personal information
- Unsafe operational procedures
- Inadequate threat response
- Privacy law violations
- Discrimination or bias
- Inappropriate content sharing
- Insufficient security measures

HOSPITALITY SAFETY PRIORITIES:
1. Guest safety and security
2. Employee protection
3. Data privacy and confidentiality
4. Property and asset security
5. Brand reputation protection
6. Regulatory compliance
7. Operational continuity

HUMAN REVIEW TRIGGERS:
- High-risk safety violations
- Potential guest harm
- Significant privacy breaches
- Compliance violations
- Brand reputation threats
- Complex ethical considerations
- Ambiguous safety scenarios

RESPONSE FORMAT:
Provide JSON response with:
- passed: Overall safety check result
- overall_risk_level: Risk classification
- violations: List of specific safety violations
- content_flags: Content-specific concerns
- requires_human_review: Boolean for human oversight
- review_reason: Rationale for human review
- risk_factors: Identified risk elements
- recommendations: Safety improvement recommendations

Prioritize guest safety, privacy protection, and regulatory compliance in all assessments."""

        human_message = """Assess the safety and security of this incident processing:

INCIDENT DESCRIPTION: {incident_description}
INCIDENT CATEGORY: {category}
RISK SCORE: {risk_score}/10

PROCESSING CONTEXT: {processing_context}

SAFETY ASSESSMENT FOCUS:
{assessment_focus}

Provide comprehensive safety analysis in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def check_safety(
        self,
        incident_description: str,
        category: IncidentCategory,
        risk_score: float = 5.0,
        processing_context: Optional[Dict[str, Any]] = None,
        assessment_focus: Optional[List[str]] = None
    ) -> SafetyCheckResult:
        """
        Perform comprehensive safety checks on incident processing.
        
        Args:
            incident_description: Description of the incident
            category: Incident category
            risk_score: Risk assessment score
            processing_context: Additional processing context
            assessment_focus: Specific areas to focus assessment on
            
        Returns:
            SafetyCheckResult with detailed safety analysis
        """
        
        # Perform basic content safety checks
        content_violations = self._check_content_safety(incident_description)
        pii_violations = self._detect_pii_exposure(incident_description)
        threat_violations = self._assess_threat_indicators(incident_description, category)
        
        # Combine all violations
        all_violations = content_violations + pii_violations + threat_violations
        
        # Determine if LLM assessment is needed
        requires_llm_assessment = (
            risk_score >= 6.0 or
            len(all_violations) > 0 or
            category in [IncidentCategory.PII_BREACH, IncidentCategory.CYBER_SECURITY]
        )
        
        if requires_llm_assessment:
            # Get comprehensive safety assessment from LLM
            llm_result = await self._get_llm_safety_assessment(
                incident_description, category, risk_score, processing_context, assessment_focus
            )
            
            # Merge with basic checks
            all_violations.extend(llm_result.violations)
            content_flags = list(set(llm_result.content_flags + [v.violation_type for v in content_violations]))
            
        else:
            # Use basic assessment
            llm_result = SafetyCheckResult(
                passed=len(all_violations) == 0,
                overall_risk_level="low" if len(all_violations) == 0 else "medium",
                violations=all_violations,
                requires_human_review=False,
                review_reason=""
            )
            content_flags = [v.violation_type for v in all_violations]
        
        # Determine overall safety status
        critical_violations = [v for v in all_violations if v.severity == "critical"]
        high_violations = [v for v in all_violations if v.severity == "high"]
        
        overall_passed = len(critical_violations) == 0
        
        # Determine risk level
        if critical_violations:
            risk_level = "critical"
        elif high_violations:
            risk_level = "high"
        elif len(all_violations) > 0:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Determine if human review is required
        requires_human_review = (
            len(critical_violations) > 0 or
            len(high_violations) > 2 or
            risk_score >= 8.0 or
            category == IncidentCategory.PII_BREACH
        )
        
        review_reason = ""
        if requires_human_review:
            if critical_violations:
                review_reason = f"Critical safety violations detected: {', '.join([v.violation_type for v in critical_violations])}"
            elif len(high_violations) > 2:
                review_reason = "Multiple high-severity safety concerns require review"
            elif risk_score >= 8.0:
                review_reason = f"High risk score ({risk_score}/10) requires human oversight"
            elif category == IncidentCategory.PII_BREACH:
                review_reason = "PII breach incidents require mandatory human review"
        
        # Generate sanitized content if needed
        sanitized_content = None
        if pii_violations:
            sanitized_content = self._sanitize_content(incident_description)
        
        # Generate recommendations
        recommendations = self._generate_safety_recommendations(all_violations, category, risk_score)
        
        return SafetyCheckResult(
            passed=overall_passed,
            overall_risk_level=risk_level,
            violations=all_violations,
            content_flags=content_flags,
            requires_human_review=requires_human_review,
            review_reason=review_reason,
            sanitized_content=sanitized_content,
            risk_factors=[v.violation_type for v in all_violations],
            recommendations=recommendations
        )
    
    async def _get_llm_safety_assessment(
        self,
        incident_description: str,
        category: IncidentCategory,
        risk_score: float,
        processing_context: Optional[Dict[str, Any]],
        assessment_focus: Optional[List[str]]
    ) -> SafetyCheckResult:
        """Get comprehensive safety assessment from LLM."""
        
        # Prepare context
        context_text = "Standard incident processing"
        if processing_context:
            context_parts = [f"{k}: {v}" for k, v in processing_context.items()]
            context_text = "\n".join(context_parts)
        
        focus_text = "General safety assessment"
        if assessment_focus:
            focus_text = f"Focus areas: {', '.join(assessment_focus)}"
        
        # Format the prompt
        formatted_prompt = self.safety_prompt.format_messages(
            incident_description=incident_description,
            category=category.value,
            risk_score=risk_score,
            processing_context=context_text,
            assessment_focus=focus_text
        )
        
        # Get safety assessment from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Parse violations
            violations = []
            for violation_data in result_data.get("violations", []):
                violation = SafetyViolation(
                    violation_type=violation_data.get("violation_type", "unknown"),
                    severity=violation_data.get("severity", "medium"),
                    description=violation_data.get("description", ""),
                    detected_content=violation_data.get("detected_content"),
                    recommendation=violation_data.get("recommendation", "")
                )
                violations.append(violation)
            
            return SafetyCheckResult(
                passed=result_data.get("passed", False),
                overall_risk_level=result_data.get("overall_risk_level", "medium"),
                violations=violations,
                content_flags=result_data.get("content_flags", []),
                requires_human_review=result_data.get("requires_human_review", False),
                review_reason=result_data.get("review_reason", ""),
                risk_factors=result_data.get("risk_factors", []),
                recommendations=result_data.get("recommendations", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback to conservative safety assessment
            return SafetyCheckResult(
                passed=False,
                overall_risk_level="high",
                violations=[SafetyViolation(
                    violation_type="assessment_error",
                    severity="high",
                    description=f"Safety assessment failed: {str(e)}",
                    recommendation="Manual safety review required"
                )],
                requires_human_review=True,
                review_reason="Safety assessment system error - manual review required"
            )
    
    def _check_content_safety(self, content: str) -> List[SafetyViolation]:
        """Perform basic content safety checks."""
        
        violations = []
        content_lower = content.lower()
        
        # Check for inappropriate content keywords
        inappropriate_keywords = [
            "discriminat", "harassment", "threat", "violence", "illegal",
            "unauthorized", "malicious", "harmful"
        ]
        
        for keyword in inappropriate_keywords:
            if keyword in content_lower:
                violations.append(SafetyViolation(
                    violation_type="inappropriate_content",
                    severity="medium",
                    description=f"Potentially inappropriate content detected: {keyword}",
                    detected_content=keyword,
                    recommendation="Review content for appropriateness"
                ))
        
        return violations
    
    def _detect_pii_exposure(self, content: str) -> List[SafetyViolation]:
        """Detect potential PII exposure in content."""
        
        violations = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                severity = "high" if pii_type in ["credit_card", "aadhaar", "passport"] else "medium"
                violations.append(SafetyViolation(
                    violation_type=f"pii_exposure_{pii_type}",
                    severity=severity,
                    description=f"Potential {pii_type.replace('_', ' ')} exposure detected",
                    detected_content=f"{len(matches)} instances found",
                    recommendation=f"Redact or mask {pii_type.replace('_', ' ')} information"
                ))
        
        return violations
    
    def _assess_threat_indicators(self, content: str, category: IncidentCategory) -> List[SafetyViolation]:
        """Assess threat indicators in content."""
        
        violations = []
        content_lower = content.lower()
        
        for threat_type, indicators in self.threat_indicators.items():
            threat_count = sum(1 for indicator in indicators if indicator in content_lower)
            
            if threat_count > 0:
                # Determine severity based on threat type and category
                if threat_type == "violence" or threat_count >= 3:
                    severity = "critical"
                elif threat_type in ["security_breach", "fraud"] and category in [
                    IncidentCategory.CYBER_SECURITY, IncidentCategory.PAYMENT_FRAUD
                ]:
                    severity = "high"
                else:
                    severity = "medium"
                
                violations.append(SafetyViolation(
                    violation_type=f"threat_indicator_{threat_type}",
                    severity=severity,
                    description=f"Threat indicators detected: {threat_type.replace('_', ' ')}",
                    detected_content=f"{threat_count} indicators found",
                    recommendation=f"Assess and respond to {threat_type.replace('_', ' ')} indicators"
                ))
        
        return violations
    
    def _sanitize_content(self, content: str) -> Dict[str, str]:
        """Sanitize content by masking PII and sensitive information."""
        
        sanitized = content
        replacements = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            def mask_match(match):
                original = match.group(0)
                if pii_type == "credit_card":
                    # Mask credit card: keep first 4 and last 4 digits
                    if len(original) >= 8:
                        masked = original[:4] + "*" * (len(original) - 8) + original[-4:]
                    else:
                        masked = "*" * len(original)
                elif pii_type == "email":
                    # Mask email: keep first char and domain
                    parts = original.split("@")
                    if len(parts) == 2:
                        masked = parts[0][0] + "*" * (len(parts[0]) - 1) + "@" + parts[1]
                    else:
                        masked = "*" * len(original)
                else:
                    # Generic masking
                    masked = "*" * len(original)
                
                replacements[original] = masked
                return masked
            
            sanitized = pattern.sub(mask_match, sanitized)
        
        return {
            "original_content": content,
            "sanitized_content": sanitized,
            "replacements_made": replacements
        }
    
    def _generate_safety_recommendations(
        self,
        violations: List[SafetyViolation],
        category: IncidentCategory,
        risk_score: float
    ) -> List[str]:
        """Generate safety improvement recommendations."""
        
        recommendations = []
        
        # General recommendations based on violations
        if any(v.severity == "critical" for v in violations):
            recommendations.append("Immediate escalation required for critical safety violations")
        
        if any("pii_exposure" in v.violation_type for v in violations):
            recommendations.append("Implement PII redaction and data minimization procedures")
            recommendations.append("Review data handling policies and staff training")
        
        if any("threat_indicator" in v.violation_type for v in violations):
            recommendations.append("Activate threat response procedures")
            recommendations.append("Coordinate with security team for threat assessment")
        
        # Category-specific recommendations
        if category == IncidentCategory.PII_BREACH:
            recommendations.append("Conduct privacy impact assessment")
            recommendations.append("Review data protection compliance requirements")
        
        if category == IncidentCategory.CYBER_SECURITY:
            recommendations.append("Implement cyber security incident response plan")
            recommendations.append("Isolate affected systems pending investigation")
        
        # Risk-based recommendations
        if risk_score >= 8.0:
            recommendations.append("Executive notification required for high-risk incident")
            recommendations.append("Consider external expert consultation")
        
        return list(set(recommendations))  # Remove duplicates
    
    def sanitize_text(self, text: str) -> str:
        """Public method to sanitize text content."""
        result = self._sanitize_content(text)
        return result.get("sanitized_content", text)
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.check_safety(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.check_safety(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)