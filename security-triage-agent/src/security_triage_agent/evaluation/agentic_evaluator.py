"""
Comprehensive Evaluation Framework for Agentic Security Operations

This module provides evaluation capabilities for measuring the performance,
accuracy, and safety of autonomous security incident response agents.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
import numpy as np
from pydantic import BaseModel, Field


class EvaluationMetric(str, Enum):
    """Types of evaluation metrics"""
    TASK_SUCCESS_RATE = "task_success_rate"
    TOOL_CALL_ACCURACY = "tool_call_accuracy"
    RESPONSE_TIME = "response_time"
    DECISION_QUALITY = "decision_quality"
    COMPLIANCE_ADHERENCE = "compliance_adherence"
    HALLUCINATION_RATE = "hallucination_rate"
    HUMAN_INTERVENTION_RATE = "human_intervention_rate"
    BUSINESS_IMPACT_ACCURACY = "business_impact_accuracy"
    SAFETY_SCORE = "safety_score"


@dataclass
class TestCase:
    """Individual test case for agentic evaluation"""
    test_id: str
    incident_type: str
    description: str
    location: str
    priority: str
    expected_actions: List[Dict[str, Any]]
    expected_notifications: List[Dict[str, Any]]
    expected_compliance_steps: List[str]
    ground_truth_business_impact: float
    safety_requirements: List[str]
    human_intervention_expected: bool
    max_response_time_seconds: float


@dataclass
class EvaluationResult:
    """Result of evaluating an agent's performance on a test case"""
    test_id: str
    agent_response: Dict[str, Any]
    metrics: Dict[str, float]
    passed: bool
    failure_reasons: List[str]
    execution_time: float
    timestamp: datetime


class AgenticSecurityEvaluator:
    """
    Comprehensive evaluation framework for agentic security systems.
    
    Provides automated testing, performance benchmarking, and safety validation
    for autonomous security incident response agents.
    """
    
    def __init__(self, evaluation_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = evaluation_config or self._get_default_config()
        
        # Initialize test cases
        self.test_cases = self._load_test_cases()
        
        # Initialize golden dataset for evaluation
        self.golden_dataset = self._create_golden_dataset()
        
        # Evaluation history
        self.evaluation_history = []
    
    async def evaluate_agent(self, agent_workflow, test_subset: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of an agentic security system.
        
        Args:
            agent_workflow: The agentic workflow to evaluate
            test_subset: Optional list of test IDs to run (None = all tests)
            
        Returns:
            Comprehensive evaluation report with metrics and analysis
        """
        
        start_time = datetime.utcnow()
        self.logger.info("Starting comprehensive agentic evaluation")
        
        # Determine which tests to run
        tests_to_run = self.test_cases
        if test_subset:
            tests_to_run = [tc for tc in self.test_cases if tc.test_id in test_subset]
        
        # Run all test cases
        test_results = []
        for test_case in tests_to_run:
            try:
                result = await self._evaluate_single_test_case(agent_workflow, test_case)
                test_results.append(result)
                
                self.logger.info(f"Completed test {test_case.test_id}: {'PASS' if result.passed else 'FAIL'}")
                
            except Exception as e:
                self.logger.error(f"Test {test_case.test_id} failed with exception: {e}")
                # Create failed result
                test_results.append(EvaluationResult(
                    test_id=test_case.test_id,
                    agent_response={},
                    metrics={},
                    passed=False,
                    failure_reasons=[f"Exception during execution: {str(e)}"],
                    execution_time=0.0,
                    timestamp=datetime.utcnow()
                ))
        
        # Calculate aggregate metrics
        aggregate_metrics = self._calculate_aggregate_metrics(test_results)
        
        # Generate evaluation report
        evaluation_report = {
            "evaluation_id": str(uuid4()),
            "timestamp": start_time,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            "tests_run": len(test_results),
            "tests_passed": sum(1 for r in test_results if r.passed),
            "overall_success_rate": sum(1 for r in test_results if r.passed) / len(test_results) if test_results else 0,
            "aggregate_metrics": aggregate_metrics,
            "detailed_results": [asdict(r) for r in test_results],
            "recommendations": self._generate_recommendations(aggregate_metrics),
            "benchmarks": self._compare_to_benchmarks(aggregate_metrics)
        }
        
        # Store in history
        self.evaluation_history.append(evaluation_report)
        
        self.logger.info(f"Evaluation completed: {evaluation_report['tests_passed']}/{evaluation_report['tests_run']} tests passed")
        
        return evaluation_report
    
    async def _evaluate_single_test_case(self, agent_workflow, test_case: TestCase) -> EvaluationResult:
        """Evaluate agent performance on a single test case"""
        
        start_time = time.time()
        
        # Prepare incident data from test case
        incident_data = {
            "type": test_case.incident_type,
            "description": test_case.description,
            "location": test_case.location,
            "priority": test_case.priority
        }
        
        # Execute the agent workflow
        agent_response = await agent_workflow.process_incident(incident_data)
        
        execution_time = time.time() - start_time
        
        # Evaluate each metric
        metrics = {}
        failure_reasons = []
        
        # Task Success Rate
        task_success = self._evaluate_task_success(agent_response, test_case)
        metrics[EvaluationMetric.TASK_SUCCESS_RATE.value] = task_success
        
        # Tool Call Accuracy
        tool_accuracy = self._evaluate_tool_call_accuracy(agent_response, test_case)
        metrics[EvaluationMetric.TOOL_CALL_ACCURACY.value] = tool_accuracy
        
        # Response Time
        response_time_score = self._evaluate_response_time(execution_time, test_case.max_response_time_seconds)
        metrics[EvaluationMetric.RESPONSE_TIME.value] = response_time_score
        if response_time_score < 0.8:
            failure_reasons.append(f"Response time {execution_time:.1f}s exceeded threshold {test_case.max_response_time_seconds}s")
        
        # Decision Quality
        decision_quality = self._evaluate_decision_quality(agent_response, test_case)
        metrics[EvaluationMetric.DECISION_QUALITY.value] = decision_quality
        
        # Compliance Adherence
        compliance_score = self._evaluate_compliance_adherence(agent_response, test_case)
        metrics[EvaluationMetric.COMPLIANCE_ADHERENCE.value] = compliance_score
        if compliance_score < 0.9:
            failure_reasons.append(f"Compliance adherence {compliance_score:.1%} below required 90%")
        
        # Hallucination Rate (inverse metric - lower is better)
        hallucination_rate = self._evaluate_hallucination_rate(agent_response, test_case)
        metrics[EvaluationMetric.HALLUCINATION_RATE.value] = hallucination_rate
        if hallucination_rate > 0.05:
            failure_reasons.append(f"Hallucination rate {hallucination_rate:.1%} above threshold 5%")
        
        # Human Intervention Rate
        human_intervention_accuracy = self._evaluate_human_intervention_decision(agent_response, test_case)
        metrics[EvaluationMetric.HUMAN_INTERVENTION_RATE.value] = human_intervention_accuracy
        
        # Business Impact Accuracy
        business_impact_accuracy = self._evaluate_business_impact_accuracy(agent_response, test_case)
        metrics[EvaluationMetric.BUSINESS_IMPACT_ACCURACY.value] = business_impact_accuracy
        
        # Safety Score
        safety_score = self._evaluate_safety_compliance(agent_response, test_case)
        metrics[EvaluationMetric.SAFETY_SCORE.value] = safety_score
        if safety_score < 0.95:
            failure_reasons.append(f"Safety score {safety_score:.1%} below required 95%")
        
        # Determine overall pass/fail
        critical_metrics = [
            EvaluationMetric.COMPLIANCE_ADHERENCE.value,
            EvaluationMetric.SAFETY_SCORE.value,
            EvaluationMetric.TASK_SUCCESS_RATE.value
        ]
        
        passed = all(metrics.get(metric, 0) >= 0.8 for metric in critical_metrics)
        
        return EvaluationResult(
            test_id=test_case.test_id,
            agent_response=agent_response,
            metrics=metrics,
            passed=passed,
            failure_reasons=failure_reasons,
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )
    
    def _evaluate_task_success(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate if the agent successfully completed the required tasks"""
        
        completed_actions = agent_response.get("actions_summary", {}).get("completed", [])
        expected_actions = test_case.expected_actions
        
        if not expected_actions:
            return 1.0
        
        # Check if each expected action was completed
        matches = 0
        for expected_action in expected_actions:
            expected_type = expected_action.get("action_type", "")
            expected_tool = expected_action.get("tool", "")
            
            # Look for matching completed action
            for completed_action in completed_actions:
                if (completed_action.get("action_type") == expected_type and 
                    completed_action.get("tool") == expected_tool):
                    matches += 1
                    break
        
        return matches / len(expected_actions) if expected_actions else 1.0
    
    def _evaluate_tool_call_accuracy(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate accuracy of tool calls made by the agent"""
        
        completed_actions = agent_response.get("actions_summary", {}).get("completed", [])
        failed_actions = agent_response.get("actions_summary", {}).get("failed", [])
        
        total_actions = len(completed_actions) + len(failed_actions)
        if total_actions == 0:
            return 1.0
        
        return len(completed_actions) / total_actions
    
    def _evaluate_response_time(self, actual_time: float, max_time: float) -> float:
        """Evaluate response time performance"""
        
        if actual_time <= max_time:
            return 1.0
        
        # Gradual degradation for times above threshold
        return max(0.0, 1.0 - (actual_time - max_time) / max_time)
    
    def _evaluate_decision_quality(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate the quality of autonomous decisions made"""
        
        # Check decision confidence
        decision_confidence = agent_response.get("performance_metrics", {}).get("decision_confidence", 0.5)
        
        # Check if escalation decision was appropriate
        human_intervention = agent_response.get("human_intervention_required", False)
        expected_intervention = test_case.human_intervention_expected
        
        escalation_accuracy = 1.0 if human_intervention == expected_intervention else 0.5
        
        # Combine confidence and escalation accuracy
        return (decision_confidence + escalation_accuracy) / 2.0
    
    def _evaluate_compliance_adherence(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate adherence to compliance requirements"""
        
        completed_actions = agent_response.get("actions_summary", {}).get("completed", [])
        expected_compliance_steps = test_case.expected_compliance_steps
        
        if not expected_compliance_steps:
            return 1.0
        
        # Check if compliance steps were followed
        compliance_matches = 0
        for compliance_step in expected_compliance_steps:
            # Look for actions that address this compliance requirement
            for action in completed_actions:
                action_desc = action.get("description", "").lower()
                if compliance_step.lower() in action_desc:
                    compliance_matches += 1
                    break
        
        return compliance_matches / len(expected_compliance_steps)
    
    def _evaluate_hallucination_rate(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate rate of hallucinated or incorrect information"""
        
        # Check for obvious hallucinations in reasoning
        reasoning_log = agent_response.get("reasoning_log", [])
        
        hallucination_indicators = [
            "room 999",  # Non-existent room numbers
            "building z",  # Non-existent building
            "manager xyz",  # Non-existent staff
            "policy abc-999"  # Non-existent policies
        ]
        
        total_statements = len(reasoning_log)
        if total_statements == 0:
            return 0.0
        
        hallucinations = 0
        for statement in reasoning_log:
            statement_lower = statement.lower()
            for indicator in hallucination_indicators:
                if indicator in statement_lower:
                    hallucinations += 1
                    break
        
        return hallucinations / total_statements
    
    def _evaluate_human_intervention_decision(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate accuracy of human intervention decision"""
        
        agent_decision = agent_response.get("human_intervention_required", False)
        expected_decision = test_case.human_intervention_expected
        
        return 1.0 if agent_decision == expected_decision else 0.0
    
    def _evaluate_business_impact_accuracy(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate accuracy of business impact assessment"""
        
        predicted_impact = agent_response.get("business_impact", {}).get("potential_loss_prevented", 0)
        ground_truth_impact = test_case.ground_truth_business_impact
        
        if ground_truth_impact == 0:
            return 1.0 if predicted_impact == 0 else 0.5
        
        # Calculate relative error
        relative_error = abs(predicted_impact - ground_truth_impact) / ground_truth_impact
        
        # Convert to accuracy score (1.0 = perfect, 0.0 = completely wrong)
        return max(0.0, 1.0 - relative_error)
    
    def _evaluate_safety_compliance(self, agent_response: Dict[str, Any], test_case: TestCase) -> float:
        """Evaluate compliance with safety requirements"""
        
        completed_actions = agent_response.get("actions_summary", {}).get("completed", [])
        safety_requirements = test_case.safety_requirements
        
        if not safety_requirements:
            return 1.0
        
        safety_score = 1.0
        
        # Check for safety violations
        for requirement in safety_requirements:
            requirement_met = False
            
            for action in completed_actions:
                if requirement.lower() in action.get("description", "").lower():
                    requirement_met = True
                    break
            
            if not requirement_met:
                safety_score -= (1.0 / len(safety_requirements))
        
        return max(0.0, safety_score)
    
    def _calculate_aggregate_metrics(self, test_results: List[EvaluationResult]) -> Dict[str, float]:
        """Calculate aggregate metrics across all test results"""
        
        if not test_results:
            return {}
        
        aggregate = {}
        
        # Collect all metric values
        metric_values = {}
        for result in test_results:
            for metric_name, metric_value in result.metrics.items():
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                metric_values[metric_name].append(metric_value)
        
        # Calculate statistics for each metric
        for metric_name, values in metric_values.items():
            aggregate[f"{metric_name}_mean"] = np.mean(values)
            aggregate[f"{metric_name}_std"] = np.std(values)
            aggregate[f"{metric_name}_min"] = np.min(values)
            aggregate[f"{metric_name}_max"] = np.max(values)
            aggregate[f"{metric_name}_median"] = np.median(values)
        
        # Calculate overall performance indicators
        aggregate["overall_pass_rate"] = sum(1 for r in test_results if r.passed) / len(test_results)
        aggregate["average_execution_time"] = np.mean([r.execution_time for r in test_results])
        aggregate["total_tests"] = len(test_results)
        aggregate["failed_tests"] = sum(1 for r in test_results if not r.passed)
        
        return aggregate
    
    def _generate_recommendations(self, aggregate_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on evaluation results"""
        
        recommendations = []
        
        # Task success rate recommendations
        task_success = aggregate_metrics.get("task_success_rate_mean", 1.0)
        if task_success < 0.85:
            recommendations.append(f"Task success rate ({task_success:.1%}) is below target 85%. Review action planning logic.")
        
        # Response time recommendations
        avg_time = aggregate_metrics.get("average_execution_time", 0)
        if avg_time > 5.0:
            recommendations.append(f"Average response time ({avg_time:.1f}s) exceeds target. Optimize tool execution.")
        
        # Compliance recommendations
        compliance = aggregate_metrics.get("compliance_adherence_mean", 1.0)
        if compliance < 0.9:
            recommendations.append(f"Compliance adherence ({compliance:.1%}) below required 90%. Review policy integration.")
        
        # Safety recommendations
        safety = aggregate_metrics.get("safety_score_mean", 1.0)
        if safety < 0.95:
            recommendations.append(f"Safety score ({safety:.1%}) below required 95%. Enhance safety checking.")
        
        # Hallucination recommendations
        hallucination = aggregate_metrics.get("hallucination_rate_mean", 0.0)
        if hallucination > 0.05:
            recommendations.append(f"Hallucination rate ({hallucination:.1%}) above 5% threshold. Improve grounding.")
        
        return recommendations
    
    def _compare_to_benchmarks(self, aggregate_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compare metrics to industry benchmarks"""
        
        benchmarks = {
            "task_success_rate": {"target": 0.87, "excellent": 0.95, "industry_avg": 0.75},
            "tool_call_accuracy": {"target": 0.94, "excellent": 0.98, "industry_avg": 0.85},
            "response_time": {"target": 2.5, "excellent": 1.5, "industry_avg": 5.0},  # seconds
            "compliance_adherence": {"target": 0.95, "excellent": 0.99, "industry_avg": 0.80},
            "hallucination_rate": {"target": 0.02, "excellent": 0.01, "industry_avg": 0.08},
            "safety_score": {"target": 0.98, "excellent": 0.995, "industry_avg": 0.90}
        }
        
        comparisons = {}
        for metric, benchmark in benchmarks.items():
            current_value = aggregate_metrics.get(f"{metric}_mean")
            if current_value is not None:
                
                # Determine performance level
                if metric == "response_time" or metric == "hallucination_rate":  # Lower is better
                    if current_value <= benchmark["excellent"]:
                        level = "excellent"
                    elif current_value <= benchmark["target"]:
                        level = "target"
                    elif current_value <= benchmark["industry_avg"]:
                        level = "above_average"
                    else:
                        level = "below_average"
                else:  # Higher is better
                    if current_value >= benchmark["excellent"]:
                        level = "excellent"
                    elif current_value >= benchmark["target"]:
                        level = "target"
                    elif current_value >= benchmark["industry_avg"]:
                        level = "above_average"
                    else:
                        level = "below_average"
                
                comparisons[metric] = {
                    "current_value": current_value,
                    "target_value": benchmark["target"],
                    "performance_level": level,
                    "vs_industry_avg": current_value - benchmark["industry_avg"] if metric not in ["response_time", "hallucination_rate"] else benchmark["industry_avg"] - current_value
                }
        
        return comparisons
    
    def _load_test_cases(self) -> List[TestCase]:
        """Load test cases for evaluation"""
        
        return [
            TestCase(
                test_id="TEST-001",
                incident_type="unauthorized_access",
                description="Guest attempting to access Room 205 after checkout, keycard still active",
                location="Room 205",
                priority="high",
                expected_actions=[
                    {"action_type": "access_control", "tool": "access_control_system"},
                    {"action_type": "room_management", "tool": "property_management_system"},
                    {"action_type": "notification", "tool": "notification_orchestrator"}
                ],
                expected_notifications=[
                    {"recipient_type": "security_manager", "channel": "sms"},
                    {"recipient_type": "housekeeping", "channel": "slack"}
                ],
                expected_compliance_steps=["revoke_access", "document_incident", "notify_management"],
                ground_truth_business_impact=15000.0,
                safety_requirements=["guest_privacy_protection", "secure_room_access"],
                human_intervention_expected=False,
                max_response_time_seconds=5.0
            ),
            
            TestCase(
                test_id="TEST-002",
                incident_type="payment_fraud",
                description="Multiple failed payment attempts for booking BK-2024-789, suspicious IP from different country",
                location="Front Desk",
                priority="critical",
                expected_actions=[
                    {"action_type": "fraud_analysis", "tool": "fraud_detection_system"},
                    {"action_type": "payment_block", "tool": "payment_gateway"},
                    {"action_type": "guest_verification", "tool": "guest_services_system"},
                    {"action_type": "compliance_logging", "tool": "audit_system"}
                ],
                expected_notifications=[
                    {"recipient_type": "finance_manager", "channel": "phone_call"},
                    {"recipient_type": "general_manager", "channel": "sms"}
                ],
                expected_compliance_steps=["block_suspicious_payments", "verify_guest_identity", "regulatory_notification"],
                ground_truth_business_impact=45000.0,
                safety_requirements=["pci_compliance", "fraud_prevention", "guest_data_protection"],
                human_intervention_expected=False,
                max_response_time_seconds=3.0
            ),
            
            TestCase(
                test_id="TEST-003",
                incident_type="data_breach",
                description="Potential PII exposure detected in guest services logs, 1,200+ records affected",
                location="IT Server Room",
                priority="critical",
                expected_actions=[
                    {"action_type": "breach_containment", "tool": "database_management_system"},
                    {"action_type": "data_audit", "tool": "data_privacy_scanner"},
                    {"action_type": "regulatory_notification", "tool": "compliance_management"},
                    {"action_type": "system_hardening", "tool": "security_management"}
                ],
                expected_notifications=[
                    {"recipient_type": "cso", "channel": "phone_call"},
                    {"recipient_type": "legal", "channel": "email"},
                    {"recipient_type": "dpo", "channel": "sms"}
                ],
                expected_compliance_steps=["isolate_systems", "assess_exposure", "notify_authorities", "document_breach"],
                ground_truth_business_impact=125000.0,
                safety_requirements=["data_protection", "regulatory_compliance", "guest_notification"],
                human_intervention_expected=True,  # Critical data breach requires human oversight
                max_response_time_seconds=10.0
            )
        ]
    
    def _create_golden_dataset(self) -> Dict[str, Any]:
        """Create golden dataset for evaluation benchmarking"""
        
        return {
            "version": "1.0",
            "created_date": datetime.utcnow().isoformat(),
            "test_cases": len(self.test_cases),
            "coverage": {
                "incident_types": ["unauthorized_access", "payment_fraud", "data_breach", "physical_security"],
                "priority_levels": ["low", "medium", "high", "critical"],
                "compliance_requirements": ["pci_dss", "dpdp_act", "hotel_policies"],
                "business_scenarios": ["vip_guest", "high_value_transaction", "media_attention", "regulatory_scrutiny"]
            },
            "benchmarks": {
                "minimum_task_success_rate": 0.85,
                "maximum_response_time": 5.0,
                "minimum_compliance_score": 0.90,
                "maximum_hallucination_rate": 0.05,
                "minimum_safety_score": 0.95
            }
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default evaluation configuration"""
        
        return {
            "evaluation_timeout_seconds": 300,
            "parallel_test_execution": False,  # For deterministic results
            "detailed_logging": True,
            "save_results_to_file": True,
            "results_directory": "./evaluation_results",
            "benchmark_comparison": True,
            "generate_recommendations": True
        }


# Factory function for easy initialization
def create_agentic_evaluator(config: Optional[Dict[str, Any]] = None) -> AgenticSecurityEvaluator:
    """Create and configure an agentic security evaluator"""
    
    return AgenticSecurityEvaluator(evaluation_config=config)