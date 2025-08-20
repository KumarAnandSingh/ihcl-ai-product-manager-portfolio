"""
Hospitality Industry Benchmarks for Security Incident Triage.

Provides industry-specific benchmarks, performance standards, and
comparative analysis for hospitality security operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

from ..core.state import IncidentCategory, IncidentPriority


class BenchmarkCategory(str, Enum):
    """Categories of benchmarks."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    SAFETY = "safety"
    EFFICIENCY = "efficiency"
    CUSTOMER_IMPACT = "customer_impact"


class BenchmarkMetric(BaseModel):
    """Individual benchmark metric."""
    metric_name: str
    category: BenchmarkCategory
    target_value: float
    threshold_value: float  # Minimum acceptable value
    unit: str
    description: str
    measurement_method: str
    
    # Industry context
    industry_average: Optional[float] = None
    best_in_class: Optional[float] = None
    regulatory_requirement: Optional[float] = None
    
    # Hospitality-specific context
    guest_impact_level: str = "low"  # low, medium, high, critical
    business_criticality: str = "medium"  # low, medium, high, critical


class BenchmarkComparison(BaseModel):
    """Comparison against benchmarks."""
    metric_name: str
    actual_value: float
    target_value: float
    threshold_value: float
    
    # Performance assessment
    meets_threshold: bool
    meets_target: bool
    performance_ratio: float  # actual/target
    
    # Relative performance
    vs_industry_average: Optional[float] = None
    vs_best_in_class: Optional[float] = None
    percentile_ranking: Optional[float] = None
    
    # Qualitative assessment
    performance_level: str  # "excellent", "good", "acceptable", "poor", "critical"
    improvement_needed: bool
    priority_level: str  # "low", "medium", "high", "critical"


class HospitalityBenchmarks:
    """
    Comprehensive benchmarks for hospitality security incident management.
    
    Provides industry standards, regulatory requirements, and best practices
    for security incident triage and response in hospitality environments.
    """
    
    def __init__(self):
        self.benchmarks = self._initialize_benchmarks()
        self.category_weights = self._initialize_category_weights()
        self.property_type_adjustments = self._initialize_property_adjustments()
    
    def _initialize_benchmarks(self) -> Dict[str, BenchmarkMetric]:
        """Initialize comprehensive hospitality security benchmarks."""
        
        benchmarks = {}
        
        # === PERFORMANCE BENCHMARKS ===
        
        # Response Time Benchmarks
        benchmarks["critical_incident_response_time"] = BenchmarkMetric(
            metric_name="critical_incident_response_time",
            category=BenchmarkCategory.PERFORMANCE,
            target_value=15.0,  # 15 minutes
            threshold_value=30.0,  # 30 minutes maximum
            unit="minutes",
            description="Maximum time to begin response for critical security incidents",
            measurement_method="time_from_detection_to_first_action",
            industry_average=22.0,
            best_in_class=10.0,
            regulatory_requirement=60.0,  # Some regulations require 1 hour
            guest_impact_level="critical",
            business_criticality="critical"
        )
        
        benchmarks["high_priority_response_time"] = BenchmarkMetric(
            metric_name="high_priority_response_time",
            category=BenchmarkCategory.PERFORMANCE,
            target_value=60.0,  # 1 hour
            threshold_value=120.0,  # 2 hours maximum
            unit="minutes",
            description="Maximum time to begin response for high priority incidents",
            measurement_method="time_from_detection_to_first_action",
            industry_average=85.0,
            best_in_class=45.0,
            guest_impact_level="high",
            business_criticality="high"
        )
        
        benchmarks["medium_priority_response_time"] = BenchmarkMetric(
            metric_name="medium_priority_response_time",
            category=BenchmarkCategory.PERFORMANCE,
            target_value=240.0,  # 4 hours
            threshold_value=480.0,  # 8 hours maximum
            unit="minutes",
            description="Maximum time to begin response for medium priority incidents",
            measurement_method="time_from_detection_to_first_action",
            industry_average=320.0,
            best_in_class=180.0,
            guest_impact_level="medium",
            business_criticality="medium"
        )
        
        # Resolution Time Benchmarks
        benchmarks["incident_resolution_time"] = BenchmarkMetric(
            metric_name="incident_resolution_time",
            category=BenchmarkCategory.PERFORMANCE,
            target_value=24.0,  # 24 hours
            threshold_value=72.0,  # 72 hours maximum
            unit="hours",
            description="Average time to fully resolve security incidents",
            measurement_method="time_from_detection_to_closure",
            industry_average=36.0,
            best_in_class=18.0,
            guest_impact_level="medium",
            business_criticality="high"
        )
        
        # === QUALITY BENCHMARKS ===
        
        # Accuracy Benchmarks
        benchmarks["classification_accuracy"] = BenchmarkMetric(
            metric_name="classification_accuracy",
            category=BenchmarkCategory.QUALITY,
            target_value=0.95,  # 95%
            threshold_value=0.85,  # 85% minimum
            unit="percentage",
            description="Accuracy of incident classification",
            measurement_method="correct_classifications_vs_total",
            industry_average=0.88,
            best_in_class=0.97,
            guest_impact_level="medium",
            business_criticality="high"
        )
        
        benchmarks["risk_assessment_accuracy"] = BenchmarkMetric(
            metric_name="risk_assessment_accuracy",
            category=BenchmarkCategory.QUALITY,
            target_value=0.90,  # 90%
            threshold_value=0.80,  # 80% minimum
            unit="percentage",
            description="Accuracy of risk level assessments",
            measurement_method="accurate_risk_scores_vs_total",
            industry_average=0.83,
            best_in_class=0.94,
            guest_impact_level="high",
            business_criticality="critical"
        )
        
        benchmarks["first_time_resolution_rate"] = BenchmarkMetric(
            metric_name="first_time_resolution_rate",
            category=BenchmarkCategory.QUALITY,
            target_value=0.85,  # 85%
            threshold_value=0.70,  # 70% minimum
            unit="percentage",
            description="Percentage of incidents resolved without reopening",
            measurement_method="incidents_resolved_first_time_vs_total",
            industry_average=0.76,
            best_in_class=0.92,
            guest_impact_level="medium",
            business_criticality="high"
        )
        
        # === COMPLIANCE BENCHMARKS ===
        
        # Regulatory Compliance
        benchmarks["dpdp_notification_compliance"] = BenchmarkMetric(
            metric_name="dpdp_notification_compliance",
            category=BenchmarkCategory.COMPLIANCE,
            target_value=1.0,  # 100%
            threshold_value=0.98,  # 98% minimum
            unit="percentage",
            description="Compliance with DPDP notification requirements",
            measurement_method="timely_notifications_vs_required",
            regulatory_requirement=1.0,
            guest_impact_level="high",
            business_criticality="critical"
        )
        
        benchmarks["pci_dss_compliance_rate"] = BenchmarkMetric(
            metric_name="pci_dss_compliance_rate",
            category=BenchmarkCategory.COMPLIANCE,
            target_value=1.0,  # 100%
            threshold_value=0.95,  # 95% minimum
            unit="percentage",
            description="Compliance with PCI DSS requirements",
            measurement_method="compliant_incidents_vs_total",
            regulatory_requirement=1.0,
            guest_impact_level="high",
            business_criticality="critical"
        )
        
        benchmarks["notification_timeliness"] = BenchmarkMetric(
            metric_name="notification_timeliness",
            category=BenchmarkCategory.COMPLIANCE,
            target_value=0.95,  # 95%
            threshold_value=0.90,  # 90% minimum
            unit="percentage",
            description="Percentage of notifications sent within required timeframes",
            measurement_method="timely_notifications_vs_total",
            industry_average=0.87,
            best_in_class=0.98,
            guest_impact_level="high",
            business_criticality="critical"
        )
        
        # === SAFETY BENCHMARKS ===
        
        # Safety Performance
        benchmarks["guest_safety_incident_rate"] = BenchmarkMetric(
            metric_name="guest_safety_incident_rate",
            category=BenchmarkCategory.SAFETY,
            target_value=0.02,  # 2% of incidents affect guest safety
            threshold_value=0.05,  # 5% maximum
            unit="percentage",
            description="Percentage of incidents that compromise guest safety",
            measurement_method="safety_incidents_vs_total",
            industry_average=0.035,
            best_in_class=0.01,
            guest_impact_level="critical",
            business_criticality="critical"
        )
        
        benchmarks["privacy_violation_rate"] = BenchmarkMetric(
            metric_name="privacy_violation_rate",
            category=BenchmarkCategory.SAFETY,
            target_value=0.01,  # 1% of incidents involve privacy violations
            threshold_value=0.03,  # 3% maximum
            unit="percentage",
            description="Percentage of incidents involving privacy violations",
            measurement_method="privacy_violations_vs_total",
            industry_average=0.025,
            best_in_class=0.005,
            guest_impact_level="critical",
            business_criticality="critical"
        )
        
        # === EFFICIENCY BENCHMARKS ===
        
        # Automation and Resource Efficiency
        benchmarks["automation_rate"] = BenchmarkMetric(
            metric_name="automation_rate",
            category=BenchmarkCategory.EFFICIENCY,
            target_value=0.80,  # 80% automated processing
            threshold_value=0.65,  # 65% minimum
            unit="percentage",
            description="Percentage of incidents processed with minimal human intervention",
            measurement_method="automated_incidents_vs_total",
            industry_average=0.72,
            best_in_class=0.88,
            guest_impact_level="low",
            business_criticality="medium"
        )
        
        benchmarks["escalation_rate"] = BenchmarkMetric(
            metric_name="escalation_rate",
            category=BenchmarkCategory.EFFICIENCY,
            target_value=0.15,  # 15% escalation rate
            threshold_value=0.25,  # 25% maximum
            unit="percentage",
            description="Percentage of incidents requiring escalation",
            measurement_method="escalated_incidents_vs_total",
            industry_average=0.22,
            best_in_class=0.12,
            guest_impact_level="medium",
            business_criticality="medium"
        )
        
        benchmarks["resource_utilization"] = BenchmarkMetric(
            metric_name="resource_utilization",
            category=BenchmarkCategory.EFFICIENCY,
            target_value=0.85,  # 85% resource utilization
            threshold_value=0.70,  # 70% minimum
            unit="percentage",
            description="Efficiency of security resource utilization",
            measurement_method="productive_time_vs_total_time",
            industry_average=0.78,
            best_in_class=0.92,
            guest_impact_level="low",
            business_criticality="medium"
        )
        
        # === CUSTOMER IMPACT BENCHMARKS ===
        
        # Guest Experience Protection
        benchmarks["guest_disruption_minimization"] = BenchmarkMetric(
            metric_name="guest_disruption_minimization",
            category=BenchmarkCategory.CUSTOMER_IMPACT,
            target_value=0.95,  # 95% of incidents cause minimal guest disruption
            threshold_value=0.85,  # 85% minimum
            unit="percentage",
            description="Percentage of incidents with minimal guest experience impact",
            measurement_method="low_impact_incidents_vs_total",
            industry_average=0.89,
            best_in_class=0.97,
            guest_impact_level="critical",
            business_criticality="critical"
        )
        
        benchmarks["guest_notification_satisfaction"] = BenchmarkMetric(
            metric_name="guest_notification_satisfaction",
            category=BenchmarkCategory.CUSTOMER_IMPACT,
            target_value=0.90,  # 90% satisfaction with notifications
            threshold_value=0.80,  # 80% minimum
            unit="percentage",
            description="Guest satisfaction with incident notifications and communication",
            measurement_method="satisfied_guests_vs_notified_guests",
            industry_average=0.82,
            best_in_class=0.95,
            guest_impact_level="high",
            business_criticality="high"
        )
        
        return benchmarks
    
    def _initialize_category_weights(self) -> Dict[BenchmarkCategory, float]:
        """Initialize weights for different benchmark categories."""
        return {
            BenchmarkCategory.SAFETY: 0.25,           # Highest priority
            BenchmarkCategory.COMPLIANCE: 0.20,       # Critical for legal/regulatory
            BenchmarkCategory.CUSTOMER_IMPACT: 0.20,  # Critical for hospitality
            BenchmarkCategory.PERFORMANCE: 0.15,      # Important for operations
            BenchmarkCategory.QUALITY: 0.15,          # Important for effectiveness
            BenchmarkCategory.EFFICIENCY: 0.05        # Lowest priority
        }
    
    def _initialize_property_adjustments(self) -> Dict[str, Dict[str, float]]:
        """Initialize property type adjustments for benchmarks."""
        return {
            "luxury_resort": {
                "guest_safety_incident_rate": 0.8,    # Stricter safety standards
                "guest_disruption_minimization": 1.1,  # Higher guest experience standards
                "automation_rate": 0.9,                # May require more human touch
                "response_time_multiplier": 0.8        # Faster response expected
            },
            "business_hotel": {
                "automation_rate": 1.1,                # Higher automation expected
                "efficiency_multiplier": 1.1,          # Higher efficiency expected
                "response_time_multiplier": 1.0        # Standard response times
            },
            "budget_hotel": {
                "automation_rate": 1.2,                # Very high automation needed
                "resource_utilization": 1.1,           # Higher efficiency required
                "response_time_multiplier": 1.2        # Slightly relaxed response times
            },
            "boutique_hotel": {
                "guest_disruption_minimization": 1.05, # Personalized service focus
                "automation_rate": 0.95,               # More human intervention acceptable
                "response_time_multiplier": 0.9        # Faster personalized response
            }
        }
    
    def get_benchmark(self, metric_name: str) -> Optional[BenchmarkMetric]:
        """Get a specific benchmark metric."""
        return self.benchmarks.get(metric_name)
    
    def get_benchmarks_by_category(
        self, category: BenchmarkCategory
    ) -> Dict[str, BenchmarkMetric]:
        """Get all benchmarks for a specific category."""
        return {
            name: benchmark for name, benchmark in self.benchmarks.items()
            if benchmark.category == category
        }
    
    def get_incident_category_benchmarks(
        self, incident_category: IncidentCategory
    ) -> Dict[str, BenchmarkMetric]:
        """Get relevant benchmarks for a specific incident category."""
        
        # Category-specific benchmark mappings
        category_mappings = {
            IncidentCategory.GUEST_ACCESS: [
                "critical_incident_response_time",
                "guest_safety_incident_rate",
                "guest_disruption_minimization",
                "classification_accuracy",
                "first_time_resolution_rate"
            ],
            IncidentCategory.PAYMENT_FRAUD: [
                "high_priority_response_time",
                "pci_dss_compliance_rate",
                "notification_timeliness",
                "risk_assessment_accuracy",
                "escalation_rate"
            ],
            IncidentCategory.PII_BREACH: [
                "critical_incident_response_time",
                "dpdp_notification_compliance",
                "privacy_violation_rate",
                "guest_notification_satisfaction",
                "compliance_rate"
            ],
            IncidentCategory.CYBER_SECURITY: [
                "critical_incident_response_time",
                "incident_resolution_time",
                "risk_assessment_accuracy",
                "escalation_rate",
                "resource_utilization"
            ],
            IncidentCategory.OPERATIONAL_SECURITY: [
                "medium_priority_response_time",
                "automation_rate",
                "first_time_resolution_rate",
                "resource_utilization",
                "guest_disruption_minimization"
            ],
            IncidentCategory.PHYSICAL_SECURITY: [
                "critical_incident_response_time",
                "guest_safety_incident_rate",
                "guest_disruption_minimization",
                "escalation_rate",
                "incident_resolution_time"
            ]
        }
        
        relevant_metrics = category_mappings.get(incident_category, [])
        return {
            name: benchmark for name, benchmark in self.benchmarks.items()
            if name in relevant_metrics
        }
    
    def get_priority_benchmarks(
        self, priority: IncidentPriority
    ) -> Dict[str, BenchmarkMetric]:
        """Get relevant benchmarks for a specific incident priority."""
        
        priority_mappings = {
            IncidentPriority.CRITICAL: [
                "critical_incident_response_time",
                "guest_safety_incident_rate",
                "privacy_violation_rate",
                "dpdp_notification_compliance",
                "guest_disruption_minimization"
            ],
            IncidentPriority.HIGH: [
                "high_priority_response_time",
                "pci_dss_compliance_rate",
                "notification_timeliness",
                "escalation_rate",
                "risk_assessment_accuracy"
            ],
            IncidentPriority.MEDIUM: [
                "medium_priority_response_time",
                "automation_rate",
                "first_time_resolution_rate",
                "classification_accuracy",
                "resource_utilization"
            ],
            IncidentPriority.LOW: [
                "automation_rate",
                "resource_utilization",
                "first_time_resolution_rate",
                "guest_disruption_minimization"
            ]
        }
        
        relevant_metrics = priority_mappings.get(priority, [])
        return {
            name: benchmark for name, benchmark in self.benchmarks.items()
            if name in relevant_metrics
        }
    
    def compare_performance(
        self,
        metric_name: str,
        actual_value: float,
        property_type: str = "business_hotel"
    ) -> BenchmarkComparison:
        """
        Compare actual performance against benchmarks.
        
        Args:
            metric_name: Name of the metric to compare
            actual_value: Actual measured value
            property_type: Type of property for adjustments
            
        Returns:
            Detailed benchmark comparison
        """
        
        benchmark = self.benchmarks.get(metric_name)
        if not benchmark:
            raise ValueError(f"Unknown benchmark metric: {metric_name}")
        
        # Apply property type adjustments
        adjusted_target = benchmark.target_value
        adjusted_threshold = benchmark.threshold_value
        
        if property_type in self.property_type_adjustments:
            adjustments = self.property_type_adjustments[property_type]
            
            # Apply specific metric adjustments
            if metric_name in adjustments:
                adjustment_factor = adjustments[metric_name]
                adjusted_target *= adjustment_factor
                adjusted_threshold *= adjustment_threshold
            
            # Apply category-wide adjustments
            category_adjustments = {
                "response_time_multiplier": ["response_time"],
                "efficiency_multiplier": ["rate", "utilization"],
            }
            
            for adj_key, keywords in category_adjustments.items():
                if adj_key in adjustments and any(kw in metric_name for kw in keywords):
                    adjustment_factor = adjustments[adj_key]
                    adjusted_target *= adjustment_factor
                    adjusted_threshold *= adjustment_factor
        
        # Calculate comparison metrics
        meets_threshold = actual_value >= adjusted_threshold
        meets_target = actual_value >= adjusted_target
        performance_ratio = actual_value / adjusted_target if adjusted_target > 0 else 0
        
        # Calculate relative performance
        vs_industry_average = None
        vs_best_in_class = None
        
        if benchmark.industry_average:
            vs_industry_average = actual_value - benchmark.industry_average
        
        if benchmark.best_in_class:
            vs_best_in_class = actual_value - benchmark.best_in_class
        
        # Determine performance level
        if performance_ratio >= 1.1:
            performance_level = "excellent"
            priority_level = "low"
        elif performance_ratio >= 1.0:
            performance_level = "good"
            priority_level = "low"
        elif performance_ratio >= 0.9:
            performance_level = "acceptable"
            priority_level = "medium"
        elif performance_ratio >= 0.8:
            performance_level = "poor"
            priority_level = "high"
        else:
            performance_level = "critical"
            priority_level = "critical"
        
        # Calculate percentile ranking (simplified)
        percentile = min(95, max(5, performance_ratio * 85))
        
        return BenchmarkComparison(
            metric_name=metric_name,
            actual_value=actual_value,
            target_value=adjusted_target,
            threshold_value=adjusted_threshold,
            meets_threshold=meets_threshold,
            meets_target=meets_target,
            performance_ratio=performance_ratio,
            vs_industry_average=vs_industry_average,
            vs_best_in_class=vs_best_in_class,
            percentile_ranking=percentile,
            performance_level=performance_level,
            improvement_needed=not meets_target,
            priority_level=priority_level
        )
    
    def generate_performance_report(
        self,
        metrics: Dict[str, float],
        property_type: str = "business_hotel",
        incident_category: Optional[IncidentCategory] = None,
        priority: Optional[IncidentPriority] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report against benchmarks.
        
        Args:
            metrics: Dictionary of metric names and values
            property_type: Type of property for adjustments
            incident_category: Optional incident category filter
            priority: Optional priority filter
            
        Returns:
            Comprehensive performance report
        """
        
        report = {
            "overall_assessment": {},
            "category_performance": {},
            "individual_metrics": {},
            "improvement_priorities": [],
            "recommendations": []
        }
        
        # Get relevant benchmarks
        relevant_benchmarks = self.benchmarks
        if incident_category:
            relevant_benchmarks = self.get_incident_category_benchmarks(incident_category)
        elif priority:
            relevant_benchmarks = self.get_priority_benchmarks(priority)
        
        # Compare each metric
        comparisons = {}
        category_scores = {category: [] for category in BenchmarkCategory}
        
        for metric_name, value in metrics.items():
            if metric_name in relevant_benchmarks:
                comparison = self.compare_performance(metric_name, value, property_type)
                comparisons[metric_name] = comparison
                
                benchmark = relevant_benchmarks[metric_name]
                category_scores[benchmark.category].append(comparison.performance_ratio)
        
        report["individual_metrics"] = comparisons
        
        # Calculate category performance
        for category, scores in category_scores.items():
            if scores:
                avg_performance = sum(scores) / len(scores)
                weight = self.category_weights.get(category, 0.1)
                
                report["category_performance"][category.value] = {
                    "average_performance": avg_performance,
                    "weight": weight,
                    "weighted_score": avg_performance * weight,
                    "metrics_count": len(scores)
                }
        
        # Calculate overall assessment
        total_weighted_score = sum(
            cat_data["weighted_score"] 
            for cat_data in report["category_performance"].values()
        )
        total_weight = sum(
            cat_data["weight"] 
            for cat_data in report["category_performance"].values()
        )
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        report["overall_assessment"] = {
            "weighted_score": overall_score,
            "performance_level": self._get_overall_performance_level(overall_score),
            "meets_industry_standards": overall_score >= 0.9,
            "critical_issues": len([
                c for c in comparisons.values() 
                if c.performance_level == "critical"
            ])
        }
        
        # Generate improvement priorities
        critical_metrics = [
            comp for comp in comparisons.values()
            if comp.performance_level in ["critical", "poor"]
        ]
        
        # Sort by business criticality and guest impact
        critical_metrics.sort(
            key=lambda x: (
                relevant_benchmarks[x.metric_name].business_criticality == "critical",
                relevant_benchmarks[x.metric_name].guest_impact_level == "critical",
                x.performance_ratio
            )
        )
        
        report["improvement_priorities"] = [
            {
                "metric": comp.metric_name,
                "current_performance": comp.performance_ratio,
                "improvement_needed": comp.target_value - comp.actual_value,
                "priority": comp.priority_level,
                "guest_impact": relevant_benchmarks[comp.metric_name].guest_impact_level
            }
            for comp in critical_metrics[:5]  # Top 5 priorities
        ]
        
        # Generate recommendations
        report["recommendations"] = self._generate_improvement_recommendations(
            comparisons, relevant_benchmarks
        )
        
        return report
    
    def _get_overall_performance_level(self, score: float) -> str:
        """Determine overall performance level from weighted score."""
        if score >= 1.1:
            return "excellent"
        elif score >= 1.0:
            return "good"
        elif score >= 0.9:
            return "acceptable"
        elif score >= 0.8:
            return "poor"
        else:
            return "critical"
    
    def _generate_improvement_recommendations(
        self,
        comparisons: Dict[str, BenchmarkComparison],
        benchmarks: Dict[str, BenchmarkMetric]
    ) -> List[str]:
        """Generate specific improvement recommendations."""
        
        recommendations = []
        
        # Safety-related recommendations
        safety_issues = [
            comp for comp in comparisons.values()
            if (benchmarks[comp.metric_name].category == BenchmarkCategory.SAFETY and
                comp.performance_level in ["critical", "poor"])
        ]
        
        if safety_issues:
            recommendations.append(
                "CRITICAL: Address safety performance gaps immediately. "
                "Guest and employee safety must be the top priority."
            )
        
        # Compliance-related recommendations
        compliance_issues = [
            comp for comp in comparisons.values()
            if (benchmarks[comp.metric_name].category == BenchmarkCategory.COMPLIANCE and
                comp.performance_level in ["critical", "poor"])
        ]
        
        if compliance_issues:
            recommendations.append(
                "HIGH PRIORITY: Improve regulatory compliance performance. "
                "Non-compliance poses significant legal and financial risks."
            )
        
        # Performance improvements
        slow_response = any(
            "response_time" in comp.metric_name and comp.performance_level == "poor"
            for comp in comparisons.values()
        )
        
        if slow_response:
            recommendations.append(
                "Optimize incident response workflows to meet timing benchmarks. "
                "Consider automation and process improvements."
            )
        
        # Quality improvements
        accuracy_issues = any(
            "accuracy" in comp.metric_name and comp.performance_level == "poor"
            for comp in comparisons.values()
        )
        
        if accuracy_issues:
            recommendations.append(
                "Enhance AI model training and validation to improve accuracy. "
                "Consider additional quality assurance measures."
            )
        
        # Customer impact improvements
        guest_impact_issues = [
            comp for comp in comparisons.values()
            if (benchmarks[comp.metric_name].guest_impact_level == "critical" and
                comp.performance_level in ["poor", "acceptable"])
        ]
        
        if guest_impact_issues:
            recommendations.append(
                "Focus on guest experience protection during incident response. "
                "Minimize disruption and improve communication."
            )
        
        return recommendations