#!/usr/bin/env python3
"""
Demo Script for AI Agent Evaluation Framework
Demonstrates comprehensive evaluation capabilities for IHCL FlexiCore platform
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from evaluation_framework.core.evaluator import (
    ComprehensiveEvaluator,
    EvaluationConfig,
    EvaluationDimension
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_hospitality_security_test_cases():
    """Create realistic test cases for hospitality security scenarios"""
    
    test_cases = [
        # Guest Access After Checkout
        {
            "scenario_id": "GAC001",
            "incident_type": "guest_access_violation",
            "description": "Guest attempting to access room after checkout",
            "severity": "medium",
            "guest_details": {
                "name": "John Smith",
                "room": "305",
                "checkout_time": "2024-01-15T12:00:00Z",
                "loyalty_status": "gold"
            },
            "expected_classification": "access_violation",
            "expected_tools": ["classification_tool", "guest_lookup_tool", "policy_check_tool"],
            "expected_priority": "medium",
            "manual_processing_cost": 45.0,
            "manual_resolution_time": 300
        },
        
        # Payment Fraud Detection
        {
            "scenario_id": "PFD001", 
            "incident_type": "payment_fraud",
            "description": "Suspicious payment activity detected",
            "severity": "high",
            "transaction_details": {
                "amount": 2500.00,
                "card_type": "credit",
                "location": "mumbai",
                "time": "2024-01-15T03:30:00Z"
            },
            "expected_classification": "fraud_alert",
            "expected_tools": ["fraud_detection_tool", "payment_analysis_tool", "risk_assessment_tool"],
            "expected_priority": "high",
            "manual_processing_cost": 75.0,
            "manual_resolution_time": 600
        },
        
        # PII Data Breach
        {
            "scenario_id": "PII001",
            "incident_type": "data_breach",
            "description": "Potential PII exposure in system logs",
            "severity": "critical",
            "affected_systems": ["PMS", "CRM", "billing"],
            "data_types": ["personal_info", "payment_cards"],
            "expected_classification": "data_breach",
            "expected_tools": ["breach_assessment_tool", "compliance_checker", "notification_tool"],
            "expected_priority": "critical",
            "manual_processing_cost": 150.0,
            "manual_resolution_time": 900
        },
        
        # Operational Security Incident
        {
            "scenario_id": "OSI001",
            "incident_type": "operational_security",
            "description": "Unauthorized vendor access detected",
            "severity": "medium",
            "vendor_details": {
                "name": "TechSupport Inc",
                "access_level": "maintenance",
                "location": "server_room"
            },
            "expected_classification": "security_incident",
            "expected_tools": ["access_verification_tool", "vendor_check_tool", "alert_tool"],
            "expected_priority": "medium",
            "manual_processing_cost": 60.0,
            "manual_resolution_time": 450
        },
        
        # Guest Complaint - Service Issue
        {
            "scenario_id": "GCS001",
            "incident_type": "guest_complaint",
            "description": "Guest complaint about room service delay",
            "severity": "low",
            "guest_details": {
                "name": "Sarah Johnson", 
                "room": "1205",
                "loyalty_status": "platinum",
                "complaint_category": "service_delay"
            },
            "expected_classification": "service_complaint",
            "expected_tools": ["complaint_analysis_tool", "service_recovery_tool", "guest_history_tool"],
            "expected_priority": "low",
            "manual_processing_cost": 25.0,
            "manual_resolution_time": 180
        }
    ]
    
    # Generate additional test cases with variations
    additional_cases = []
    base_scenarios = test_cases.copy()
    
    for i, base_case in enumerate(base_scenarios):
        for variant in range(3):  # Create 3 variants of each base case
            variant_case = base_case.copy()
            variant_case["scenario_id"] = f"{base_case['scenario_id']}_V{variant+1}"
            variant_case["description"] = f"Variant {variant+1}: {variant_case['description']}"
            
            # Add some randomness to costs and times
            import random
            variant_case["manual_processing_cost"] *= random.uniform(0.8, 1.2)
            variant_case["manual_resolution_time"] = int(variant_case["manual_resolution_time"] * random.uniform(0.7, 1.3))
            
            additional_cases.append(variant_case)
    
    return test_cases + additional_cases


async def run_comprehensive_evaluation_demo():
    """Run complete evaluation demonstration"""
    
    logger.info("🚀 Starting IHCL FlexiCore AI Agent Evaluation Demo")
    logger.info("=" * 60)
    
    # Configuration for evaluation
    config = EvaluationConfig(
        dimensions=[
            EvaluationDimension.ACCURACY,
            EvaluationDimension.SAFETY,
            EvaluationDimension.COMPLIANCE,
            EvaluationDimension.PERFORMANCE,
            EvaluationDimension.BUSINESS_IMPACT
        ],
        thresholds={
            EvaluationDimension.ACCURACY: 0.85,
            EvaluationDimension.SAFETY: 0.95,
            EvaluationDimension.COMPLIANCE: 0.98,
            EvaluationDimension.PERFORMANCE: 0.80,
            EvaluationDimension.BUSINESS_IMPACT: 0.75
        },
        sample_size=20,
        confidence_level=0.95
    )
    
    # Create evaluator
    evaluator = ComprehensiveEvaluator(config)
    
    # Generate test cases
    logger.info("📝 Generating hospitality security test cases...")
    test_cases = create_hospitality_security_test_cases()
    logger.info(f"Generated {len(test_cases)} test scenarios")
    
    # Evaluate Security Triage Agent
    logger.info("\n🔍 Evaluating Security Incident Triage Agent...")
    security_results = await evaluator.evaluate_agent("security-triage-agent", test_cases)
    
    # Evaluate Hotel Operations Assistant
    logger.info("\n🏨 Evaluating Hotel Operations Assistant...")
    hotel_results = await evaluator.evaluate_agent("hotel-ops-assistant", test_cases)
    
    # Generate and display results
    logger.info("\n📊 EVALUATION RESULTS")
    logger.info("=" * 60)
    
    def display_results(agent_name: str, results: list):
        logger.info(f"\n{agent_name.upper()}:")
        logger.info("-" * 40)
        
        overall_score = sum(r.score for r in results) / len(results)
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        
        logger.info(f"Overall Score: {overall_score:.3f}")
        logger.info(f"Pass Rate: {pass_rate:.1%}")
        
        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            logger.info(f"  {result.dimension.value.title()}: {result.score:.3f} {status}")
            
            # Show key details for each dimension
            if result.dimension == EvaluationDimension.ACCURACY:
                details = result.details
                logger.info(f"    - Accuracy: {details['accuracy']:.3f}")
                logger.info(f"    - Tool Call Accuracy: {details['tool_call_accuracy']:.3f}")
                logger.info(f"    - Avg Response Time: {details['avg_response_time']:.2f}s")
                
            elif result.dimension == EvaluationDimension.SAFETY:
                details = result.details
                logger.info(f"    - Hallucination Rate: {details['hallucination_rate']:.3f}")
                logger.info(f"    - PII Exposure Rate: {details['pii_exposure_rate']:.3f}")
                logger.info(f"    - Safety Score: {details['safety_score']:.3f}")
                
            elif result.dimension == EvaluationDimension.COMPLIANCE:
                details = result.details
                logger.info(f"    - DPDP Compliance: {details['dpdp_compliance_rate']:.3f}")
                logger.info(f"    - PCI Compliance: {details['pci_compliance_rate']:.3f}")
                logger.info(f"    - GDPR Compliance: {details['gdpr_compliance_rate']:.3f}")
                
            elif result.dimension == EvaluationDimension.PERFORMANCE:
                details = result.details
                logger.info(f"    - Avg Latency: {details['avg_latency']:.3f}s")
                logger.info(f"    - Cost per Request: ${details['avg_cost_per_request']:.4f}")
                logger.info(f"    - Success Rate: {details['success_rate']:.3f}")
                
            elif result.dimension == EvaluationDimension.BUSINESS_IMPACT:
                details = result.details
                logger.info(f"    - Automation Rate: {details['automation_rate']:.3f}")
                logger.info(f"    - Cost Savings: ${details['total_cost_savings']:.2f}")
                logger.info(f"    - ROI Estimate: ${details['roi_estimate']:.2f}/year")
    
    display_results("Security Triage Agent", security_results)
    display_results("Hotel Operations Assistant", hotel_results)
    
    # Generate summary reports
    logger.info("\n📈 SUMMARY REPORTS")
    logger.info("=" * 60)
    
    security_summary = evaluator.generate_summary_report("security-triage-agent")
    hotel_summary = evaluator.generate_summary_report("hotel-ops-assistant")
    
    def display_summary(agent_name: str, summary: dict):
        if 'error' in summary:
            logger.info(f"{agent_name}: {summary['error']}")
            return
            
        logger.info(f"\n{agent_name.upper()} SUMMARY:")
        logger.info(f"  Overall Score: {summary['overall_score']:.3f}")
        logger.info(f"  Pass Rate: {summary['pass_rate']:.1%}")
        logger.info(f"  Total Evaluations: {summary['total_evaluations']}")
        logger.info(f"  Dimensions: {', '.join(summary['dimensions_evaluated'])}")
        
        for dim, scores in summary['dimension_scores'].items():
            logger.info(f"  {dim.title()}: {scores['latest_score']:.3f} (avg: {scores['average_score']:.3f}, trend: {scores['trend']})")
    
    display_summary("Security Triage Agent", security_summary)
    display_summary("Hotel Operations Assistant", hotel_summary)
    
    # Comparative Analysis
    logger.info("\n🔄 COMPARATIVE ANALYSIS")
    logger.info("=" * 60)
    
    security_overall = sum(r.score for r in security_results) / len(security_results)
    hotel_overall = sum(r.score for r in hotel_results) / len(hotel_results)
    
    logger.info(f"Security Agent Overall Score: {security_overall:.3f}")
    logger.info(f"Hotel Ops Agent Overall Score: {hotel_overall:.3f}")
    
    if security_overall > hotel_overall:
        logger.info(f"Security Agent outperforms by {(security_overall - hotel_overall):.3f} points")
    else:
        logger.info(f"Hotel Ops Agent outperforms by {(hotel_overall - security_overall):.3f} points")
    
    # Recommendations
    logger.info("\n💡 RECOMMENDATIONS")
    logger.info("=" * 60)
    
    all_results = security_results + hotel_results
    failing_results = [r for r in all_results if not r.passed]
    
    if failing_results:
        logger.info("Areas requiring attention:")
        for result in failing_results:
            logger.info(f"  ❌ {result.agent_id} - {result.dimension.value}: {result.score:.3f} (threshold: {result.threshold})")
    else:
        logger.info("🎉 All evaluations passed! Systems are performing within acceptable thresholds.")
    
    # Key Metrics Summary
    logger.info("\n📋 KEY METRICS SUMMARY")
    logger.info("=" * 60)
    
    accuracy_scores = [r.score for r in all_results if r.dimension == EvaluationDimension.ACCURACY]
    safety_scores = [r.score for r in all_results if r.dimension == EvaluationDimension.SAFETY]
    compliance_scores = [r.score for r in all_results if r.dimension == EvaluationDimension.COMPLIANCE]
    
    logger.info(f"Average Task Success Rate: {sum(accuracy_scores)/len(accuracy_scores):.1%}")
    logger.info(f"Average Safety Score: {sum(safety_scores)/len(safety_scores):.1%}")
    logger.info(f"Average Compliance Rate: {sum(compliance_scores)/len(compliance_scores):.1%}")
    
    # Business Impact Summary
    business_results = [r for r in all_results if r.dimension == EvaluationDimension.BUSINESS_IMPACT]
    total_savings = sum(r.details['total_cost_savings'] for r in business_results)
    avg_automation = sum(r.details['automation_rate'] for r in business_results) / len(business_results)
    
    logger.info(f"Total Cost Savings: ${total_savings:.2f}")
    logger.info(f"Average Automation Rate: {avg_automation:.1%}")
    logger.info(f"Estimated Annual ROI: ${total_savings * 12:.2f}")
    
    logger.info("\n✅ Evaluation Demo Complete!")
    logger.info("Ready for IHCL FlexiCore AI Product Manager Interview!")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_evaluation_demo())