"""
Incident Prioritization Tool for Security Triage Agent.

Provides AI-powered prioritization and risk assessment of security incidents
based on hospitality industry impact factors and business context.
"""

import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import IncidentPriority, IncidentCategory, IncidentMetadata, RiskAssessment


class RiskAssessmentResult(BaseModel):
    """Detailed risk assessment result."""
    risk_score: float = Field(ge=0.0, le=10.0)
    risk_factors: List[str] = Field(default_factory=list)
    business_impact: str
    guest_impact: str
    financial_impact: str
    reputation_impact: str
    operational_impact: str
    likelihood_score: float = Field(ge=0.0, le=10.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    time_sensitivity: str
    escalation_triggers: List[str] = Field(default_factory=list)


class PrioritizationResult(BaseModel):
    """Result of incident prioritization."""
    priority: IncidentPriority
    reasoning: str
    risk_assessment: RiskAssessmentResult
    recommended_sla: str
    stakeholders_to_notify: List[str] = Field(default_factory=list)
    immediate_actions_required: bool = False


class IncidentPrioritizer(BaseTool):
    """
    AI-powered incident prioritization tool for hospitality security scenarios.
    
    Evaluates incident priority based on multiple factors including business impact,
    guest safety, financial implications, and regulatory requirements.
    """
    
    name: str = "incident_prioritizer"
    description: str = "Prioritize security incidents based on impact and risk assessment"
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        model_name: str = "gpt-4",
        temperature: float = 0.2,
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
        
        self.prioritization_prompt = self._create_prioritization_prompt()
        self.risk_assessment_prompt = self._create_risk_assessment_prompt()
    
    def _create_prioritization_prompt(self) -> ChatPromptTemplate:
        """Create the prioritization prompt with hospitality context."""
        
        system_message = """You are an expert security analyst specializing in hospitality incident prioritization. Your role is to assess the priority level of security incidents based on hospitality industry impact factors.

PRIORITY LEVELS:
1. CRITICAL - Immediate threat to guest/staff safety, active security breach, major system compromise
   - SLA: Immediate response (15 minutes)
   - Examples: Active data breach, guest safety threat, payment system compromise

2. HIGH - Significant security concern requiring urgent attention
   - SLA: 1 hour response
   - Examples: Unauthorized access incident, fraud detection, compliance violation

3. MEDIUM - Moderate security issue requiring timely response
   - SLA: 4 hours response
   - Examples: Policy violations, minor system issues, routine security concerns

4. LOW - Minor security matter for routine handling
   - SLA: 24 hours response
   - Examples: Minor policy infractions, informational security events

5. INFORMATIONAL - Security-related information requiring documentation only
   - SLA: 72 hours response
   - Examples: Security awareness items, routine notifications

PRIORITIZATION FACTORS:
1. Guest Safety & Security Impact
2. Business Operations Impact
3. Financial Impact (direct costs, revenue loss)
4. Reputation & Brand Impact
5. Regulatory Compliance Requirements
6. Data Privacy Implications
7. System Availability Impact
8. Time Sensitivity & Urgency
9. Scope of Affected Parties
10. Legal & Liability Exposure

HOSPITALITY-SPECIFIC CONSIDERATIONS:
- Guest experience and satisfaction
- Peak vs. off-peak operational periods
- Property type and guest demographics
- Seasonal business patterns
- Local regulatory environment
- Brand standards and reputation protection

RESPONSE FORMAT:
Respond with JSON containing:
- priority: The assigned priority level
- reasoning: Detailed explanation for the priority assignment
- risk_assessment: Comprehensive risk analysis
- recommended_sla: Response time requirement
- stakeholders_to_notify: List of stakeholders requiring notification
- immediate_actions_required: Boolean indicating if immediate action is needed"""

        human_message = """Prioritize this security incident:

INCIDENT CATEGORY: {category}
DESCRIPTION: {description}
RISK ASSESSMENT: {risk_assessment}

METADATA:
{metadata_context}

Provide detailed prioritization analysis in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _create_risk_assessment_prompt(self) -> ChatPromptTemplate:
        """Create the risk assessment prompt."""
        
        system_message = """You are an expert security risk analyst for the hospitality industry. Assess the risk level and potential impact of security incidents with focus on hotel operations.

RISK ASSESSMENT FRAMEWORK:
Risk Score = (Impact Score × Likelihood Score) / 10
- Impact Score: 1-10 (10 = catastrophic)
- Likelihood Score: 1-10 (10 = certain to occur)
- Final Risk Score: 0.1-10.0

IMPACT CATEGORIES:
1. Guest Impact (safety, privacy, experience)
2. Business Impact (operations, revenue, continuity)
3. Financial Impact (direct costs, losses, fines)
4. Reputation Impact (brand damage, media exposure)
5. Operational Impact (system downtime, process disruption)

RISK FACTORS TO CONSIDER:
- Scope of affected parties (guests, staff, systems)
- Data sensitivity involved
- System criticality
- Time sensitivity
- Regulatory implications
- Recovery complexity
- Historical incident patterns

HOSPITALITY RISK MULTIPLIERS:
- Guest safety issues: +2 risk points
- Payment system impact: +1.5 risk points
- Brand reputation threat: +1.5 risk points
- Regulatory compliance: +1 risk point
- Peak season timing: +0.5 risk points

RESPONSE FORMAT:
JSON with detailed risk assessment including all impact categories and specific hospitality factors."""

        human_message = """Assess the risk for this incident:

CATEGORY: {category}
DESCRIPTION: {description}

METADATA:
{metadata_context}

Provide comprehensive risk assessment in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def assess_risk(
        self,
        category: IncidentCategory,
        description: str,
        metadata: Optional[IncidentMetadata] = None
    ) -> RiskAssessment:
        """
        Perform detailed risk assessment for an incident.
        
        Args:
            category: Incident category
            description: Incident description
            metadata: Additional metadata
            
        Returns:
            RiskAssessment with detailed risk analysis
        """
        
        # Prepare metadata context
        metadata_context = self._format_metadata_context(metadata)
        
        # Format the prompt
        formatted_prompt = self.risk_assessment_prompt.format_messages(
            category=category.value,
            description=description,
            metadata_context=metadata_context
        )
        
        # Get risk assessment from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Create risk assessment
            risk_score = max(0.0, min(10.0, float(result_data.get("risk_score", 5.0))))
            likelihood_score = max(0.0, min(10.0, float(result_data.get("likelihood_score", 5.0))))
            confidence_score = max(0.0, min(1.0, float(result_data.get("confidence_score", 0.7))))
            
            # Determine mitigation urgency based on risk score
            if risk_score >= 8.0:
                mitigation_urgency = IncidentPriority.CRITICAL
            elif risk_score >= 6.0:
                mitigation_urgency = IncidentPriority.HIGH
            elif risk_score >= 4.0:
                mitigation_urgency = IncidentPriority.MEDIUM
            elif risk_score >= 2.0:
                mitigation_urgency = IncidentPriority.LOW
            else:
                mitigation_urgency = IncidentPriority.INFORMATIONAL
            
            return RiskAssessment(
                risk_score=risk_score,
                risk_factors=result_data.get("risk_factors", []),
                mitigation_urgency=mitigation_urgency,
                potential_impact=result_data.get("potential_impact", "Moderate impact expected"),
                likelihood_score=likelihood_score,
                confidence_score=confidence_score
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback risk assessment
            return self._fallback_risk_assessment(category, description, str(e))
    
    async def prioritize(
        self,
        category: IncidentCategory,
        risk_assessment: RiskAssessment,
        metadata: Optional[IncidentMetadata] = None
    ) -> PrioritizationResult:
        """
        Prioritize an incident based on category and risk assessment.
        
        Args:
            category: Incident category
            risk_assessment: Risk assessment results
            metadata: Additional metadata
            
        Returns:
            PrioritizationResult with priority and detailed reasoning
        """
        
        # Prepare inputs
        metadata_context = self._format_metadata_context(metadata)
        risk_context = f"""Risk Score: {risk_assessment.risk_score}/10
Risk Factors: {', '.join(risk_assessment.risk_factors)}
Potential Impact: {risk_assessment.potential_impact}
Likelihood: {risk_assessment.likelihood_score}/10
Confidence: {risk_assessment.confidence_score}"""
        
        # Format the prompt
        formatted_prompt = self.prioritization_prompt.format_messages(
            category=category.value,
            description=f"Category: {category.value}",
            risk_assessment=risk_context,
            metadata_context=metadata_context
        )
        
        # Get prioritization from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Validate priority
            try:
                priority = IncidentPriority(result_data["priority"].lower())
            except (KeyError, ValueError):
                priority = risk_assessment.mitigation_urgency
            
            # Create detailed risk assessment result
            risk_assessment_result = RiskAssessmentResult(
                risk_score=risk_assessment.risk_score,
                risk_factors=risk_assessment.risk_factors,
                business_impact=result_data.get("business_impact", "Moderate business impact"),
                guest_impact=result_data.get("guest_impact", "Potential guest impact"),
                financial_impact=result_data.get("financial_impact", "Moderate financial impact"),
                reputation_impact=result_data.get("reputation_impact", "Potential reputation impact"),
                operational_impact=result_data.get("operational_impact", "Operational impact possible"),
                likelihood_score=risk_assessment.likelihood_score,
                confidence_score=risk_assessment.confidence_score,
                time_sensitivity=result_data.get("time_sensitivity", "Moderate"),
                escalation_triggers=result_data.get("escalation_triggers", [])
            )
            
            # Determine SLA based on priority
            sla_mapping = {
                IncidentPriority.CRITICAL: "15 minutes",
                IncidentPriority.HIGH: "1 hour",
                IncidentPriority.MEDIUM: "4 hours",
                IncidentPriority.LOW: "24 hours",
                IncidentPriority.INFORMATIONAL: "72 hours"
            }
            
            # Determine stakeholders based on priority and category
            stakeholders = self._determine_stakeholders(priority, category, metadata)
            
            return PrioritizationResult(
                priority=priority,
                reasoning=result_data.get("reasoning", f"Prioritized as {priority.value} based on risk assessment"),
                risk_assessment=risk_assessment_result,
                recommended_sla=result_data.get("recommended_sla", sla_mapping[priority]),
                stakeholders_to_notify=stakeholders,
                immediate_actions_required=priority in [IncidentPriority.CRITICAL, IncidentPriority.HIGH]
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback prioritization
            return self._fallback_prioritization(category, risk_assessment, str(e))
    
    def _format_metadata_context(self, metadata: Optional[IncidentMetadata]) -> str:
        """Format metadata into context string."""
        if not metadata:
            return "No additional metadata provided"
        
        context_parts = []
        if metadata.location:
            context_parts.append(f"Location: {metadata.location}")
        if metadata.property_code:
            context_parts.append(f"Property: {metadata.property_code}")
        if metadata.affected_systems:
            context_parts.append(f"Affected Systems: {', '.join(metadata.affected_systems)}")
        if metadata.affected_guests:
            context_parts.append(f"Affected Guests: {len(metadata.affected_guests)}")
        if metadata.affected_employees:
            context_parts.append(f"Affected Employees: {len(metadata.affected_employees)}")
        if metadata.business_impact:
            context_parts.append(f"Business Impact: {metadata.business_impact}")
        if metadata.estimated_cost:
            context_parts.append(f"Estimated Cost: ${metadata.estimated_cost:,.2f}")
        
        return "\n".join(context_parts) if context_parts else "No additional metadata provided"
    
    def _determine_stakeholders(
        self,
        priority: IncidentPriority,
        category: IncidentCategory,
        metadata: Optional[IncidentMetadata]
    ) -> List[str]:
        """Determine stakeholders to notify based on incident characteristics."""
        
        stakeholders = ["security_team"]
        
        # Priority-based stakeholders
        if priority == IncidentPriority.CRITICAL:
            stakeholders.extend(["security_manager", "operations_manager", "general_manager"])
        elif priority == IncidentPriority.HIGH:
            stakeholders.extend(["security_manager", "operations_manager"])
        elif priority == IncidentPriority.MEDIUM:
            stakeholders.append("security_manager")
        
        # Category-specific stakeholders
        category_stakeholders = {
            IncidentCategory.PAYMENT_FRAUD: ["finance_team", "revenue_manager"],
            IncidentCategory.PII_BREACH: ["privacy_officer", "legal_team"],
            IncidentCategory.CYBER_SECURITY: ["it_security", "it_manager"],
            IncidentCategory.COMPLIANCE_VIOLATION: ["compliance_officer", "legal_team"],
            IncidentCategory.GUEST_ACCESS: ["front_office", "housekeeping_manager"],
            IncidentCategory.VENDOR_ACCESS: ["procurement", "vendor_manager"]
        }
        
        if category in category_stakeholders:
            stakeholders.extend(category_stakeholders[category])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(stakeholders))
    
    def _fallback_risk_assessment(
        self, 
        category: IncidentCategory, 
        description: str, 
        error: str
    ) -> RiskAssessment:
        """Provide fallback risk assessment when LLM parsing fails."""
        
        # Category-based risk scoring
        category_risk_scores = {
            IncidentCategory.CYBER_SECURITY: 7.0,
            IncidentCategory.PII_BREACH: 8.0,
            IncidentCategory.PAYMENT_FRAUD: 7.5,
            IncidentCategory.PHYSICAL_SECURITY: 6.0,
            IncidentCategory.GUEST_ACCESS: 5.5,
            IncidentCategory.COMPLIANCE_VIOLATION: 6.5,
            IncidentCategory.OPERATIONAL_SECURITY: 4.0,
            IncidentCategory.VENDOR_ACCESS: 5.0
        }
        
        risk_score = category_risk_scores.get(category, 5.0)
        
        # Determine priority based on risk score
        if risk_score >= 7.0:
            priority = IncidentPriority.HIGH
        elif risk_score >= 5.0:
            priority = IncidentPriority.MEDIUM
        else:
            priority = IncidentPriority.LOW
        
        return RiskAssessment(
            risk_score=risk_score,
            risk_factors=[f"fallback_assessment_{category.value}", "llm_parsing_error"],
            mitigation_urgency=priority,
            potential_impact=f"Estimated {priority.value} impact based on category {category.value}",
            likelihood_score=5.0,
            confidence_score=0.5
        )
    
    def _fallback_prioritization(
        self, 
        category: IncidentCategory,
        risk_assessment: RiskAssessment,
        error: str
    ) -> PrioritizationResult:
        """Provide fallback prioritization when LLM parsing fails."""
        
        priority = risk_assessment.mitigation_urgency
        
        risk_assessment_result = RiskAssessmentResult(
            risk_score=risk_assessment.risk_score,
            risk_factors=risk_assessment.risk_factors,
            business_impact="Unable to assess - fallback mode",
            guest_impact="Unable to assess - fallback mode",
            financial_impact="Unable to assess - fallback mode",
            reputation_impact="Unable to assess - fallback mode",
            operational_impact="Unable to assess - fallback mode",
            likelihood_score=risk_assessment.likelihood_score,
            confidence_score=risk_assessment.confidence_score,
            time_sensitivity="Unknown",
            escalation_triggers=["fallback_mode"]
        )
        
        sla_mapping = {
            IncidentPriority.CRITICAL: "15 minutes",
            IncidentPriority.HIGH: "1 hour",
            IncidentPriority.MEDIUM: "4 hours",
            IncidentPriority.LOW: "24 hours",
            IncidentPriority.INFORMATIONAL: "72 hours"
        }
        
        return PrioritizationResult(
            priority=priority,
            reasoning=f"Fallback prioritization due to error: {error}. Based on risk score {risk_assessment.risk_score}",
            risk_assessment=risk_assessment_result,
            recommended_sla=sla_mapping[priority],
            stakeholders_to_notify=self._determine_stakeholders(priority, category, None),
            immediate_actions_required=priority in [IncidentPriority.CRITICAL, IncidentPriority.HIGH]
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.prioritize(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.prioritize(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)