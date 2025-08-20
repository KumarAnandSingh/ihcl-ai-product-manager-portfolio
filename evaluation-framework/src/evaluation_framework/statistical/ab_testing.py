"""
Advanced A/B testing framework for comparing agentic AI systems.

This module provides comprehensive statistical testing capabilities for:
- Model comparison and benchmarking
- Performance regression detection
- Statistical significance testing
- Power analysis and sample size calculation
- Multi-variate testing
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    ttest_ind, ttest_rel, mannwhitneyu, wilcoxon,
    chi2_contingency, fisher_exact, bootstrap
)
from sklearn.utils import resample

from ..core.types import EvaluationResult, MetricType
from ..utils.config import Config


@dataclass
class ABTestResult:
    """Results from an A/B test comparison."""
    test_name: str
    agent_a: str
    agent_b: str
    metric: str
    
    # Sample statistics
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    std_a: float
    std_b: float
    
    # Test results
    test_statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    
    # Interpretation
    is_significant: bool
    significance_level: float
    practical_significance: bool
    recommendation: str
    
    # Additional metadata
    test_method: str
    assumptions_met: bool
    warnings: List[str]
    timestamp: datetime


class ABTestFramework:
    """
    Comprehensive A/B testing framework for agentic AI system comparison.
    
    Provides statistical testing capabilities with proper assumptions checking,
    effect size calculation, and practical significance assessment.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the A/B testing framework."""
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Default significance levels
        self.default_alpha = 0.05
        self.bonferroni_correction = True
        
        # Effect size thresholds for practical significance
        self.effect_size_thresholds = {
            "small": 0.2,
            "medium": 0.5, 
            "large": 0.8,
        }
        
        # Minimum detectable effect sizes by metric
        self.min_detectable_effects = {
            MetricType.ACCURACY: 0.05,  # 5% improvement
            MetricType.LATENCY: 0.20,   # 20% reduction
            MetricType.SAFETY: 0.02,    # 2% improvement
            MetricType.COMPLIANCE: 0.01, # 1% improvement
            MetricType.COST: 0.15,      # 15% reduction
        }
    
    def compare_agents(
        self,
        results_a: List[EvaluationResult],
        results_b: List[EvaluationResult],
        significance_level: float = 0.05,
        metrics: Optional[List[MetricType]] = None,
    ) -> Dict[str, ABTestResult]:
        """
        Compare two agents across multiple metrics.
        
        Args:
            results_a: Evaluation results for agent A
            results_b: Evaluation results for agent B
            significance_level: Statistical significance level (alpha)
            metrics: Specific metrics to compare (None for all)
            
        Returns:
            Dictionary of test results by metric
        """
        if not results_a or not results_b:
            raise ValueError("Both result sets must be non-empty")
        
        agent_a_name = results_a[0].agent_name
        agent_b_name = results_b[0].agent_name
        
        # Extract available metrics
        if metrics is None:
            metrics_a = set()
            metrics_b = set()
            
            for result in results_a:
                for metric in result.metrics:
                    metrics_a.add(metric.metric_type)
            
            for result in results_b:
                for metric in result.metrics:
                    metrics_b.add(metric.metric_type)
            
            metrics = list(metrics_a.intersection(metrics_b))
        
        # Apply Bonferroni correction if testing multiple metrics
        if self.bonferroni_correction and len(metrics) > 1:
            adjusted_alpha = significance_level / len(metrics)
        else:
            adjusted_alpha = significance_level
        
        test_results = {}
        
        for metric_type in metrics:
            try:
                # Extract metric values
                values_a = self._extract_metric_values(results_a, metric_type)
                values_b = self._extract_metric_values(results_b, metric_type)
                
                if not values_a or not values_b:
                    self.logger.warning(f"Insufficient data for metric {metric_type}")
                    continue
                
                # Perform A/B test
                test_result = self._perform_ab_test(
                    values_a, values_b,
                    agent_a_name, agent_b_name,
                    metric_type, adjusted_alpha
                )
                
                test_results[metric_type.value] = test_result
                
            except Exception as e:
                self.logger.error(f"A/B test failed for {metric_type}: {e}")
        
        return test_results
    
    def _perform_ab_test(
        self,
        values_a: List[float],
        values_b: List[float], 
        agent_a: str,
        agent_b: str,
        metric_type: MetricType,
        alpha: float,
    ) -> ABTestResult:
        """Perform statistical test between two samples."""
        
        # Convert to numpy arrays
        a = np.array(values_a)
        b = np.array(values_b)
        
        # Calculate basic statistics
        n_a, n_b = len(a), len(b)
        mean_a, mean_b = np.mean(a), np.mean(b)
        std_a, std_b = np.std(a, ddof=1), np.std(b, ddof=1)
        
        warnings_list = []
        assumptions_met = True
        
        # Check sample size requirements
        if n_a < 3 or n_b < 3:
            warnings_list.append("Very small sample size (n < 3)")
            assumptions_met = False
        
        # Choose appropriate test based on assumptions
        test_method, test_stat, p_value = self._choose_and_run_test(
            a, b, warnings_list
        )
        
        # Calculate effect size
        effect_size = self._calculate_effect_size(a, b, test_method)
        
        # Calculate confidence interval for difference
        ci_lower, ci_upper = self._calculate_confidence_interval(
            a, b, alpha, test_method
        )
        
        # Determine significance
        is_significant = p_value < alpha
        
        # Check practical significance
        min_effect = self.min_detectable_effects.get(metric_type, 0.1)
        practical_significance = abs(effect_size) >= min_effect
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            agent_a, agent_b, mean_a, mean_b, is_significant,
            practical_significance, effect_size, metric_type
        )
        
        return ABTestResult(
            test_name=f"{agent_a}_vs_{agent_b}_{metric_type.value}",
            agent_a=agent_a,
            agent_b=agent_b,
            metric=metric_type.value,
            n_a=n_a,
            n_b=n_b,
            mean_a=mean_a,
            mean_b=mean_b,
            std_a=std_a,
            std_b=std_b,
            test_statistic=test_stat,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=effect_size,
            is_significant=is_significant,
            significance_level=alpha,
            practical_significance=practical_significance,
            recommendation=recommendation,
            test_method=test_method,
            assumptions_met=assumptions_met,
            warnings=warnings_list,
            timestamp=datetime.utcnow(),
        )
    
    def _choose_and_run_test(
        self, a: np.ndarray, b: np.ndarray, warnings_list: List[str]
    ) -> Tuple[str, float, float]:
        """Choose and run appropriate statistical test."""
        
        # Check normality assumptions
        normality_a = self._check_normality(a)
        normality_b = self._check_normality(b)
        
        # Check equal variances
        equal_variances = self._check_equal_variances(a, b)
        
        if not equal_variances:
            warnings_list.append("Unequal variances detected")
        
        # Choose test based on assumptions
        if normality_a and normality_b:
            if equal_variances:
                # Student's t-test (equal variances)
                stat, p_value = ttest_ind(a, b, equal_var=True)
                test_method = "students_t_test"
            else:
                # Welch's t-test (unequal variances)
                stat, p_value = ttest_ind(a, b, equal_var=False)
                test_method = "welch_t_test"
        else:
            # Non-parametric Mann-Whitney U test
            warnings_list.append("Non-normal distribution, using non-parametric test")
            stat, p_value = mannwhitneyu(a, b, alternative='two-sided')
            test_method = "mann_whitney_u"
        
        return test_method, stat, p_value
    
    def _check_normality(self, data: np.ndarray, alpha: float = 0.05) -> bool:
        """Check if data follows normal distribution."""
        if len(data) < 8:
            # Too small for reliable normality test
            return True  # Assume normal for small samples
        
        # Use Shapiro-Wilk test
        try:
            _, p_value = stats.shapiro(data)
            return p_value > alpha
        except Exception:
            return True  # Assume normal if test fails
    
    def _check_equal_variances(
        self, a: np.ndarray, b: np.ndarray, alpha: float = 0.05
    ) -> bool:
        """Check if two samples have equal variances."""
        try:
            # Levene's test for equal variances
            _, p_value = stats.levene(a, b)
            return p_value > alpha
        except Exception:
            return True  # Assume equal variances if test fails
    
    def _calculate_effect_size(
        self, a: np.ndarray, b: np.ndarray, test_method: str
    ) -> float:
        """Calculate effect size (Cohen's d or equivalent)."""
        
        if test_method in ["students_t_test", "welch_t_test"]:
            # Cohen's d
            pooled_std = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + 
                                 (len(b) - 1) * np.var(b, ddof=1)) / 
                                (len(a) + len(b) - 2))
            
            if pooled_std == 0:
                return 0.0
            
            return (np.mean(a) - np.mean(b)) / pooled_std
            
        elif test_method == "mann_whitney_u":
            # Rank-biserial correlation (effect size for Mann-Whitney U)
            n_a, n_b = len(a), len(b)
            u_statistic, _ = mannwhitneyu(a, b, alternative='two-sided')
            
            # Convert to rank-biserial correlation
            rb_correlation = 1 - (2 * u_statistic) / (n_a * n_b)
            return rb_correlation
        
        else:
            # Fallback: normalized difference
            pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
            if pooled_std == 0:
                return 0.0
            return (np.mean(a) - np.mean(b)) / pooled_std
    
    def _calculate_confidence_interval(
        self,
        a: np.ndarray,
        b: np.ndarray, 
        alpha: float,
        test_method: str,
        n_bootstrap: int = 1000,
    ) -> Tuple[float, float]:
        """Calculate confidence interval for difference in means."""
        
        confidence_level = 1 - alpha
        
        try:
            if test_method in ["students_t_test", "welch_t_test"]:
                # Parametric CI for difference in means
                mean_diff = np.mean(a) - np.mean(b)
                
                # Standard error of difference
                se_diff = np.sqrt(np.var(a, ddof=1)/len(a) + np.var(b, ddof=1)/len(b))
                
                # Degrees of freedom
                if test_method == "students_t_test":
                    df = len(a) + len(b) - 2
                else:  # Welch's t-test
                    s_a_sq, s_b_sq = np.var(a, ddof=1), np.var(b, ddof=1)
                    n_a, n_b = len(a), len(b)
                    
                    df = ((s_a_sq/n_a + s_b_sq/n_b)**2) / \
                         ((s_a_sq/n_a)**2/(n_a-1) + (s_b_sq/n_b)**2/(n_b-1))
                
                # t-critical value
                t_crit = stats.t.ppf(1 - alpha/2, df)
                
                margin_error = t_crit * se_diff
                return (mean_diff - margin_error, mean_diff + margin_error)
            
            else:
                # Bootstrap CI for non-parametric tests
                return self._bootstrap_ci(a, b, confidence_level, n_bootstrap)
                
        except Exception as e:
            self.logger.warning(f"CI calculation failed: {e}")
            # Fallback: simple percentile method
            return self._bootstrap_ci(a, b, confidence_level, n_bootstrap)
    
    def _bootstrap_ci(
        self,
        a: np.ndarray,
        b: np.ndarray,
        confidence_level: float,
        n_bootstrap: int = 1000,
    ) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval."""
        
        def stat_func(x, y):
            return np.mean(x) - np.mean(y)
        
        # Generate bootstrap samples
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            a_boot = resample(a, n_samples=len(a), random_state=None)
            b_boot = resample(b, n_samples=len(b), random_state=None)
            
            bootstrap_stats.append(stat_func(a_boot, b_boot))
        
        bootstrap_stats = np.array(bootstrap_stats)
        
        # Calculate percentiles
        alpha = 1 - confidence_level
        lower_percentile = (alpha/2) * 100
        upper_percentile = (1 - alpha/2) * 100
        
        ci_lower = np.percentile(bootstrap_stats, lower_percentile)
        ci_upper = np.percentile(bootstrap_stats, upper_percentile)
        
        return (ci_lower, ci_upper)
    
    def _generate_recommendation(
        self,
        agent_a: str,
        agent_b: str,
        mean_a: float,
        mean_b: float,
        is_significant: bool,
        practical_significance: bool,
        effect_size: float,
        metric_type: MetricType,
    ) -> str:
        """Generate actionable recommendation based on test results."""
        
        # Determine which agent performed better
        better_agent = agent_a if mean_a > mean_b else agent_b
        worse_agent = agent_b if mean_a > mean_b else agent_a
        
        # For some metrics, lower is better (latency, cost, hallucination)
        lower_is_better = metric_type in [
            MetricType.LATENCY, MetricType.COST, MetricType.HALLUCINATION
        ]
        
        if lower_is_better:
            better_agent = agent_a if mean_a < mean_b else agent_b
            worse_agent = agent_b if mean_a < mean_b else agent_a
        
        improvement = abs(mean_a - mean_b)
        improvement_pct = (improvement / max(abs(mean_a), abs(mean_b))) * 100
        
        if is_significant and practical_significance:
            return (f"**STRONG RECOMMENDATION**: Deploy {better_agent}. "
                   f"Shows {improvement_pct:.1f}% improvement over {worse_agent} "
                   f"with statistical significance (p < 0.05) and practical impact "
                   f"(effect size = {effect_size:.3f}).")
        
        elif is_significant and not practical_significance:
            return (f"**WEAK RECOMMENDATION**: {better_agent} shows statistically "
                   f"significant but small improvement ({improvement_pct:.1f}%). "
                   f"Consider cost-benefit analysis before switching.")
        
        elif not is_significant and practical_significance:
            return (f"**INCONCLUSIVE**: {better_agent} shows {improvement_pct:.1f}% "
                   f"improvement but not statistically significant. "
                   f"Consider collecting more data or running longer experiment.")
        
        else:
            return (f"**NO RECOMMENDATION**: No significant difference found "
                   f"between {agent_a} and {agent_b}. Both perform similarly "
                   f"on {metric_type.value}.")
    
    def _extract_metric_values(
        self, results: List[EvaluationResult], metric_type: MetricType
    ) -> List[float]:
        """Extract metric values from evaluation results."""
        values = []
        
        for result in results:
            metric = result.get_metric(metric_type)
            if metric is not None:
                values.append(metric.value)
        
        return values
    
    def calculate_required_sample_size(
        self,
        effect_size: float,
        power: float = 0.8,
        alpha: float = 0.05,
        two_sided: bool = True,
    ) -> int:
        """
        Calculate required sample size for detecting a given effect.
        
        Args:
            effect_size: Minimum detectable effect size (Cohen's d)
            power: Statistical power (1 - beta)
            alpha: Type I error rate
            two_sided: Whether test is two-sided
            
        Returns:
            Required sample size per group
        """
        
        # Use Cohen's formula for sample size calculation
        if two_sided:
            z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        z_beta = stats.norm.ppf(power)
        
        # Cohen's formula
        n = 2 * ((z_alpha + z_beta) / effect_size)**2
        
        return int(np.ceil(n))
    
    def run_power_analysis(
        self,
        sample_sizes: List[int],
        effect_size: float,
        alpha: float = 0.05,
    ) -> Dict[int, float]:
        """
        Calculate statistical power for different sample sizes.
        
        Args:
            sample_sizes: List of sample sizes to analyze
            effect_size: Expected effect size
            alpha: Significance level
            
        Returns:
            Dictionary mapping sample size to statistical power
        """
        
        power_results = {}
        z_alpha = stats.norm.ppf(1 - alpha/2)
        
        for n in sample_sizes:
            # Calculate power using Cohen's formula
            z_beta = effect_size * np.sqrt(n/2) - z_alpha
            power = stats.norm.cdf(z_beta)
            power_results[n] = max(0.0, min(1.0, power))
        
        return power_results
    
    def sequential_testing(
        self,
        results_a: List[EvaluationResult],
        results_b: List[EvaluationResult],
        metric_type: MetricType,
        alpha: float = 0.05,
        beta: float = 0.2,
        effect_size: float = 0.5,
        check_interval: int = 10,
    ) -> Dict[str, Any]:
        """
        Perform sequential A/B testing with early stopping.
        
        Args:
            results_a: Ongoing results for agent A
            results_b: Ongoing results for agent B  
            metric_type: Metric to analyze
            alpha: Type I error rate
            beta: Type II error rate (1 - power)
            effect_size: Minimum detectable effect
            check_interval: How often to check for significance
            
        Returns:
            Sequential testing results with stopping recommendation
        """
        
        values_a = self._extract_metric_values(results_a, metric_type)
        values_b = self._extract_metric_values(results_b, metric_type)
        
        n_a, n_b = len(values_a), len(values_b)
        min_samples = max(n_a, n_b)
        
        # Sequential testing boundaries (simplified Wald sequential test)
        log_alpha = np.log(alpha)
        log_beta = np.log(beta)
        log_one_minus_alpha = np.log(1 - alpha)
        log_one_minus_beta = np.log(1 - beta)
        
        # Calculate test statistic for current data
        if min_samples >= check_interval:
            test_result = self._perform_ab_test(
                values_a, values_b,
                results_a[0].agent_name if results_a else "Agent_A",
                results_b[0].agent_name if results_b else "Agent_B", 
                metric_type, alpha
            )
            
            # Sequential boundaries
            upper_boundary = log_one_minus_beta - log_alpha
            lower_boundary = log_beta - log_one_minus_alpha
            
            # Log likelihood ratio (simplified)
            mean_diff = np.mean(values_a) - np.mean(values_b)
            se_diff = np.sqrt(np.var(values_a, ddof=1)/len(values_a) + 
                            np.var(values_b, ddof=1)/len(values_b))
            
            if se_diff > 0:
                z_score = mean_diff / se_diff
                log_lr = z_score * effect_size - (effect_size**2) / 2
            else:
                log_lr = 0
            
            # Decision
            if log_lr >= upper_boundary:
                decision = "stop_reject_null"
                recommendation = f"Stop test: {results_a[0].agent_name if results_a else 'Agent_A'} is significantly better"
            elif log_lr <= lower_boundary:
                decision = "stop_accept_null"
                recommendation = "Stop test: No significant difference detected"
            else:
                decision = "continue"
                recommendation = f"Continue testing: Need more data (current n={min_samples})"
            
            return {
                "decision": decision,
                "recommendation": recommendation,
                "current_sample_size": min_samples,
                "test_result": test_result,
                "log_likelihood_ratio": log_lr,
                "boundaries": {
                    "upper": upper_boundary,
                    "lower": lower_boundary,
                },
                "estimated_remaining_samples": max(0, 
                    self.calculate_required_sample_size(effect_size, 1-beta, alpha) - min_samples
                ),
            }
        
        else:
            return {
                "decision": "continue",
                "recommendation": f"Continue testing: Insufficient data (current n={min_samples}, minimum={check_interval})",
                "current_sample_size": min_samples,
                "estimated_remaining_samples": check_interval - min_samples,
            }
    
    def multi_armed_bandit_analysis(
        self,
        agent_results: Dict[str, List[EvaluationResult]],
        metric_type: MetricType,
        exploration_rate: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Analyze multiple agents using multi-armed bandit approach.
        
        Args:
            agent_results: Dictionary mapping agent names to results
            metric_type: Metric to optimize
            exploration_rate: Epsilon for epsilon-greedy strategy
            
        Returns:
            Bandit analysis with recommendations
        """
        
        agent_stats = {}
        
        for agent_name, results in agent_results.items():
            values = self._extract_metric_values(results, metric_type)
            
            if values:
                agent_stats[agent_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values, ddof=1),
                    "n": len(values),
                    "confidence_bound": self._calculate_ucb(values),
                }
        
        if not agent_stats:
            return {"error": "No valid data found"}
        
        # Determine best agent
        # For metrics where lower is better
        lower_is_better = metric_type in [
            MetricType.LATENCY, MetricType.COST, MetricType.HALLUCINATION
        ]
        
        if lower_is_better:
            best_agent = min(agent_stats.keys(), key=lambda x: agent_stats[x]["mean"])
            best_ucb_agent = min(agent_stats.keys(), key=lambda x: agent_stats[x]["confidence_bound"])
        else:
            best_agent = max(agent_stats.keys(), key=lambda x: agent_stats[x]["mean"])
            best_ucb_agent = max(agent_stats.keys(), key=lambda x: agent_stats[x]["confidence_bound"])
        
        # Thompson Sampling probabilities
        thompson_probs = self._calculate_thompson_probabilities(
            agent_stats, lower_is_better
        )
        
        return {
            "best_agent_mean": best_agent,
            "best_agent_ucb": best_ucb_agent,
            "agent_statistics": agent_stats,
            "thompson_sampling_probabilities": thompson_probs,
            "recommendation": {
                "exploit": best_agent,
                "explore": best_ucb_agent,
                "strategy": f"Use epsilon-greedy with ε={exploration_rate}",
            },
        }
    
    def _calculate_ucb(self, values: List[float], c: float = 1.0) -> float:
        """Calculate Upper Confidence Bound."""
        if not values:
            return float('inf')
        
        mean = np.mean(values)
        n = len(values)
        confidence_width = c * np.sqrt(np.log(n) / n) if n > 0 else 0
        
        return mean + confidence_width
    
    def _calculate_thompson_probabilities(
        self,
        agent_stats: Dict[str, Dict],
        lower_is_better: bool,
        n_samples: int = 1000,
    ) -> Dict[str, float]:
        """Calculate Thompson sampling probabilities."""
        
        probabilities = {}
        agent_names = list(agent_stats.keys())
        
        if len(agent_names) <= 1:
            return {name: 1.0 for name in agent_names}
        
        win_counts = {name: 0 for name in agent_names}
        
        # Monte Carlo simulation
        for _ in range(n_samples):
            agent_samples = {}
            
            # Sample from posterior distribution (assuming normal)
            for name, stats in agent_stats.items():
                mean = stats["mean"]
                std = stats["std"]
                n = stats["n"]
                
                # Sample from t-distribution (more conservative)
                if n > 1:
                    sample = np.random.normal(mean, std / np.sqrt(n))
                else:
                    sample = mean
                
                agent_samples[name] = sample
            
            # Determine winner for this sample
            if lower_is_better:
                winner = min(agent_samples.keys(), key=lambda x: agent_samples[x])
            else:
                winner = max(agent_samples.keys(), key=lambda x: agent_samples[x])
            
            win_counts[winner] += 1
        
        # Convert counts to probabilities
        for name in agent_names:
            probabilities[name] = win_counts[name] / n_samples
        
        return probabilities