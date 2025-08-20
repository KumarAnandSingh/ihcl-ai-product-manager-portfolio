"""
Response Generation Tool for Security Triage Agent.

Provides AI-powered generation of structured incident response plans
tailored to hospitality security scenarios and selected playbooks.
"""

import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import IncidentState, IncidentResponse


class ResponseGenerationResult(BaseModel):
    """Result of response generation."""
    response_plan: IncidentResponse
    customization_applied: List[str] = Field(default_factory=list)
    estimated_resources: Dict[str, Any] = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)
    risk_mitigation_actions: List[str] = Field(default_factory=list)
    stakeholder_communications: List[Dict[str, str]] = Field(default_factory=list)


class ResponseGenerator(BaseTool):
    """
    AI-powered incident response generation tool for hospitality security.
    
    Generates comprehensive, actionable incident response plans based on
    incident characteristics, selected playbooks, and hospitality best practices.
    """
    
    name: str = "response_generator"
    description: str = "Generate structured incident response plans for security incidents"
    
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
        
        self.response_prompt = self._create_response_prompt()
    
    def _create_response_prompt(self) -> ChatPromptTemplate:
        """Create the response generation prompt."""
        
        system_message = """You are an expert security incident response coordinator specializing in hospitality industry operations. Your role is to generate comprehensive, actionable incident response plans that address security incidents while maintaining guest service excellence and operational continuity.

INCIDENT RESPONSE FRAMEWORK:

1. IMMEDIATE ACTIONS (0-30 minutes):
   - Threat containment and stabilization
   - Safety assessment and protection
   - Initial stakeholder notification
   - Evidence preservation
   - System isolation (if required)

2. INVESTIGATION STEPS (30 minutes - 4 hours):
   - Detailed incident analysis
   - Evidence collection and documentation
   - Root cause investigation
   - Impact assessment
   - Timeline reconstruction

3. CONTAINMENT MEASURES (concurrent with investigation):
   - Security control implementation
   - Access restrictions
   - System hardening
   - Process modifications
   - Monitoring enhancement

4. NOTIFICATION REQUIREMENTS:
   - Internal stakeholders
   - Regulatory authorities
   - Affected parties (guests/employees)
   - Law enforcement (if required)
   - Business partners/vendors

5. DOCUMENTATION REQUIREMENTS:
   - Incident report creation
   - Evidence cataloging
   - Decision rationale
   - Timeline documentation
   - Compliance reporting

6. FOLLOW-UP ACTIONS:
   - Remediation implementation
   - Process improvements
   - Training updates
   - Policy revisions
   - Monitoring protocols

HOSPITALITY-SPECIFIC CONSIDERATIONS:

GUEST EXPERIENCE PROTECTION:
- Minimize guest disruption
- Maintain service quality
- Protect guest privacy
- Communicate transparently
- Provide compensation if appropriate

OPERATIONAL CONTINUITY:
- Maintain critical operations
- Minimize revenue impact
- Preserve staff productivity
- Protect brand reputation
- Ensure compliance adherence

STAKEHOLDER MANAGEMENT:
- Guest communication strategy
- Staff briefing protocols
- Management escalation
- Vendor coordination
- Media response preparation

BUSINESS IMPACT MITIGATION:
- Revenue protection measures
- Cost containment strategies
- Insurance coordination
- Legal risk management
- Reputation protection

REGULATORY COMPLIANCE:
- DPDP notification timelines
- PCI DSS reporting requirements
- Local law enforcement coordination
- Industry standard adherence
- Documentation standards

RESPONSE PLAN STRUCTURE:

Generate responses with specific, actionable items that include:
- Clear action descriptions
- Responsible parties
- Timeline requirements
- Success criteria
- Required resources
- Escalation triggers

Ensure all actions are:
- Specific and measurable
- Realistic and achievable
- Time-bound with clear deadlines
- Appropriate for hospitality context
- Compliant with relevant regulations
- Focused on business continuity

RESPONSE FORMAT:
Provide JSON response with:
- immediate_actions: Priority actions for first 30 minutes
- investigation_steps: Detailed investigation procedures
- containment_measures: Security containment actions
- notification_requirements: Stakeholder notification plan
- documentation_requirements: Required documentation
- follow_up_actions: Post-incident follow-up activities
- estimated_resources: Resource requirements
- success_criteria: Measurable success indicators
- risk_mitigation_actions: Risk reduction measures
- stakeholder_communications: Communication templates

Prioritize guest safety, business continuity, and regulatory compliance in all response plans."""

        human_message = """Generate a comprehensive incident response plan for this security incident:

INCIDENT DETAILS:
Category: {category}
Priority: {priority}
Risk Score: {risk_score}/10

INCIDENT DESCRIPTION:
{description}

SELECTED PLAYBOOK:
{playbook_details}

COMPLIANCE REQUIREMENTS:
{compliance_requirements}

INCIDENT CONTEXT:
{incident_context}

SAFETY CONSIDERATIONS:
{safety_considerations}

Generate a detailed, actionable response plan in JSON format that addresses all aspects of incident response while maintaining hospitality service standards."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def generate_response(
        self,
        incident_state: IncidentState
    ) -> IncidentResponse:
        """
        Generate comprehensive incident response plan.
        
        Args:
            incident_state: Complete incident state with all analysis results
            
        Returns:
            IncidentResponse with detailed response plan
        """
        
        # Prepare context information
        risk_score = incident_state.risk_assessment.risk_score if incident_state.risk_assessment else 5.0
        
        # Format playbook details
        playbook_details = "No playbook selected"
        if incident_state.selected_playbook:
            playbook = incident_state.selected_playbook
            playbook_details = f"""
Playbook: {playbook.name}
Description: {playbook.description}
Required Actions: {', '.join(playbook.required_actions)}
Compliance Frameworks: {', '.join([fw.value for fw in playbook.compliance_frameworks])}
Escalation Criteria: {', '.join(playbook.escalation_criteria.keys())}
"""
        
        # Format compliance requirements
        compliance_text = "No specific compliance requirements identified"
        compliance_result = incident_state.tool_results.get("compliance_check")
        if compliance_result:
            compliance_parts = []
            if compliance_result.get("requires_legal_review"):
                compliance_parts.append("Legal review required")
            if compliance_result.get("requires_regulatory_notification"):
                compliance_parts.append("Regulatory notification required")
            if compliance_result.get("notification_deadlines"):
                deadlines = compliance_result["notification_deadlines"]
                compliance_parts.append(f"Notification deadlines: {', '.join([f'{k}: {v}' for k, v in deadlines.items()])}")
            
            if compliance_parts:
                compliance_text = "\n".join(compliance_parts)
        
        # Format incident context
        context_parts = []
        if incident_state.metadata.location:
            context_parts.append(f"Location: {incident_state.metadata.location}")
        if incident_state.metadata.property_code:
            context_parts.append(f"Property: {incident_state.metadata.property_code}")
        if incident_state.metadata.affected_guests:
            context_parts.append(f"Affected Guests: {len(incident_state.metadata.affected_guests)}")
        if incident_state.metadata.affected_systems:
            context_parts.append(f"Affected Systems: {', '.join(incident_state.metadata.affected_systems)}")
        if incident_state.metadata.business_impact:
            context_parts.append(f"Business Impact: {incident_state.metadata.business_impact}")
        
        incident_context = "\n".join(context_parts) if context_parts else "Standard incident context"
        
        # Format safety considerations
        safety_text = "Standard safety protocols apply"
        safety_result = incident_state.tool_results.get("safety_check")
        if safety_result:
            safety_parts = []
            if safety_result.get("requires_human_review"):
                safety_parts.append(f"Human review required: {safety_result.get('review_reason', 'Safety concerns')}")
            if safety_result.get("violations"):
                violations = safety_result["violations"]
                safety_parts.append(f"Safety violations: {len(violations)} identified")
            if safety_result.get("overall_risk_level"):
                safety_parts.append(f"Safety risk level: {safety_result['overall_risk_level']}")
            
            if safety_parts:
                safety_text = "\n".join(safety_parts)
        
        # Format the prompt
        formatted_prompt = self.response_prompt.format_messages(
            category=incident_state.category.value if incident_state.category else "unknown",
            priority=incident_state.severity.value if incident_state.severity else "medium",
            risk_score=risk_score,
            description=incident_state.description,
            playbook_details=playbook_details,
            compliance_requirements=compliance_text,
            incident_context=incident_context,
            safety_considerations=safety_text
        )
        
        # Get response plan from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Create incident response object
            incident_response = IncidentResponse(
                immediate_actions=result_data.get("immediate_actions", []),
                investigation_steps=result_data.get("investigation_steps", []),
                containment_measures=result_data.get("containment_measures", []),
                notification_requirements=result_data.get("notification_requirements", []),
                documentation_requirements=result_data.get("documentation_requirements", []),
                follow_up_actions=result_data.get("follow_up_actions", [])
            )
            
            # Enhance response based on incident characteristics
            incident_response = self._enhance_response_plan(
                incident_response, incident_state, result_data
            )
            
            return incident_response
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback response generation
            return self._generate_fallback_response(incident_state, str(e))
    
    def _enhance_response_plan(
        self,
        response: IncidentResponse,
        incident_state: IncidentState,
        llm_data: Dict[str, Any]
    ) -> IncidentResponse:
        """Enhance the response plan based on incident characteristics."""
        
        # Add priority-specific actions
        if incident_state.severity and incident_state.severity.value in ["critical", "high"]:
            if "Executive notification within 30 minutes" not in response.immediate_actions:
                response.immediate_actions.insert(0, "Executive notification within 30 minutes")
        
        # Add category-specific actions
        if incident_state.category:
            category_actions = self._get_category_specific_actions(incident_state.category)
            
            # Add to appropriate sections
            for action_type, actions in category_actions.items():
                if action_type == "immediate":
                    response.immediate_actions.extend([a for a in actions if a not in response.immediate_actions])
                elif action_type == "investigation":
                    response.investigation_steps.extend([a for a in actions if a not in response.investigation_steps])
                elif action_type == "containment":
                    response.containment_measures.extend([a for a in actions if a not in response.containment_measures])
                elif action_type == "notification":
                    response.notification_requirements.extend([a for a in actions if a not in response.notification_requirements])
                elif action_type == "documentation":
                    response.documentation_requirements.extend([a for a in actions if a not in response.documentation_requirements])
                elif action_type == "followup":
                    response.follow_up_actions.extend([a for a in actions if a not in response.follow_up_actions])
        
        # Add compliance-driven actions
        compliance_result = incident_state.tool_results.get("compliance_check")
        if compliance_result:
            if compliance_result.get("requires_regulatory_notification"):
                notification_action = "Prepare and submit regulatory notifications within required timeframes"
                if notification_action not in response.notification_requirements:
                    response.notification_requirements.append(notification_action)
            
            if compliance_result.get("requires_legal_review"):
                legal_action = "Coordinate with legal team for compliance review and guidance"
                if legal_action not in response.immediate_actions:
                    response.immediate_actions.append(legal_action)
        
        # Add safety-driven actions
        safety_result = incident_state.tool_results.get("safety_check")
        if safety_result and safety_result.get("requires_human_review"):
            safety_action = f"Escalate to security manager for human review: {safety_result.get('review_reason', 'Safety concerns')}"
            if safety_action not in response.immediate_actions:
                response.immediate_actions.insert(0, safety_action)
        
        return response
    
    def _get_category_specific_actions(self, category) -> Dict[str, List[str]]:
        """Get category-specific response actions."""
        
        from ..core.state import IncidentCategory
        
        category_actions = {
            IncidentCategory.GUEST_ACCESS: {
                "immediate": [
                    "Verify current guest access status and disable if necessary",
                    "Check security footage for unauthorized access patterns"
                ],
                "investigation": [
                    "Review guest checkout procedures and timing",
                    "Analyze access control logs for the affected period",
                    "Interview housekeeping and front desk staff"
                ],
                "containment": [
                    "Update access control systems to prevent further unauthorized access",
                    "Implement additional verification procedures for checkout process"
                ],
                "notification": [
                    "Notify front office manager and housekeeping supervisor",
                    "Inform affected guests if privacy may have been compromised"
                ],
                "documentation": [
                    "Document access control system logs and configurations",
                    "Record guest interaction history and checkout procedures"
                ],
                "followup": [
                    "Review and update guest access policies",
                    "Provide additional training to front desk staff"
                ]
            },
            
            IncidentCategory.PAYMENT_FRAUD: {
                "immediate": [
                    "Isolate affected payment processing systems",
                    "Notify payment processor and card brands",
                    "Preserve transaction logs and evidence"
                ],
                "investigation": [
                    "Analyze transaction patterns for fraud indicators",
                    "Review POS system security and access logs",
                    "Coordinate with payment processor fraud team"
                ],
                "containment": [
                    "Implement additional payment verification controls",
                    "Enhance monitoring of payment transactions"
                ],
                "notification": [
                    "Notify affected customers of potential fraud",
                    "Submit required reports to card brands and regulators"
                ],
                "documentation": [
                    "Document all fraudulent transactions and patterns",
                    "Maintain detailed forensic evidence logs"
                ],
                "followup": [
                    "Implement enhanced fraud detection measures",
                    "Review and update payment security procedures"
                ]
            },
            
            IncidentCategory.PII_BREACH: {
                "immediate": [
                    "Contain the data exposure and prevent further access",
                    "Notify privacy officer and legal team",
                    "Preserve forensic evidence of the breach"
                ],
                "investigation": [
                    "Conduct detailed impact assessment of exposed data",
                    "Determine root cause and attack vectors",
                    "Analyze scope of affected individuals"
                ],
                "containment": [
                    "Implement additional data access controls",
                    "Enhance data encryption and protection measures"
                ],
                "notification": [
                    "Prepare breach notifications for affected individuals",
                    "Submit required regulatory notifications"
                ],
                "documentation": [
                    "Document all exposed data types and individuals affected",
                    "Maintain comprehensive breach response documentation"
                ],
                "followup": [
                    "Implement data protection improvements",
                    "Conduct privacy training for relevant staff"
                ]
            },
            
            IncidentCategory.CYBER_SECURITY: {
                "immediate": [
                    "Isolate affected systems from network",
                    "Activate cyber security incident response team",
                    "Begin forensic evidence collection"
                ],
                "investigation": [
                    "Conduct detailed malware and threat analysis",
                    "Analyze attack vectors and system vulnerabilities",
                    "Determine scope of system compromise"
                ],
                "containment": [
                    "Implement network segmentation and access controls",
                    "Deploy additional security monitoring tools"
                ],
                "notification": [
                    "Notify IT security team and management",
                    "Coordinate with external cyber security experts if needed"
                ],
                "documentation": [
                    "Document attack timeline and system impacts",
                    "Maintain detailed forensic analysis reports"
                ],
                "followup": [
                    "Implement security patches and updates",
                    "Conduct security awareness training"
                ]
            }
        }
        
        return category_actions.get(category, {
            "immediate": ["Assess immediate security risks"],
            "investigation": ["Conduct standard security investigation"],
            "containment": ["Implement appropriate containment measures"],
            "notification": ["Notify relevant stakeholders"],
            "documentation": ["Document incident details and response"],
            "followup": ["Review and improve security procedures"]
        })
    
    def _generate_fallback_response(self, incident_state: IncidentState, error: str) -> IncidentResponse:
        """Generate fallback response when LLM parsing fails."""
        
        # Create basic response based on incident characteristics
        immediate_actions = [
            "Assess immediate security risks and threats",
            "Notify security team and management",
            "Preserve any available evidence"
        ]
        
        investigation_steps = [
            "Conduct preliminary incident investigation",
            "Gather additional details and evidence",
            "Analyze incident scope and impact"
        ]
        
        containment_measures = [
            "Implement basic security containment measures",
            "Monitor for additional threats or incidents"
        ]
        
        notification_requirements = [
            "Notify security manager and operations team",
            "Prepare stakeholder communications as needed"
        ]
        
        documentation_requirements = [
            "Document all incident details and timeline",
            "Record response actions taken",
            f"Note: Response generation error - {error}"
        ]
        
        follow_up_actions = [
            "Conduct post-incident review",
            "Implement lessons learned",
            "Update security procedures as needed"
        ]
        
        # Enhance based on priority
        if incident_state.severity and incident_state.severity.value in ["critical", "high"]:
            immediate_actions.insert(0, "URGENT: Executive notification required immediately")
            notification_requirements.insert(0, "Immediate escalation to executive team")
        
        return IncidentResponse(
            immediate_actions=immediate_actions,
            investigation_steps=investigation_steps,
            containment_measures=containment_measures,
            notification_requirements=notification_requirements,
            documentation_requirements=documentation_requirements,
            follow_up_actions=follow_up_actions
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.generate_response(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.generate_response(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)