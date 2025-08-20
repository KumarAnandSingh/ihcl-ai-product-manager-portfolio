"""
LangGraph workflow definition for Security Incident Triage Agent.

Implements the multi-step orchestration for incident processing with
proper state management, error handling, and human-in-the-loop gates.
"""

from typing import Dict, Any, Literal, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .state import IncidentState, IncidentPriority, IncidentCategory
from ..tools.classification import IncidentClassifier
from ..tools.prioritization import IncidentPrioritizer  
from ..tools.playbook_selector import PlaybookSelector
from ..tools.response_generator import ResponseGenerator
from ..tools.compliance_checker import ComplianceChecker
from ..tools.safety_guardrails import SafetyGuardrails
from ..memory.session_manager import SessionManager
from ..evaluation.metrics_tracker import MetricsTracker


class SecurityTriageWorkflow:
    """
    LangGraph workflow for security incident triage and response.
    
    Implements a comprehensive state machine for processing security incidents
    in hospitality environments with proper safety controls and compliance checks.
    """
    
    def __init__(
        self,
        classifier: IncidentClassifier,
        prioritizer: IncidentPrioritizer,
        playbook_selector: PlaybookSelector,
        response_generator: ResponseGenerator,
        compliance_checker: ComplianceChecker,
        safety_guardrails: SafetyGuardrails,
        session_manager: SessionManager,
        metrics_tracker: MetricsTracker,
        checkpointer: SqliteSaver = None
    ):
        self.classifier = classifier
        self.prioritizer = prioritizer
        self.playbook_selector = playbook_selector
        self.response_generator = response_generator
        self.compliance_checker = compliance_checker
        self.safety_guardrails = safety_guardrails
        self.session_manager = session_manager
        self.metrics_tracker = metrics_tracker
        self.checkpointer = checkpointer
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with all nodes and edges."""
        
        workflow = StateGraph(IncidentState)
        
        # Add workflow nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("classify_incident", self._classify_incident)
        workflow.add_node("assess_risk", self._assess_risk)
        workflow.add_node("safety_check", self._safety_check)
        workflow.add_node("prioritize_incident", self._prioritize_incident)
        workflow.add_node("select_playbook", self._select_playbook)
        workflow.add_node("compliance_check", self._compliance_check)
        workflow.add_node("human_approval_gate", self._human_approval_gate)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("execute_immediate_actions", self._execute_immediate_actions)
        workflow.add_node("document_incident", self._document_incident)
        workflow.add_node("notify_stakeholders", self._notify_stakeholders)
        workflow.add_node("schedule_followup", self._schedule_followup)
        workflow.add_node("update_metrics", self._update_metrics)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        # Define workflow edges with conditional routing
        workflow.add_edge("validate_input", "classify_incident")
        workflow.add_edge("classify_incident", "assess_risk")
        workflow.add_edge("assess_risk", "safety_check")
        
        # Safety check routing
        workflow.add_conditional_edges(
            "safety_check",
            self._safety_check_router,
            {
                "continue": "prioritize_incident",
                "reject": "handle_error",
                "human_review": "human_approval_gate"
            }
        )
        
        workflow.add_edge("prioritize_incident", "select_playbook")
        workflow.add_edge("select_playbook", "compliance_check")
        
        # Compliance check routing
        workflow.add_conditional_edges(
            "compliance_check",
            self._compliance_check_router,
            {
                "approved": "generate_response",
                "requires_approval": "human_approval_gate",
                "rejected": "handle_error"
            }
        )
        
        # Human approval gate routing
        workflow.add_conditional_edges(
            "human_approval_gate",
            self._human_approval_router,
            {
                "approved": "generate_response",
                "rejected": "handle_error",
                "pending": "human_approval_gate"  # Wait for approval
            }
        )
        
        workflow.add_edge("generate_response", "execute_immediate_actions")
        
        # Execution routing based on incident priority
        workflow.add_conditional_edges(
            "execute_immediate_actions",
            self._execution_router,
            {
                "document": "document_incident",
                "notify": "notify_stakeholders",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("document_incident", "notify_stakeholders")
        workflow.add_edge("notify_stakeholders", "schedule_followup")
        workflow.add_edge("schedule_followup", "update_metrics")
        workflow.add_edge("update_metrics", END)
        workflow.add_edge("handle_error", END)
        
        return workflow
    
    async def _validate_input(self, state: IncidentState) -> IncidentState:
        """Validate and sanitize input incident data."""
        try:
            state.update_step("validate_input")
            
            # Basic validation
            if not state.title or not state.description:
                raise ValueError("Incident must have title and description")
            
            # Sanitize input
            state.title = self.safety_guardrails.sanitize_text(state.title)
            state.description = self.safety_guardrails.sanitize_text(state.description)
            
            # Add system message
            state.add_message(
                SystemMessage(content="Security incident triage workflow initiated")
            )
            
            # Load session context
            session_context = await self.session_manager.get_session_context(state.incident_id)
            state.session_context.update(session_context)
            
            state.add_tool_result("input_validation", {"status": "passed"})
            
            return state
            
        except Exception as e:
            state.mark_step_failed("validate_input", str(e))
            raise
    
    async def _classify_incident(self, state: IncidentState) -> IncidentState:
        """Classify the incident using AI-powered classification tool."""
        try:
            state.update_step("classify_incident")
            
            classification_result = await self.classifier.classify(
                title=state.title,
                description=state.description,
                metadata=state.metadata
            )
            
            state.category = classification_result.category
            state.classification_confidence = classification_result.confidence
            state.add_tool_result("classification", classification_result.dict())
            
            # Add classification message
            state.add_message(
                AIMessage(content=f"Incident classified as: {state.category.value} "
                                f"(confidence: {state.classification_confidence:.2f})")
            )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("classify_incident", str(e))
            raise
    
    async def _assess_risk(self, state: IncidentState) -> IncidentState:
        """Assess risk level and potential impact."""
        try:
            state.update_step("assess_risk")
            
            risk_assessment = await self.prioritizer.assess_risk(
                category=state.category,
                description=state.description,
                metadata=state.metadata
            )
            
            state.risk_assessment = risk_assessment
            state.add_tool_result("risk_assessment", risk_assessment.dict())
            
            return state
            
        except Exception as e:
            state.mark_step_failed("assess_risk", str(e))
            raise
    
    async def _safety_check(self, state: IncidentState) -> IncidentState:
        """Perform safety guardrails check."""
        try:
            state.update_step("safety_check")
            
            safety_result = await self.safety_guardrails.check_safety(
                incident_description=state.description,
                category=state.category,
                risk_score=state.risk_assessment.risk_score if state.risk_assessment else 0.0
            )
            
            state.safety_guardrails_passed = safety_result.passed
            state.add_tool_result("safety_check", safety_result.dict())
            
            # Request human review for high-risk scenarios
            if safety_result.requires_human_review:
                state.request_human_intervention(
                    intervention_type="safety_review",
                    reason=safety_result.review_reason,
                    urgency=IncidentPriority.HIGH,
                    approver_role="security_manager"
                )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("safety_check", str(e))
            raise
    
    async def _prioritize_incident(self, state: IncidentState) -> IncidentState:
        """Prioritize the incident based on classification and risk assessment."""
        try:
            state.update_step("prioritize_incident")
            
            priority_result = await self.prioritizer.prioritize(
                category=state.category,
                risk_assessment=state.risk_assessment,
                metadata=state.metadata
            )
            
            state.severity = priority_result.priority
            state.add_tool_result("prioritization", priority_result.dict())
            
            state.add_message(
                AIMessage(content=f"Incident prioritized as: {state.severity.value}")
            )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("prioritize_incident", str(e))
            raise
    
    async def _select_playbook(self, state: IncidentState) -> IncidentState:
        """Select appropriate security playbook for incident response."""
        try:
            state.update_step("select_playbook")
            
            playbook_result = await self.playbook_selector.select_playbooks(
                category=state.category,
                priority=state.severity,
                risk_assessment=state.risk_assessment
            )
            
            state.applicable_playbooks = playbook_result.applicable_playbooks
            state.selected_playbook = playbook_result.recommended_playbook
            state.add_tool_result("playbook_selection", playbook_result.dict())
            
            return state
            
        except Exception as e:
            state.mark_step_failed("select_playbook", str(e))
            raise
    
    async def _compliance_check(self, state: IncidentState) -> IncidentState:
        """Check compliance requirements for the incident response."""
        try:
            state.update_step("compliance_check")
            
            compliance_result = await self.compliance_checker.check_compliance(
                category=state.category,
                playbook=state.selected_playbook,
                metadata=state.metadata
            )
            
            state.compliance_checks = compliance_result.framework_checks
            state.add_tool_result("compliance_check", compliance_result.dict())
            
            # Request approval for compliance-sensitive actions
            if compliance_result.requires_legal_review:
                state.request_human_intervention(
                    intervention_type="legal_review",
                    reason="Compliance requirements mandate legal review",
                    urgency=state.severity,
                    approver_role="legal_counsel",
                    timeout_minutes=240  # 4 hours for legal review
                )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("compliance_check", str(e))
            raise
    
    async def _human_approval_gate(self, state: IncidentState) -> IncidentState:
        """Handle human approval requirements."""
        try:
            state.update_step("human_approval_gate")
            
            # Check if there are pending approvals
            if state.pending_approvals:
                # In a real implementation, this would integrate with approval systems
                # For now, we'll simulate based on incident priority
                auto_approve_conditions = [
                    state.severity in [IncidentPriority.LOW, IncidentPriority.INFORMATIONAL],
                    len(state.pending_approvals) == 1 and state.pending_approvals[0].intervention_type == "safety_review"
                ]
                
                if any(auto_approve_conditions):
                    # Auto-approve low-risk scenarios
                    for approval in state.pending_approvals[:]:
                        state.approve_intervention(
                            intervention_type=approval.intervention_type,
                            approver="system_auto_approval",
                            decision=True,
                            notes="Auto-approved based on low risk assessment"
                        )
            
            state.add_tool_result("human_approval", {
                "pending_count": len(state.pending_approvals),
                "approval_history": state.approval_history
            })
            
            return state
            
        except Exception as e:
            state.mark_step_failed("human_approval_gate", str(e))
            raise
    
    async def _generate_response(self, state: IncidentState) -> IncidentState:
        """Generate structured incident response plan."""
        try:
            state.update_step("generate_response")
            
            response = await self.response_generator.generate_response(
                incident_state=state
            )
            
            state.incident_response = response
            state.add_tool_result("response_generation", response.dict())
            
            state.add_message(
                AIMessage(content=f"Incident response plan generated with "
                                f"{len(response.immediate_actions)} immediate actions")
            )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("generate_response", str(e))
            raise
    
    async def _execute_immediate_actions(self, state: IncidentState) -> IncidentState:
        """Execute immediate response actions."""
        try:
            state.update_step("execute_immediate_actions")
            
            executed_actions = []
            failed_actions = []
            
            if state.incident_response:
                for action in state.incident_response.immediate_actions:
                    try:
                        # In production, this would call specific action handlers
                        # For demo, we'll simulate action execution
                        action_result = await self._simulate_action_execution(action, state)
                        executed_actions.append({
                            "action": action,
                            "result": action_result,
                            "status": "completed"
                        })
                    except Exception as action_error:
                        failed_actions.append({
                            "action": action,
                            "error": str(action_error),
                            "status": "failed"
                        })
            
            state.add_tool_result("action_execution", {
                "executed": executed_actions,
                "failed": failed_actions
            })
            
            return state
            
        except Exception as e:
            state.mark_step_failed("execute_immediate_actions", str(e))
            raise
    
    async def _document_incident(self, state: IncidentState) -> IncidentState:
        """Document the incident and response for audit trail."""
        try:
            state.update_step("document_incident")
            
            # Store incident in persistent memory
            await self.session_manager.store_incident(state)
            
            # Update metrics
            await self.metrics_tracker.record_incident_processed(
                category=state.category,
                priority=state.severity,
                processing_time=(state.updated_at - state.created_at).total_seconds()
            )
            
            state.add_tool_result("documentation", {
                "incident_id": state.incident_id,
                "documented_at": state.updated_at.isoformat()
            })
            
            return state
            
        except Exception as e:
            state.mark_step_failed("document_incident", str(e))
            raise
    
    async def _notify_stakeholders(self, state: IncidentState) -> IncidentState:
        """Notify relevant stakeholders about the incident."""
        try:
            state.update_step("notify_stakeholders")
            
            notifications_sent = []
            
            if state.incident_response:
                for notification in state.incident_response.notification_requirements:
                    # In production, integrate with notification systems
                    notification_result = await self._simulate_notification(notification, state)
                    notifications_sent.append(notification_result)
            
            state.add_tool_result("notifications", {
                "sent": notifications_sent,
                "count": len(notifications_sent)
            })
            
            return state
            
        except Exception as e:
            state.mark_step_failed("notify_stakeholders", str(e))
            raise
    
    async def _schedule_followup(self, state: IncidentState) -> IncidentState:
        """Schedule follow-up actions and monitoring."""
        try:
            state.update_step("schedule_followup")
            
            followup_tasks = []
            
            if state.incident_response:
                for action in state.incident_response.follow_up_actions:
                    followup_tasks.append({
                        "action": action,
                        "scheduled_for": "24_hours",  # Simplified scheduling
                        "assignee": "security_team"
                    })
            
            state.add_tool_result("followup_scheduling", {
                "tasks": followup_tasks,
                "count": len(followup_tasks)
            })
            
            return state
            
        except Exception as e:
            state.mark_step_failed("schedule_followup", str(e))
            raise
    
    async def _update_metrics(self, state: IncidentState) -> IncidentState:
        """Update final metrics and quality scores."""
        try:
            state.update_step("update_metrics")
            
            # Calculate quality scores
            quality_scores = await self.metrics_tracker.calculate_quality_scores(state)
            state.quality_scores = quality_scores
            
            # Record final metrics
            final_metrics = {
                "total_processing_time": (state.updated_at - state.created_at).total_seconds(),
                "steps_completed": len(state.completed_steps),
                "steps_failed": len(state.failed_steps),
                "human_interventions": len(state.approval_history),
                "overall_quality_score": quality_scores.get("overall", 0.0)
            }
            
            state.processing_metrics.update(final_metrics)
            
            state.add_message(
                AIMessage(content=f"Incident processing completed. "
                                f"Quality score: {quality_scores.get('overall', 0.0):.2f}")
            )
            
            return state
            
        except Exception as e:
            state.mark_step_failed("update_metrics", str(e))
            raise
    
    async def _handle_error(self, state: IncidentState) -> IncidentState:
        """Handle workflow errors and cleanup."""
        try:
            state.update_step("handle_error")
            
            error_summary = {
                "failed_steps": state.failed_steps,
                "error_count": len(state.failed_steps),
                "last_error": state.tool_results.get(f"{state.current_step}_failure")
            }
            
            state.add_tool_result("error_handling", error_summary)
            
            # Record error metrics
            await self.metrics_tracker.record_workflow_error(
                incident_id=state.incident_id,
                error_step=state.current_step,
                error_details=error_summary
            )
            
            state.add_message(
                AIMessage(content=f"Workflow terminated due to error in step: {state.current_step}")
            )
            
            return state
            
        except Exception as e:
            # Final fallback - log and continue
            state.add_tool_result("final_error", str(e))
            return state
    
    # Router functions for conditional edges
    
    def _safety_check_router(self, state: IncidentState) -> Literal["continue", "reject", "human_review"]:
        """Route based on safety check results."""
        if not state.safety_guardrails_passed:
            return "reject"
        
        safety_result = state.tool_results.get("safety_check", {})
        if safety_result.get("requires_human_review", False):
            return "human_review"
        
        return "continue"
    
    def _compliance_check_router(self, state: IncidentState) -> Literal["approved", "requires_approval", "rejected"]:
        """Route based on compliance check results."""
        compliance_result = state.tool_results.get("compliance_check", {})
        
        if compliance_result.get("requires_legal_review", False):
            return "requires_approval"
        
        if any(not passed for passed in state.compliance_checks.values()):
            return "rejected"
        
        return "approved"
    
    def _human_approval_router(self, state: IncidentState) -> Literal["approved", "rejected", "pending"]:
        """Route based on human approval status."""
        if state.pending_approvals:
            return "pending"
        
        # Check if any approvals were rejected
        for approval in state.approval_history:
            if not approval.get("decision", True):
                return "rejected"
        
        return "approved"
    
    def _execution_router(self, state: IncidentState) -> Literal["document", "notify", "error"]:
        """Route based on action execution results."""
        execution_result = state.tool_results.get("action_execution", {})
        failed_actions = execution_result.get("failed", [])
        
        if failed_actions and len(failed_actions) > len(execution_result.get("executed", [])):
            return "error"
        
        return "document"
    
    # Utility methods
    
    async def _simulate_action_execution(self, action: str, state: IncidentState) -> Dict[str, Any]:
        """Simulate action execution for demo purposes."""
        # In production, this would call actual security systems
        return {
            "action": action,
            "status": "simulated",
            "timestamp": state.updated_at.isoformat()
        }
    
    async def _simulate_notification(self, notification: str, state: IncidentState) -> Dict[str, Any]:
        """Simulate notification sending for demo purposes."""
        return {
            "type": notification,
            "status": "sent",
            "timestamp": state.updated_at.isoformat(),
            "recipients": ["security_team", "ops_manager"]
        }


def create_triage_workflow(
    classifier: IncidentClassifier,
    prioritizer: IncidentPrioritizer,
    playbook_selector: PlaybookSelector,
    response_generator: ResponseGenerator,
    compliance_checker: ComplianceChecker,
    safety_guardrails: SafetyGuardrails,
    session_manager: SessionManager,
    metrics_tracker: MetricsTracker,
    checkpointer: SqliteSaver = None
) -> StateGraph:
    """
    Factory function to create the security triage workflow.
    
    Returns a compiled LangGraph workflow ready for execution.
    """
    workflow_manager = SecurityTriageWorkflow(
        classifier=classifier,
        prioritizer=prioritizer,
        playbook_selector=playbook_selector,
        response_generator=response_generator,
        compliance_checker=compliance_checker,
        safety_guardrails=safety_guardrails,
        session_manager=session_manager,
        metrics_tracker=metrics_tracker,
        checkpointer=checkpointer
    )
    
    return workflow_manager.workflow.compile(checkpointer=checkpointer)