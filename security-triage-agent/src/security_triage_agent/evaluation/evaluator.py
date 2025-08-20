"""
Incident Evaluation System for Security Triage Agent.

Provides comprehensive evaluation of incident processing quality, accuracy,
and effectiveness with structured criteria and scoring mechanisms.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.state import IncidentState, IncidentCategory, IncidentPriority
from .metrics_tracker import MetricsTracker


class EvaluationDimension(str, Enum):
    """Evaluation dimensions for incident processing."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    TIMELINESS = "timeliness"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"


class EvaluationCriteria(BaseModel):
    """Evaluation criteria for specific dimensions."""
    dimension: EvaluationDimension
    weight: float = Field(ge=0.0, le=1.0)
    min_threshold: float = Field(ge=0.0, le=1.0)
    target_score: float = Field(ge=0.0, le=1.0)
    evaluation_method: str
    success_indicators: List[str] = Field(default_factory=list)
    failure_indicators: List[str] = Field(default_factory=list)


class DimensionScore(BaseModel):
    """Score for a specific evaluation dimension."""
    dimension: EvaluationDimension
    score: float = Field(ge=0.0, le=1.0)
    max_possible: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)
    
    # Detailed breakdown
    criteria_met: List[str] = Field(default_factory=list)
    criteria_missed: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    
    # Evidence and reasoning
    evidence: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""


class EvaluationResult(BaseModel):
    """Comprehensive evaluation result for incident processing."""
    incident_id: str
    evaluation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Overall scores
    overall_score: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)
    grade: str  # A, B, C, D, F
    
    # Dimension scores
    dimension_scores: List[DimensionScore] = Field(default_factory=list)
    
    # Summary metrics
    total_criteria: int = 0
    criteria_met: int = 0
    criteria_missed: int = 0
    
    # Quality assessment
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Compliance and safety
    compliance_status: str = "unknown"  # compliant, non_compliant, partial
    safety_status: str = "unknown"     # safe, at_risk, unsafe
    
    # Benchmarking
    benchmark_comparison: Dict[str, float] = Field(default_factory=dict)
    industry_percentile: Optional[float] = None


class IncidentEvaluator:
    """
    Comprehensive incident evaluation system.
    
    Evaluates incident processing across multiple dimensions with
    structured criteria, weighted scoring, and detailed feedback.
    """
    
    def __init__(
        self,
        metrics_tracker: Optional[MetricsTracker] = None,
        custom_criteria: Optional[List[EvaluationCriteria]] = None
    ):
        self.metrics_tracker = metrics_tracker
        self.evaluation_criteria = custom_criteria or self._initialize_default_criteria()
        
        # Industry benchmarks for comparison
        self.industry_benchmarks = self._initialize_industry_benchmarks()
    
    def _initialize_default_criteria(self) -> List[EvaluationCriteria]:
        """Initialize default evaluation criteria for hospitality security."""
        
        criteria = []
        
        # Accuracy Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.ACCURACY,
            weight=0.2,
            min_threshold=0.8,
            target_score=0.95,
            evaluation_method="classification_and_prioritization_accuracy",
            success_indicators=[
                "correct_incident_classification",
                "appropriate_priority_assignment", 
                "accurate_risk_assessment",
                "relevant_playbook_selection"
            ],
            failure_indicators=[
                "misclassification_of_incident_type",
                "inappropriate_priority_level",
                "inaccurate_risk_evaluation",
                "irrelevant_response_plan"
            ]
        ))
        
        # Completeness Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.COMPLETENESS,
            weight=0.18,
            min_threshold=0.85,
            target_score=0.95,
            evaluation_method="response_completeness_analysis",
            success_indicators=[
                "comprehensive_immediate_actions",
                "detailed_investigation_steps",
                "complete_notification_plan",
                "thorough_documentation_requirements",
                "appropriate_follow_up_actions"
            ],
            failure_indicators=[
                "missing_critical_response_elements",
                "incomplete_stakeholder_notifications",
                "insufficient_investigation_procedures",
                "inadequate_documentation_plan"
            ]
        ))
        
        # Timeliness Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.TIMELINESS,
            weight=0.15,
            min_threshold=0.8,
            target_score=0.9,
            evaluation_method="sla_and_timeline_compliance",
            success_indicators=[
                "within_priority_sla_limits",
                "rapid_initial_response",
                "timely_stakeholder_notification",
                "appropriate_escalation_timing"
            ],
            failure_indicators=[
                "sla_violations",
                "delayed_critical_notifications",
                "slow_initial_response",
                "missed_escalation_windows"
            ]
        ))
        
        # Safety Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.SAFETY,
            weight=0.2,
            min_threshold=0.9,
            target_score=0.98,
            evaluation_method="safety_guardrails_assessment",
            success_indicators=[
                "guest_safety_prioritized",
                "employee_protection_measures",
                "pii_privacy_protection",
                "risk_mitigation_implemented",
                "safety_violations_addressed"
            ],
            failure_indicators=[
                "guest_safety_compromised",
                "privacy_violations",
                "inadequate_risk_controls",
                "safety_protocols_ignored"
            ]
        ))
        
        # Compliance Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.COMPLIANCE,
            weight=0.15,
            min_threshold=0.95,
            target_score=0.98,
            evaluation_method="regulatory_compliance_check",
            success_indicators=[
                "dpdp_requirements_met",
                "pci_dss_compliance_maintained",
                "notification_deadlines_observed",
                "documentation_standards_followed",
                "legal_requirements_satisfied"
            ],
            failure_indicators=[
                "regulatory_violations",
                "missed_notification_deadlines",
                "compliance_gaps",
                "inadequate_legal_review"
            ]
        ))
        
        # Efficiency Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.EFFICIENCY,
            weight=0.07,
            min_threshold=0.7,
            target_score=0.85,
            evaluation_method="automation_and_resource_optimization",
            success_indicators=[
                "high_automation_utilization",
                "minimal_human_intervention",
                "efficient_resource_allocation",
                "streamlined_workflow_execution"
            ],
            failure_indicators=[
                "excessive_manual_intervention",
                "workflow_inefficiencies",
                "resource_waste",
                "unnecessary_escalations"
            ]
        ))
        
        # Quality Criteria
        criteria.append(EvaluationCriteria(
            dimension=EvaluationDimension.QUALITY,
            weight=0.05,
            min_threshold=0.8,
            target_score=0.9,
            evaluation_method="output_quality_assessment",
            success_indicators=[
                "clear_response_instructions",
                "actionable_recommendations",
                "professional_communication",
                "comprehensive_analysis"
            ],
            failure_indicators=[
                "unclear_instructions",
                "vague_recommendations",
                "poor_communication_quality",
                "superficial_analysis"
            ]
        ))
        
        return criteria
    
    def _initialize_industry_benchmarks(self) -> Dict[str, float]:
        """Initialize hospitality industry benchmarks."""
        return {
            "guest_access_incidents_accuracy": 0.92,
            "payment_fraud_detection_rate": 0.95,
            "pii_breach_response_time": 0.88,
            "cyber_security_containment": 0.85,
            "compliance_adherence_rate": 0.96,
            "overall_incident_resolution": 0.89,
            "automation_efficiency": 0.82,
            "stakeholder_satisfaction": 0.87
        }
    
    async def evaluate_incident(self, incident_state: IncidentState) -> EvaluationResult:
        """
        Perform comprehensive evaluation of incident processing.
        
        Args:
            incident_state: Complete incident state to evaluate
            
        Returns:
            Comprehensive evaluation result
        """
        
        evaluation_result = EvaluationResult(
            incident_id=incident_state.incident_id
        )
        
        dimension_scores = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Evaluate each dimension
        for criteria in self.evaluation_criteria:
            dimension_score = await self._evaluate_dimension(
                incident_state, criteria
            )
            dimension_scores.append(dimension_score)
            
            total_weighted_score += dimension_score.weighted_score
            total_weight += dimension_score.weight
        
        evaluation_result.dimension_scores = dimension_scores
        
        # Calculate overall scores
        evaluation_result.weighted_score = total_weighted_score
        evaluation_result.overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Assign grade
        evaluation_result.grade = self._calculate_grade(evaluation_result.overall_score)
        
        # Calculate summary metrics
        all_criteria_met = sum(len(ds.criteria_met) for ds in dimension_scores)
        all_criteria_missed = sum(len(ds.criteria_missed) for ds in dimension_scores)
        
        evaluation_result.criteria_met = all_criteria_met
        evaluation_result.criteria_missed = all_criteria_missed
        evaluation_result.total_criteria = all_criteria_met + all_criteria_missed
        
        # Generate qualitative assessments
        evaluation_result.strengths = self._identify_strengths(dimension_scores)
        evaluation_result.weaknesses = self._identify_weaknesses(dimension_scores)
        evaluation_result.recommendations = self._generate_recommendations(dimension_scores)
        
        # Assess compliance and safety status
        evaluation_result.compliance_status = self._assess_compliance_status(dimension_scores)
        evaluation_result.safety_status = self._assess_safety_status(dimension_scores)
        
        # Benchmark comparison
        evaluation_result.benchmark_comparison = self._compare_to_benchmarks(
            incident_state, dimension_scores
        )
        evaluation_result.industry_percentile = self._calculate_industry_percentile(
            evaluation_result.overall_score
        )
        
        return evaluation_result
    
    async def _evaluate_dimension(
        self,
        incident_state: IncidentState,
        criteria: EvaluationCriteria
    ) -> DimensionScore:
        """Evaluate a specific dimension of incident processing."""
        
        dimension_score = DimensionScore(
            dimension=criteria.dimension,
            weight=criteria.weight,
            max_possible=1.0
        )
        
        # Route to specific evaluation method
        if criteria.evaluation_method == "classification_and_prioritization_accuracy":
            score = await self._evaluate_accuracy(incident_state, criteria)
        elif criteria.evaluation_method == "response_completeness_analysis":
            score = await self._evaluate_completeness(incident_state, criteria)
        elif criteria.evaluation_method == "sla_and_timeline_compliance":
            score = await self._evaluate_timeliness(incident_state, criteria)
        elif criteria.evaluation_method == "safety_guardrails_assessment":
            score = await self._evaluate_safety(incident_state, criteria)
        elif criteria.evaluation_method == "regulatory_compliance_check":
            score = await self._evaluate_compliance(incident_state, criteria)
        elif criteria.evaluation_method == "automation_and_resource_optimization":
            score = await self._evaluate_efficiency(incident_state, criteria)
        elif criteria.evaluation_method == "output_quality_assessment":
            score = await self._evaluate_quality(incident_state, criteria)
        else:
            score = 0.5  # Default moderate score
        
        dimension_score.score = score
        dimension_score.weighted_score = score * criteria.weight
        
        # Determine criteria met/missed
        if score >= criteria.target_score:
            dimension_score.criteria_met = criteria.success_indicators
        elif score >= criteria.min_threshold:
            # Partial success
            met_count = int(len(criteria.success_indicators) * score)
            dimension_score.criteria_met = criteria.success_indicators[:met_count]
            dimension_score.criteria_missed = criteria.success_indicators[met_count:]
        else:
            dimension_score.criteria_missed = criteria.success_indicators
            dimension_score.improvement_areas = criteria.failure_indicators
        
        return dimension_score
    
    async def _evaluate_accuracy(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate classification and prioritization accuracy."""
        
        accuracy_score = 0.0
        components = 0
        
        # Classification accuracy (if ground truth available)
        if incident_state.classification_confidence:
            accuracy_score += incident_state.classification_confidence
            components += 1
        
        # Risk assessment quality
        if incident_state.risk_assessment:
            risk_score = incident_state.risk_assessment.confidence_score
            accuracy_score += risk_score
            components += 1
        
        # Playbook selection appropriateness
        if incident_state.selected_playbook and incident_state.category:
            if incident_state.category in incident_state.selected_playbook.applicable_categories:
                accuracy_score += 0.9  # High score for appropriate selection
            else:
                accuracy_score += 0.3  # Low score for inappropriate selection
            components += 1
        
        # Tool results quality
        tool_results = incident_state.tool_results
        if tool_results:
            # Average confidence scores from tools
            confidences = []
            for result in tool_results.values():
                if isinstance(result, dict) and "confidence" in result:
                    confidences.append(result["confidence"])
            
            if confidences:
                accuracy_score += sum(confidences) / len(confidences)
                components += 1
        
        return accuracy_score / components if components > 0 else 0.5
    
    async def _evaluate_completeness(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate response completeness."""
        
        if not incident_state.incident_response:
            return 0.0
        
        response = incident_state.incident_response
        completeness_factors = []
        
        # Check each response component
        components = {
            "immediate_actions": response.immediate_actions,
            "investigation_steps": response.investigation_steps,
            "containment_measures": response.containment_measures,
            "notification_requirements": response.notification_requirements,
            "documentation_requirements": response.documentation_requirements,
            "follow_up_actions": response.follow_up_actions
        }
        
        for component_name, component_list in components.items():
            if component_list and len(component_list) > 0:
                # Score based on number of items (more comprehensive = higher score)
                if len(component_list) >= 3:
                    completeness_factors.append(1.0)
                elif len(component_list) >= 2:
                    completeness_factors.append(0.8)
                else:
                    completeness_factors.append(0.6)
            else:
                completeness_factors.append(0.0)
        
        # Calculate overall completeness
        base_completeness = sum(completeness_factors) / len(completeness_factors)
        
        # Bonus for category-specific completeness
        category_bonus = 0.0
        if incident_state.category and incident_state.selected_playbook:
            required_actions = set(incident_state.selected_playbook.required_actions)
            all_response_actions = set()
            for component_list in components.values():
                all_response_actions.update(component_list)
            
            action_coverage = len(required_actions & all_response_actions) / len(required_actions)
            category_bonus = action_coverage * 0.1  # Up to 10% bonus
        
        return min(1.0, base_completeness + category_bonus)
    
    async def _evaluate_timeliness(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate SLA and timeline compliance."""
        
        processing_time = (incident_state.updated_at - incident_state.created_at).total_seconds()
        
        # SLA compliance based on priority
        sla_targets = {
            IncidentPriority.CRITICAL: 900,    # 15 minutes
            IncidentPriority.HIGH: 3600,       # 1 hour
            IncidentPriority.MEDIUM: 14400,    # 4 hours
            IncidentPriority.LOW: 86400,       # 24 hours
            IncidentPriority.INFORMATIONAL: 259200  # 72 hours
        }
        
        if incident_state.severity:
            target_time = sla_targets.get(incident_state.severity, 3600)
            
            if processing_time <= target_time * 0.5:
                return 1.0  # Excellent timing
            elif processing_time <= target_time:
                return 0.9  # Good timing
            elif processing_time <= target_time * 1.5:
                return 0.7  # Acceptable timing
            elif processing_time <= target_time * 2:
                return 0.5  # Slow timing
            else:
                return 0.2  # Very slow timing
        
        return 0.5  # Default if no priority set
    
    async def _evaluate_safety(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate safety guardrails and protection measures."""
        
        safety_result = incident_state.tool_results.get("safety_check", {})
        
        if not safety_result:
            return 0.5  # Neutral if no safety check performed
        
        # Base score from safety check pass/fail
        base_score = 0.9 if safety_result.get("passed", False) else 0.3
        
        # Adjust for violations
        violations = safety_result.get("violations", [])
        if violations:
            critical_count = sum(1 for v in violations if v.get("severity") == "critical")
            high_count = sum(1 for v in violations if v.get("severity") == "high")
            medium_count = sum(1 for v in violations if v.get("severity") == "medium")
            
            violation_penalty = (critical_count * 0.4) + (high_count * 0.2) + (medium_count * 0.1)
            base_score = max(0.0, base_score - violation_penalty)
        
        # Bonus for appropriate human escalation
        if (safety_result.get("requires_human_review") and 
            incident_state.requires_human_intervention):
            base_score = min(1.0, base_score + 0.1)
        
        # Guest safety priority assessment
        if incident_state.category in [
            incident_state.category.GUEST_ACCESS,
            incident_state.category.PII_BREACH,
            incident_state.category.PHYSICAL_SECURITY
        ]:
            # Higher safety standards for guest-related incidents
            base_score *= 0.9 if base_score >= 0.8 else 0.7
        
        return base_score
    
    async def _evaluate_compliance(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate regulatory compliance adherence."""
        
        compliance_result = incident_state.tool_results.get("compliance_check", {})
        
        if not compliance_result:
            return 0.5  # Neutral if no compliance check
        
        # Framework compliance
        framework_checks = compliance_result.get("framework_checks", {})
        if framework_checks:
            passed_frameworks = sum(1 for passed in framework_checks.values() if passed)
            total_frameworks = len(framework_checks)
            framework_score = passed_frameworks / total_frameworks
        else:
            framework_score = 0.5
        
        # Violations penalty
        violations = compliance_result.get("violations", [])
        violation_penalty = min(0.5, len(violations) * 0.15)
        
        # Legal review appropriateness
        legal_bonus = 0.0
        if (compliance_result.get("requires_legal_review") and 
            incident_state.requires_human_intervention):
            legal_bonus = 0.05
        
        # Notification timeliness (if applicable)
        notification_score = 1.0  # Default to perfect if no notifications required
        notification_deadlines = compliance_result.get("notification_deadlines", {})
        if notification_deadlines:
            # This would be enhanced with actual deadline tracking
            # For now, assume compliance based on escalation
            if incident_state.requires_human_intervention:
                notification_score = 0.9  # Good score for escalation
            else:
                notification_score = 0.7  # Lower score without escalation
        
        compliance_score = (framework_score * 0.4 + notification_score * 0.3 + 
                          (1.0 - violation_penalty) * 0.3 + legal_bonus)
        
        return max(0.0, min(1.0, compliance_score))
    
    async def _evaluate_efficiency(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate automation and resource efficiency."""
        
        efficiency_factors = []
        
        # Automation utilization
        automation_score = 1.0 - (len(incident_state.approval_history) * 0.2)
        efficiency_factors.append(max(0.0, automation_score))
        
        # Workflow efficiency (completed vs failed steps)
        completed = len(incident_state.completed_steps)
        failed = len(incident_state.failed_steps)
        total_steps = completed + failed
        
        if total_steps > 0:
            workflow_efficiency = completed / total_steps
            efficiency_factors.append(workflow_efficiency)
        
        # Processing speed relative to complexity
        processing_time = (incident_state.updated_at - incident_state.created_at).total_seconds()
        complexity_estimate = len(incident_state.tool_results) + len(incident_state.completed_steps)
        
        if complexity_estimate > 0:
            time_per_operation = processing_time / complexity_estimate
            # Lower time per operation = higher efficiency
            speed_efficiency = max(0.0, min(1.0, 1.0 - (time_per_operation / 300)))  # 5 min baseline
            efficiency_factors.append(speed_efficiency)
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.5
    
    async def _evaluate_quality(
        self, incident_state: IncidentState, criteria: EvaluationCriteria
    ) -> float:
        """Evaluate output quality and professionalism."""
        
        quality_factors = []
        
        # Response plan quality
        if incident_state.incident_response:
            response = incident_state.incident_response
            
            # Action clarity and specificity
            all_actions = (response.immediate_actions + response.investigation_steps + 
                          response.containment_measures + response.follow_up_actions)
            
            if all_actions:
                # Assess action quality based on length and specificity
                avg_action_length = sum(len(action) for action in all_actions) / len(all_actions)
                clarity_score = min(1.0, avg_action_length / 50)  # 50 char baseline for good actions
                quality_factors.append(clarity_score)
        
        # Tool output quality
        tool_quality_scores = []
        for tool_result in incident_state.tool_results.values():
            if isinstance(tool_result, dict) and "confidence" in tool_result:
                tool_quality_scores.append(tool_result["confidence"])
        
        if tool_quality_scores:
            avg_tool_quality = sum(tool_quality_scores) / len(tool_quality_scores)
            quality_factors.append(avg_tool_quality)
        
        # Communication quality (based on message clarity)
        message_quality = 0.8  # Default good score
        if incident_state.messages:
            # Could enhance with actual content analysis
            quality_factors.append(message_quality)
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.7
    
    def _calculate_grade(self, overall_score: float) -> str:
        """Calculate letter grade from overall score."""
        if overall_score >= 0.9:
            return "A"
        elif overall_score >= 0.8:
            return "B"
        elif overall_score >= 0.7:
            return "C"
        elif overall_score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _identify_strengths(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify strengths from dimension scores."""
        strengths = []
        
        for ds in dimension_scores:
            if ds.score >= 0.9:
                strengths.append(f"Excellent {ds.dimension.value} performance")
            elif ds.score >= 0.8:
                strengths.append(f"Strong {ds.dimension.value} execution")
        
        return strengths
    
    def _identify_weaknesses(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify weaknesses from dimension scores."""
        weaknesses = []
        
        for ds in dimension_scores:
            if ds.score < 0.6:
                weaknesses.append(f"Poor {ds.dimension.value} performance")
            elif ds.score < 0.8:
                weaknesses.append(f"Below-target {ds.dimension.value} execution")
        
        return weaknesses
    
    def _generate_recommendations(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Find lowest scoring dimensions
        lowest_scores = sorted(dimension_scores, key=lambda x: x.score)[:2]
        
        for ds in lowest_scores:
            if ds.score < 0.8:
                if ds.dimension == EvaluationDimension.ACCURACY:
                    recommendations.append(
                        "Improve classification accuracy through better training data and validation"
                    )
                elif ds.dimension == EvaluationDimension.TIMELINESS:
                    recommendations.append(
                        "Optimize workflow timing and reduce processing delays"
                    )
                elif ds.dimension == EvaluationDimension.SAFETY:
                    recommendations.append(
                        "Strengthen safety protocols and violation detection"
                    )
                elif ds.dimension == EvaluationDimension.COMPLIANCE:
                    recommendations.append(
                        "Enhance compliance checking and regulatory adherence"
                    )
        
        return recommendations
    
    def _assess_compliance_status(self, dimension_scores: List[DimensionScore]) -> str:
        """Assess overall compliance status."""
        compliance_score = next(
            (ds.score for ds in dimension_scores if ds.dimension == EvaluationDimension.COMPLIANCE),
            0.5
        )
        
        if compliance_score >= 0.95:
            return "compliant"
        elif compliance_score >= 0.8:
            return "partial"
        else:
            return "non_compliant"
    
    def _assess_safety_status(self, dimension_scores: List[DimensionScore]) -> str:
        """Assess overall safety status."""
        safety_score = next(
            (ds.score for ds in dimension_scores if ds.dimension == EvaluationDimension.SAFETY),
            0.5
        )
        
        if safety_score >= 0.9:
            return "safe"
        elif safety_score >= 0.7:
            return "at_risk"
        else:
            return "unsafe"
    
    def _compare_to_benchmarks(
        self,
        incident_state: IncidentState,
        dimension_scores: List[DimensionScore]
    ) -> Dict[str, float]:
        """Compare performance to industry benchmarks."""
        
        comparison = {}
        
        # Category-specific benchmarks
        if incident_state.category:
            category_key = f"{incident_state.category.value}_accuracy"
            if category_key in self.industry_benchmarks:
                accuracy_score = next(
                    (ds.score for ds in dimension_scores if ds.dimension == EvaluationDimension.ACCURACY),
                    0.5
                )
                comparison[category_key] = accuracy_score - self.industry_benchmarks[category_key]
        
        # General benchmarks
        overall_score = sum(ds.weighted_score for ds in dimension_scores)
        comparison["overall_vs_industry"] = overall_score - self.industry_benchmarks.get(
            "overall_incident_resolution", 0.89
        )
        
        return comparison
    
    def _calculate_industry_percentile(self, overall_score: float) -> float:
        """Calculate industry percentile based on overall score."""
        # Simplified percentile calculation
        # In practice, this would use historical industry data
        
        if overall_score >= 0.95:
            return 95.0
        elif overall_score >= 0.9:
            return 85.0
        elif overall_score >= 0.8:
            return 70.0
        elif overall_score >= 0.7:
            return 50.0
        elif overall_score >= 0.6:
            return 30.0
        else:
            return 15.0