"""Main evaluation framework orchestrating all evaluation components."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Set

import structlog
from rich.progress import Progress, TaskID

from ..datasets.golden_dataset import GoldenDataset
from ..metrics.evaluation_metrics import EvaluationMetrics
from ..hallucination.detector import HallucinationDetector
from ..compliance.validator import ComplianceValidator
from ..benchmarking.performance import PerformanceBenchmark
from ..statistical.ab_testing import ABTestFramework
from ..reporting.generator import ReportGenerator
from ..utils.config import Config
from .evaluator import AgentEvaluator
from .types import (
    EvaluationConfig,
    EvaluationResult,
    EvaluationStatus,
    MetricType,
    TestCase,
)

logger = structlog.get_logger(__name__)


class EvaluationFramework:
    """
    Comprehensive evaluation framework for agentic AI systems.
    
    Orchestrates all evaluation components including dataset management,
    metrics calculation, hallucination detection, compliance validation,
    performance benchmarking, and statistical analysis.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the evaluation framework."""
        self.config = config or Config()
        self.logger = logger.bind(component="EvaluationFramework")
        
        # Initialize core components
        self.golden_dataset = GoldenDataset(self.config)
        self.metrics_calculator = EvaluationMetrics(self.config)
        self.hallucination_detector = HallucinationDetector(self.config)
        self.compliance_validator = ComplianceValidator(self.config)
        self.performance_benchmark = PerformanceBenchmark(self.config)
        self.ab_testing = ABTestFramework(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Evaluation state
        self.evaluators: Dict[str, AgentEvaluator] = {}
        self.results: List[EvaluationResult] = []
        self.running_evaluations: Set[str] = set()
        
        self.logger.info("Evaluation framework initialized", config=self.config.to_dict())
    
    def register_agent(self, agent_config: Dict) -> str:
        """Register an agent for evaluation."""
        agent_name = agent_config["name"]
        evaluator = AgentEvaluator(
            agent_config=agent_config,
            metrics_calculator=self.metrics_calculator,
            hallucination_detector=self.hallucination_detector,
            compliance_validator=self.compliance_validator,
        )
        self.evaluators[agent_name] = evaluator
        
        self.logger.info("Agent registered", agent_name=agent_name)
        return agent_name
    
    def load_test_suite(self, suite_name: str) -> List[TestCase]:
        """Load a test suite from the golden dataset."""
        test_cases = self.golden_dataset.get_test_suite(suite_name)
        self.logger.info("Test suite loaded", suite=suite_name, count=len(test_cases))
        return test_cases
    
    async def evaluate_single(
        self,
        agent_name: str,
        test_case: TestCase,
        metrics: Optional[List[MetricType]] = None,
    ) -> EvaluationResult:
        """Evaluate a single agent on a single test case."""
        if agent_name not in self.evaluators:
            raise ValueError(f"Agent {agent_name} not registered")
        
        evaluator = self.evaluators[agent_name]
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(
                "Starting single evaluation",
                agent=agent_name,
                test_case=test_case.id,
            )
            
            result = await evaluator.evaluate(test_case, metrics)
            result.execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(
                "Single evaluation completed",
                agent=agent_name,
                test_case=test_case.id,
                score=result.get_overall_score(),
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Single evaluation failed",
                agent=agent_name,
                test_case=test_case.id,
                error=str(e),
            )
            
            return EvaluationResult(
                test_case_id=test_case.id,
                agent_name=agent_name,
                status=EvaluationStatus.FAILED,
                errors=[str(e)],
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def evaluate_batch(
        self,
        agent_names: List[str],
        test_cases: List[TestCase],
        config: EvaluationConfig,
    ) -> List[EvaluationResult]:
        """Evaluate multiple agents on multiple test cases."""
        results = []
        
        # Validate agents
        for agent_name in agent_names:
            if agent_name not in self.evaluators:
                raise ValueError(f"Agent {agent_name} not registered")
        
        total_evaluations = len(agent_names) * len(test_cases)
        
        with Progress() as progress:
            task = progress.add_task(
                "Running evaluations...", 
                total=total_evaluations
            )
            
            if config.parallel_execution:
                results = await self._evaluate_parallel(
                    agent_names, test_cases, config, progress, task
                )
            else:
                results = await self._evaluate_sequential(
                    agent_names, test_cases, config, progress, task
                )
        
        self.results.extend(results)
        return results
    
    async def _evaluate_parallel(
        self,
        agent_names: List[str],
        test_cases: List[TestCase],
        config: EvaluationConfig,
        progress: Progress,
        task: TaskID,
    ) -> List[EvaluationResult]:
        """Run evaluations in parallel."""
        semaphore = asyncio.Semaphore(config.max_workers)
        
        async def evaluate_with_semaphore(agent_name: str, test_case: TestCase):
            async with semaphore:
                result = await self.evaluate_single(agent_name, test_case, config.metrics)
                progress.advance(task)
                return result
        
        tasks = [
            evaluate_with_semaphore(agent_name, test_case)
            for agent_name in agent_names
            for test_case in test_cases
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error("Evaluation task failed", error=str(result))
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _evaluate_sequential(
        self,
        agent_names: List[str],
        test_cases: List[TestCase],
        config: EvaluationConfig,
        progress: Progress,
        task: TaskID,
    ) -> List[EvaluationResult]:
        """Run evaluations sequentially."""
        results = []
        
        for agent_name in agent_names:
            for test_case in test_cases:
                result = await self.evaluate_single(agent_name, test_case, config.metrics)
                results.append(result)
                progress.advance(task)
        
        return results
    
    def run_ab_test(
        self,
        agent_a: str,
        agent_b: str,
        test_cases: List[TestCase],
        significance_level: float = 0.05,
    ) -> Dict:
        """Run A/B test between two agents."""
        if agent_a not in self.evaluators:
            raise ValueError(f"Agent {agent_a} not registered")
        if agent_b not in self.evaluators:
            raise ValueError(f"Agent {agent_b} not registered")
        
        # Get results for both agents
        results_a = [r for r in self.results if r.agent_name == agent_a]
        results_b = [r for r in self.results if r.agent_name == agent_b]
        
        if not results_a or not results_b:
            raise ValueError("No evaluation results found for A/B testing")
        
        return self.ab_testing.compare_agents(
            results_a, results_b, significance_level
        )
    
    def benchmark_performance(
        self,
        agent_name: str,
        load_levels: List[int],
        duration: int = 60,
    ) -> Dict:
        """Run performance benchmarking for an agent."""
        if agent_name not in self.evaluators:
            raise ValueError(f"Agent {agent_name} not registered")
        
        evaluator = self.evaluators[agent_name]
        return self.performance_benchmark.run_load_test(
            evaluator, load_levels, duration
        )
    
    def validate_compliance(
        self,
        results: List[EvaluationResult],
        regulations: Optional[List[str]] = None,
    ) -> Dict:
        """Validate compliance across evaluation results."""
        regulations = regulations or ["GDPR", "PCI DSS", "DPDP"]
        return self.compliance_validator.validate_batch(results, regulations)
    
    def detect_hallucinations(
        self,
        results: List[EvaluationResult],
        threshold: float = 0.8,
    ) -> Dict:
        """Detect hallucinations in evaluation results."""
        return self.hallucination_detector.detect_batch(results, threshold)
    
    def generate_report(
        self,
        results: List[EvaluationResult],
        report_type: str = "comprehensive",
        output_path: Optional[str] = None,
    ) -> str:
        """Generate evaluation report."""
        return self.report_generator.generate(
            results=results,
            report_type=report_type,
            output_path=output_path,
        )
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for all evaluation results."""
        if not self.results:
            return {"message": "No evaluation results available"}
        
        # Overall statistics
        total_evaluations = len(self.results)
        successful = len([r for r in self.results if r.status == EvaluationStatus.COMPLETED])
        failed = len([r for r in self.results if r.status == EvaluationStatus.FAILED])
        
        # Agent performance
        agent_scores = {}
        for result in self.results:
            if result.agent_name not in agent_scores:
                agent_scores[result.agent_name] = []
            agent_scores[result.agent_name].append(result.get_overall_score())
        
        # Metric statistics
        metric_stats = self.metrics_calculator.get_aggregate_statistics(self.results)
        
        return {
            "overview": {
                "total_evaluations": total_evaluations,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total_evaluations if total_evaluations > 0 else 0,
            },
            "agent_performance": {
                agent: {
                    "mean_score": sum(scores) / len(scores),
                    "evaluations": len(scores),
                }
                for agent, scores in agent_scores.items()
            },
            "metrics": metric_stats,
        }
    
    def export_results(self, format: str = "json", output_path: Optional[str] = None) -> str:
        """Export evaluation results in specified format."""
        if format == "json":
            return self._export_json(output_path)
        elif format == "csv":
            return self._export_csv(output_path)
        elif format == "xlsx":
            return self._export_excel(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, output_path: Optional[str] = None) -> str:
        """Export results as JSON."""
        import json
        from pathlib import Path
        
        if not output_path:
            output_path = f"evaluation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_path)
        
        # Convert results to dict format
        data = {
            "metadata": {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_results": len(self.results),
                "framework_version": "1.0.0",
            },
            "results": [
                {
                    "test_case_id": r.test_case_id,
                    "agent_name": r.agent_name,
                    "status": r.status.value,
                    "metrics": [
                        {
                            "type": m.metric_type.value,
                            "value": m.value,
                            "unit": m.unit,
                            "passed": m.passed,
                        }
                        for m in r.metrics
                    ],
                    "execution_time": r.execution_time,
                    "timestamp": r.timestamp.isoformat(),
                    "overall_score": r.get_overall_score(),
                }
                for r in self.results
            ],
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(output_path)
    
    def _export_csv(self, output_path: Optional[str] = None) -> str:
        """Export results as CSV."""
        import pandas as pd
        from pathlib import Path
        
        if not output_path:
            output_path = f"evaluation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Flatten results for CSV
        rows = []
        for result in self.results:
            base_row = {
                "test_case_id": result.test_case_id,
                "agent_name": result.agent_name,
                "status": result.status.value,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat(),
                "overall_score": result.get_overall_score(),
            }
            
            # Add metric values as columns
            for metric in result.metrics:
                base_row[f"{metric.metric_type.value}_value"] = metric.value
                base_row[f"{metric.metric_type.value}_passed"] = metric.passed
            
            rows.append(base_row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        
        return str(output_path)
    
    def _export_excel(self, output_path: Optional[str] = None) -> str:
        """Export results as Excel with multiple sheets."""
        import pandas as pd
        from pathlib import Path
        
        if not output_path:
            output_path = f"evaluation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary = self.get_summary_statistics()
            pd.DataFrame([summary["overview"]]).to_excel(
                writer, sheet_name="Summary", index=False
            )
            
            # Detailed results sheet
            self._export_csv(None)  # Create temporary CSV data
            rows = []
            for result in self.results:
                base_row = {
                    "test_case_id": result.test_case_id,
                    "agent_name": result.agent_name,
                    "status": result.status.value,
                    "execution_time": result.execution_time,
                    "timestamp": result.timestamp.isoformat(),
                    "overall_score": result.get_overall_score(),
                }
                
                for metric in result.metrics:
                    base_row[f"{metric.metric_type.value}_value"] = metric.value
                    base_row[f"{metric.metric_type.value}_passed"] = metric.passed
                
                rows.append(base_row)
            
            pd.DataFrame(rows).to_excel(writer, sheet_name="Detailed Results", index=False)
            
            # Agent comparison sheet
            agent_data = []
            for agent, perf in summary["agent_performance"].items():
                agent_data.append({
                    "agent_name": agent,
                    "mean_score": perf["mean_score"],
                    "total_evaluations": perf["evaluations"],
                })
            
            pd.DataFrame(agent_data).to_excel(
                writer, sheet_name="Agent Comparison", index=False
            )
        
        return str(output_path)