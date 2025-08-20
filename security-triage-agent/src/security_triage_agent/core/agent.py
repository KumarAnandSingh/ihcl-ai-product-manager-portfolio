"""
Main Security Incident Triage Agent Implementation.

Production-ready agent that orchestrates the complete incident triage workflow
with proper error handling, monitoring, and hospitality industry best practices.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite import SqliteSaver

from .state import IncidentState, IncidentCategory, IncidentPriority
from .workflow import create_triage_workflow
from ..tools import (
    IncidentClassifier, IncidentPrioritizer, PlaybookSelector,
    ResponseGenerator, ComplianceChecker, SafetyGuardrails
)
from ..memory import SessionManager, PersistentStorage, MemoryRetriever
from ..evaluation import MetricsTracker, IncidentEvaluator, HospitalityBenchmarks
from ..utils.config import SecurityTriageConfig
from ..utils.logger import setup_logger


class SecurityTriageAgent:
    """
    Production-ready Security Incident Triage Agent for hospitality environments.
    
    Provides comprehensive incident processing with AI-powered analysis,
    automated response generation, and human-in-the-loop capabilities.
    """
    
    def __init__(
        self,
        config: Optional[SecurityTriageConfig] = None,
        llm_model: str = "gpt-4",
        temperature: float = 0.1
    ):
        """
        Initialize the Security Triage Agent.
        
        Args:
            config: Configuration object
            llm_model: LLM model to use
            temperature: LLM temperature setting
        """
        
        self.config = config or SecurityTriageConfig()
        self.logger = setup_logger("security_triage_agent", self.config.log_level)
        
        # Initialize LLM
        self.llm = self._initialize_llm(llm_model, temperature)
        
        # Initialize storage systems
        self.persistent_storage = PersistentStorage(self.config.database_path)
        self.session_manager = SessionManager(
            redis_url=self.config.redis_url,
            session_ttl_hours=self.config.session_ttl_hours
        )
        
        # Initialize memory and evaluation systems
        self.memory_retriever = MemoryRetriever(self.persistent_storage)
        self.metrics_tracker = MetricsTracker(self.persistent_storage)
        self.evaluator = IncidentEvaluator(self.metrics_tracker)
        self.benchmarks = HospitalityBenchmarks()
        
        # Initialize tools
        self.classifier = IncidentClassifier(self.llm, temperature=temperature)
        self.prioritizer = IncidentPrioritizer(self.llm, temperature=temperature)
        self.playbook_selector = PlaybookSelector(self.llm, temperature=temperature)
        self.response_generator = ResponseGenerator(self.llm, temperature=temperature)
        self.compliance_checker = ComplianceChecker(self.llm, temperature=temperature)
        self.safety_guardrails = SafetyGuardrails(self.llm, temperature=temperature)
        
        # Initialize workflow
        self.checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{self.config.checkpoint_db_path}")
        self.workflow = None
        
        # Agent state
        self.is_initialized = False
        self.active_incidents = {}
    
    async def initialize(self) -> None:
        """Initialize the agent and all subsystems."""
        try:
            self.logger.info("Initializing Security Triage Agent...")
            
            # Initialize storage systems
            await self.persistent_storage.initialize()
            await self.session_manager.initialize()
            
            # Create workflow
            self.workflow = create_triage_workflow(
                classifier=self.classifier,
                prioritizer=self.prioritizer,
                playbook_selector=self.playbook_selector,
                response_generator=self.response_generator,
                compliance_checker=self.compliance_checker,
                safety_guardrails=self.safety_guardrails,
                session_manager=self.session_manager,
                metrics_tracker=self.metrics_tracker,
                checkpointer=self.checkpointer
            )
            
            self.is_initialized = True
            self.logger.info("Security Triage Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def process_incident(
        self,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a security incident through the complete triage workflow.
        
        Args:
            title: Incident title
            description: Detailed incident description
            metadata: Additional incident metadata
            user_context: User context information
            
        Returns:
            Complete incident processing results
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        # Generate unique incident ID
        incident_id = f"inc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        
        try:
            self.logger.info(f"Processing incident {incident_id}: {title}")
            
            # Start metrics tracking
            await self.metrics_tracker.start_incident_tracking(incident_id)
            
            # Create session
            session_id = await self.session_manager.create_session(
                incident_id, user_context
            )
            
            # Get historical context
            historical_context = await self.memory_retriever.get_historical_context(
                title, description, metadata=metadata
            )
            
            # Create initial incident state
            incident_state = IncidentState(
                incident_id=incident_id,
                title=title,
                description=description,
                historical_context=historical_context.dict() if historical_context else {}
            )
            
            # Add metadata if provided
            if metadata:
                incident_state.metadata.location = metadata.get("location")
                incident_state.metadata.property_code = metadata.get("property_code")
                incident_state.metadata.affected_systems = metadata.get("affected_systems", [])
                incident_state.metadata.affected_guests = metadata.get("affected_guests", [])
                incident_state.metadata.affected_employees = metadata.get("affected_employees", [])
                incident_state.metadata.business_impact = metadata.get("business_impact")
                incident_state.metadata.estimated_cost = metadata.get("estimated_cost")
                incident_state.metadata.reporting_system = metadata.get("reporting_system")
                incident_state.metadata.reported_by = metadata.get("reported_by")
            
            # Store in active incidents
            self.active_incidents[incident_id] = incident_state
            
            # Process through workflow
            config = {"configurable": {"thread_id": incident_id}}
            
            final_state = None
            async for state_update in self.workflow.astream(incident_state, config):
                # Log workflow progress
                if "messages" in state_update:
                    latest_message = state_update["messages"][-1] if state_update["messages"] else None
                    if latest_message:
                        self.logger.debug(f"Workflow update for {incident_id}: {latest_message.content}")
                
                # Update stored state
                final_state = state_update
                self.active_incidents[incident_id] = final_state
                
                # Store workflow checkpoint
                await self.session_manager.store_workflow_checkpoint(
                    incident_id, final_state.get("current_step", "unknown"), state_update
                )
            
            # Final evaluation
            if final_state:
                incident_state = final_state
                
                # Calculate quality scores
                quality_scores = await self.metrics_tracker.calculate_quality_scores(incident_state)
                incident_state.quality_scores = quality_scores
                
                # Perform comprehensive evaluation
                evaluation_result = await self.evaluator.evaluate_incident(incident_state)
                
                # Store final incident state
                await self.persistent_storage.store_incident(incident_state)
                
                # Generate response summary
                response = self._generate_response_summary(
                    incident_state, evaluation_result, historical_context
                )
                
                self.logger.info(
                    f"Successfully processed incident {incident_id}. "
                    f"Quality score: {quality_scores.get('overall', 0):.2f}"
                )
                
                return response
            
            else:
                raise RuntimeError("Workflow did not produce final state")
                
        except Exception as e:
            self.logger.error(f"Error processing incident {incident_id}: {e}")
            
            # Record workflow error
            await self.metrics_tracker.record_workflow_error(
                incident_id, "process_incident", {"error": str(e)}
            )
            
            # Return error response
            return {
                "incident_id": incident_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        finally:
            # Clean up active incident
            if incident_id in self.active_incidents:
                del self.active_incidents[incident_id]
    
    async def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an incident.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Incident status information
        """
        
        # Check active incidents first
        if incident_id in self.active_incidents:
            state = self.active_incidents[incident_id]
            return {
                "incident_id": incident_id,
                "status": "processing",
                "current_step": state.current_step,
                "completed_steps": state.completed_steps,
                "requires_human_intervention": state.requires_human_intervention,
                "pending_approvals": len(state.pending_approvals),
                "updated_at": state.updated_at.isoformat()
            }
        
        # Check persistent storage
        incident_record = await self.persistent_storage.get_incident(incident_id)
        if incident_record:
            return {
                "incident_id": incident_id,
                "status": incident_record.status,
                "category": incident_record.category,
                "priority": incident_record.priority,
                "risk_score": incident_record.risk_score,
                "created_at": incident_record.created_at.isoformat(),
                "updated_at": incident_record.updated_at.isoformat(),
                "processing_time": incident_record.processing_time_seconds,
                "human_interventions": incident_record.human_interventions
            }
        
        return None
    
    async def approve_intervention(
        self,
        incident_id: str,
        intervention_type: str,
        approver: str,
        decision: bool,
        notes: str = ""
    ) -> bool:
        """
        Process human approval for intervention request.
        
        Args:
            incident_id: Incident identifier
            intervention_type: Type of intervention
            approver: Person providing approval
            decision: Approval decision
            notes: Additional notes
            
        Returns:
            Success status
        """
        
        if incident_id in self.active_incidents:
            state = self.active_incidents[incident_id]
            state.approve_intervention(intervention_type, approver, decision, notes)
            
            # Record intervention
            await self.metrics_tracker.record_human_intervention(
                incident_id, intervention_type, f"Approval: {decision}", None
            )
            
            self.logger.info(
                f"Intervention {intervention_type} for {incident_id} "
                f"{'approved' if decision else 'rejected'} by {approver}"
            )
            
            return True
        
        return False
    
    async def get_performance_dashboard(
        self,
        days: int = 7,
        category: Optional[IncidentCategory] = None
    ) -> Dict[str, Any]:
        """
        Get performance dashboard data.
        
        Args:
            days: Number of days to include
            category: Optional category filter
            
        Returns:
            Dashboard data
        """
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get performance metrics
        performance_metrics = await self.metrics_tracker.get_performance_summary(
            start_date, end_date
        )
        
        # Get quality metrics
        quality_metrics = await self.metrics_tracker.get_quality_summary(
            start_date, end_date
        )
        
        # Get hallucination metrics
        hallucination_metrics = await self.metrics_tracker.get_hallucination_summary(
            start_date, end_date
        )
        
        # Get incident analytics
        incident_analytics = await self.persistent_storage.get_incident_analytics(
            start_date, end_date, "daily"
        )
        
        # Benchmark comparison
        benchmark_metrics = {
            "automation_rate": performance_metrics.automation_rate,
            "escalation_rate": performance_metrics.escalation_rate,
            "first_time_resolution_rate": performance_metrics.first_time_resolution_rate,
            "response_completeness": quality_metrics.response_completeness,
            "compliance_score": quality_metrics.compliance_score,
            "safety_score": quality_metrics.safety_score
        }
        
        benchmark_report = self.benchmarks.generate_performance_report(
            benchmark_metrics, property_type="business_hotel", incident_category=category
        )
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "performance_metrics": performance_metrics.dict(),
            "quality_metrics": quality_metrics.dict(),
            "hallucination_metrics": hallucination_metrics.dict(),
            "incident_analytics": incident_analytics,
            "benchmark_comparison": benchmark_report,
            "active_incidents": len(self.active_incidents),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def search_incidents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search historical incidents.
        
        Args:
            filters: Search filters
            limit: Maximum results
            
        Returns:
            List of incident records
        """
        
        incident_records = await self.persistent_storage.search_incidents(
            filters=filters, limit=limit
        )
        
        return [
            {
                "incident_id": record.incident_id,
                "title": record.title,
                "category": record.category,
                "priority": record.priority,
                "status": record.status,
                "risk_score": record.risk_score,
                "created_at": record.created_at.isoformat(),
                "processing_time": record.processing_time_seconds,
                "human_interventions": record.human_interventions,
                "requires_followup": record.requires_followup
            }
            for record in incident_records
        ]
    
    async def cleanup(self) -> None:
        """Clean up agent resources and perform maintenance."""
        try:
            self.logger.info("Performing agent cleanup...")
            
            # Clean up old metrics
            metrics_cleaned = await self.metrics_tracker.cleanup_old_metrics()
            
            # Clean up old incident records
            records_cleaned = await self.persistent_storage.cleanup_old_records(
                retention_days=self.config.data_retention_days
            )
            
            # Clean up expired sessions
            sessions_cleaned = await self.session_manager.cleanup_expired_sessions()
            
            # Close connections
            await self.session_manager.close()
            
            self.logger.info(
                f"Cleanup completed: {metrics_cleaned} metrics, "
                f"{records_cleaned} records, {sessions_cleaned} sessions cleaned"
            )
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _initialize_llm(self, model_name: str, temperature: float):
        """Initialize the language model."""
        if "gpt" in model_name.lower():
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                model_kwargs={"response_format": {"type": "json_object"}}
            )
        elif "claude" in model_name.lower():
            return ChatAnthropic(
                model=model_name,
                temperature=temperature
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    def _generate_response_summary(
        self,
        incident_state: IncidentState,
        evaluation_result,
        historical_context
    ) -> Dict[str, Any]:
        """Generate comprehensive response summary."""
        
        # Basic incident information
        response = {
            "incident_id": incident_state.incident_id,
            "title": incident_state.title,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            
            # Classification results
            "classification": {
                "category": incident_state.category.value if incident_state.category else None,
                "priority": incident_state.severity.value if incident_state.severity else None,
                "confidence": incident_state.classification_confidence,
                "risk_score": incident_state.risk_assessment.risk_score if incident_state.risk_assessment else None
            },
            
            # Response plan
            "response_plan": None,
            
            # Quality and evaluation
            "quality_scores": incident_state.quality_scores,
            "evaluation": {
                "overall_score": evaluation_result.overall_score,
                "grade": evaluation_result.grade,
                "compliance_status": evaluation_result.compliance_status,
                "safety_status": evaluation_result.safety_status,
                "strengths": evaluation_result.strengths,
                "recommendations": evaluation_result.recommendations
            },
            
            # Processing metadata
            "processing": {
                "total_time_seconds": (incident_state.updated_at - incident_state.created_at).total_seconds(),
                "completed_steps": incident_state.completed_steps,
                "failed_steps": incident_state.failed_steps,
                "human_interventions": len(incident_state.approval_history),
                "tool_results": list(incident_state.tool_results.keys())
            },
            
            # Historical context
            "historical_insights": None
        }
        
        # Add response plan if available
        if incident_state.incident_response:
            response["response_plan"] = {
                "immediate_actions": incident_state.incident_response.immediate_actions,
                "investigation_steps": incident_state.incident_response.investigation_steps,
                "containment_measures": incident_state.incident_response.containment_measures,
                "notification_requirements": incident_state.incident_response.notification_requirements,
                "documentation_requirements": incident_state.incident_response.documentation_requirements,
                "follow_up_actions": incident_state.incident_response.follow_up_actions
            }
        
        # Add historical insights if available
        if historical_context:
            response["historical_insights"] = {
                "similar_incidents_found": len(historical_context.similar_incidents),
                "patterns_identified": len(historical_context.identified_patterns),
                "recommendations": historical_context.recommendations[:3],  # Top 3
                "success_metrics": historical_context.success_metrics
            }
        
        return response