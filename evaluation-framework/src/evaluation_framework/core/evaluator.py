"""
Core Evaluation Engine for Agentic AI Systems
Comprehensive multi-dimensional evaluation framework for IHCL FlexiCore platform
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


class EvaluationDimension(Enum):
    """Evaluation dimensions for comprehensive AI agent assessment"""
    ACCURACY = "accuracy"
    SAFETY = "safety" 
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    BUSINESS_IMPACT = "business_impact"


@dataclass
class EvaluationResult:
    """Structured evaluation result with comprehensive metrics"""
    agent_id: str
    timestamp: datetime
    dimension: EvaluationDimension
    score: float
    details: Dict[str, Any]
    metadata: Dict[str, Any]
    passed: bool
    threshold: float


@dataclass
class EvaluationConfig:
    """Configuration for evaluation runs"""
    dimensions: List[EvaluationDimension]
    thresholds: Dict[EvaluationDimension, float]
    sample_size: int = 100
    confidence_level: float = 0.95
    parallel_workers: int = 4
    timeout_seconds: int = 300


class ComprehensiveEvaluator:
    """
    Multi-dimensional evaluator for agentic AI systems
    Supports accuracy, safety, compliance, performance, and business impact assessment
    """
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.evaluation_history: List[EvaluationResult] = []
        
    async def evaluate_agent(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> List[EvaluationResult]:
        """
        Comprehensive multi-dimensional agent evaluation
        
        Args:
            agent_id: Identifier for the agent being evaluated
            test_cases: List of test scenarios with expected outputs
            
        Returns:
            List of evaluation results across all dimensions
        """
        logger.info(f"Starting comprehensive evaluation for agent: {agent_id}")
        
        results = []
        
        # Run evaluations for each dimension in parallel
        evaluation_tasks = []
        for dimension in self.config.dimensions:
            task = self._evaluate_dimension(agent_id, dimension, test_cases)
            evaluation_tasks.append(task)
        
        dimension_results = await asyncio.gather(*evaluation_tasks)
        
        for result in dimension_results:
            if result:
                results.append(result)
                self.evaluation_history.append(result)
        
        logger.info(f"Completed evaluation for {agent_id}: {len(results)} dimensions assessed")
        return results
    
    async def _evaluate_dimension(
        self, 
        agent_id: str, 
        dimension: EvaluationDimension, 
        test_cases: List[Dict[str, Any]]
    ) -> Optional[EvaluationResult]:
        """Evaluate a specific dimension"""
        
        logger.info(f"Evaluating {dimension.value} for {agent_id}")
        
        try:
            if dimension == EvaluationDimension.ACCURACY:
                return await self._evaluate_accuracy(agent_id, test_cases)
            elif dimension == EvaluationDimension.SAFETY:
                return await self._evaluate_safety(agent_id, test_cases)
            elif dimension == EvaluationDimension.COMPLIANCE:
                return await self._evaluate_compliance(agent_id, test_cases)
            elif dimension == EvaluationDimension.PERFORMANCE:
                return await self._evaluate_performance(agent_id, test_cases)
            elif dimension == EvaluationDimension.BUSINESS_IMPACT:
                return await self._evaluate_business_impact(agent_id, test_cases)
                
        except Exception as e:
            logger.error(f"Error evaluating {dimension.value}: {str(e)}")
            return None
    
    async def _evaluate_accuracy(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate task completion accuracy"""
        
        predictions = []
        actuals = []
        tool_accuracies = []
        response_times = []
        
        for test_case in test_cases[:self.config.sample_size]:
            start_time = time.time()
            
            # Simulate agent execution (replace with actual agent call)
            prediction = await self._simulate_agent_execution(agent_id, test_case)
            
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            # Extract metrics
            predictions.append(prediction.get('classification', 'unknown'))
            actuals.append(test_case.get('expected_classification', 'unknown'))
            
            # Tool usage accuracy
            expected_tools = test_case.get('expected_tools', [])
            used_tools = prediction.get('tools_used', [])
            tool_accuracy = len(set(expected_tools) & set(used_tools)) / max(len(expected_tools), 1)
            tool_accuracies.append(tool_accuracy)
        
        # Calculate accuracy metrics
        accuracy = accuracy_score(actuals, predictions)
        precision = precision_score(actuals, predictions, average='weighted', zero_division=0)
        recall = recall_score(actuals, predictions, average='weighted', zero_division=0)
        f1 = f1_score(actuals, predictions, average='weighted', zero_division=0)
        
        avg_tool_accuracy = np.mean(tool_accuracies)
        avg_response_time = np.mean(response_times)
        
        details = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'tool_call_accuracy': avg_tool_accuracy,
            'avg_response_time': avg_response_time,
            'sample_size': len(test_cases),
            'confidence_interval': self._calculate_confidence_interval(accuracy, len(test_cases))
        }
        
        threshold = self.config.thresholds[EvaluationDimension.ACCURACY]
        passed = accuracy >= threshold
        
        return EvaluationResult(
            agent_id=agent_id,
            timestamp=datetime.now(),
            dimension=EvaluationDimension.ACCURACY,
            score=accuracy,
            details=details,
            metadata={'model_version': '1.0', 'test_suite': 'hospitality_security'},
            passed=passed,
            threshold=threshold
        )
    
    async def _evaluate_safety(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate safety metrics including hallucination detection"""
        
        hallucinations = 0
        pii_exposures = 0
        bias_incidents = 0
        total_responses = 0
        
        for test_case in test_cases[:self.config.sample_size]:
            prediction = await self._simulate_agent_execution(agent_id, test_case)
            total_responses += 1
            
            # Hallucination detection
            if self._detect_hallucination(prediction, test_case):
                hallucinations += 1
            
            # PII exposure detection
            if self._detect_pii_exposure(prediction):
                pii_exposures += 1
            
            # Bias detection
            if self._detect_bias(prediction, test_case):
                bias_incidents += 1
        
        hallucination_rate = hallucinations / total_responses
        pii_exposure_rate = pii_exposures / total_responses
        bias_rate = bias_incidents / total_responses
        
        # Overall safety score (inverse of risk)
        safety_score = 1.0 - (hallucination_rate * 0.5 + pii_exposure_rate * 0.3 + bias_rate * 0.2)
        
        details = {
            'hallucination_rate': hallucination_rate,
            'pii_exposure_rate': pii_exposure_rate,
            'bias_rate': bias_rate,
            'safety_score': safety_score,
            'total_responses_evaluated': total_responses,
            'hallucination_incidents': hallucinations,
            'pii_incidents': pii_exposures,
            'bias_incidents': bias_incidents
        }
        
        threshold = self.config.thresholds[EvaluationDimension.SAFETY]
        passed = safety_score >= threshold
        
        return EvaluationResult(
            agent_id=agent_id,
            timestamp=datetime.now(),
            dimension=EvaluationDimension.SAFETY,
            score=safety_score,
            details=details,
            metadata={'safety_framework': 'comprehensive', 'detection_models': 'v2.0'},
            passed=passed,
            threshold=threshold
        )
    
    async def _evaluate_compliance(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate regulatory compliance (DPDP, PCI DSS, GDPR)"""
        
        dpdp_violations = 0
        pci_violations = 0
        gdpr_violations = 0
        total_checks = 0
        
        for test_case in test_cases[:self.config.sample_size]:
            prediction = await self._simulate_agent_execution(agent_id, test_case)
            total_checks += 1
            
            # DPDP Act 2023 compliance
            if not self._check_dpdp_compliance(prediction, test_case):
                dpdp_violations += 1
            
            # PCI DSS compliance
            if not self._check_pci_compliance(prediction, test_case):
                pci_violations += 1
            
            # GDPR compliance
            if not self._check_gdpr_compliance(prediction, test_case):
                gdpr_violations += 1
        
        dpdp_compliance = 1.0 - (dpdp_violations / total_checks)
        pci_compliance = 1.0 - (pci_violations / total_checks)
        gdpr_compliance = 1.0 - (gdpr_violations / total_checks)
        
        # Weighted compliance score
        overall_compliance = (dpdp_compliance * 0.4 + pci_compliance * 0.3 + gdpr_compliance * 0.3)
        
        details = {
            'dpdp_compliance_rate': dpdp_compliance,
            'pci_compliance_rate': pci_compliance,
            'gdpr_compliance_rate': gdpr_compliance,
            'overall_compliance_score': overall_compliance,
            'total_compliance_checks': total_checks,
            'dpdp_violations': dpdp_violations,
            'pci_violations': pci_violations,
            'gdpr_violations': gdpr_violations
        }
        
        threshold = self.config.thresholds[EvaluationDimension.COMPLIANCE]
        passed = overall_compliance >= threshold
        
        return EvaluationResult(
            agent_id=agent_id,
            timestamp=datetime.now(),
            dimension=EvaluationDimension.COMPLIANCE,
            score=overall_compliance,
            details=details,
            metadata={'regulations': ['DPDP', 'PCI_DSS', 'GDPR'], 'audit_trail': True},
            passed=passed,
            threshold=threshold
        )
    
    async def _evaluate_performance(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate performance metrics (latency, throughput, cost)"""
        
        response_times = []
        token_costs = []
        memory_usage = []
        success_rates = []
        
        for test_case in test_cases[:self.config.sample_size]:
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            prediction = await self._simulate_agent_execution(agent_id, test_case)
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            response_times.append(end_time - start_time)
            memory_usage.append(end_memory - start_memory)
            
            # Calculate token cost (mock calculation)
            token_cost = self._calculate_token_cost(prediction)
            token_costs.append(token_cost)
            
            # Success rate
            success = prediction.get('success', False)
            success_rates.append(1 if success else 0)
        
        avg_latency = np.mean(response_times)
        p95_latency = np.percentile(response_times, 95)
        avg_cost = np.mean(token_costs)
        avg_memory = np.mean(memory_usage)
        success_rate = np.mean(success_rates)
        throughput = 1 / avg_latency if avg_latency > 0 else 0
        
        # Performance score based on SLA targets
        latency_score = max(0, 1 - (avg_latency - 1.0) / 2.0)  # Target: <1s optimal, <3s acceptable
        cost_score = max(0, 1 - (avg_cost - 0.01) / 0.04)      # Target: <$0.01 optimal, <$0.05 acceptable
        performance_score = (latency_score * 0.4 + cost_score * 0.3 + success_rate * 0.3)
        
        details = {
            'avg_latency': avg_latency,
            'p95_latency': p95_latency,
            'avg_cost_per_request': avg_cost,
            'avg_memory_usage_mb': avg_memory,
            'success_rate': success_rate,
            'throughput_rps': throughput,
            'performance_score': performance_score,
            'latency_score': latency_score,
            'cost_score': cost_score,
            'total_requests': len(test_cases)
        }
        
        threshold = self.config.thresholds[EvaluationDimension.PERFORMANCE]
        passed = performance_score >= threshold
        
        return EvaluationResult(
            agent_id=agent_id,
            timestamp=datetime.now(),
            dimension=EvaluationDimension.PERFORMANCE,
            score=performance_score,
            details=details,
            metadata={'sla_targets': {'latency': 2.0, 'cost': 0.05}, 'measurement_period': '5min'},
            passed=passed,
            threshold=threshold
        )
    
    async def _evaluate_business_impact(
        self, 
        agent_id: str, 
        test_cases: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate business impact metrics"""
        
        automation_rates = []
        customer_satisfaction_scores = []
        cost_savings = []
        resolution_improvements = []
        
        for test_case in test_cases[:self.config.sample_size]:
            prediction = await self._simulate_agent_execution(agent_id, test_case)
            
            # Automation rate (% of tasks completed without human intervention)
            automation_rate = 1 if prediction.get('human_required', False) == False else 0
            automation_rates.append(automation_rate)
            
            # Customer satisfaction impact (simulated)
            satisfaction_impact = prediction.get('satisfaction_impact', 0.0)
            customer_satisfaction_scores.append(satisfaction_impact)
            
            # Cost savings calculation
            manual_cost = test_case.get('manual_processing_cost', 50.0)
            automated_cost = prediction.get('processing_cost', 2.0)
            savings = max(0, manual_cost - automated_cost)
            cost_savings.append(savings)
            
            # Resolution time improvement
            manual_time = test_case.get('manual_resolution_time', 300)  # 5 minutes
            automated_time = prediction.get('resolution_time', 120)     # 2 minutes
            improvement = max(0, (manual_time - automated_time) / manual_time)
            resolution_improvements.append(improvement)
        
        avg_automation_rate = np.mean(automation_rates)
        avg_satisfaction_impact = np.mean(customer_satisfaction_scores)
        total_cost_savings = np.sum(cost_savings)
        avg_resolution_improvement = np.mean(resolution_improvements)
        
        # Business impact score
        business_impact_score = (
            avg_automation_rate * 0.3 +
            (avg_satisfaction_impact + 1) / 2 * 0.2 +  # Normalize to 0-1
            min(total_cost_savings / 1000, 1.0) * 0.2 +  # Cap at $1000 savings
            avg_resolution_improvement * 0.3
        )
        
        details = {
            'automation_rate': avg_automation_rate,
            'customer_satisfaction_impact': avg_satisfaction_impact,
            'total_cost_savings': total_cost_savings,
            'avg_resolution_time_improvement': avg_resolution_improvement,
            'business_impact_score': business_impact_score,
            'roi_estimate': total_cost_savings * 12,  # Annualized
            'efficiency_gain_percentage': avg_resolution_improvement * 100
        }
        
        threshold = self.config.thresholds[EvaluationDimension.BUSINESS_IMPACT]
        passed = business_impact_score >= threshold
        
        return EvaluationResult(
            agent_id=agent_id,
            timestamp=datetime.now(),
            dimension=EvaluationDimension.BUSINESS_IMPACT,
            score=business_impact_score,
            details=details,
            metadata={'measurement_period': '30days', 'baseline': 'manual_process'},
            passed=passed,
            threshold=threshold
        )
    
    # Helper methods
    async def _simulate_agent_execution(self, agent_id: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent execution for testing purposes"""
        # In production, this would make actual API calls to agents
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'classification': test_case.get('expected_classification', 'security_incident'),
            'tools_used': ['classification_tool', 'priority_tool'],
            'success': True,
            'processing_cost': 0.02,
            'resolution_time': 120,
            'human_required': False,
            'satisfaction_impact': 0.15,
            'response_text': f"Processed {test_case.get('incident_type', 'security incident')}"
        }
    
    def _detect_hallucination(self, prediction: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Mock hallucination detection"""
        return False  # Placeholder
    
    def _detect_pii_exposure(self, prediction: Dict[str, Any]) -> bool:
        """Mock PII exposure detection"""
        response_text = prediction.get('response_text', '')
        # Simple regex patterns for common PII
        import re
        
        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response_text):
            return True
        
        # Phone number pattern
        if re.search(r'\b\d{3}-\d{3}-\d{4}\b', response_text):
            return True
        
        return False
    
    def _detect_bias(self, prediction: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Mock bias detection"""
        return False  # Placeholder
    
    def _check_dpdp_compliance(self, prediction: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Check DPDP Act 2023 compliance"""
        # Check for data processing consent
        # Check for data localization requirements
        # Check for breach notification procedures
        return not self._detect_pii_exposure(prediction)
    
    def _check_pci_compliance(self, prediction: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Check PCI DSS compliance"""
        # Check for payment data protection
        # Check for secure transmission
        return True  # Placeholder
    
    def _check_gdpr_compliance(self, prediction: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """Check GDPR compliance"""
        # Check for data subject rights
        # Check for lawful basis for processing
        return True  # Placeholder
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import psutil
        return psutil.Process().memory_info().rss / 1024 / 1024
    
    def _calculate_token_cost(self, prediction: Dict[str, Any]) -> float:
        """Calculate token cost for the prediction"""
        return prediction.get('processing_cost', 0.02)
    
    def _calculate_confidence_interval(self, score: float, sample_size: int) -> Tuple[float, float]:
        """Calculate confidence interval for the score"""
        if sample_size < 2:
            return (score, score)
        
        z_score = stats.norm.ppf(1 - (1 - self.config.confidence_level) / 2)
        margin_of_error = z_score * np.sqrt(score * (1 - score) / sample_size)
        
        return (max(0, score - margin_of_error), min(1, score + margin_of_error))
    
    def generate_summary_report(self, agent_id: str) -> Dict[str, Any]:
        """Generate comprehensive evaluation summary report"""
        
        agent_results = [r for r in self.evaluation_history if r.agent_id == agent_id]
        
        if not agent_results:
            return {'error': f'No evaluation results found for agent: {agent_id}'}
        
        # Group results by dimension
        dimension_scores = {}
        for result in agent_results:
            dim = result.dimension.value
            if dim not in dimension_scores:
                dimension_scores[dim] = []
            dimension_scores[dim].append(result.score)
        
        # Calculate summary statistics
        summary = {
            'agent_id': agent_id,
            'evaluation_period': {
                'start': min(r.timestamp for r in agent_results),
                'end': max(r.timestamp for r in agent_results)
            },
            'total_evaluations': len(agent_results),
            'dimensions_evaluated': list(dimension_scores.keys()),
            'overall_score': np.mean([r.score for r in agent_results]),
            'pass_rate': sum(1 for r in agent_results if r.passed) / len(agent_results),
            'dimension_scores': {
                dim: {
                    'latest_score': scores[-1],
                    'average_score': np.mean(scores),
                    'trend': 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable',
                    'evaluations_count': len(scores)
                }
                for dim, scores in dimension_scores.items()
            }
        }
        
        return summary