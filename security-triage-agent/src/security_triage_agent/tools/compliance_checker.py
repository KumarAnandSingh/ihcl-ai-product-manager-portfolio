"""
Compliance Checking Tool for Security Triage Agent.

Provides comprehensive compliance validation for security incidents and responses
against hospitality industry regulations and standards.
"""

import json
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import (
    ComplianceFramework, SecurityPlaybook, IncidentCategory, 
    IncidentMetadata
)


class ComplianceRequirement(BaseModel):
    """Individual compliance requirement."""
    requirement_id: str
    framework: ComplianceFramework
    description: str
    mandatory: bool = True
    timeline_hours: Optional[int] = None
    responsible_party: str
    evidence_required: List[str] = Field(default_factory=list)


class ComplianceResult(BaseModel):
    """Result of compliance checking."""
    framework_checks: Dict[ComplianceFramework, bool] = Field(default_factory=dict)
    requirements: List[ComplianceRequirement] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    requires_legal_review: bool = False
    requires_regulatory_notification: bool = False
    notification_deadlines: Dict[str, str] = Field(default_factory=dict)
    documentation_requirements: List[str] = Field(default_factory=list)
    risk_mitigation_actions: List[str] = Field(default_factory=list)


class ComplianceChecker(BaseTool):
    """
    Comprehensive compliance checking tool for hospitality security incidents.
    
    Validates incident response against relevant regulatory frameworks including
    DPDP, PCI DSS, GDPR, and industry standards.
    """
    
    name: str = "compliance_checker"
    description: str = "Check compliance requirements for security incidents and responses"
    
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
        
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        self.compliance_prompt = self._create_compliance_prompt()
    
    def _initialize_compliance_frameworks(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Initialize compliance framework definitions and requirements."""
        
        frameworks = {}
        
        # Data Protection and Digital Privacy Act (India)
        frameworks[ComplianceFramework.DPDP] = {
            "name": "Data Protection and Digital Privacy Act (India)",
            "scope": "Personal data processing and protection",
            "notification_requirements": {
                "data_breach": {
                    "authority": "Data Protection Board",
                    "timeline_hours": 72,
                    "conditions": ["risk_to_data_principal", "significant_harm_likelihood"]
                },
                "affected_individuals": {
                    "timeline_hours": 72,
                    "conditions": ["high_risk_to_rights_freedoms"]
                }
            },
            "key_requirements": [
                "lawful_basis_for_processing",
                "data_minimization",
                "purpose_limitation", 
                "storage_limitation",
                "security_safeguards",
                "breach_notification",
                "consent_management"
            ],
            "penalties": {
                "max_fine": "INR 500 crores or 4% of global turnover",
                "conditions": "serious data fiduciary violations"
            }
        }
        
        # PCI Data Security Standard
        frameworks[ComplianceFramework.PCI_DSS] = {
            "name": "Payment Card Industry Data Security Standard",
            "scope": "Cardholder data protection",
            "notification_requirements": {
                "card_brands": {
                    "timeline_hours": 24,
                    "conditions": ["suspected_compromise", "actual_compromise"]
                },
                "acquiring_bank": {
                    "timeline_hours": 24,
                    "conditions": ["account_data_compromise"]
                }
            },
            "key_requirements": [
                "build_secure_network",
                "protect_cardholder_data",
                "maintain_vulnerability_program",
                "strong_access_controls",
                "monitor_network_access",
                "information_security_policy"
            ],
            "incident_response": [
                "forensic_investigation",
                "compromise_assessment",
                "remediation_plan",
                "compliance_validation"
            ]
        }
        
        # General Data Protection Regulation (for international guests)
        frameworks[ComplianceFramework.GDPR] = {
            "name": "General Data Protection Regulation",
            "scope": "EU resident personal data",
            "notification_requirements": {
                "supervisory_authority": {
                    "timeline_hours": 72,
                    "conditions": ["likely_high_risk"]
                },
                "data_subjects": {
                    "timeline": "without_undue_delay",
                    "conditions": ["high_risk_to_rights_freedoms"]
                }
            },
            "key_requirements": [
                "lawfulness_fairness_transparency",
                "purpose_limitation",
                "data_minimization",
                "accuracy",
                "storage_limitation",
                "integrity_confidentiality",
                "accountability"
            ]
        }
        
        return frameworks
    
    def _create_compliance_prompt(self) -> ChatPromptTemplate:
        """Create the compliance checking prompt."""
        
        system_message = """You are an expert compliance analyst specializing in hospitality industry regulatory requirements. Your role is to assess security incidents and response plans for compliance with relevant frameworks.

COMPLIANCE FRAMEWORKS FOR HOSPITALITY:

1. DPDP (Data Protection and Digital Privacy Act - India)
   - Applies to: Personal data of Indian residents
   - Key Requirements: Lawful processing, data minimization, security safeguards
   - Breach Notification: 72 hours to Data Protection Board if risk to data principal
   - Penalties: Up to INR 500 crores or 4% of global turnover

2. PCI DSS (Payment Card Industry Data Security Standard)
   - Applies to: Cardholder data handling
   - Key Requirements: Secure network, protect cardholder data, access controls
   - Breach Notification: 24 hours to card brands and acquiring bank
   - Validation: Annual compliance assessment required

3. GDPR (General Data Protection Regulation)
   - Applies to: Personal data of EU residents (international guests)
   - Key Requirements: Lawful basis, data minimization, individual rights
   - Breach Notification: 72 hours to supervisory authority, notify individuals if high risk
   - Penalties: Up to €20 million or 4% of annual turnover

4. CCPA (California Consumer Privacy Act)
   - Applies to: Personal information of California residents
   - Key Requirements: Consumer rights, privacy notices, data deletion
   - Breach Notification: Specific requirements for unauthorized access

HOSPITALITY-SPECIFIC CONSIDERATIONS:
- Guest privacy expectations and rights
- International guest data handling
- Payment processing compliance
- Employee data protection
- Vendor data sharing agreements
- Cross-border data transfers
- Hotel loyalty program data
- Surveillance and monitoring data

COMPLIANCE ASSESSMENT PROCESS:
1. Identify applicable frameworks based on incident characteristics
2. Assess current compliance status
3. Identify violations or gaps
4. Determine notification requirements and deadlines
5. Recommend remediation actions
6. Assess legal review requirements
7. Document evidence and audit trail requirements

RISK FACTORS REQUIRING HEIGHTENED COMPLIANCE:
- High-volume data exposure
- Sensitive personal data (payment, health, biometric)
- Cross-border data transfer
- Media attention or public exposure
- Repeat violations or systemic issues
- Vulnerable populations (children, VIPs)

RESPONSE FORMAT:
Provide JSON response with:
- framework_checks: Pass/fail status for each applicable framework
- requirements: List of specific compliance requirements
- violations: Identified compliance violations
- recommendations: Compliance improvement recommendations
- requires_legal_review: Boolean for legal review requirement
- requires_regulatory_notification: Boolean for regulatory notification
- notification_deadlines: Specific notification timelines
- documentation_requirements: Required documentation for compliance
- risk_mitigation_actions: Actions to mitigate compliance risk"""

        human_message = """Assess compliance requirements for this security incident:

INCIDENT CATEGORY: {category}
INCIDENT DESCRIPTION: {description}

SELECTED PLAYBOOK:
{playbook_details}

INCIDENT METADATA:
{metadata}

SPECIFIC ASSESSMENT REQUESTS:
{assessment_context}

Provide comprehensive compliance analysis in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def check_compliance(
        self,
        category: IncidentCategory,
        playbook: Optional[SecurityPlaybook] = None,
        metadata: Optional[IncidentMetadata] = None,
        incident_description: str = "",
        assessment_context: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Check compliance requirements for a security incident.
        
        Args:
            category: Incident category
            playbook: Selected security playbook
            metadata: Incident metadata
            incident_description: Description of the incident
            assessment_context: Additional context for assessment
            
        Returns:
            ComplianceResult with detailed compliance analysis
        """
        
        # Determine applicable frameworks based on incident characteristics
        applicable_frameworks = self._determine_applicable_frameworks(category, metadata)
        
        # Prepare playbook details
        playbook_details = "No playbook selected"
        if playbook:
            playbook_details = f"""
Playbook: {playbook.name}
Actions: {', '.join(playbook.required_actions)}
Compliance Frameworks: {', '.join([fw.value for fw in playbook.compliance_frameworks])}
"""
        
        # Prepare metadata context
        metadata_context = self._format_metadata_for_compliance(metadata)
        
        # Prepare assessment context
        context_text = "Standard compliance assessment"
        if assessment_context:
            context_parts = [f"{k}: {v}" for k, v in assessment_context.items()]
            context_text = "\n".join(context_parts)
        
        # Format the prompt
        formatted_prompt = self.compliance_prompt.format_messages(
            category=category.value,
            description=incident_description,
            playbook_details=playbook_details,
            metadata=metadata_context,
            assessment_context=context_text
        )
        
        # Get compliance assessment from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Parse framework checks
            framework_checks = {}
            for framework_name, status in result_data.get("framework_checks", {}).items():
                try:
                    framework = ComplianceFramework(framework_name.lower())
                    framework_checks[framework] = bool(status)
                except ValueError:
                    continue
            
            # Parse requirements
            requirements = []
            for req_data in result_data.get("requirements", []):
                try:
                    framework = ComplianceFramework(req_data.get("framework", "").lower())
                    requirement = ComplianceRequirement(
                        requirement_id=req_data.get("requirement_id", ""),
                        framework=framework,
                        description=req_data.get("description", ""),
                        mandatory=req_data.get("mandatory", True),
                        timeline_hours=req_data.get("timeline_hours"),
                        responsible_party=req_data.get("responsible_party", "security_team"),
                        evidence_required=req_data.get("evidence_required", [])
                    )
                    requirements.append(requirement)
                except (ValueError, KeyError):
                    continue
            
            # Additional compliance analysis
            compliance_result = ComplianceResult(
                framework_checks=framework_checks,
                requirements=requirements,
                violations=result_data.get("violations", []),
                recommendations=result_data.get("recommendations", []),
                requires_legal_review=result_data.get("requires_legal_review", False),
                requires_regulatory_notification=result_data.get("requires_regulatory_notification", False),
                notification_deadlines=result_data.get("notification_deadlines", {}),
                documentation_requirements=result_data.get("documentation_requirements", []),
                risk_mitigation_actions=result_data.get("risk_mitigation_actions", [])
            )
            
            # Add framework-specific requirements
            compliance_result = self._add_framework_requirements(
                compliance_result, applicable_frameworks, category, metadata
            )
            
            return compliance_result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback compliance check
            return self._fallback_compliance_check(category, applicable_frameworks, str(e))
    
    def _determine_applicable_frameworks(
        self,
        category: IncidentCategory,
        metadata: Optional[IncidentMetadata]
    ) -> List[ComplianceFramework]:
        """Determine which compliance frameworks apply to the incident."""
        
        applicable = []
        
        # Category-based framework determination
        if category in [IncidentCategory.PII_BREACH, IncidentCategory.OPERATIONAL_SECURITY]:
            applicable.append(ComplianceFramework.DPDP)
            
            # Add GDPR for international guests
            if metadata and (
                "international" in str(metadata.location).lower() or
                "eu" in str(metadata.location).lower() or
                any("eu_" in guest for guest in metadata.affected_guests)
            ):
                applicable.append(ComplianceFramework.GDPR)
        
        if category == IncidentCategory.PAYMENT_FRAUD:
            applicable.append(ComplianceFramework.PCI_DSS)
        
        # Always consider DPDP for Indian operations
        if ComplianceFramework.DPDP not in applicable:
            applicable.append(ComplianceFramework.DPDP)
        
        return applicable
    
    def _format_metadata_for_compliance(self, metadata: Optional[IncidentMetadata]) -> str:
        """Format metadata with compliance-relevant information."""
        
        if not metadata:
            return "No metadata provided"
        
        compliance_relevant = []
        
        if metadata.affected_guests:
            compliance_relevant.append(f"Affected Guests: {len(metadata.affected_guests)}")
        
        if metadata.affected_employees:
            compliance_relevant.append(f"Affected Employees: {len(metadata.affected_employees)}")
        
        if metadata.affected_systems:
            payment_systems = [s for s in metadata.affected_systems if "payment" in s.lower() or "pos" in s.lower()]
            if payment_systems:
                compliance_relevant.append(f"Payment Systems Affected: {', '.join(payment_systems)}")
            
            data_systems = [s for s in metadata.affected_systems if "database" in s.lower() or "crm" in s.lower()]
            if data_systems:
                compliance_relevant.append(f"Data Systems Affected: {', '.join(data_systems)}")
        
        if metadata.location:
            compliance_relevant.append(f"Location: {metadata.location}")
        
        if metadata.property_code:
            compliance_relevant.append(f"Property: {metadata.property_code}")
        
        return "\n".join(compliance_relevant) if compliance_relevant else "No compliance-relevant metadata"
    
    def _add_framework_requirements(
        self,
        result: ComplianceResult,
        applicable_frameworks: List[ComplianceFramework],
        category: IncidentCategory,
        metadata: Optional[IncidentMetadata]
    ) -> ComplianceResult:
        """Add framework-specific requirements based on incident characteristics."""
        
        for framework in applicable_frameworks:
            framework_info = self.compliance_frameworks.get(framework, {})
            
            if framework == ComplianceFramework.DPDP:
                # DPDP-specific requirements
                if category == IncidentCategory.PII_BREACH:
                    result.requirements.append(ComplianceRequirement(
                        requirement_id="DPDP_BREACH_001",
                        framework=framework,
                        description="Assess risk to data principal and notify DPB within 72 hours if significant harm likely",
                        timeline_hours=72,
                        responsible_party="privacy_officer",
                        evidence_required=["risk_assessment", "harm_analysis", "notification_copy"]
                    ))
                    
                    result.notification_deadlines["data_protection_board"] = "72 hours from discovery"
                    result.requires_regulatory_notification = True
            
            elif framework == ComplianceFramework.PCI_DSS:
                # PCI DSS-specific requirements
                if category == IncidentCategory.PAYMENT_FRAUD:
                    result.requirements.append(ComplianceRequirement(
                        requirement_id="PCI_INCIDENT_001",
                        framework=framework,
                        description="Notify card brands and acquiring bank within 24 hours of suspected compromise",
                        timeline_hours=24,
                        responsible_party="payments_team",
                        evidence_required=["incident_report", "forensic_logs", "remediation_plan"]
                    ))
                    
                    result.notification_deadlines["card_brands"] = "24 hours from discovery"
                    result.notification_deadlines["acquiring_bank"] = "24 hours from discovery"
                    result.requires_legal_review = True
            
            elif framework == ComplianceFramework.GDPR:
                # GDPR-specific requirements for EU guests
                if category == IncidentCategory.PII_BREACH:
                    result.requirements.append(ComplianceRequirement(
                        requirement_id="GDPR_BREACH_001",
                        framework=framework,
                        description="Notify relevant EU supervisory authority within 72 hours",
                        timeline_hours=72,
                        responsible_party="privacy_officer",
                        evidence_required=["breach_assessment", "notification_form", "impact_analysis"]
                    ))
                    
                    if metadata and len(metadata.affected_guests) > 100:
                        result.requirements.append(ComplianceRequirement(
                            requirement_id="GDPR_INDIVIDUAL_001",
                            framework=framework,
                            description="Notify affected individuals without undue delay if high risk",
                            timeline_hours=72,
                            responsible_party="customer_service",
                            evidence_required=["individual_notifications", "communication_records"]
                        ))
        
        return result
    
    def _fallback_compliance_check(
        self,
        category: IncidentCategory,
        applicable_frameworks: List[ComplianceFramework],
        error: str
    ) -> ComplianceResult:
        """Provide fallback compliance check when LLM parsing fails."""
        
        # Basic framework checks - assume compliance gaps for safety
        framework_checks = {framework: False for framework in applicable_frameworks}
        
        # Basic requirements based on category
        requirements = []
        if category == IncidentCategory.PII_BREACH:
            requirements.append(ComplianceRequirement(
                requirement_id="FALLBACK_PRIVACY_001",
                framework=ComplianceFramework.DPDP,
                description="Manual compliance review required due to parsing error",
                responsible_party="privacy_officer",
                evidence_required=["manual_review_report"]
            ))
        
        return ComplianceResult(
            framework_checks=framework_checks,
            requirements=requirements,
            violations=[f"Compliance assessment failed: {error}"],
            recommendations=["Conduct manual compliance review", "Consult legal counsel"],
            requires_legal_review=True,
            requires_regulatory_notification=False,  # Conservative approach
            documentation_requirements=["fallback_compliance_report", "manual_review_documentation"],
            risk_mitigation_actions=["immediate_legal_consultation", "compliance_specialist_review"]
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.check_compliance(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.check_compliance(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)