"""
Agentic Security Incident Response Workflow using LangGraph.

This module implements a true agentic AI system that autonomously responds to
security incidents by making decisions, executing actions, and coordinating
multi-system responses across hotel management systems.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict, Literal
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.sqlite import SqliteSaver

from ..tools.hotel_management_tools import (
    PropertyManagementTool, 
    AccessControlTool, 
    NotificationOrchestratorTool
)
from ..autonomous.decision_engine import AutonomousDecisionEngine
from ..business.impact_tracker import BusinessImpactTracker


class AgentState(TypedDict):
    """State maintained throughout the agentic workflow"""
    # Core incident information
    incident_id: str
    incident_type: str
    description: str
    location: str
    priority: str
    timestamp: str
    
    # Analysis results
    risk_assessment: Optional[Dict[str, Any]]
    business_impact: Optional[Dict[str, Any]]
    decision_confidence: Optional[float]
    
    # Execution tracking
    actions_planned: List[Dict[str, Any]]
    actions_completed: List[Dict[str, Any]]
    actions_failed: List[Dict[str, Any]]
    
    # System integrations
    guest_info: Optional[Dict[str, Any]]
    room_status: Optional[str]
    access_logs: Optional[List[Dict[str, Any]]]
    
    # Communication tracking
    notifications_sent: List[Dict[str, Any]]
    escalations_made: List[Dict[str, Any]]
    
    # Workflow control
    current_step: str
    requires_human_intervention: bool
    workflow_complete: bool
    
    # Messages and reasoning
    messages: List[BaseMessage]
    reasoning_log: List[str]
    
    # Performance metrics
    start_time: str
    response_time_seconds: Optional[float]
    automation_success_rate: Optional[float]


class AgenticSecurityWorkflow:
    """
    Autonomous security incident response workflow that demonstrates true agentic AI capabilities.
    
    This system:
    1. Receives security incidents
    2. Autonomously analyzes risk and business impact 
    3. Makes informed decisions about response actions
    4. Executes coordinated actions across multiple hotel systems
    5. Monitors outcomes and adapts responses
    6. Escalates when human intervention is needed
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 pms_api_url: str = "https://demo-pms.tajhotels.com",
                 access_control_api_url: str = "https://demo-access.tajhotels.com",
                 notification_config: Dict[str, Any] = None):
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM with specific configuration for agentic reasoning
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,  # Low temperature for consistent decision-making
            max_tokens=2000,
            api_key=openai_api_key
        )
        
        # Initialize hotel management tools
        self.pms_tool = PropertyManagementTool(
            pms_api_url=pms_api_url,
            api_key="demo-pms-key"  # In production, use proper secrets management
        )
        
        self.access_control_tool = AccessControlTool(
            access_control_api_url=access_control_api_url,
            api_key="demo-access-key"
        )
        
        self.notification_tool = NotificationOrchestratorTool(
            notification_config=notification_config or {}
        )
        
        # Initialize decision engine and impact tracker
        self.decision_engine = AutonomousDecisionEngine()
        self.impact_tracker = BusinessImpactTracker()
        
        # Set up tool executor
        self.tools = [self.pms_tool, self.access_control_tool, self.notification_tool]
        self.tool_executor = ToolExecutor(self.tools)
        
        # Build the agentic workflow graph
        self.workflow = self._build_workflow_graph()
        
        # Initialize checkpoint saver for workflow persistence
        self.checkpointer = SqliteSaver.from_conn_string(":memory:")
        self.compiled_workflow = self.workflow.compile(checkpointer=self.checkpointer)
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow for autonomous incident response"""
        
        workflow = StateGraph(AgentState)
        
        # Define workflow nodes
        workflow.add_node("incident_analysis", self._analyze_incident)
        workflow.add_node("risk_assessment", self._assess_risk_and_impact)
        workflow.add_node("decision_making", self._make_autonomous_decisions)
        workflow.add_node("action_planning", self._plan_response_actions)
        workflow.add_node("system_integration", self._execute_system_actions)
        workflow.add_node("notification_coordination", self._coordinate_notifications)
        workflow.add_node("outcome_monitoring", self._monitor_and_adapt)
        workflow.add_node("human_escalation", self._escalate_to_human)
        workflow.add_node("workflow_completion", self._complete_workflow)
        
        # Define the workflow flow with conditional routing
        workflow.set_entry_point("incident_analysis")
        
        workflow.add_edge("incident_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "decision_making")
        workflow.add_edge("decision_making", "action_planning")
        
        # Conditional routing based on decision confidence
        workflow.add_conditional_edges(
            "action_planning",
            self._should_proceed_autonomously,
            {
                "autonomous": "system_integration",
                "escalate": "human_escalation"
            }
        )
        
        workflow.add_edge("system_integration", "notification_coordination")
        workflow.add_edge("notification_coordination", "outcome_monitoring")
        
        # Conditional routing based on outcome monitoring
        workflow.add_conditional_edges(
            "outcome_monitoring",
            self._check_completion_status,
            {
                "complete": "workflow_completion",
                "continue": "action_planning",  # Re-plan if needed
                "escalate": "human_escalation"
            }
        )
        
        workflow.add_edge("human_escalation", "workflow_completion")
        workflow.add_edge("workflow_completion", END)
        
        return workflow
    
    async def process_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a security incident through the autonomous workflow.
        
        Args:
            incident_data: Dictionary containing incident details
            
        Returns:
            Comprehensive incident response summary with actions taken
        """
        
        # Initialize agent state
        incident_id = incident_data.get("incident_id", str(uuid4()))
        
        initial_state = AgentState(
            incident_id=incident_id,
            incident_type=incident_data.get("type", "unknown"),
            description=incident_data.get("description", ""),
            location=incident_data.get("location", ""),
            priority=incident_data.get("priority", "medium"),
            timestamp=datetime.utcnow().isoformat(),
            
            # Initialize empty collections
            actions_planned=[],
            actions_completed=[],
            actions_failed=[],
            notifications_sent=[],
            escalations_made=[],
            messages=[],
            reasoning_log=[],
            
            # Set initial workflow state
            current_step="incident_analysis",
            requires_human_intervention=False,
            workflow_complete=False,
            start_time=datetime.utcnow().isoformat()
        )
        
        try:
            self.logger.info(f"Starting autonomous incident response for {incident_id}")
            
            # Execute the agentic workflow
            config = {"configurable": {"thread_id": incident_id}}
            
            final_state = None
            async for state in self.compiled_workflow.astream(initial_state, config):
                final_state = state
                
                # Log progress for demonstration
                current_step = list(state.keys())[0] if state else "unknown"
                self.logger.info(f"Incident {incident_id}: Executing step '{current_step}'")
            
            if final_state:
                workflow_state = list(final_state.values())[0]
                
                # Calculate final performance metrics
                end_time = datetime.utcnow()
                start_time = datetime.fromisoformat(workflow_state["start_time"])
                response_time = (end_time - start_time).total_seconds()
                
                # Calculate automation success rate
                total_actions = len(workflow_state["actions_planned"])
                successful_actions = len(workflow_state["actions_completed"])
                automation_rate = (successful_actions / total_actions) if total_actions > 0 else 0.0
                
                # Update business impact metrics
                await self.impact_tracker.record_incident_outcome(
                    incident_id=incident_id,
                    incident_type=workflow_state["incident_type"],
                    response_time_seconds=response_time,
                    automation_success_rate=automation_rate,
                    business_impact_prevented=workflow_state.get("business_impact", {}).get("prevented_loss", 0)
                )
                
                # Return comprehensive response summary
                return {
                    "incident_id": incident_id,
                    "response_status": "completed" if workflow_state["workflow_complete"] else "in_progress",
                    "autonomous_actions_taken": len(workflow_state["actions_completed"]),
                    "human_intervention_required": workflow_state["requires_human_intervention"],
                    "response_time_seconds": response_time,
                    "automation_success_rate": automation_rate,
                    "business_impact": workflow_state.get("business_impact", {}),
                    "actions_summary": {
                        "planned": workflow_state["actions_planned"],
                        "completed": workflow_state["actions_completed"],
                        "failed": workflow_state["actions_failed"]
                    },
                    "notifications_sent": workflow_state["notifications_sent"],
                    "reasoning_log": workflow_state["reasoning_log"],
                    "performance_metrics": {
                        "decision_confidence": workflow_state.get("decision_confidence", 0.0),
                        "system_integrations": len([a for a in workflow_state["actions_completed"] if "api_call" in a]),
                        "escalation_level": len(workflow_state["escalations_made"])
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed for incident {incident_id}: {e}")
            return {
                "incident_id": incident_id,
                "response_status": "failed",
                "error": str(e),
                "autonomous_actions_taken": 0,
                "human_intervention_required": True
            }
    
    # Workflow Node Implementations
    
    async def _analyze_incident(self, state: AgentState) -> AgentState:
        """Analyze the incident and extract key information"""
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert security analyst for a luxury hotel. 
            Analyze the incident and provide structured analysis.
            
            Focus on:
            1. Incident severity and urgency
            2. Potential security implications
            3. Guest safety considerations
            4. Operational impact
            5. Required immediate actions
            """),
            ("human", """Analyze this security incident:
            
            Type: {incident_type}
            Location: {location}
            Description: {description}
            
            Provide a structured analysis with specific recommendations.""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                analysis_prompt.format_messages(
                    incident_type=state["incident_type"],
                    location=state["location"], 
                    description=state["description"]
                )
            )
            
            # Log reasoning
            reasoning = f"Incident Analysis: {response.content[:200]}..."
            state["reasoning_log"].append(reasoning)
            state["messages"].append(response)
            state["current_step"] = "risk_assessment"
            
            self.logger.info(f"Completed incident analysis for {state['incident_id']}")
            
        except Exception as e:
            self.logger.error(f"Incident analysis failed: {e}")
            state["requires_human_intervention"] = True
        
        return state
    
    async def _assess_risk_and_impact(self, state: AgentState) -> AgentState:
        """Perform comprehensive risk assessment and business impact analysis"""
        
        try:
            # Use decision engine for multi-criteria risk assessment
            risk_assessment = await self.decision_engine.assess_incident_risk(
                incident_type=state["incident_type"],
                location=state["location"],
                description=state["description"],
                timestamp=state["timestamp"]
            )
            
            # Calculate business impact
            business_impact = await self.impact_tracker.calculate_potential_impact(
                incident_type=state["incident_type"],
                location=state["location"],
                priority=state["priority"]
            )
            
            state["risk_assessment"] = risk_assessment
            state["business_impact"] = business_impact
            state["current_step"] = "decision_making"
            
            reasoning = f"Risk Level: {risk_assessment.get('overall_risk', 'unknown')}, Business Impact: ${business_impact.get('potential_loss', 0)}"
            state["reasoning_log"].append(reasoning)
            
            self.logger.info(f"Risk assessment completed for {state['incident_id']}: {reasoning}")
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            state["requires_human_intervention"] = True
        
        return state
    
    async def _make_autonomous_decisions(self, state: AgentState) -> AgentState:
        """Make autonomous decisions based on risk assessment and business impact"""
        
        decision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an autonomous security decision-making system.
            Based on the risk assessment and business impact, make specific operational decisions.
            
            You can autonomously decide to:
            1. Update room status in PMS
            2. Revoke/grant access permissions  
            3. Notify appropriate personnel
            4. Coordinate with other hotel systems
            5. Escalate to management if needed
            
            Provide specific, actionable decisions with high confidence scores."""),
            ("human", """Make autonomous decisions for this incident:
            
            Risk Assessment: {risk_assessment}
            Business Impact: {business_impact}
            Current Priority: {priority}
            
            What specific actions should be taken immediately?""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                decision_prompt.format_messages(
                    risk_assessment=json.dumps(state["risk_assessment"], indent=2),
                    business_impact=json.dumps(state["business_impact"], indent=2),
                    priority=state["priority"]
                )
            )
            
            # Use decision engine to calculate confidence
            confidence = await self.decision_engine.calculate_decision_confidence(
                risk_level=state["risk_assessment"].get("overall_risk", 0.5),
                business_impact=state["business_impact"].get("impact_score", 0.5),
                incident_type=state["incident_type"]
            )
            
            state["decision_confidence"] = confidence
            state["current_step"] = "action_planning"
            
            reasoning = f"Decision Confidence: {confidence:.2f}, Response: {response.content[:150]}..."
            state["reasoning_log"].append(reasoning)
            state["messages"].append(response)
            
            self.logger.info(f"Autonomous decision made for {state['incident_id']} with {confidence:.1%} confidence")
            
        except Exception as e:
            self.logger.error(f"Decision making failed: {e}")
            state["requires_human_intervention"] = True
        
        return state
    
    async def _plan_response_actions(self, state: AgentState) -> AgentState:
        """Plan specific response actions based on decisions made"""
        
        try:
            # Extract planned actions from the decision response
            actions_planned = []
            
            # Based on incident type and risk level, plan specific actions
            risk_level = state["risk_assessment"].get("overall_risk", 0.5)
            incident_type = state["incident_type"]
            
            if "access" in incident_type.lower() or "unauthorized" in state["description"].lower():
                actions_planned.extend([
                    {
                        "action_type": "access_control",
                        "tool": "access_control_system",
                        "method": "revoke_access",
                        "parameters": {"card_id": "GUEST_123", "reason": "Security incident"},
                        "priority": "high",
                        "estimated_duration": 30
                    },
                    {
                        "action_type": "room_management",
                        "tool": "property_management_system", 
                        "method": "update_room_status",
                        "parameters": {"room_number": state["location"], "status": "security_hold", "reason": "Security incident under investigation"},
                        "priority": "high",
                        "estimated_duration": 60
                    }
                ])
            
            if risk_level > 0.7:  # High risk incidents
                actions_planned.append({
                    "action_type": "notification",
                    "tool": "notification_orchestrator",
                    "method": "notify_security_team",
                    "parameters": {
                        "incident_id": state["incident_id"],
                        "priority": "high",
                        "location": state["location"],
                        "summary": state["description"][:100]
                    },
                    "priority": "critical",
                    "estimated_duration": 120
                })
            
            if state["business_impact"].get("potential_loss", 0) > 10000:  # Significant business impact
                actions_planned.append({
                    "action_type": "management_alert",
                    "tool": "notification_orchestrator",
                    "method": "alert_management", 
                    "parameters": {
                        "incident_summary": state["description"],
                        "escalation_level": 3,
                        "business_impact": f"Potential loss: ${state['business_impact'].get('potential_loss', 0)}"
                    },
                    "priority": "high",
                    "estimated_duration": 180
                })
            
            state["actions_planned"] = actions_planned
            state["current_step"] = "system_integration"
            
            reasoning = f"Planned {len(actions_planned)} autonomous actions based on risk level {risk_level:.2f}"
            state["reasoning_log"].append(reasoning)
            
            self.logger.info(f"Action planning completed for {state['incident_id']}: {len(actions_planned)} actions planned")
            
        except Exception as e:
            self.logger.error(f"Action planning failed: {e}")
            state["requires_human_intervention"] = True
        
        return state
    
    async def _execute_system_actions(self, state: AgentState) -> AgentState:
        """Execute planned actions across hotel management systems"""
        
        actions_completed = []
        actions_failed = []
        
        for action in state["actions_planned"]:
            try:
                self.logger.info(f"Executing {action['action_type']} for incident {state['incident_id']}")
                
                # Execute the specific tool action
                result = await self._execute_tool_action(action)
                
                if result.get("success", False):
                    action["execution_result"] = result
                    action["completed_at"] = datetime.utcnow().isoformat()
                    actions_completed.append(action)
                    
                    self.logger.info(f"Successfully completed {action['action_type']}")
                else:
                    action["error"] = result.get("error", "Unknown error")
                    actions_failed.append(action)
                    
                    self.logger.error(f"Failed to execute {action['action_type']}: {action.get('error', 'Unknown error')}")
                
                # Small delay between actions to prevent overwhelming systems
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Action execution error: {e}")
                action["error"] = str(e)
                actions_failed.append(action)
        
        state["actions_completed"] = actions_completed
        state["actions_failed"] = actions_failed
        state["current_step"] = "notification_coordination"
        
        success_rate = len(actions_completed) / len(state["actions_planned"]) if state["actions_planned"] else 0
        reasoning = f"Executed {len(actions_completed)}/{len(state['actions_planned'])} actions successfully ({success_rate:.1%})"
        state["reasoning_log"].append(reasoning)
        
        return state
    
    async def _coordinate_notifications(self, state: AgentState) -> AgentState:
        """Coordinate notifications based on actions taken and results"""
        
        notifications_sent = []
        
        try:
            # Determine who needs to be notified based on actions taken
            if state["actions_completed"]:
                # Notify security team about successful actions
                notification_result = await self.notification_tool.notify_security_team(
                    incident_id=state["incident_id"],
                    priority=state["priority"],
                    location=state["location"],
                    summary=f"Autonomous response completed: {len(state['actions_completed'])} actions taken"
                )
                notifications_sent.extend(notification_result)
            
            if state["actions_failed"]:
                # Escalate failed actions to management
                escalation_summary = f"Security incident {state['incident_id']}: {len(state['actions_failed'])} autonomous actions failed"
                management_alerts = await self.notification_tool.alert_management(
                    incident_summary=escalation_summary,
                    escalation_level=2,
                    business_impact="Automated response partially failed - manual intervention may be required"
                )
                notifications_sent.extend(management_alerts)
        
            state["notifications_sent"] = notifications_sent
            state["current_step"] = "outcome_monitoring"
            
            reasoning = f"Sent {len(notifications_sent)} notifications to coordinate response"
            state["reasoning_log"].append(reasoning)
            
        except Exception as e:
            self.logger.error(f"Notification coordination failed: {e}")
            # Non-critical failure - continue workflow
        
        return state
    
    async def _monitor_and_adapt(self, state: AgentState) -> AgentState:
        """Monitor action outcomes and adapt response if needed"""
        
        try:
            # Calculate overall success metrics
            total_planned = len(state["actions_planned"])
            total_completed = len(state["actions_completed"])
            total_failed = len(state["actions_failed"])
            
            success_rate = (total_completed / total_planned) if total_planned > 0 else 0
            
            # Update automation success rate
            state["automation_success_rate"] = success_rate
            
            # Determine if workflow should continue, complete, or escalate
            if success_rate >= 0.8:  # 80% success rate
                state["workflow_complete"] = True
                state["current_step"] = "workflow_completion"
                
                reasoning = f"Workflow successful: {success_rate:.1%} automation success rate"
                state["reasoning_log"].append(reasoning)
                
            elif success_rate >= 0.5:  # 50-80% success rate
                # Partial success - may need additional actions
                reasoning = f"Partial success ({success_rate:.1%}) - evaluating need for additional actions"
                state["reasoning_log"].append(reasoning)
                
                # Could re-plan here if needed, for now we'll complete
                state["workflow_complete"] = True
                state["current_step"] = "workflow_completion"
                
            else:  # Less than 50% success rate
                state["requires_human_intervention"] = True
                state["current_step"] = "human_escalation"
                
                reasoning = f"Low success rate ({success_rate:.1%}) - escalating to human intervention"
                state["reasoning_log"].append(reasoning)
        
            # Calculate total response time
            start_time = datetime.fromisoformat(state["start_time"])
            response_time = (datetime.utcnow() - start_time).total_seconds()
            state["response_time_seconds"] = response_time
            
        except Exception as e:
            self.logger.error(f"Outcome monitoring failed: {e}")
            state["requires_human_intervention"] = True
        
        return state
    
    async def _escalate_to_human(self, state: AgentState) -> AgentState:
        """Escalate to human when autonomous response is insufficient"""
        
        escalation_summary = {
            "incident_id": state["incident_id"],
            "escalation_reason": "Autonomous response insufficient or failed",
            "actions_attempted": len(state["actions_planned"]),
            "actions_successful": len(state["actions_completed"]),
            "actions_failed": len(state["actions_failed"]),
            "business_impact": state.get("business_impact", {}),
            "recommended_actions": "Manual review and intervention required"
        }
        
        state["escalations_made"].append(escalation_summary)
        state["workflow_complete"] = True
        state["current_step"] = "workflow_completion"
        
        reasoning = f"Escalated to human intervention due to insufficient autonomous response"
        state["reasoning_log"].append(reasoning)
        
        self.logger.warning(f"Incident {state['incident_id']} escalated to human intervention")
        
        return state
    
    async def _complete_workflow(self, state: AgentState) -> AgentState:
        """Complete the workflow and generate final summary"""
        
        # Calculate final metrics
        end_time = datetime.utcnow()
        start_time = datetime.fromisoformat(state["start_time"])
        total_response_time = (end_time - start_time).total_seconds()
        
        state["response_time_seconds"] = total_response_time
        state["workflow_complete"] = True
        
        # Log completion
        completion_summary = {
            "incident_id": state["incident_id"],
            "total_response_time_seconds": total_response_time,
            "autonomous_actions_taken": len(state["actions_completed"]),
            "automation_success_rate": state.get("automation_success_rate", 0.0),
            "human_intervention_required": state["requires_human_intervention"],
            "workflow_status": "completed"
        }
        
        reasoning = f"Workflow completed in {total_response_time:.1f}s with {len(state['actions_completed'])} successful autonomous actions"
        state["reasoning_log"].append(reasoning)
        
        self.logger.info(f"Incident {state['incident_id']} workflow completed: {completion_summary}")
        
        return state
    
    # Workflow Helper Methods
    
    async def _execute_tool_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool action"""
        
        tool_name = action["tool"]
        method_name = action["method"]
        parameters = action.get("parameters", {})
        
        try:
            if tool_name == "property_management_system":
                if method_name == "update_room_status":
                    result = await self.pms_tool.update_room_status(
                        room_number=parameters.get("room_number"),
                        status=parameters.get("status"),
                        reason=parameters.get("reason")
                    )
                    return {"success": result, "tool": tool_name, "method": method_name}
                
            elif tool_name == "access_control_system":
                if method_name == "revoke_access":
                    result = await self.access_control_tool.revoke_access(
                        card_id=parameters.get("card_id"),
                        reason=parameters.get("reason")
                    )
                    return {"success": result.success, "tool": tool_name, "method": method_name, "details": result.dict()}
                
            elif tool_name == "notification_orchestrator":
                if method_name == "notify_security_team":
                    results = await self.notification_tool.notify_security_team(
                        incident_id=parameters.get("incident_id"),
                        priority=parameters.get("priority"),
                        location=parameters.get("location"),
                        summary=parameters.get("summary")
                    )
                    success_count = sum(1 for r in results if r.success)
                    return {"success": success_count > 0, "tool": tool_name, "method": method_name, "notifications_sent": success_count}
                    
                elif method_name == "alert_management":
                    results = await self.notification_tool.alert_management(
                        incident_summary=parameters.get("incident_summary"),
                        escalation_level=parameters.get("escalation_level"),
                        business_impact=parameters.get("business_impact")
                    )
                    success_count = sum(1 for r in results if r.success)
                    return {"success": success_count > 0, "tool": tool_name, "method": method_name, "alerts_sent": success_count}
            
            return {"success": False, "error": f"Unknown tool method: {tool_name}.{method_name}"}
            
        except Exception as e:
            return {"success": False, "error": str(e), "tool": tool_name, "method": method_name}
    
    def _should_proceed_autonomously(self, state: AgentState) -> Literal["autonomous", "escalate"]:
        """Determine if workflow should proceed autonomously or escalate to human"""
        
        confidence = state.get("decision_confidence", 0.0)
        risk_level = state.get("risk_assessment", {}).get("overall_risk", 0.5)
        
        # Escalate if confidence is too low or risk is too high
        if confidence < 0.6 or risk_level > 0.8:
            return "escalate"
        
        return "autonomous"
    
    def _check_completion_status(self, state: AgentState) -> Literal["complete", "continue", "escalate"]:
        """Check if workflow should complete, continue, or escalate"""
        
        if state.get("requires_human_intervention", False):
            return "escalate"
        
        if state.get("workflow_complete", False):
            return "complete"
        
        # Check if we need to continue (re-plan actions)
        success_rate = state.get("automation_success_rate", 0.0)
        if success_rate < 0.5:
            return "escalate"
        
        return "complete"


# Factory function for easy initialization
async def create_agentic_security_workflow(openai_api_key: str) -> AgenticSecurityWorkflow:
    """Create and configure an agentic security workflow instance"""
    
    notification_config = {
        "sms_provider": "twilio",
        "email_provider": "sendgrid",
        "slack_webhook": "https://hooks.slack.com/demo",
        "phone_provider": "twilio"
    }
    
    workflow = AgenticSecurityWorkflow(
        openai_api_key=openai_api_key,
        notification_config=notification_config
    )
    
    return workflow