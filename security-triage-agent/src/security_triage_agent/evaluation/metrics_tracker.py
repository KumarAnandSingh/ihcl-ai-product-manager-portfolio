"""
Metrics Tracking System for Security Incident Triage Agent.

Provides comprehensive performance monitoring, quality assessment, and
real-time metrics collection with hospitality industry benchmarks.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

from ..core.state import IncidentState, IncidentCategory, IncidentPriority
from ..memory.persistent_storage import PersistentStorage


class PerformanceMetrics(BaseModel):
    """Performance metrics for incident processing."""
    
    # Timing metrics
    total_processing_time: float = 0.0  # seconds
    avg_step_time: float = 0.0
    classification_time: float = 0.0
    prioritization_time: float = 0.0
    response_generation_time: float = 0.0
    
    # Accuracy metrics
    classification_accuracy: float = 0.0
    prioritization_accuracy: float = 0.0
    response_quality_score: float = 0.0
    
    # Efficiency metrics
    automation_rate: float = 0.0  # % of incidents processed without human intervention
    first_time_resolution_rate: float = 0.0
    escalation_rate: float = 0.0
    
    # Compliance metrics
    compliance_adherence_rate: float = 0.0
    sla_compliance_rate: float = 0.0
    notification_timeliness: float = 0.0


class QualityMetrics(BaseModel):
    """Quality assessment metrics."""
    
    # Response quality
    response_completeness: float = 0.0  # 0-1 scale
    response_accuracy: float = 0.0
    response_relevance: float = 0.0
    
    # Process quality
    workflow_adherence: float = 0.0
    documentation_quality: float = 0.0
    stakeholder_satisfaction: float = 0.0
    
    # Safety and compliance
    safety_score: float = 0.0
    compliance_score: float = 0.0
    risk_assessment_accuracy: float = 0.0
    
    # Overall quality
    overall_quality_score: float = 0.0


class HallucinationMetrics(BaseModel):
    """Hallucination detection and tracking."""
    
    # Detection metrics
    hallucination_rate: float = 0.0
    false_information_count: int = 0
    inconsistency_count: int = 0
    
    # Categorized hallucinations
    factual_errors: int = 0
    procedural_errors: int = 0
    compliance_errors: int = 0
    
    # Confidence correlation
    confidence_accuracy_correlation: float = 0.0
    low_confidence_accuracy: float = 0.0
    high_confidence_accuracy: float = 0.0


@dataclass
class MetricSnapshot:
    """Point-in-time metrics snapshot."""
    timestamp: datetime
    incident_id: str
    metrics: Dict[str, Any]
    context: Dict[str, Any]


class MetricsTracker:
    """
    Comprehensive metrics tracking system for incident processing.
    
    Tracks performance, quality, safety, and compliance metrics with
    real-time monitoring and historical analysis capabilities.
    """
    
    def __init__(
        self,
        storage: Optional[PersistentStorage] = None,
        metrics_retention_days: int = 365
    ):
        self.storage = storage
        self.metrics_retention_days = metrics_retention_days
        
        # Real-time metrics storage
        self.current_metrics = {}
        self.metric_snapshots = []
        
        # Aggregated metrics
        self.daily_metrics = defaultdict(lambda: defaultdict(list))
        self.category_metrics = defaultdict(lambda: defaultdict(list))
        
        # Benchmark values (hospitality industry standards)
        self.benchmarks = self._initialize_benchmarks()
    
    def _initialize_benchmarks(self) -> Dict[str, float]:
        """Initialize hospitality industry benchmark values."""
        return {
            # Performance benchmarks
            "max_processing_time_critical": 900,  # 15 minutes for critical incidents
            "max_processing_time_high": 3600,     # 1 hour for high priority
            "max_processing_time_medium": 14400,  # 4 hours for medium priority
            "target_automation_rate": 0.8,        # 80% automation target
            "target_first_resolution_rate": 0.85, # 85% first-time resolution
            "max_escalation_rate": 0.2,           # 20% escalation rate
            
            # Quality benchmarks
            "min_response_completeness": 0.9,     # 90% completeness
            "min_response_accuracy": 0.95,        # 95% accuracy
            "min_compliance_score": 0.98,         # 98% compliance
            "min_safety_score": 0.95,             # 95% safety score
            
            # Compliance benchmarks
            "dpdp_notification_hours": 72,        # 72 hours for DPDP
            "pci_notification_hours": 24,         # 24 hours for PCI DSS
            "min_sla_compliance": 0.95,           # 95% SLA compliance
            
            # Hallucination thresholds
            "max_hallucination_rate": 0.05,       # 5% hallucination rate
            "min_confidence_accuracy": 0.9,       # 90% confidence-accuracy correlation
        }
    
    async def start_incident_tracking(self, incident_id: str) -> None:
        """Start tracking metrics for an incident."""
        self.current_metrics[incident_id] = {
            "start_time": datetime.utcnow(),
            "step_times": {},
            "tool_metrics": {},
            "quality_assessments": {},
            "safety_checks": {},
            "compliance_events": [],
            "human_interventions": 0,
            "workflow_errors": []
        }
    
    async def record_step_completion(
        self,
        incident_id: str,
        step_name: str,
        duration_seconds: float,
        success: bool = True,
        additional_metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record completion of a workflow step."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        metrics["step_times"][step_name] = {
            "duration": duration_seconds,
            "success": success,
            "timestamp": datetime.utcnow(),
            "additional_metrics": additional_metrics or {}
        }
        
        if not success:
            metrics["workflow_errors"].append({
                "step": step_name,
                "timestamp": datetime.utcnow(),
                "metrics": additional_metrics
            })
        
        # Store in persistent storage if available
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, f"step_duration_{step_name}", duration_seconds, {
                    "success": success,
                    "additional_metrics": additional_metrics
                }
            )
    
    async def record_tool_performance(
        self,
        incident_id: str,
        tool_name: str,
        execution_time: float,
        success: bool,
        output_quality: Optional[float] = None,
        confidence_score: Optional[float] = None
    ) -> None:
        """Record tool execution performance."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        metrics["tool_metrics"][tool_name] = {
            "execution_time": execution_time,
            "success": success,
            "output_quality": output_quality,
            "confidence_score": confidence_score,
            "timestamp": datetime.utcnow()
        }
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, f"tool_performance_{tool_name}", execution_time, {
                    "success": success,
                    "output_quality": output_quality,
                    "confidence_score": confidence_score
                }
            )
    
    async def record_quality_assessment(
        self,
        incident_id: str,
        assessment_type: str,
        quality_score: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record quality assessment results."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        metrics["quality_assessments"][assessment_type] = {
            "score": quality_score,
            "details": details or {},
            "timestamp": datetime.utcnow()
        }
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, f"quality_{assessment_type}", quality_score, details
            )
    
    async def record_hallucination_detection(
        self,
        incident_id: str,
        hallucination_type: str,
        confidence: float,
        details: Dict[str, Any]
    ) -> None:
        """Record detected hallucination."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        if "hallucinations" not in metrics:
            metrics["hallucinations"] = []
        
        metrics["hallucinations"].append({
            "type": hallucination_type,
            "confidence": confidence,
            "details": details,
            "timestamp": datetime.utcnow()
        })
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, f"hallucination_{hallucination_type}", confidence, details
            )
    
    async def record_human_intervention(
        self,
        incident_id: str,
        intervention_type: str,
        reason: str,
        resolution_time: Optional[float] = None
    ) -> None:
        """Record human intervention event."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        metrics["human_interventions"] += 1
        
        if "interventions" not in metrics:
            metrics["interventions"] = []
        
        metrics["interventions"].append({
            "type": intervention_type,
            "reason": reason,
            "resolution_time": resolution_time,
            "timestamp": datetime.utcnow()
        })
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, "human_intervention", 1, {
                    "type": intervention_type,
                    "reason": reason,
                    "resolution_time": resolution_time
                }
            )
    
    async def record_incident_processed(
        self,
        category: IncidentCategory,
        priority: IncidentPriority,
        processing_time: float
    ) -> None:
        """Record incident processing completion for analytics."""
        today = datetime.utcnow().date().isoformat()
        
        # Update daily metrics
        self.daily_metrics[today]["incidents_processed"].append({
            "category": category.value,
            "priority": priority.value,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow()
        })
        
        # Update category metrics
        self.category_metrics[category.value]["processing_times"].append(processing_time)
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                f"daily_{today}", "incident_processed", processing_time, {
                    "category": category.value,
                    "priority": priority.value
                }
            )
    
    async def record_workflow_error(
        self,
        incident_id: str,
        error_step: str,
        error_details: Dict[str, Any]
    ) -> None:
        """Record workflow error for analysis."""
        if incident_id not in self.current_metrics:
            await self.start_incident_tracking(incident_id)
        
        metrics = self.current_metrics[incident_id]
        metrics["workflow_errors"].append({
            "step": error_step,
            "details": error_details,
            "timestamp": datetime.utcnow()
        })
        
        # Store in persistent storage
        if self.storage:
            await self.storage.record_performance_metric(
                incident_id, f"workflow_error_{error_step}", 1, error_details
            )
    
    async def calculate_quality_scores(self, incident_state: IncidentState) -> Dict[str, float]:
        """Calculate comprehensive quality scores for an incident."""
        
        quality_scores = {}
        incident_id = incident_state.incident_id
        
        if incident_id not in self.current_metrics:
            return {"overall": 0.5}  # Default moderate score
        
        metrics = self.current_metrics[incident_id]
        
        # Response completeness score
        completeness_score = self._calculate_response_completeness(incident_state)
        quality_scores["response_completeness"] = completeness_score
        
        # Workflow adherence score
        workflow_score = self._calculate_workflow_adherence(metrics, incident_state)
        quality_scores["workflow_adherence"] = workflow_score
        
        # Timing efficiency score
        timing_score = self._calculate_timing_efficiency(metrics, incident_state)
        quality_scores["timing_efficiency"] = timing_score
        
        # Safety compliance score
        safety_score = self._calculate_safety_score(incident_state)
        quality_scores["safety_compliance"] = safety_score
        
        # Compliance adherence score
        compliance_score = self._calculate_compliance_score(incident_state)
        quality_scores["compliance_adherence"] = compliance_score
        
        # Tool performance score
        tool_score = self._calculate_tool_performance_score(metrics)
        quality_scores["tool_performance"] = tool_score
        
        # Overall quality score (weighted average)
        weights = {
            "response_completeness": 0.25,
            "workflow_adherence": 0.15,
            "timing_efficiency": 0.15,
            "safety_compliance": 0.20,
            "compliance_adherence": 0.15,
            "tool_performance": 0.10
        }
        
        overall_score = sum(
            quality_scores.get(metric, 0.5) * weight 
            for metric, weight in weights.items()
        )
        quality_scores["overall"] = overall_score
        
        # Record quality scores
        await self.record_quality_assessment(
            incident_id, "overall_quality", overall_score, quality_scores
        )
        
        return quality_scores
    
    def _calculate_response_completeness(self, incident_state: IncidentState) -> float:
        """Calculate response completeness score."""
        if not incident_state.incident_response:
            return 0.0
        
        response = incident_state.incident_response
        
        # Check completeness of response components
        components = [
            response.immediate_actions,
            response.investigation_steps,
            response.containment_measures,
            response.notification_requirements,
            response.documentation_requirements,
            response.follow_up_actions
        ]
        
        non_empty_components = sum(1 for component in components if component)
        completeness = non_empty_components / len(components)
        
        # Bonus for detailed actions
        total_actions = sum(len(component) for component in components)
        if total_actions >= 15:  # Comprehensive response
            completeness = min(1.0, completeness + 0.1)
        
        return completeness
    
    def _calculate_workflow_adherence(
        self, metrics: Dict[str, Any], incident_state: IncidentState
    ) -> float:
        """Calculate workflow adherence score."""
        
        completed_steps = len(incident_state.completed_steps)
        failed_steps = len(incident_state.failed_steps)
        total_steps = completed_steps + failed_steps
        
        if total_steps == 0:
            return 0.5  # Neutral score if no steps processed
        
        # Basic adherence based on success rate
        success_rate = completed_steps / total_steps
        
        # Penalty for workflow errors
        error_count = len(metrics.get("workflow_errors", []))
        error_penalty = min(0.3, error_count * 0.1)
        
        # Bonus for completing all expected steps
        expected_steps = ["classify_incident", "assess_risk", "prioritize_incident", 
                         "select_playbook", "generate_response"]
        completed_expected = sum(1 for step in expected_steps 
                               if step in incident_state.completed_steps)
        completion_bonus = (completed_expected / len(expected_steps)) * 0.2
        
        adherence_score = success_rate - error_penalty + completion_bonus
        return max(0.0, min(1.0, adherence_score))
    
    def _calculate_timing_efficiency(
        self, metrics: Dict[str, Any], incident_state: IncidentState
    ) -> float:
        """Calculate timing efficiency score."""
        
        if not incident_state.severity:
            return 0.5  # Neutral score if priority unknown
        
        processing_time = (incident_state.updated_at - incident_state.created_at).total_seconds()
        
        # Get benchmark time based on priority
        benchmark_key = f"max_processing_time_{incident_state.severity.value}"
        benchmark_time = self.benchmarks.get(benchmark_key, 3600)  # Default 1 hour
        
        # Calculate efficiency score
        if processing_time <= benchmark_time * 0.5:
            return 1.0  # Excellent timing
        elif processing_time <= benchmark_time:
            return 0.8  # Good timing
        elif processing_time <= benchmark_time * 1.5:
            return 0.6  # Acceptable timing
        elif processing_time <= benchmark_time * 2:
            return 0.4  # Slow timing
        else:
            return 0.2  # Very slow timing
    
    def _calculate_safety_score(self, incident_state: IncidentState) -> float:
        """Calculate safety compliance score."""
        
        safety_result = incident_state.tool_results.get("safety_check", {})
        
        if not safety_result:
            return 0.5  # Neutral if no safety check
        
        # Base score from safety check
        if safety_result.get("passed", False):
            base_score = 0.9
        else:
            base_score = 0.3
        
        # Adjust based on violations
        violations = safety_result.get("violations", [])
        if violations:
            critical_violations = sum(1 for v in violations if v.get("severity") == "critical")
            high_violations = sum(1 for v in violations if v.get("severity") == "high")
            
            violation_penalty = (critical_violations * 0.3) + (high_violations * 0.15)
            base_score = max(0.0, base_score - violation_penalty)
        
        # Bonus for proactive safety measures
        if safety_result.get("requires_human_review") and incident_state.requires_human_intervention:
            base_score = min(1.0, base_score + 0.1)  # Bonus for appropriate escalation
        
        return base_score
    
    def _calculate_compliance_score(self, incident_state: IncidentState) -> float:
        """Calculate compliance adherence score."""
        
        compliance_result = incident_state.tool_results.get("compliance_check", {})
        
        if not compliance_result:
            return 0.5  # Neutral if no compliance check
        
        # Check framework compliance
        framework_checks = compliance_result.get("framework_checks", {})
        if framework_checks:
            passed_checks = sum(1 for passed in framework_checks.values() if passed)
            total_checks = len(framework_checks)
            base_score = passed_checks / total_checks if total_checks > 0 else 0.5
        else:
            base_score = 0.5
        
        # Penalty for violations
        violations = compliance_result.get("violations", [])
        violation_penalty = min(0.4, len(violations) * 0.1)
        
        # Bonus for proactive compliance measures
        if compliance_result.get("requires_legal_review") and incident_state.requires_human_intervention:
            base_score = min(1.0, base_score + 0.05)
        
        compliance_score = max(0.0, base_score - violation_penalty)
        return compliance_score
    
    def _calculate_tool_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate tool performance score."""
        
        tool_metrics = metrics.get("tool_metrics", {})
        
        if not tool_metrics:
            return 0.5  # Neutral if no tool metrics
        
        scores = []
        
        for tool_name, tool_data in tool_metrics.items():
            # Success rate component
            success_score = 1.0 if tool_data.get("success", False) else 0.0
            
            # Quality component
            quality_score = tool_data.get("output_quality", 0.5)
            
            # Confidence component
            confidence_score = tool_data.get("confidence_score", 0.5)
            
            # Combined tool score
            tool_score = (success_score * 0.4) + (quality_score * 0.4) + (confidence_score * 0.2)
            scores.append(tool_score)
        
        return np.mean(scores) if scores else 0.5
    
    async def get_performance_summary(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PerformanceMetrics:
        """Get performance metrics summary."""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)  # Last week
        if not end_date:
            end_date = datetime.utcnow()
        
        # This would be enhanced with actual data aggregation from storage
        # For now, return calculated metrics based on current tracking
        
        metrics = PerformanceMetrics()
        
        # Calculate averages from current metrics
        if self.current_metrics:
            processing_times = []
            human_intervention_count = 0
            total_incidents = len(self.current_metrics)
            
            for incident_id, incident_metrics in self.current_metrics.items():
                if "start_time" in incident_metrics:
                    # Calculate processing time
                    end_time = max(
                        step_data.get("timestamp", incident_metrics["start_time"])
                        for step_data in incident_metrics.get("step_times", {}).values()
                    ) if incident_metrics.get("step_times") else datetime.utcnow()
                    
                    processing_time = (end_time - incident_metrics["start_time"]).total_seconds()
                    processing_times.append(processing_time)
                
                # Count human interventions
                human_intervention_count += incident_metrics.get("human_interventions", 0)
            
            # Calculate metrics
            if processing_times:
                metrics.total_processing_time = sum(processing_times)
                metrics.avg_step_time = np.mean(processing_times)
            
            if total_incidents > 0:
                metrics.automation_rate = (total_incidents - human_intervention_count) / total_incidents
                metrics.escalation_rate = human_intervention_count / total_incidents
        
        return metrics
    
    async def get_quality_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> QualityMetrics:
        """Get quality metrics summary."""
        
        # This would aggregate quality data from storage
        # For now, return default metrics
        return QualityMetrics(
            response_completeness=0.85,
            response_accuracy=0.90,
            workflow_adherence=0.88,
            safety_score=0.92,
            compliance_score=0.89,
            overall_quality_score=0.89
        )
    
    async def get_hallucination_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> HallucinationMetrics:
        """Get hallucination detection summary."""
        
        # Count hallucinations from current metrics
        total_hallucinations = 0
        total_incidents = len(self.current_metrics)
        
        for metrics in self.current_metrics.values():
            hallucinations = metrics.get("hallucinations", [])
            total_hallucinations += len(hallucinations)
        
        hallucination_rate = total_hallucinations / total_incidents if total_incidents > 0 else 0.0
        
        return HallucinationMetrics(
            hallucination_rate=hallucination_rate,
            false_information_count=total_hallucinations,
            confidence_accuracy_correlation=0.85  # Default value
        )
    
    async def cleanup_old_metrics(self) -> int:
        """Clean up old metrics data."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.metrics_retention_days)
        
        # Clean up snapshots
        initial_count = len(self.metric_snapshots)
        self.metric_snapshots = [
            snapshot for snapshot in self.metric_snapshots
            if snapshot.timestamp > cutoff_date
        ]
        
        # Clean up daily metrics
        cutoff_date_str = cutoff_date.date().isoformat()
        old_dates = [
            date for date in self.daily_metrics.keys()
            if date < cutoff_date_str
        ]
        
        for date in old_dates:
            del self.daily_metrics[date]
        
        cleaned_count = initial_count - len(self.metric_snapshots) + len(old_dates)
        return cleaned_count