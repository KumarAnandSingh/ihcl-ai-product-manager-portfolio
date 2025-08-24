"""
Business Impact Tracking and ROI Measurement System for Hotel Security Operations.

This module provides comprehensive business impact measurement, ROI calculation,
and operational efficiency tracking to demonstrate the value of autonomous
security incident management for hotel operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import pandas as pd
import numpy as np
from pydantic import BaseModel

from ..core.state import IncidentState, IncidentCategory, IncidentPriority


class MetricCategory(str, Enum):
    """Categories of business metrics"""
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    COST_SAVINGS = "cost_savings"
    GUEST_SATISFACTION = "guest_satisfaction"
    COMPLIANCE_ADHERENCE = "compliance_adherence"
    RISK_MITIGATION = "risk_mitigation"
    STAFF_PRODUCTIVITY = "staff_productivity"


class ROIComponent(str, Enum):
    """Components of ROI calculation"""
    COST_AVOIDANCE = "cost_avoidance"
    TIME_SAVINGS = "time_savings"
    AUTOMATION_BENEFIT = "automation_benefit"
    REPUTATION_PROTECTION = "reputation_protection"
    COMPLIANCE_VALUE = "compliance_value"
    GUEST_RETENTION = "guest_retention"


@dataclass
class IncidentROI:
    """Complete ROI analysis for a single incident"""
    incident_id: str
    incident_category: IncidentCategory
    incident_priority: IncidentPriority
    
    # Investment (costs)
    total_investment: float
    prevention_costs: float
    response_costs: float
    technology_costs: float
    staff_time_costs: float
    
    # Returns (value created)
    total_value: float
    cost_avoidance: float
    automation_benefit: float
    reputation_protection_value: float
    compliance_value: float
    guest_satisfaction_value: float
    
    # ROI metrics
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    
    # Operational metrics
    time_to_resolution_minutes: int
    automation_percentage: float
    human_interventions_required: int
    guest_satisfaction_preserved: float
    compliance_violations_prevented: int
    
    # Business impact
    affected_guests_count: int
    revenue_protected: float
    operational_disruption_avoided: float
    brand_impact_score: float
    
    # Comparative metrics
    vs_manual_processing_time: float  # How much faster than manual
    vs_manual_processing_cost: float  # How much cheaper than manual
    vs_industry_benchmark: float  # Performance vs industry standard
    
    calculation_timestamp: datetime


class SecurityEfficiencyScore(BaseModel):
    """Comprehensive security operation efficiency scoring"""
    
    # Overall scores (0-100)
    overall_score: float
    response_time_score: float
    automation_score: float
    guest_protection_score: float
    cost_efficiency_score: float
    compliance_score: float
    
    # Detailed metrics
    avg_response_time_minutes: float
    automation_rate_percentage: float
    guest_impact_rate: float
    cost_per_incident: float
    compliance_adherence_rate: float
    
    # Benchmark comparison
    industry_benchmark_percentile: int  # Which percentile vs industry
    performance_trend: str  # "improving", "stable", "declining"
    
    # Improvement recommendations
    primary_improvement_area: str
    improvement_recommendations: List[str]
    potential_score_increase: float


class HotelOperationalMetrics(BaseModel):
    """Hotel-specific operational metrics"""
    
    property_code: str
    measurement_period: Tuple[datetime, datetime]
    
    # Security incident metrics
    total_incidents: int
    incidents_by_category: Dict[IncidentCategory, int]
    incidents_by_priority: Dict[IncidentPriority, int]
    avg_incidents_per_day: float
    
    # Response performance
    avg_response_time_by_category: Dict[IncidentCategory, float]
    sla_compliance_rate: float
    escalation_rate: float
    
    # Automation metrics
    automation_rate_overall: float
    automation_rate_by_category: Dict[IncidentCategory, float]
    human_intervention_rate: float
    
    # Guest impact metrics
    guest_complaints_prevented: int
    guest_satisfaction_incidents_resolved: int
    guest_compensation_avoided: float
    
    # Financial metrics
    total_cost_savings: float
    cost_per_incident_processed: float
    manual_vs_automated_cost_ratio: float
    
    # Compliance metrics
    regulatory_violations_prevented: int
    compliance_reporting_accuracy: float
    audit_findings_prevented: int
    
    # Staff productivity metrics
    staff_time_saved_hours: float
    staff_productivity_increase: float
    training_requirements_reduced: float


class BusinessImpactTracker:
    """
    Comprehensive business impact measurement and ROI calculation system
    for autonomous hotel security operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize calculators
        self.cost_calculator = OperationalCostCalculator()
        self.efficiency_tracker = EfficiencyTracker()
        self.satisfaction_monitor = GuestSatisfactionMonitor()
        self.compliance_tracker = ComplianceTracker()
        
        # ROI calculation parameters
        self.roi_parameters = self._load_roi_parameters()
        
        # Historical data for benchmarking
        self.historical_data = []
        self.industry_benchmarks = self._load_industry_benchmarks()
    
    async def calculate_incident_roi(self, incident_state: IncidentState, 
                                   execution_results: Dict[str, Any]) -> IncidentROI:
        """
        Calculate comprehensive ROI for a single incident handling.
        
        This is the main method for demonstrating business value of autonomous
        incident response, comparing automated vs manual processing.
        """
        
        self.logger.info(f"Calculating ROI for incident {incident_state.incident_id}")
        
        # Step 1: Calculate all investment components
        investment_breakdown = await self._calculate_investment_costs(
            incident_state, execution_results
        )
        
        # Step 2: Calculate all value/return components
        value_breakdown = await self._calculate_value_returns(
            incident_state, execution_results
        )
        
        # Step 3: Calculate comparative metrics (vs manual processing)
        manual_comparison = await self._calculate_manual_comparison(
            incident_state, execution_results
        )
        
        # Step 4: Calculate operational metrics
        operational_metrics = await self._calculate_operational_metrics(
            incident_state, execution_results
        )
        
        # Step 5: Calculate ROI and financial metrics
        total_investment = sum(investment_breakdown.values())
        total_value = sum(value_breakdown.values())
        
        roi_percentage = ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        payback_period = self._calculate_payback_period(total_investment, total_value)
        npv = self._calculate_net_present_value(total_investment, total_value)
        
        return IncidentROI(
            incident_id=incident_state.incident_id,
            incident_category=incident_state.category,
            incident_priority=incident_state.severity,
            
            # Investment breakdown
            total_investment=total_investment,
            prevention_costs=investment_breakdown.get('prevention', 0),
            response_costs=investment_breakdown.get('response', 0),
            technology_costs=investment_breakdown.get('technology', 0),
            staff_time_costs=investment_breakdown.get('staff_time', 0),
            
            # Value breakdown
            total_value=total_value,
            cost_avoidance=value_breakdown.get('cost_avoidance', 0),
            automation_benefit=value_breakdown.get('automation_benefit', 0),
            reputation_protection_value=value_breakdown.get('reputation_protection', 0),
            compliance_value=value_breakdown.get('compliance_value', 0),
            guest_satisfaction_value=value_breakdown.get('guest_satisfaction', 0),
            
            # ROI metrics
            roi_percentage=roi_percentage,
            payback_period_months=payback_period,
            net_present_value=npv,
            
            # Operational metrics
            time_to_resolution_minutes=operational_metrics['resolution_time_minutes'],
            automation_percentage=operational_metrics['automation_percentage'],
            human_interventions_required=operational_metrics['human_interventions'],
            guest_satisfaction_preserved=operational_metrics['guest_satisfaction_preserved'],
            compliance_violations_prevented=operational_metrics['compliance_violations_prevented'],
            
            # Business impact
            affected_guests_count=len(incident_state.metadata.affected_guests or []),
            revenue_protected=operational_metrics['revenue_protected'],
            operational_disruption_avoided=operational_metrics['disruption_avoided'],
            brand_impact_score=operational_metrics['brand_impact_score'],
            
            # Comparative metrics
            vs_manual_processing_time=manual_comparison['time_improvement'],
            vs_manual_processing_cost=manual_comparison['cost_improvement'],
            vs_industry_benchmark=manual_comparison['vs_industry_benchmark'],
            
            calculation_timestamp=datetime.utcnow()
        )
    
    async def calculate_operational_efficiency_score(self, 
                                                   measurement_period: timedelta = timedelta(days=30),
                                                   property_code: Optional[str] = None) -> SecurityEfficiencyScore:
        """
        Calculate comprehensive security operation efficiency score for a property.
        
        This provides executive-level visibility into security operations performance.
        """
        
        # Get historical incident data
        end_date = datetime.utcnow()
        start_date = end_date - measurement_period
        
        incidents = await self._get_incidents_for_period(start_date, end_date, property_code)
        
        if not incidents:
            return self._generate_default_efficiency_score()
        
        # Calculate core metrics
        metrics = await self._calculate_efficiency_metrics(incidents)
        
        # Score calculations (0-100 scale)
        response_time_score = self._score_response_time(metrics['avg_response_time'])
        automation_score = metrics['automation_rate'] * 100
        guest_protection_score = (1 - metrics['guest_impact_rate']) * 100
        cost_efficiency_score = self._score_cost_efficiency(metrics['cost_per_incident'])
        compliance_score = metrics['compliance_rate'] * 100
        
        # Overall weighted score
        weights = {
            'response_time': 0.25,
            'automation': 0.25,
            'guest_protection': 0.20,
            'cost_efficiency': 0.15,
            'compliance': 0.15
        }
        
        overall_score = (
            weights['response_time'] * response_time_score +
            weights['automation'] * automation_score +
            weights['guest_protection'] * guest_protection_score +
            weights['cost_efficiency'] * cost_efficiency_score +
            weights['compliance'] * compliance_score
        )
        
        # Benchmark comparison
        benchmark_percentile = await self._calculate_industry_percentile(overall_score)
        performance_trend = await self._analyze_performance_trend(incidents)
        
        # Improvement recommendations
        improvement_analysis = self._analyze_improvement_opportunities({
            'response_time_score': response_time_score,
            'automation_score': automation_score,
            'guest_protection_score': guest_protection_score,
            'cost_efficiency_score': cost_efficiency_score,
            'compliance_score': compliance_score
        })
        
        return SecurityEfficiencyScore(
            overall_score=overall_score,
            response_time_score=response_time_score,
            automation_score=automation_score,
            guest_protection_score=guest_protection_score,
            cost_efficiency_score=cost_efficiency_score,
            compliance_score=compliance_score,
            
            # Detailed metrics
            avg_response_time_minutes=metrics['avg_response_time'],
            automation_rate_percentage=metrics['automation_rate'] * 100,
            guest_impact_rate=metrics['guest_impact_rate'],
            cost_per_incident=metrics['cost_per_incident'],
            compliance_adherence_rate=metrics['compliance_rate'],
            
            # Benchmark comparison
            industry_benchmark_percentile=benchmark_percentile,
            performance_trend=performance_trend,
            
            # Improvements
            primary_improvement_area=improvement_analysis['primary_area'],
            improvement_recommendations=improvement_analysis['recommendations'],
            potential_score_increase=improvement_analysis['potential_increase']
        )
    
    async def generate_executive_dashboard_metrics(self, 
                                                 properties: List[str] = None,
                                                 period_days: int = 90) -> Dict[str, Any]:
        """
        Generate executive-level dashboard metrics showing business impact
        of autonomous security operations across multiple properties.
        """
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Aggregate metrics across properties
        total_metrics = {
            'total_incidents_processed': 0,
            'total_cost_savings': 0,
            'total_time_saved_hours': 0,
            'automation_rate_average': 0,
            'guest_satisfaction_improvement': 0,
            'compliance_violations_prevented': 0,
            'roi_percentage_average': 0
        }
        
        property_details = []
        
        for property_code in (properties or await self._get_all_property_codes()):
            property_metrics = await self._calculate_property_metrics(
                property_code, start_date, end_date
            )
            
            # Aggregate totals
            total_metrics['total_incidents_processed'] += property_metrics['incidents_count']
            total_metrics['total_cost_savings'] += property_metrics['cost_savings']
            total_metrics['total_time_saved_hours'] += property_metrics['time_saved_hours']
            
            property_details.append({
                'property_code': property_code,
                'metrics': property_metrics
            })
        
        # Calculate averages
        property_count = len(property_details) or 1
        total_metrics['automation_rate_average'] = sum(
            p['metrics']['automation_rate'] for p in property_details
        ) / property_count
        
        total_metrics['roi_percentage_average'] = sum(
            p['metrics']['roi_percentage'] for p in property_details
        ) / property_count
        
        # Calculate business impact indicators
        business_impact = self._calculate_business_impact_indicators(total_metrics)
        
        return {
            'summary_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': period_days,
                'properties_included': len(property_details)
            },
            
            'executive_summary': {
                'total_incidents_handled': total_metrics['total_incidents_processed'],
                'total_roi_percentage': total_metrics['roi_percentage_average'],
                'total_cost_savings_inr': total_metrics['total_cost_savings'],
                'operational_efficiency_gain': business_impact['efficiency_gain_percentage'],
                'guest_satisfaction_improvement': business_impact['satisfaction_improvement'],
                'compliance_excellence_score': business_impact['compliance_score']
            },
            
            'key_performance_indicators': {
                'average_response_time_minutes': business_impact['avg_response_time'],
                'automation_rate_percentage': total_metrics['automation_rate_average'] * 100,
                'cost_per_incident_inr': business_impact['cost_per_incident'],
                'staff_productivity_increase': business_impact['productivity_increase'],
                'technology_utilization_score': business_impact['tech_utilization']
            },
            
            'business_value_delivered': {
                'annual_cost_savings_projection': total_metrics['total_cost_savings'] * (365 / period_days),
                'staff_hours_saved_annually': total_metrics['total_time_saved_hours'] * (365 / period_days),
                'guest_complaints_prevented': business_impact['complaints_prevented'],
                'revenue_protection_value': business_impact['revenue_protected'],
                'brand_risk_mitigation_value': business_impact['brand_protection_value']
            },
            
            'property_breakdown': property_details,
            
            'strategic_insights': await self._generate_strategic_insights(total_metrics, business_impact),
            
            'generated_at': datetime.utcnow().isoformat()
        }
    
    # Cost calculation methods
    
    async def _calculate_investment_costs(self, incident_state: IncidentState, 
                                        execution_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all investment costs for incident handling"""
        
        costs = {}
        
        # Technology costs (API calls, system usage, etc.)
        costs['technology'] = await self._calculate_technology_costs(incident_state, execution_results)
        
        # Staff time costs (human interventions, oversight)
        costs['staff_time'] = await self._calculate_staff_time_costs(incident_state, execution_results)
        
        # Response costs (immediate actions, resources deployed)
        costs['response'] = await self._calculate_response_costs(incident_state, execution_results)
        
        # Prevention costs (proactive measures, system updates)
        costs['prevention'] = await self._calculate_prevention_costs(incident_state)
        
        return costs
    
    async def _calculate_value_returns(self, incident_state: IncidentState,
                                     execution_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all value/return components"""
        
        returns = {}
        
        # Cost avoidance (what would have been lost without intervention)
        returns['cost_avoidance'] = await self._calculate_cost_avoidance(incident_state)
        
        # Automation benefit (cost saved vs manual processing)
        returns['automation_benefit'] = await self._calculate_automation_benefit(incident_state, execution_results)
        
        # Reputation protection value
        returns['reputation_protection'] = await self._calculate_reputation_protection_value(incident_state)
        
        # Compliance value (fines avoided, audit readiness)
        returns['compliance_value'] = await self._calculate_compliance_value(incident_state)
        
        # Guest satisfaction value
        returns['guest_satisfaction'] = await self._calculate_guest_satisfaction_value(incident_state)
        
        return returns
    
    async def _calculate_cost_avoidance(self, incident_state: IncidentState) -> float:
        """Calculate costs that were avoided through prompt incident response"""
        
        base_avoidance = {
            IncidentCategory.GUEST_ACCESS: 15000,      # Room revenue loss, guest compensation
            IncidentCategory.PAYMENT_FRAUD: 50000,     # Fraudulent transaction amounts
            IncidentCategory.PII_BREACH: 200000,       # Regulatory fines, legal costs
            IncidentCategory.CYBER_SECURITY: 500000,   # System downtime, data recovery
            IncidentCategory.OPERATIONAL_SECURITY: 5000,    # Minor operational disruption
            IncidentCategory.PHYSICAL_SECURITY: 25000,  # Asset protection, insurance
            IncidentCategory.VENDOR_ACCESS: 10000,      # Vendor relationship costs
            IncidentCategory.COMPLIANCE_VIOLATION: 100000  # Regulatory penalties
        }
        
        base_cost = base_avoidance.get(incident_state.category, 10000)
        
        # Adjust based on incident severity
        severity_multipliers = {
            IncidentPriority.INFORMATIONAL: 0.1,
            IncidentPriority.LOW: 0.3,
            IncidentPriority.MEDIUM: 1.0,
            IncidentPriority.HIGH: 2.5,
            IncidentPriority.CRITICAL: 5.0
        }
        
        multiplier = severity_multipliers.get(incident_state.severity, 1.0)
        
        # Adjust based on affected scope
        scope_multiplier = 1.0
        if incident_state.metadata.affected_guests:
            scope_multiplier *= (1 + len(incident_state.metadata.affected_guests) * 0.1)
        if incident_state.metadata.affected_systems:
            scope_multiplier *= (1 + len(incident_state.metadata.affected_systems) * 0.2)
        
        return base_cost * multiplier * min(scope_multiplier, 3.0)
    
    async def _calculate_automation_benefit(self, incident_state: IncidentState,
                                          execution_results: Dict[str, Any]) -> float:
        """Calculate value created through automation vs manual processing"""
        
        # Time savings
        automated_time = execution_results.get('processing_time_seconds', 1800)  # 30 min default
        manual_time_estimate = self._estimate_manual_processing_time(incident_state)
        time_saved_hours = max(0, (manual_time_estimate - automated_time) / 3600)
        
        # Cost per hour of security staff time (blended rate)
        security_staff_cost_per_hour = 75  # ₹75/hour blended rate
        time_savings_value = time_saved_hours * security_staff_cost_per_hour
        
        # Accuracy improvement value (fewer errors, less rework)
        accuracy_improvement_value = self._calculate_accuracy_improvement_value(incident_state)
        
        # Consistency value (standardized response, best practices)
        consistency_value = self._calculate_consistency_value(incident_state)
        
        # 24/7 availability value (no shift/holiday delays)
        availability_value = self._calculate_availability_value(incident_state)
        
        return time_savings_value + accuracy_improvement_value + consistency_value + availability_value
    
    def _estimate_manual_processing_time(self, incident_state: IncidentState) -> int:
        """Estimate time for manual processing in seconds"""
        
        base_times = {
            IncidentCategory.GUEST_ACCESS: 3600,       # 1 hour
            IncidentCategory.PAYMENT_FRAUD: 7200,      # 2 hours  
            IncidentCategory.PII_BREACH: 14400,        # 4 hours
            IncidentCategory.CYBER_SECURITY: 10800,    # 3 hours
            IncidentCategory.OPERATIONAL_SECURITY: 2700,    # 45 minutes
            IncidentCategory.PHYSICAL_SECURITY: 5400,  # 1.5 hours
            IncidentCategory.VENDOR_ACCESS: 4500,      # 1.25 hours
            IncidentCategory.COMPLIANCE_VIOLATION: 21600   # 6 hours
        }
        
        base_time = base_times.get(incident_state.category, 3600)
        
        # Add complexity factors
        complexity_factors = 0
        if incident_state.metadata.affected_guests and len(incident_state.metadata.affected_guests) > 5:
            complexity_factors += 0.5
        if incident_state.metadata.affected_systems and len(incident_state.metadata.affected_systems) > 2:
            complexity_factors += 0.3
        if incident_state.requires_human_intervention:
            complexity_factors += 0.2
        
        return int(base_time * (1 + complexity_factors))
    
    # Additional helper methods
    
    def _load_roi_parameters(self) -> Dict[str, Any]:
        """Load ROI calculation parameters"""
        return {
            'discount_rate': 0.10,  # 10% annual discount rate
            'staff_hourly_costs': {
                'security_officer': 50,
                'security_manager': 100,
                'operations_manager': 150,
                'general_manager': 300
            },
            'guest_satisfaction_value_per_point': 5000,  # ₹5K per satisfaction point
            'reputation_impact_multipliers': {
                IncidentCategory.PII_BREACH: 3.0,
                IncidentCategory.CYBER_SECURITY: 2.5,
                IncidentCategory.PAYMENT_FRAUD: 2.0
            }
        }
    
    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """Load hospitality industry benchmarks"""
        return {
            'response_time_benchmarks': {
                'excellent': 15,    # minutes
                'good': 30,
                'average': 60,
                'poor': 120
            },
            'automation_rate_benchmarks': {
                'excellent': 0.85,
                'good': 0.70,
                'average': 0.50,
                'poor': 0.30
            },
            'cost_per_incident_benchmarks': {
                'excellent': 500,   # ₹
                'good': 1000,
                'average': 2000,
                'poor': 4000
            }
        }


class OperationalCostCalculator:
    """Calculate operational costs for security incident processing"""
    
    async def calculate_technology_costs(self, incident_state: IncidentState,
                                       execution_results: Dict[str, Any]) -> float:
        """Calculate technology-related costs"""
        
        # API call costs
        api_costs = execution_results.get('api_calls_count', 0) * 0.10  # ₹0.10 per API call
        
        # LLM processing costs
        tokens_used = execution_results.get('tokens_used', 5000)
        llm_costs = tokens_used * 0.002  # ₹0.002 per token
        
        # System resource costs
        processing_time_seconds = execution_results.get('processing_time_seconds', 300)
        compute_costs = processing_time_seconds * 0.01  # ₹0.01 per second
        
        return api_costs + llm_costs + compute_costs


class EfficiencyTracker:
    """Track operational efficiency improvements"""
    
    async def calculate_time_savings(self, incident_data: Dict[str, Any]) -> float:
        """Calculate time savings vs manual processing"""
        # Implementation here
        return 0.0


class GuestSatisfactionMonitor:
    """Monitor guest satisfaction impact"""
    
    async def measure_satisfaction_impact(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Measure impact on guest satisfaction"""
        # Implementation here
        return {}


class ComplianceTracker:
    """Track compliance adherence and value"""
    
    async def calculate_compliance_value(self, incident_state: IncidentState) -> Dict[str, float]:
        """Calculate value of compliance adherence"""
        # Implementation here
        return {}