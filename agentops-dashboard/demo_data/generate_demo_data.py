"""Generate comprehensive demo data for AgentOps Dashboard portfolio demonstration."""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import asyncio
import numpy as np

# Simulate data for the past week
START_DATE = datetime.utcnow() - timedelta(days=7)
END_DATE = datetime.utcnow()

# Agent configurations
AGENTS = [
    {
        "name": "security-triage-agent",
        "type": "security",
        "version": "2.1.0",
        "base_success_rate": 0.965,
        "avg_duration_ms": 1200,
        "avg_cost": 0.045
    },
    {
        "name": "hotel-guest-service",
        "type": "guest_service", 
        "version": "1.8.3",
        "base_success_rate": 0.982,
        "avg_duration_ms": 850,
        "avg_cost": 0.032
    },
    {
        "name": "fraud-detection-agent",
        "type": "security",
        "version": "1.5.1",
        "base_success_rate": 0.941,
        "avg_duration_ms": 2100,
        "avg_cost": 0.078
    },
    {
        "name": "complaint-handler-agent",
        "type": "guest_service",
        "version": "1.3.2",
        "base_success_rate": 0.956,
        "avg_duration_ms": 1450,
        "avg_cost": 0.055
    },
    {
        "name": "quality-assurance-agent",
        "type": "quality",
        "version": "1.1.0",
        "base_success_rate": 0.973,
        "avg_duration_ms": 950,
        "avg_cost": 0.038
    }
]

# Models and providers
MODELS = [
    {"name": "gpt-4-turbo", "provider": "openai", "input_cost": 0.01, "output_cost": 0.03},
    {"name": "gpt-3.5-turbo", "provider": "openai", "input_cost": 0.0015, "output_cost": 0.002},
    {"name": "claude-3-sonnet", "provider": "anthropic", "input_cost": 0.003, "output_cost": 0.015},
    {"name": "claude-3-haiku", "provider": "anthropic", "input_cost": 0.00025, "output_cost": 0.00125},
]

# Environments
ENVIRONMENTS = ["production", "staging", "development"]

# Security incident types
SECURITY_INCIDENT_TYPES = [
    "prompt_injection",
    "pii_exposure", 
    "unauthorized_access",
    "compliance_violation",
    "data_breach",
    "malicious_input",
    "safety_violation"
]

# Sample task types
TASK_TYPES = [
    "incident_triage",
    "guest_inquiry", 
    "fraud_analysis",
    "complaint_resolution",
    "quality_check",
    "security_scan",
    "data_validation"
]


def generate_execution_id() -> str:
    """Generate a realistic execution ID."""
    return f"exec_{uuid.uuid4().hex[:16]}"


def generate_session_id() -> str:
    """Generate a realistic session ID."""
    return f"sess_{uuid.uuid4().hex[:12]}"


def generate_realistic_timestamp(start: datetime, end: datetime) -> datetime:
    """Generate a realistic timestamp with business hour bias."""
    # Weight towards business hours (9 AM - 6 PM)
    total_seconds = int((end - start).total_seconds())
    random_seconds = random.randint(0, total_seconds)
    timestamp = start + timedelta(seconds=random_seconds)
    
    # Bias towards business hours
    hour = timestamp.hour
    if 9 <= hour <= 18:  # Business hours
        # 70% chance to keep business hour timestamp
        if random.random() < 0.7:
            return timestamp
    
    # Adjust to business hours with some probability
    if random.random() < 0.3:
        business_hour = random.randint(9, 18)
        timestamp = timestamp.replace(hour=business_hour)
    
    return timestamp


def generate_agent_execution() -> Dict[str, Any]:
    """Generate a realistic agent execution record."""
    agent = random.choice(AGENTS)
    model = random.choice(MODELS)
    environment = random.choices(
        ENVIRONMENTS, 
        weights=[0.7, 0.2, 0.1]  # Production weighted higher
    )[0]
    
    start_time = generate_realistic_timestamp(START_DATE, END_DATE)
    
    # Generate realistic duration with some variance
    base_duration = agent["avg_duration_ms"]
    duration_variance = random.uniform(0.5, 1.8)
    duration_ms = int(base_duration * duration_variance)
    end_time = start_time + timedelta(milliseconds=duration_ms)
    
    # Determine success based on agent's base success rate
    success = random.random() < agent["base_success_rate"]
    
    # Generate token usage
    input_tokens = random.randint(50, 500)
    output_tokens = random.randint(100, 800) if success else random.randint(20, 100)
    total_tokens = input_tokens + output_tokens
    
    # Calculate cost
    cost = (
        input_tokens * model["input_cost"] / 1000 +
        output_tokens * model["output_cost"] / 1000
    )
    
    # Generate quality scores
    base_confidence = 0.85 if success else 0.45
    confidence_score = max(0.0, min(1.0, base_confidence + random.uniform(-0.15, 0.15)))
    
    accuracy_score = max(0.0, min(1.0, confidence_score + random.uniform(-0.1, 0.1)))
    safety_score = max(0.7, min(1.0, 0.92 + random.uniform(-0.1, 0.08)))
    
    execution = {
        "execution_id": generate_execution_id(),
        "agent_name": agent["name"],
        "agent_version": agent["version"],
        "agent_type": agent["type"],
        "session_id": generate_session_id(),
        "user_id": f"user_{random.randint(1000, 9999)}",
        "environment": environment,
        "task_id": f"task_{uuid.uuid4().hex[:12]}",
        "task_type": random.choice(TASK_TYPES),
        "task_description": f"Process {random.choice(TASK_TYPES).replace('_', ' ')} request",
        "priority": random.choices(
            ["low", "medium", "high", "critical"],
            weights=[0.3, 0.5, 0.15, 0.05]
        )[0],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat() if success else None,
        "duration_ms": duration_ms if success else None,
        "status": "completed" if success else random.choice(["failed", "timeout"]),
        "success": success,
        "error_message": None if success else f"Processing error in {agent['name']}",
        "error_type": None if success else random.choice(["timeout", "api_error", "validation_error"]),
        "tools_used": {
            "classification_tool": True,
            "database_query": True,
            "notification_sender": success
        } if success else {},
        "tool_calls_count": random.randint(2, 8) if success else random.randint(0, 3),
        "tool_success_rate": random.uniform(0.85, 1.0) if success else random.uniform(0.2, 0.7),
        "model_name": model["name"],
        "model_provider": model["provider"],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_usd": round(cost, 6),
        "cost_breakdown": {
            "input_cost": round(input_tokens * model["input_cost"] / 1000, 6),
            "output_cost": round(output_tokens * model["output_cost"] / 1000, 6),
            "total_cost": round(cost, 6)
        },
        "confidence_score": round(confidence_score, 3),
        "accuracy_score": round(accuracy_score, 3),
        "safety_score": round(safety_score, 3),
        "input_data": {
            "request_type": random.choice(TASK_TYPES),
            "priority": random.choice(["low", "medium", "high"]),
            "context": "Sample input context"
        },
        "output_data": {
            "decision": "approved" if success else "failed",
            "confidence": confidence_score,
            "reasoning": "Automated decision based on analysis"
        } if success else None,
        "metadata": {
            "client_version": "1.0.0",
            "request_source": random.choice(["web", "mobile", "api"]),
            "region": random.choice(["us-east-1", "eu-west-1", "ap-south-1"])
        },
        "memory_usage_mb": round(random.uniform(50, 200), 2),
        "cpu_usage_percent": round(random.uniform(10, 80), 2)
    }
    
    return execution


def generate_security_incident() -> Dict[str, Any]:
    """Generate a realistic security incident."""
    incident_type = random.choice(SECURITY_INCIDENT_TYPES)
    
    # Severity distribution: most incidents are low/medium
    severity = random.choices(
        ["critical", "high", "medium", "low"],
        weights=[0.05, 0.15, 0.40, 0.40]
    )[0]
    
    detected_at = generate_realistic_timestamp(START_DATE, END_DATE)
    
    # Resolution status based on age and severity
    age_hours = (datetime.utcnow() - detected_at).total_seconds() / 3600
    
    if severity == "critical":
        resolved_prob = min(0.9, age_hours / 4)  # 4 hour target
    elif severity == "high":
        resolved_prob = min(0.8, age_hours / 24)  # 24 hour target
    else:
        resolved_prob = min(0.7, age_hours / 72)  # 72 hour target
    
    is_resolved = random.random() < resolved_prob
    status = "resolved" if is_resolved else random.choice(["open", "investigating"])
    
    incident = {
        "incident_id": f"sec_{uuid.uuid4().hex[:16]}",
        "execution_id": generate_execution_id() if random.random() < 0.7 else None,
        "incident_type": incident_type,
        "severity": severity,
        "category": "security",
        "detected_at": detected_at.isoformat(),
        "detected_by": "security_monitor_v2",
        "detection_method": "automated",
        "title": f"{incident_type.replace('_', ' ').title()} Detected",
        "description": f"Automated detection of {incident_type} in agent execution",
        "affected_systems": [random.choice(AGENTS)["name"]],
        "status": status,
        "assigned_to": f"security_team_{random.randint(1, 5)}" if status != "open" else None,
        "resolution_time": (detected_at + timedelta(hours=random.randint(1, 48))).isoformat() if is_resolved else None,
        "risk_score": random.uniform(3.0, 9.0),
        "impact_level": severity,
        "likelihood": random.choice(["very_high", "high", "medium", "low"]),
        "compliance_violation": incident_type == "compliance_violation" or random.random() < 0.2,
        "regulations_affected": ["GDPR", "CCPA"] if incident_type in ["pii_exposure", "data_breach"] else None,
        "data_classification": random.choice(["public", "internal", "confidential"]),
        "pii_exposed": incident_type == "pii_exposure",
        "pii_types": ["email", "phone"] if incident_type == "pii_exposure" else None,
        "records_affected": random.randint(1, 100) if incident_type in ["pii_exposure", "data_breach"] else None,
        "attack_vector": random.choice(["input_manipulation", "api_abuse", "social_engineering"]),
        "vulnerability_exploited": f"{incident_type}_vulnerability",
        "indicators_of_compromise": {
            "suspicious_patterns": [f"pattern_{random.randint(1, 10)}"],
            "source_ips": [f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"]
        },
        "evidence": {
            "log_entries": [f"log_{uuid.uuid4().hex[:8]}"],
            "screenshots": []
        },
        "immediate_actions": [
            "Isolated affected system",
            "Notified security team",
            "Initiated investigation"
        ],
        "mitigation_steps": [
            "Applied security patch",
            "Updated monitoring rules",
            "Increased logging level"
        ] if is_resolved else None,
        "business_impact": f"{severity.title()} impact on operations",
        "financial_impact": random.uniform(1000, 50000) if severity in ["critical", "high"] else None,
        "notifications_sent": True,
        "notification_recipients": ["security@company.com", "ops@company.com"],
        "external_reporting_required": severity == "critical",
        "reported_to_authorities": False,
        "root_cause": "Configuration misconfiguration" if is_resolved else None,
        "resolution_summary": f"Incident resolved by updating {incident_type} controls" if is_resolved else None,
        "lessons_learned": "Enhanced monitoring and alerting" if is_resolved else None,
        "environment": random.choices(ENVIRONMENTS, weights=[0.6, 0.3, 0.1])[0],
        "source_system": random.choice(AGENTS)["name"],
        "incident_metadata": {
            "detection_confidence": random.uniform(0.7, 1.0),
            "false_positive_probability": random.uniform(0.0, 0.3)
        }
    }
    
    return incident


def generate_evaluation_result(execution_id: str = None) -> Dict[str, Any]:
    """Generate a realistic evaluation result."""
    if not execution_id:
        execution_id = generate_execution_id()
    
    evaluator_name = random.choice(["security_evaluator", "guest_service_evaluator", "quality_evaluator"])
    evaluation_time = generate_realistic_timestamp(START_DATE, END_DATE)
    
    # Generate realistic scores with some correlation
    base_score = random.uniform(0.7, 0.95)
    noise = random.uniform(-0.1, 0.1)
    
    overall_score = max(0.0, min(1.0, base_score + noise))
    accuracy_score = max(0.0, min(1.0, base_score + random.uniform(-0.05, 0.05)))
    safety_score = max(0.0, min(1.0, base_score + random.uniform(-0.03, 0.03)))
    
    passed = overall_score >= 0.8 and safety_score >= 0.85
    
    evaluation = {
        "evaluation_id": f"eval_{uuid.uuid4().hex[:16]}",
        "execution_id": execution_id,
        "evaluation_type": "automatic",
        "evaluator_name": evaluator_name,
        "evaluator_version": "1.0.0",
        "test_suite": random.choice(["production", "security", "quality", "compliance"]),
        "test_case": f"test_case_{random.randint(1, 50)}",
        "test_description": "Automated evaluation of agent performance",
        "evaluation_time": evaluation_time.isoformat(),
        "evaluation_duration_ms": random.randint(100, 1000),
        "overall_score": round(overall_score, 3),
        "passed": passed,
        "grade": "A" if overall_score >= 0.9 else "B" if overall_score >= 0.8 else "C",
        "accuracy_score": round(accuracy_score, 3),
        "relevance_score": round(max(0.0, min(1.0, base_score + random.uniform(-0.08, 0.08))), 3),
        "safety_score": round(safety_score, 3),
        "coherence_score": round(max(0.0, min(1.0, base_score + random.uniform(-0.06, 0.06))), 3),
        "completeness_score": round(max(0.0, min(1.0, base_score + random.uniform(-0.07, 0.07))), 3),
        "efficiency_score": round(max(0.0, min(1.0, base_score + random.uniform(-0.05, 0.05))), 3),
        "hallucination_detected": random.random() < 0.05,
        "hallucination_score": random.uniform(0.0, 0.3) if random.random() < 0.05 else None,
        "pii_exposure_detected": random.random() < 0.02,
        "bias_detected": random.random() < 0.03,
        "toxicity_score": random.uniform(0.0, 0.1),
        "task_completion_rate": 1.0 if passed else random.uniform(0.3, 0.9),
        "tool_usage_accuracy": round(max(0.0, min(1.0, base_score + random.uniform(-0.1, 0.1))), 3),
        "response_appropriateness": round(max(0.0, min(1.0, base_score + random.uniform(-0.05, 0.05))), 3),
        "baseline_score": round(max(0.0, min(1.0, base_score - 0.1)), 3),
        "improvement_percentage": round(random.uniform(-5, 15), 2),
        "statistical_significance": round(random.uniform(0.8, 0.99), 3),
        "expected_output": {"expected_decision": "approved", "confidence_threshold": 0.8},
        "actual_output": {"decision": "approved" if passed else "rejected", "confidence": overall_score},
        "ground_truth": {"correct_decision": "approved", "reasoning": "Valid request"},
        "human_feedback": None,
        "human_rating": random.randint(3, 5) if random.random() < 0.1 else None,
        "evaluator_comments": "Automated evaluation completed successfully",
        "error_categories": {"logic_errors": 0, "safety_issues": 1 if not passed else 0},
        "failure_modes": {"timeout": False, "exception": False, "safety_violation": not passed},
        "metrics_breakdown": {
            "response_time": random.randint(500, 2000),
            "token_efficiency": random.uniform(0.7, 1.0),
            "cost_efficiency": random.uniform(0.8, 1.0)
        },
        "evaluation_metadata": {
            "model_temperature": 0.7,
            "max_tokens": 1000,
            "evaluation_framework": "AgentOps v1.0"
        },
        "environment": random.choices(ENVIRONMENTS, weights=[0.7, 0.2, 0.1])[0],
        "model_version": random.choice(MODELS)["name"],
        "configuration_hash": f"config_{uuid.uuid4().hex[:8]}"
    }
    
    return evaluation


def generate_cost_tracking() -> Dict[str, Any]:
    """Generate a realistic cost tracking record."""
    service = random.choice(MODELS)
    billing_date = (START_DATE + timedelta(days=random.randint(0, 7))).date()
    
    # Generate usage metrics
    request_count = random.randint(100, 5000)
    input_tokens = random.randint(50000, 500000)
    output_tokens = random.randint(20000, 300000)
    total_tokens = input_tokens + output_tokens
    
    # Calculate costs
    input_cost = input_tokens * service["input_cost"] / 1000
    output_cost = output_tokens * service["output_cost"] / 1000
    total_cost = input_cost + output_cost
    
    cost_record = {
        "cost_id": f"cost_{uuid.uuid4().hex[:16]}",
        "execution_id": generate_execution_id() if random.random() < 0.3 else None,
        "billing_date": billing_date.isoformat(),
        "billing_hour": random.randint(0, 23),
        "service_name": service["name"],
        "service_type": "llm_api",
        "provider": service["provider"],
        "model_name": service["name"],
        "model_version": "latest",
        "model_tier": service["name"].split("-")[0],
        "request_count": request_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "base_cost": round(total_cost * 0.8, 6),
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "processing_cost": round(total_cost * 0.1, 6),
        "storage_cost": round(total_cost * 0.1, 6),
        "total_cost": round(total_cost, 6),
        "input_price_per_token": service["input_cost"] / 1000,
        "output_price_per_token": service["output_cost"] / 1000,
        "request_price": round(total_cost / request_count, 6),
        "project_name": random.choice(["ihcl-agents", "security-platform", "guest-services"]),
        "team_name": random.choice(["security-team", "guest-services", "ai-platform"]),
        "cost_center": f"cc_{random.randint(1000, 9999)}",
        "environment": random.choices(ENVIRONMENTS, weights=[0.7, 0.2, 0.1])[0],
        "agent_name": random.choice(AGENTS)["name"],
        "task_type": random.choice(TASK_TYPES),
        "user_id": f"user_{random.randint(1000, 9999)}",
        "session_id": generate_session_id(),
        "latency_ms": random.randint(500, 3000),
        "success_rate": random.uniform(0.9, 1.0),
        "quality_score": random.uniform(0.8, 0.95),
        "optimization_potential": random.uniform(0, 25) if random.random() < 0.3 else 0,
        "recommended_model": random.choice(MODELS)["name"] if random.random() < 0.2 else None,
        "caching_eligible": random.random() < 0.4,
        "batch_eligible": random.random() < 0.3,
        "budget_category": random.choice(["production", "development", "testing"]),
        "budget_allocation": round(random.uniform(1000, 10000), 2),
        "budget_remaining": round(random.uniform(500, 8000), 2),
        "cost_per_task": round(total_cost / max(1, random.randint(1, 50)), 6),
        "cost_per_user": round(total_cost / max(1, random.randint(1, 20)), 6),
        "cost_per_successful_outcome": round(total_cost / max(1, random.randint(1, 30)), 6),
        "baseline_cost": round(total_cost * 1.1, 6),
        "cost_variance": round(random.uniform(-10, 10), 2),
        "cost_trend": random.choice(["increasing", "decreasing", "stable"]),
        "tags": [random.choice(["production", "ai", "security", "customer-service"])],
        "metadata": {
            "region": random.choice(["us-east-1", "eu-west-1", "ap-south-1"]),
            "instance_type": random.choice(["standard", "optimized", "premium"])
        },
        "business_value": round(random.uniform(100, 1000), 2),
        "roi_percentage": round(random.uniform(150, 400), 2),
        "payback_period_days": random.randint(30, 180)
    }
    
    return cost_record


def save_demo_data():
    """Generate and save comprehensive demo data."""
    print("Generating comprehensive demo data for AgentOps Dashboard...")
    
    # Generate executions (5000 records)
    print("Generating agent executions...")
    executions = []
    for i in range(5000):
        executions.append(generate_agent_execution())
        if i % 1000 == 0:
            print(f"  Generated {i+1}/5000 executions")
    
    # Generate security incidents (150 records)
    print("Generating security incidents...")
    incidents = []
    for i in range(150):
        incidents.append(generate_security_incident())
    
    # Generate evaluations (3000 records)
    print("Generating evaluation results...")
    evaluations = []
    for i in range(3000):
        # 70% linked to executions, 30% standalone
        execution_id = executions[random.randint(0, len(executions)-1)]["execution_id"] if random.random() < 0.7 else None
        evaluations.append(generate_evaluation_result(execution_id))
        if i % 1000 == 0:
            print(f"  Generated {i+1}/3000 evaluations")
    
    # Generate cost tracking (2000 records)
    print("Generating cost tracking records...")
    costs = []
    for i in range(2000):
        costs.append(generate_cost_tracking())
        if i % 500 == 0:
            print(f"  Generated {i+1}/2000 cost records")
    
    # Save all data to JSON files
    demo_data = {
        "executions": executions,
        "security_incidents": incidents,
        "evaluations": evaluations,
        "cost_tracking": costs,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "data_period": {
                "start": START_DATE.isoformat(),
                "end": END_DATE.isoformat()
            },
            "record_counts": {
                "executions": len(executions),
                "security_incidents": len(incidents),
                "evaluations": len(evaluations),
                "cost_tracking": len(costs)
            }
        }
    }
    
    # Save to files
    with open("/Users/priyasingh/ihcl-ai-portfolio/agentops-dashboard/demo_data/demo_data.json", "w") as f:
        json.dump(demo_data, f, indent=2, default=str)
    
    # Save individual files for easier testing
    with open("/Users/priyasingh/ihcl-ai-portfolio/agentops-dashboard/demo_data/executions.json", "w") as f:
        json.dump(executions, f, indent=2, default=str)
    
    with open("/Users/priyasingh/ihcl-ai-portfolio/agentops-dashboard/demo_data/security_incidents.json", "w") as f:
        json.dump(incidents, f, indent=2, default=str)
    
    with open("/Users/priyasingh/ihcl-ai-portfolio/agentops-dashboard/demo_data/evaluations.json", "w") as f:
        json.dump(evaluations, f, indent=2, default=str)
    
    with open("/Users/priyasingh/ihcl-ai-portfolio/agentops-dashboard/demo_data/cost_tracking.json", "w") as f:
        json.dump(costs, f, indent=2, default=str)
    
    print("\nDemo data generation completed!")
    print(f"Generated {len(executions)} executions")
    print(f"Generated {len(incidents)} security incidents")
    print(f"Generated {len(evaluations)} evaluations")
    print(f"Generated {len(costs)} cost tracking records")
    print("\nFiles saved to demo_data/ directory")


if __name__ == "__main__":
    save_demo_data()