"""
Security Playbook Selection Tool for Security Triage Agent.

Provides AI-powered selection of appropriate security response playbooks
based on incident characteristics and hospitality industry best practices.
"""

import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import (
    IncidentCategory, IncidentPriority, SecurityPlaybook, 
    ComplianceFramework, ActionRequirement, RiskAssessment
)


class PlaybookSelectionResult(BaseModel):
    """Result of playbook selection process."""
    recommended_playbook: SecurityPlaybook
    applicable_playbooks: List[SecurityPlaybook] = Field(default_factory=list)
    selection_reasoning: str
    customization_notes: List[str] = Field(default_factory=list)
    escalation_paths: Dict[str, str] = Field(default_factory=dict)
    estimated_completion_time: str


class PlaybookSelector(BaseTool):
    """
    AI-powered security playbook selection tool for hospitality incidents.
    
    Selects the most appropriate response playbook based on incident characteristics,
    risk assessment, and hospitality industry context.
    """
    
    name: str = "playbook_selector"
    description: str = "Select appropriate security response playbooks for incidents"
    
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
        
        self.playbook_repository = self._initialize_playbook_repository()
        self.selection_prompt = self._create_selection_prompt()
    
    def _initialize_playbook_repository(self) -> Dict[str, SecurityPlaybook]:
        """Initialize the repository of security playbooks."""
        
        playbooks = {}
        
        # Guest Access Incident Playbook
        playbooks["guest_access_standard"] = SecurityPlaybook(
            playbook_id="guest_access_standard",
            name="Guest Access Incident Response",
            description="Standard response for unauthorized guest access incidents",
            applicable_categories=[IncidentCategory.GUEST_ACCESS],
            required_actions=[
                "verify_incident_details",
                "secure_affected_areas",
                "investigate_access_method",
                "review_guest_history",
                "update_access_controls",
                "document_findings",
                "notify_stakeholders"
            ],
            action_requirements={
                "secure_affected_areas": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True,
                    timeout_minutes=30
                ),
                "update_access_controls": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                ),
                "notify_stakeholders": ActionRequirement(
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "guest_safety_risk": "immediate_escalation",
                "multiple_properties": "regional_manager",
                "media_attention": "corporate_communications"
            },
            compliance_frameworks=[
                ComplianceFramework.DPDP,
                ComplianceFramework.PCI_DSS
            ]
        )
        
        # Payment Fraud Playbook
        playbooks["payment_fraud_response"] = SecurityPlaybook(
            playbook_id="payment_fraud_response",
            name="Payment Fraud Incident Response",
            description="Comprehensive response for payment fraud incidents",
            applicable_categories=[IncidentCategory.PAYMENT_FRAUD],
            required_actions=[
                "isolate_affected_systems",
                "preserve_evidence",
                "notify_payment_processors",
                "conduct_fraud_analysis",
                "implement_fraud_controls",
                "notify_affected_customers",
                "file_regulatory_reports",
                "coordinate_with_authorities"
            ],
            action_requirements={
                "isolate_affected_systems": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True,
                    timeout_minutes=15
                ),
                "notify_payment_processors": ActionRequirement(
                    requires_human_approval=True,
                    requires_compliance_check=True,
                    timeout_minutes=60
                ),
                "notify_affected_customers": ActionRequirement(
                    requires_human_approval=True,
                    requires_legal_review=True,
                    requires_documentation=True
                ),
                "file_regulatory_reports": ActionRequirement(
                    requires_legal_review=True,
                    requires_compliance_check=True,
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "fraud_amount_threshold": "50000",
                "multiple_cards_affected": "immediate_escalation",
                "law_enforcement_required": "legal_team"
            },
            compliance_frameworks=[
                ComplianceFramework.PCI_DSS,
                ComplianceFramework.DPDP
            ]
        )
        
        # PII Breach Playbook
        playbooks["pii_breach_response"] = SecurityPlaybook(
            playbook_id="pii_breach_response",
            name="Personal Data Breach Response",
            description="Comprehensive response for personal data breaches",
            applicable_categories=[IncidentCategory.PII_BREACH],
            required_actions=[
                "contain_breach",
                "assess_data_exposure",
                "preserve_forensic_evidence",
                "notify_privacy_officer",
                "conduct_impact_assessment",
                "prepare_breach_notifications",
                "implement_remediation",
                "update_security_controls",
                "conduct_lessons_learned"
            ],
            action_requirements={
                "contain_breach": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True,
                    timeout_minutes=30
                ),
                "notify_privacy_officer": ActionRequirement(
                    requires_documentation=True,
                    timeout_minutes=60
                ),
                "prepare_breach_notifications": ActionRequirement(
                    requires_legal_review=True,
                    requires_compliance_check=True,
                    requires_documentation=True
                ),
                "implement_remediation": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "high_risk_data": "immediate_escalation",
                "large_number_affected": "regulatory_notification_required",
                "media_exposure_risk": "corporate_communications"
            },
            compliance_frameworks=[
                ComplianceFramework.DPDP,
                ComplianceFramework.GDPR
            ]
        )
        
        # Cybersecurity Incident Playbook
        playbooks["cybersecurity_response"] = SecurityPlaybook(
            playbook_id="cybersecurity_response",
            name="Cybersecurity Incident Response",
            description="Response for cybersecurity threats and attacks",
            applicable_categories=[IncidentCategory.CYBER_SECURITY],
            required_actions=[
                "activate_incident_team",
                "isolate_affected_systems",
                "collect_forensic_evidence",
                "analyze_attack_vectors",
                "implement_containment",
                "eradicate_threats",
                "recover_systems",
                "conduct_post_incident_review"
            ],
            action_requirements={
                "activate_incident_team": ActionRequirement(
                    requires_documentation=True,
                    timeout_minutes=15
                ),
                "isolate_affected_systems": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True,
                    timeout_minutes=30
                ),
                "collect_forensic_evidence": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                ),
                "recover_systems": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "critical_systems_affected": "immediate_escalation",
                "ransomware_detected": "executive_notification",
                "customer_data_risk": "privacy_officer_notification"
            },
            compliance_frameworks=[
                ComplianceFramework.DPDP,
                ComplianceFramework.PCI_DSS
            ]
        )
        
        # Operational Security Playbook
        playbooks["operational_security"] = SecurityPlaybook(
            playbook_id="operational_security",
            name="Operational Security Incident Response",
            description="Response for operational security violations",
            applicable_categories=[IncidentCategory.OPERATIONAL_SECURITY],
            required_actions=[
                "investigate_violation",
                "interview_involved_parties",
                "review_security_procedures",
                "implement_corrective_actions",
                "provide_additional_training",
                "update_policies",
                "monitor_compliance"
            ],
            action_requirements={
                "investigate_violation": ActionRequirement(
                    requires_documentation=True
                ),
                "interview_involved_parties": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                ),
                "implement_corrective_actions": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "repeat_violations": "hr_notification",
                "safety_risk": "immediate_escalation",
                "policy_gap_identified": "policy_review_required"
            },
            compliance_frameworks=[
                ComplianceFramework.DPDP
            ]
        )
        
        # Physical Security Playbook
        playbooks["physical_security"] = SecurityPlaybook(
            playbook_id="physical_security",
            name="Physical Security Incident Response",
            description="Response for physical security breaches",
            applicable_categories=[IncidentCategory.PHYSICAL_SECURITY],
            required_actions=[
                "secure_breach_area",
                "review_security_footage",
                "conduct_facility_inspection",
                "update_access_controls",
                "coordinate_with_security",
                "implement_additional_measures",
                "conduct_staff_briefing"
            ],
            action_requirements={
                "secure_breach_area": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True,
                    timeout_minutes=15
                ),
                "coordinate_with_security": ActionRequirement(
                    requires_documentation=True
                ),
                "implement_additional_measures": ActionRequirement(
                    requires_human_approval=True,
                    requires_documentation=True
                )
            },
            escalation_criteria={
                "guest_area_affected": "immediate_escalation",
                "valuables_missing": "law_enforcement",
                "safety_systems_compromised": "emergency_protocols"
            },
            compliance_frameworks=[]
        )
        
        return playbooks
    
    def _create_selection_prompt(self) -> ChatPromptTemplate:
        """Create the playbook selection prompt."""
        
        system_message = """You are an expert security incident response coordinator for the hospitality industry. Your role is to select the most appropriate security response playbook based on incident characteristics.

PLAYBOOK SELECTION CRITERIA:
1. Incident Category Alignment
2. Risk Level and Priority
3. Compliance Requirements
4. Resource Availability
5. Time Sensitivity
6. Stakeholder Impact
7. Business Operations Impact
8. Regulatory Obligations

HOSPITALITY CONTEXT FACTORS:
- Guest experience protection
- Business continuity requirements
- Brand reputation considerations
- Seasonal/operational timing
- Property-specific constraints
- Regulatory environment
- Staff capability and availability

CUSTOMIZATION CONSIDERATIONS:
- Incident-specific circumstances
- Available resources and expertise
- Time constraints and urgency
- Stakeholder availability
- System dependencies
- Communication requirements

ESCALATION PATH FACTORS:
- Incident severity and scope
- Stakeholder impact level
- Regulatory notification requirements
- Media/public attention risk
- Financial impact thresholds
- Legal implications

RESPONSE FORMAT:
Provide JSON response with:
- recommended_playbook: The primary playbook selection
- applicable_playbooks: List of all relevant playbooks
- selection_reasoning: Detailed rationale for selection
- customization_notes: Specific adaptations needed
- escalation_paths: Defined escalation criteria and contacts
- estimated_completion_time: Expected timeline for execution

Consider the specific hospitality context and ensure recommendations align with hotel operational requirements and guest service standards."""

        human_message = """Select the most appropriate security response playbook:

INCIDENT DETAILS:
Category: {category}
Priority: {priority}
Risk Score: {risk_score}/10

RISK ASSESSMENT:
{risk_assessment}

AVAILABLE PLAYBOOKS:
{available_playbooks}

INCIDENT CONTEXT:
{incident_context}

Provide detailed playbook selection analysis in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def select_playbooks(
        self,
        category: IncidentCategory,
        priority: IncidentPriority,
        risk_assessment: Optional[RiskAssessment] = None,
        incident_context: Optional[Dict[str, Any]] = None
    ) -> PlaybookSelectionResult:
        """
        Select appropriate security playbooks for an incident.
        
        Args:
            category: Incident category
            priority: Incident priority level
            risk_assessment: Risk assessment results
            incident_context: Additional incident context
            
        Returns:
            PlaybookSelectionResult with recommended playbook and analysis
        """
        
        # Filter applicable playbooks by category
        applicable_playbooks = [
            playbook for playbook in self.playbook_repository.values()
            if category in playbook.applicable_categories
        ]
        
        if not applicable_playbooks:
            # Fallback to operational security playbook
            applicable_playbooks = [self.playbook_repository["operational_security"]]
        
        # Prepare context for LLM
        risk_score = risk_assessment.risk_score if risk_assessment else 5.0
        risk_context = ""
        if risk_assessment:
            risk_context = f"""Risk Factors: {', '.join(risk_assessment.risk_factors)}
Potential Impact: {risk_assessment.potential_impact}
Likelihood: {risk_assessment.likelihood_score}/10
Confidence: {risk_assessment.confidence_score}"""
        
        # Format available playbooks
        playbook_summaries = []
        for playbook in applicable_playbooks:
            summary = f"""
ID: {playbook.playbook_id}
Name: {playbook.name}
Description: {playbook.description}
Actions: {len(playbook.required_actions)} steps
Compliance: {', '.join([fw.value for fw in playbook.compliance_frameworks])}
"""
            playbook_summaries.append(summary.strip())
        
        available_playbooks_text = "\n\n".join(playbook_summaries)
        
        # Format incident context
        context_text = "Standard incident context"
        if incident_context:
            context_parts = [f"{k}: {v}" for k, v in incident_context.items()]
            context_text = "\n".join(context_parts)
        
        # Format the prompt
        formatted_prompt = self.selection_prompt.format_messages(
            category=category.value,
            priority=priority.value,
            risk_score=risk_score,
            risk_assessment=risk_context,
            available_playbooks=available_playbooks_text,
            incident_context=context_text
        )
        
        # Get playbook selection from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Find recommended playbook
            recommended_playbook_id = result_data.get("recommended_playbook", {}).get("playbook_id")
            recommended_playbook = None
            
            for playbook in applicable_playbooks:
                if playbook.playbook_id == recommended_playbook_id:
                    recommended_playbook = playbook
                    break
            
            # Fallback to first applicable playbook
            if not recommended_playbook:
                recommended_playbook = applicable_playbooks[0]
            
            # Apply customizations if needed
            customized_playbook = self._customize_playbook(
                recommended_playbook,
                priority,
                risk_assessment,
                result_data.get("customization_notes", [])
            )
            
            return PlaybookSelectionResult(
                recommended_playbook=customized_playbook,
                applicable_playbooks=applicable_playbooks,
                selection_reasoning=result_data.get(
                    "selection_reasoning",
                    f"Selected {recommended_playbook.name} based on category {category.value}"
                ),
                customization_notes=result_data.get("customization_notes", []),
                escalation_paths=result_data.get("escalation_paths", {}),
                estimated_completion_time=result_data.get(
                    "estimated_completion_time",
                    self._estimate_completion_time(priority, len(recommended_playbook.required_actions))
                )
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback selection
            return self._fallback_selection(applicable_playbooks, category, priority, str(e))
    
    def _customize_playbook(
        self,
        playbook: SecurityPlaybook,
        priority: IncidentPriority,
        risk_assessment: Optional[RiskAssessment],
        customization_notes: List[str]
    ) -> SecurityPlaybook:
        """
        Customize a playbook based on incident characteristics.
        
        Args:
            playbook: Base playbook to customize
            priority: Incident priority
            risk_assessment: Risk assessment results
            customization_notes: Specific customization requirements
            
        Returns:
            Customized security playbook
        """
        
        # Create a copy of the playbook for customization
        customized_playbook = SecurityPlaybook(
            playbook_id=f"{playbook.playbook_id}_customized",
            name=f"{playbook.name} (Customized)",
            description=playbook.description,
            applicable_categories=playbook.applicable_categories,
            required_actions=playbook.required_actions.copy(),
            action_requirements=playbook.action_requirements.copy(),
            escalation_criteria=playbook.escalation_criteria.copy(),
            compliance_frameworks=playbook.compliance_frameworks
        )
        
        # Adjust timeouts based on priority
        if priority == IncidentPriority.CRITICAL:
            # Reduce timeouts for critical incidents
            for action, requirements in customized_playbook.action_requirements.items():
                if requirements.timeout_minutes:
                    requirements.timeout_minutes = max(5, requirements.timeout_minutes // 2)
        elif priority in [IncidentPriority.LOW, IncidentPriority.INFORMATIONAL]:
            # Increase timeouts for lower priority incidents
            for action, requirements in customized_playbook.action_requirements.items():
                if requirements.timeout_minutes:
                    requirements.timeout_minutes = min(480, requirements.timeout_minutes * 2)
        
        # Add risk-based actions
        if risk_assessment and risk_assessment.risk_score >= 8.0:
            # High-risk incidents require additional actions
            if "executive_notification" not in customized_playbook.required_actions:
                customized_playbook.required_actions.append("executive_notification")
                customized_playbook.action_requirements["executive_notification"] = ActionRequirement(
                    requires_human_approval=False,
                    requires_documentation=True,
                    timeout_minutes=30
                )
        
        return customized_playbook
    
    def _estimate_completion_time(self, priority: IncidentPriority, action_count: int) -> str:
        """Estimate playbook completion time based on priority and complexity."""
        
        base_time_per_action = {
            IncidentPriority.CRITICAL: 15,    # 15 minutes per action
            IncidentPriority.HIGH: 30,        # 30 minutes per action
            IncidentPriority.MEDIUM: 60,      # 1 hour per action
            IncidentPriority.LOW: 120,        # 2 hours per action
            IncidentPriority.INFORMATIONAL: 240  # 4 hours per action
        }
        
        minutes_per_action = base_time_per_action.get(priority, 60)
        total_minutes = action_count * minutes_per_action
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        elif total_minutes < 1440:  # Less than 24 hours
            hours = total_minutes // 60
            return f"{hours} hours"
        else:
            days = total_minutes // 1440
            return f"{days} days"
    
    def _fallback_selection(
        self,
        applicable_playbooks: List[SecurityPlaybook],
        category: IncidentCategory,
        priority: IncidentPriority,
        error: str
    ) -> PlaybookSelectionResult:
        """Provide fallback playbook selection when LLM parsing fails."""
        
        # Select the first applicable playbook as fallback
        recommended_playbook = applicable_playbooks[0] if applicable_playbooks else self.playbook_repository["operational_security"]
        
        return PlaybookSelectionResult(
            recommended_playbook=recommended_playbook,
            applicable_playbooks=applicable_playbooks,
            selection_reasoning=f"Fallback selection due to parsing error: {error}. "
                             f"Selected {recommended_playbook.name} for category {category.value}",
            customization_notes=[f"Fallback mode - manual review recommended"],
            escalation_paths={"fallback_escalation": "security_manager"},
            estimated_completion_time=self._estimate_completion_time(priority, len(recommended_playbook.required_actions))
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.select_playbooks(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.select_playbooks(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)