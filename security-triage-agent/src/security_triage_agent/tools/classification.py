"""
Incident Classification Tool for Security Triage Agent.

Provides AI-powered classification of security incidents into hospitality-specific
categories with confidence scoring and detailed reasoning.
"""

import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..core.state import IncidentCategory, IncidentMetadata


class ClassificationResult(BaseModel):
    """Result of incident classification."""
    category: IncidentCategory
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    alternative_categories: List[IncidentCategory] = Field(default_factory=list)
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    severity_indicators: List[str] = Field(default_factory=list)


class IncidentClassifier(BaseTool):
    """
    AI-powered incident classification tool for hospitality security scenarios.
    
    Uses advanced prompting techniques to accurately categorize security incidents
    with proper context understanding and hospitality domain expertise.
    """
    
    name: str = "incident_classifier"
    description: str = "Classify security incidents into hospitality-specific categories"
    
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
        
        self.classification_prompt = self._create_classification_prompt()
    
    def _create_classification_prompt(self) -> ChatPromptTemplate:
        """Create the classification prompt with hospitality security expertise."""
        
        system_message = """You are an expert security analyst specializing in hospitality and hotel security incidents. Your role is to accurately classify security incidents into specific categories based on hospitality industry context.

INCIDENT CATEGORIES:
1. GUEST_ACCESS - Unauthorized guest access issues
   - Guest accessing rooms after checkout
   - Unauthorized use of guest credentials
   - Bypassing access controls in guest areas
   - Misuse of guest privileges

2. PAYMENT_FRAUD - Payment and billing fraud incidents
   - Credit card fraud in hotel transactions
   - Billing discrepancies and manipulation
   - Fraudulent charge disputes
   - POS system compromise

3. PII_BREACH - Personal identifiable information breaches
   - Guest data exposure or theft
   - Employee personal data compromise
   - Unauthorized access to guest records
   - Data leakage from hotel systems

4. OPERATIONAL_SECURITY - Operational security violations
   - Staff security policy violations
   - Unauthorized access to restricted areas
   - Security procedure non-compliance
   - Operational control failures

5. VENDOR_ACCESS - Vendor and contractor access issues
   - Unauthorized vendor access
   - Contractor security violations
   - Third-party system compromise
   - Vendor credential misuse

6. PHYSICAL_SECURITY - Physical security breaches
   - Unauthorized building access
   - Security system failures
   - Physical asset theft or damage
   - Perimeter security violations

7. CYBER_SECURITY - Cybersecurity incidents
   - Network intrusions
   - Malware or ransomware attacks
   - System compromises
   - Cyber threats to hotel infrastructure

8. COMPLIANCE_VIOLATION - Regulatory compliance issues
   - Data protection law violations
   - Industry standard non-compliance
   - Audit finding remediation
   - Regulatory reporting requirements

CLASSIFICATION PROCESS:
1. Analyze the incident title and description
2. Identify key security indicators and hospitality context
3. Consider the primary impact and affected systems
4. Determine the most appropriate category
5. Assess confidence level based on available information
6. Extract relevant entities (guest IDs, room numbers, systems, etc.)
7. Identify severity indicators

RESPONSE FORMAT:
Respond with a JSON object containing:
- category: The primary incident category
- confidence: Confidence score (0.0 to 1.0)
- reasoning: Detailed explanation for the classification
- alternative_categories: List of other possible categories
- extracted_entities: Relevant entities found in the incident
- severity_indicators: Factors that indicate incident severity

Consider hospitality-specific context:
- Guest privacy and safety implications
- Business operations impact
- Regulatory compliance requirements
- Reputation and brand protection
- Revenue and financial impact"""

        human_message = """Classify this security incident:

TITLE: {title}
DESCRIPTION: {description}

ADDITIONAL CONTEXT:
{metadata_context}

Provide detailed classification analysis in JSON format."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    async def classify(
        self,
        title: str,
        description: str,
        metadata: Optional[IncidentMetadata] = None
    ) -> ClassificationResult:
        """
        Classify a security incident.
        
        Args:
            title: Incident title
            description: Detailed incident description
            metadata: Additional incident metadata
            
        Returns:
            ClassificationResult with category, confidence, and reasoning
        """
        
        # Prepare metadata context
        metadata_context = "None provided"
        if metadata:
            context_parts = []
            if metadata.location:
                context_parts.append(f"Location: {metadata.location}")
            if metadata.property_code:
                context_parts.append(f"Property: {metadata.property_code}")
            if metadata.affected_systems:
                context_parts.append(f"Affected Systems: {', '.join(metadata.affected_systems)}")
            if metadata.affected_guests:
                context_parts.append(f"Affected Guests: {len(metadata.affected_guests)} guests")
            if metadata.reporting_system:
                context_parts.append(f"Reported by: {metadata.reporting_system}")
            
            if context_parts:
                metadata_context = "\n".join(context_parts)
        
        # Format the prompt
        formatted_prompt = self.classification_prompt.format_messages(
            title=title,
            description=description,
            metadata_context=metadata_context
        )
        
        # Get classification from LLM
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            # Parse JSON response
            if hasattr(response, 'content'):
                result_data = json.loads(response.content)
            else:
                result_data = json.loads(str(response))
            
            # Validate and create result
            category = IncidentCategory(result_data["category"].lower())
            confidence = max(0.0, min(1.0, float(result_data["confidence"])))
            
            # Parse alternative categories
            alternative_categories = []
            for alt_cat in result_data.get("alternative_categories", []):
                try:
                    alternative_categories.append(IncidentCategory(alt_cat.lower()))
                except ValueError:
                    continue  # Skip invalid categories
            
            return ClassificationResult(
                category=category,
                confidence=confidence,
                reasoning=result_data.get("reasoning", "No reasoning provided"),
                alternative_categories=alternative_categories,
                extracted_entities=result_data.get("extracted_entities", {}),
                severity_indicators=result_data.get("severity_indicators", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback classification
            return self._fallback_classification(title, description, str(e))
    
    def _fallback_classification(
        self, 
        title: str, 
        description: str, 
        error: str
    ) -> ClassificationResult:
        """
        Provide fallback classification when LLM parsing fails.
        Uses keyword-based heuristics for basic classification.
        """
        
        text = f"{title} {description}".lower()
        
        # Keyword-based classification heuristics
        classification_keywords = {
            IncidentCategory.GUEST_ACCESS: [
                "guest", "room", "checkout", "access", "key", "door", "unauthorized entry"
            ],
            IncidentCategory.PAYMENT_FRAUD: [
                "payment", "credit card", "fraud", "billing", "transaction", "pos", "charge"
            ],
            IncidentCategory.PII_BREACH: [
                "personal", "data", "privacy", "guest information", "leak", "exposure", "pii"
            ],
            IncidentCategory.OPERATIONAL_SECURITY: [
                "staff", "employee", "procedure", "policy", "operation", "training"
            ],
            IncidentCategory.VENDOR_ACCESS: [
                "vendor", "contractor", "third party", "supplier", "external"
            ],
            IncidentCategory.PHYSICAL_SECURITY: [
                "physical", "building", "security camera", "alarm", "theft", "break-in"
            ],
            IncidentCategory.CYBER_SECURITY: [
                "cyber", "network", "malware", "hacking", "system", "computer", "virus"
            ],
            IncidentCategory.COMPLIANCE_VIOLATION: [
                "compliance", "regulation", "audit", "law", "violation", "policy breach"
            ]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in classification_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Select best match or default
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(0.8, category_scores[best_category] / 10.0)
        else:
            best_category = IncidentCategory.OPERATIONAL_SECURITY
            confidence = 0.3
        
        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            reasoning=f"Fallback classification due to parsing error: {error}. "
                     f"Used keyword-based heuristics.",
            alternative_categories=[],
            extracted_entities={},
            severity_indicators=["parsing_error", "fallback_classification"]
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous tool interface (required by BaseTool)."""
        import asyncio
        result = asyncio.run(self.classify(*args, **kwargs))
        return json.dumps(result.dict(), indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous tool interface."""
        result = await self.classify(*args, **kwargs)
        return json.dumps(result.dict(), indent=2)