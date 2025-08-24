"""
RAG-powered Hotel Policy Knowledge Base for Agentic Security Operations

This module implements a Retrieval-Augmented Generation system that provides
the security agent with real-time access to hotel policies, procedures, and
compliance guidelines for informed decision-making.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class PolicyDocument(BaseModel):
    """Hotel policy document model"""
    document_id: str
    title: str
    category: str
    content: str
    version: str
    effective_date: datetime
    last_updated: datetime
    compliance_level: str  # mandatory, recommended, optional
    applicable_properties: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class KnowledgeQuery(BaseModel):
    """Knowledge base query model"""
    query_text: str
    incident_type: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = None
    property_code: Optional[str] = None
    max_results: int = 5
    similarity_threshold: float = 0.7


class PolicyRetrievalResult(BaseModel):
    """Result of policy retrieval"""
    documents: List[Dict[str, Any]]
    query: str
    retrieval_metadata: Dict[str, Any]
    timestamp: datetime


class HotelPolicyKnowledgeBase:
    """
    RAG-powered knowledge base for hotel security policies and procedures.
    
    Provides contextual policy retrieval for autonomous decision-making in
    security incident response scenarios.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 vector_store_path: str = "./knowledge_base_store",
                 embedding_model: str = "text-embedding-ada-002"):
        
        self.logger = logging.getLogger(__name__)
        self.vector_store_path = vector_store_path
        
        # Initialize embeddings and LLM
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model=embedding_model
        )
        
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.0
        )
        
        # Initialize text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize or load vector store
        self.vector_store = None
        self.retriever = None
        self._initialize_vector_store()
        
        # Load hotel policies if not already loaded
        self._load_default_policies()
    
    def _initialize_vector_store(self):
        """Initialize the vector store for policy documents"""
        try:
            if os.path.exists(self.vector_store_path):
                # Load existing vector store
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
                self.logger.info("Loaded existing vector store")
            else:
                # Create new vector store
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
                self.logger.info("Created new vector store")
            
            # Set up the retriever with compression
            base_retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 10}
            )
            
            # Add contextual compression for better results
            compressor = LLMChainExtractor.from_llm(self.llm)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _load_default_policies(self):
        """Load default hotel security policies into the knowledge base"""
        
        default_policies = self._get_default_policy_documents()
        
        # Check if policies are already loaded
        if self.vector_store._collection.count() > 0:
            self.logger.info(f"Knowledge base already contains {self.vector_store._collection.count()} documents")
            return
        
        # Load policies into vector store
        documents = []
        for policy in default_policies:
            # Split policy content into chunks
            chunks = self.text_splitter.split_text(policy.content)
            
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "document_id": policy.document_id,
                        "title": policy.title,
                        "category": policy.category,
                        "version": policy.version,
                        "compliance_level": policy.compliance_level,
                        "applicable_properties": policy.applicable_properties,
                        "tags": policy.tags,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)
        
        # Add documents to vector store
        if documents:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            
            self.logger.info(f"Loaded {len(documents)} policy document chunks into knowledge base")
    
    async def query_policies(self, query: KnowledgeQuery) -> PolicyRetrievalResult:
        """
        Query the knowledge base for relevant policies and procedures.
        
        Args:
            query: Knowledge query with context and filters
            
        Returns:
            PolicyRetrievalResult with relevant policy documents
        """
        
        try:
            # Enhance query with context
            enhanced_query = self._enhance_query_context(query)
            
            # Retrieve relevant documents
            documents = await self._retrieve_documents(enhanced_query, query.max_results)
            
            # Filter by similarity threshold
            filtered_docs = [
                doc for doc in documents 
                if self._calculate_relevance_score(doc, query.query_text) >= query.similarity_threshold
            ]
            
            # Prepare retrieval metadata
            retrieval_metadata = {
                "original_query": query.query_text,
                "enhanced_query": enhanced_query,
                "total_candidates": len(documents),
                "filtered_results": len(filtered_docs),
                "similarity_threshold": query.similarity_threshold,
                "retrieval_method": "contextual_compression"
            }
            
            # Format results
            formatted_docs = []
            for doc in filtered_docs:
                formatted_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": self._calculate_relevance_score(doc, query.query_text)
                })
            
            self.logger.info(f"Retrieved {len(formatted_docs)} relevant policy documents")
            
            return PolicyRetrievalResult(
                documents=formatted_docs,
                query=enhanced_query,
                retrieval_metadata=retrieval_metadata,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Policy query failed: {e}")
            # Return empty result on failure
            return PolicyRetrievalResult(
                documents=[],
                query=query.query_text,
                retrieval_metadata={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    async def get_compliance_requirements(self, incident_type: str, location: str) -> Dict[str, Any]:
        """
        Get specific compliance requirements for an incident type and location.
        
        Args:
            incident_type: Type of security incident
            location: Incident location
            
        Returns:
            Dictionary with compliance requirements and procedures
        """
        
        compliance_query = KnowledgeQuery(
            query_text=f"compliance requirements procedures {incident_type} {location}",
            incident_type=incident_type,
            location=location,
            max_results=3
        )
        
        result = await self.query_policies(compliance_query)
        
        # Extract compliance-specific information
        compliance_info = {
            "mandatory_actions": [],
            "reporting_requirements": [],
            "timeline_constraints": [],
            "documentation_needed": [],
            "notification_requirements": []
        }
        
        for doc in result.documents:
            content = doc["content"].lower()
            
            # Extract mandatory actions
            if "mandatory" in content or "required" in content:
                compliance_info["mandatory_actions"].append({
                    "action": doc["content"],
                    "source": doc["metadata"]["title"],
                    "compliance_level": doc["metadata"]["compliance_level"]
                })
            
            # Extract reporting requirements
            if "report" in content or "notify" in content:
                compliance_info["reporting_requirements"].append({
                    "requirement": doc["content"],
                    "source": doc["metadata"]["title"]
                })
            
            # Extract timeline information
            if "hour" in content or "day" in content or "immediate" in content:
                compliance_info["timeline_constraints"].append({
                    "constraint": doc["content"],
                    "source": doc["metadata"]["title"]
                })
        
        return compliance_info
    
    async def get_escalation_procedures(self, incident_priority: str, incident_type: str) -> Dict[str, Any]:
        """
        Get escalation procedures for specific incident types and priorities.
        
        Args:
            incident_priority: Priority level (low, medium, high, critical)
            incident_type: Type of security incident
            
        Returns:
            Dictionary with escalation procedures and contact information
        """
        
        escalation_query = KnowledgeQuery(
            query_text=f"escalation procedures {incident_priority} {incident_type} management contacts",
            incident_type=incident_type,
            priority=incident_priority,
            max_results=3
        )
        
        result = await self.query_policies(escalation_query)
        
        escalation_info = {
            "escalation_levels": [],
            "contact_hierarchy": [],
            "escalation_triggers": [],
            "time_thresholds": []
        }
        
        for doc in result.documents:
            escalation_info["escalation_levels"].append({
                "procedure": doc["content"],
                "source": doc["metadata"]["title"],
                "applicable_priority": incident_priority
            })
        
        return escalation_info
    
    def _enhance_query_context(self, query: KnowledgeQuery) -> str:
        """Enhance the query with additional context"""
        
        enhanced_parts = [query.query_text]
        
        if query.incident_type:
            enhanced_parts.append(f"incident type: {query.incident_type}")
        
        if query.location:
            enhanced_parts.append(f"location: {query.location}")
        
        if query.priority:
            enhanced_parts.append(f"priority: {query.priority}")
        
        if query.property_code:
            enhanced_parts.append(f"property: {query.property_code}")
        
        return " ".join(enhanced_parts)
    
    async def _retrieve_documents(self, query: str, max_results: int) -> List[Document]:
        """Retrieve documents using the contextual compression retriever"""
        
        try:
            # Use the compressed retriever for better results
            documents = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.retriever.get_relevant_documents(query)
            )
            
            return documents[:max_results]
            
        except Exception as e:
            self.logger.error(f"Document retrieval failed: {e}")
            return []
    
    def _calculate_relevance_score(self, document: Document, query: str) -> float:
        """Calculate relevance score for a document (simplified implementation)"""
        
        # Simple keyword-based relevance scoring
        # In production, this would use more sophisticated similarity metrics
        
        doc_content = document.page_content.lower()
        query_terms = query.lower().split()
        
        matches = sum(1 for term in query_terms if term in doc_content)
        score = matches / len(query_terms) if query_terms else 0
        
        # Boost score for high-compliance documents
        if document.metadata.get("compliance_level") == "mandatory":
            score *= 1.2
        
        return min(score, 1.0)
    
    def _get_default_policy_documents(self) -> List[PolicyDocument]:
        """Get default hotel security policy documents"""
        
        return [
            PolicyDocument(
                document_id="SEC-POL-001",
                title="Unauthorized Access Response Procedures",
                category="Access Control",
                content="""
                UNAUTHORIZED ACCESS INCIDENT RESPONSE PROCEDURES
                
                IMMEDIATE ACTIONS (within 5 minutes):
                1. Revoke all access credentials associated with the incident
                2. Update room status to "Security Hold" in PMS system
                3. Notify Security Manager immediately via SMS/phone
                4. Document all actions taken with timestamps
                
                INVESTIGATION PROCEDURES:
                1. Review access logs for 48-hour period before incident
                2. Check guest checkout status and payment completion
                3. Verify identity of person involved in incident
                4. Interview relevant staff members (housekeeping, front desk)
                
                COMPLIANCE REQUIREMENTS:
                - All actions must be documented within 1 hour
                - Guest privacy must be maintained throughout investigation
                - Incident report must be filed within 24 hours
                - Management notification required for all unauthorized access incidents
                
                ESCALATION TRIGGERS:
                - VIP guest involvement: Immediate GM notification
                - Multiple room involvement: Regional Security Manager
                - Media attention potential: Corporate Communications
                - Legal implications: Legal Counsel within 2 hours
                """,
                version="2.1",
                effective_date=datetime(2024, 1, 1),
                last_updated=datetime(2024, 1, 15),
                compliance_level="mandatory",
                applicable_properties=["all"],
                tags=["access_control", "unauthorized_access", "security_response"]
            ),
            
            PolicyDocument(
                document_id="SEC-POL-002", 
                title="Payment Fraud Detection and Response",
                category="Financial Security",
                content="""
                PAYMENT FRAUD INCIDENT RESPONSE PROCEDURES
                
                FRAUD DETECTION CRITERIA:
                1. Multiple payment failures (>3) within 30 minutes
                2. Payments from different countries within 24 hours
                3. Unusual payment amounts (>$10,000 or <$1)
                4. Mismatched billing and guest information
                5. Use of flagged IP addresses or VPN services
                
                IMMEDIATE RESPONSE (within 2 minutes):
                1. Block suspicious payment methods immediately
                2. Flag guest account for manual verification
                3. Notify Finance Manager and Security Manager
                4. Generate fraud alert report with transaction details
                
                INVESTIGATION PROCEDURES:
                1. Verify guest identity through secondary authentication
                2. Contact card issuing bank if necessary
                3. Review previous stays and payment history
                4. Check for patterns across other bookings
                
                COMPLIANCE REQUIREMENTS:
                - PCI DSS compliance must be maintained throughout
                - All payment data handling follows PCI guidelines
                - Incident must be reported to payment processor within 4 hours
                - Regulatory notification required for losses >$5,000
                
                CUSTOMER COMMUNICATION:
                - Explain security measures are for their protection
                - Provide alternative payment methods if legitimate
                - Apologize for any inconvenience caused
                - Follow up within 24 hours to ensure resolution
                """,
                version="1.8",
                effective_date=datetime(2024, 1, 1),
                last_updated=datetime(2024, 1, 20),
                compliance_level="mandatory",
                applicable_properties=["all"],
                tags=["payment_fraud", "financial_security", "pci_compliance"]
            ),
            
            PolicyDocument(
                document_id="SEC-POL-003",
                title="Data Privacy Breach Response Protocol",
                category="Data Protection",
                content="""
                DATA PRIVACY BREACH RESPONSE PROTOCOL
                
                BREACH CLASSIFICATION:
                Level 1: Potential exposure of <100 guest records
                Level 2: Exposure of 100-1000 guest records  
                Level 3: Exposure of >1000 guest records or payment data
                Level 4: Exposure with external threat actor involvement
                
                IMMEDIATE CONTAINMENT (within 30 minutes):
                1. Isolate affected systems to prevent further exposure
                2. Preserve evidence for forensic analysis
                3. Notify Data Protection Officer immediately
                4. Begin incident documentation and timeline
                
                ASSESSMENT PROCEDURES:
                1. Determine scope and scale of potential exposure
                2. Identify types of personal data potentially affected
                3. Assess risk to affected individuals
                4. Evaluate likelihood of harm or misuse
                
                REGULATORY COMPLIANCE:
                - DPDP Act notification required within 72 hours for high-risk breaches
                - Individual notification within 72 hours if high risk to rights
                - Credit monitoring services for payment data exposure
                - Regulatory authority cooperation fully required
                
                COMMUNICATION PROTOCOL:
                Internal: Legal, IT Security, Senior Management, PR
                External: Regulatory authorities, affected guests, media (if required)
                
                REMEDIATION STEPS:
                1. Fix security vulnerabilities that caused breach
                2. Enhance monitoring and detection capabilities
                3. Provide additional staff training on data protection
                4. Review and update data handling procedures
                """,
                version="3.2",
                effective_date=datetime(2024, 1, 1),
                last_updated=datetime(2024, 1, 25),
                compliance_level="mandatory",
                applicable_properties=["all"],
                tags=["data_breach", "privacy", "dpdp_compliance", "notification"]
            ),
            
            PolicyDocument(
                document_id="SEC-POL-004",
                title="Physical Security Incident Management",
                category="Physical Security",
                content="""
                PHYSICAL SECURITY INCIDENT MANAGEMENT
                
                INCIDENT CATEGORIES:
                1. Unauthorized area access
                2. Suspicious activity or persons
                3. Theft or property damage
                4. Emergency situations (medical, fire, etc.)
                5. Workplace violence or threats
                
                RESPONSE PRIORITIES:
                1. Ensure guest and staff safety
                2. Secure the affected area
                3. Preserve evidence
                4. Coordinate with appropriate authorities
                5. Maintain business continuity
                
                IMMEDIATE ACTIONS:
                1. Assess immediate threat level
                2. Deploy security personnel to scene
                3. Activate surveillance systems
                4. Coordinate with local emergency services if needed
                5. Notify management based on severity
                
                AREA-SPECIFIC PROCEDURES:
                Guest Rooms: Ensure guest privacy, coordinate with housekeeping
                Public Areas: Manage guest communications, maintain calm environment
                Restricted Areas: Immediate lockdown, access log review
                Parking Areas: Coordinate with valet services, check vehicle security
                
                DOCUMENTATION REQUIREMENTS:
                1. Incident report within 2 hours
                2. Photo/video evidence collection
                3. Witness statement collection
                4. Timeline of all actions taken
                5. Follow-up action plan
                
                ESCALATION MATRIX:
                Low Risk: Security Supervisor + Duty Manager
                Medium Risk: Security Manager + Department Head + GM
                High Risk: Security Manager + GM + Regional Security
                Critical: All above + Corporate Security + Legal + PR
                """,
                version="2.5",
                effective_date=datetime(2024, 1, 1),
                last_updated=datetime(2024, 1, 18),
                compliance_level="mandatory",
                applicable_properties=["all"],
                tags=["physical_security", "incident_response", "emergency_procedures"]
            ),
            
            PolicyDocument(
                document_id="SEC-POL-005",
                title="Guest Communication During Security Incidents",
                category="Guest Relations",
                content="""
                GUEST COMMUNICATION PROTOCOL FOR SECURITY INCIDENTS
                
                COMMUNICATION PRINCIPLES:
                1. Transparency with appropriate discretion
                2. Prompt and proactive communication
                3. Empathy and understanding
                4. Professional and reassuring tone
                5. Privacy protection for all guests
                
                INCIDENT-SPECIFIC MESSAGING:
                
                Access Control Issues:
                "We have temporarily updated your room access as a security precaution. Our team will assist you with re-entry. We apologize for any inconvenience."
                
                Payment Security:
                "Our security systems have flagged unusual payment activity. This is a protective measure. Please contact our front desk to verify your payment method."
                
                Data Privacy Concerns:
                "We are investigating a potential security matter that may have affected guest information. We will contact you directly with specific details if your information was involved."
                
                Physical Security Events:
                "We are addressing a security matter in your area. For your safety, please remain in your room/follow staff instructions. We will update you shortly."
                
                COMMUNICATION CHANNELS:
                In-Person: For immediate, sensitive matters
                Phone: For urgent notifications requiring response
                SMS: For quick updates and non-sensitive alerts  
                Email: For detailed explanations and follow-up
                In-Room Messages: For non-urgent notifications
                
                TIMING GUIDELINES:
                Immediate (0-15 minutes): Safety-related communications
                Short-term (15-60 minutes): Service impact notifications
                Follow-up (1-24 hours): Resolution updates and status
                Post-incident (24-72 hours): Summary and preventive measures
                
                VIP GUEST PROTOCOL:
                - Personal notification by GM or senior manager
                - Dedicated concierge support during incident
                - Enhanced privacy protection measures
                - Premium amenities as service recovery
                """,
                version="1.4",
                effective_date=datetime(2024, 1, 1),
                last_updated=datetime(2024, 1, 22),
                compliance_level="recommended",
                applicable_properties=["all"],
                tags=["guest_communication", "customer_service", "incident_management"]
            )
        ]


# Factory function for easy initialization
async def create_hotel_knowledge_base(openai_api_key: str) -> HotelPolicyKnowledgeBase:
    """Create and initialize the hotel policy knowledge base"""
    
    knowledge_base = HotelPolicyKnowledgeBase(openai_api_key=openai_api_key)
    
    return knowledge_base