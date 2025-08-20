"""
IHCL Evaluation Framework

A comprehensive evaluation framework for agentic AI systems in hospitality security.
Provides multi-dimensional evaluation, golden dataset management, automated testing,
hallucination detection, A/B testing, compliance validation, and performance benchmarking.
"""

__version__ = "1.0.0"
__author__ = "IHCL AI Portfolio Team"

from .core.evaluator import AgentEvaluator
from .core.framework import EvaluationFramework
from .datasets.golden_dataset import GoldenDataset
from .metrics.evaluation_metrics import EvaluationMetrics
from .hallucination.detector import HallucinationDetector
from .compliance.validator import ComplianceValidator
from .benchmarking.performance import PerformanceBenchmark
from .statistical.ab_testing import ABTestFramework

__all__ = [
    "AgentEvaluator",
    "EvaluationFramework", 
    "GoldenDataset",
    "EvaluationMetrics",
    "HallucinationDetector",
    "ComplianceValidator",
    "PerformanceBenchmark",
    "ABTestFramework",
]