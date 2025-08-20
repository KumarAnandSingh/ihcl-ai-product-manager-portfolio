#!/usr/bin/env python3
"""
Security Incident Triage Agent - Interactive Demo

This demo showcases the production-ready capabilities of the Security Incident
Triage Agent specifically designed for hospitality/hotel security scenarios.

Features demonstrated:
- AI-powered incident classification and prioritization
- Hospitality-specific security playbooks and responses
- Human-in-the-loop gates for high-risk actions
- Compliance checking (DPDP, PCI DSS) with automated notifications
- Safety guardrails and content validation
- Comprehensive evaluation and quality metrics
- Real-time performance monitoring and benchmarking

Usage:
    python examples/demo_security_triage.py
    
Requirements:
    - Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment
    - Redis server running (optional, will fallback to in-memory)
    - Python 3.10+ with all dependencies installed
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from security_triage_agent.core.agent import SecurityTriageAgent
from security_triage_agent.utils.config import SecurityTriageConfig
from security_triage_agent.utils.logger import setup_logger
from security_triage_agent.core.state import IncidentCategory, IncidentPriority


class DemoRunner:
    """Interactive demo runner for Security Incident Triage Agent."""
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.logger = setup_logger("demo", "INFO")
        self.agent = None
        
        # Demo scenarios
        self.demo_scenarios = self._load_demo_scenarios()
    
    def _load_demo_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-defined demo scenarios for different incident types."""
        
        return {
            "guest_access": {
                "title": "Unauthorized Guest Room Access After Checkout",
                "description": (
                    "Guest John Smith (Room 1205) reported accessing his hotel room "
                    "using his key card 4 hours after checkout at 11:00 AM. Security "
                    "discovered the access when the new guest for Room 1205 found "
                    "someone's belongings still in the room at 3:00 PM. Key card "
                    "system logs confirm access at 3:15 PM using Mr. Smith's card."
                ),
                "metadata": {
                    "location": "Floor 12, Room 1205",
                    "property_code": "IHCL_TAJ_MUMBAI_001",
                    "affected_guests": ["john.smith@email.com", "new.guest@email.com"],
                    "affected_systems": ["key_card_system", "room_access_control"],
                    "business_impact": "Guest satisfaction impact, potential privacy breach",
                    "reporting_system": "front_desk_manager",
                    "reported_by": "Front Desk Manager - Sarah Patel"
                },
                "expected_category": IncidentCategory.GUEST_ACCESS,
                "expected_priority": IncidentPriority.HIGH
            },
            
            "payment_fraud": {
                "title": "Suspicious Credit Card Transaction Pattern at Restaurant",
                "description": (
                    "Payment monitoring system flagged 7 credit card transactions "
                    "totaling ₹2,50,000 ($3,000) processed within 15 minutes at "
                    "Tanjore restaurant. All transactions show similar amounts "
                    "(₹35,000-40,000) and were processed using different cards "
                    "but same POS terminal. Transaction patterns suggest potential "
                    "card skimming or fraudulent processing."
                ),
                "metadata": {
                    "location": "Tanjore Restaurant - Main Dining",
                    "property_code": "IHCL_TAJ_MUMBAI_001", 
                    "affected_systems": ["pos_system_rest_001", "payment_processor"],
                    "estimated_cost": 250000.0,
                    "business_impact": "Financial loss risk, payment processor investigation",
                    "reporting_system": "fraud_detection_system",
                    "reported_by": "Finance Manager - Amit Kumar"
                },
                "expected_category": IncidentCategory.PAYMENT_FRAUD,
                "expected_priority": IncidentPriority.HIGH
            },
            
            "pii_breach": {
                "title": "Unauthorized Access to Guest Database - Potential Data Breach",
                "description": (
                    "Security Information and Event Management (SIEM) system detected "
                    "unauthorized access to the guest database containing personal "
                    "information of 1,247 guests. Access occurred between 2:00 AM and "
                    "2:45 AM IST using suspended employee credentials (EMP_001234). "
                    "Accessed data includes names, addresses, phone numbers, email "
                    "addresses, passport numbers, and stay preferences. No payment "
                    "information was accessed."
                ),
                "metadata": {
                    "location": "Data Center - Primary Server Room",
                    "property_code": "IHCL_TAJ_MUMBAI_001",
                    "affected_guests": ["1247 guest records compromised"],
                    "affected_employees": ["Former employee ID: EMP_001234"],
                    "affected_systems": ["guest_crm_db", "reservation_system"],
                    "business_impact": "DPDP compliance violation, potential regulatory fine",
                    "reporting_system": "siem_monitoring",
                    "reported_by": "IT Security Manager - Priya Sharma"
                },
                "expected_category": IncidentCategory.PII_BREACH,
                "expected_priority": IncidentPriority.CRITICAL
            },
            
            "cyber_security": {
                "title": "Ransomware Attack Attempt on Hotel Management Systems",
                "description": (
                    "Advanced threat detection system identified and blocked a "
                    "sophisticated ransomware attack targeting the hotel management "
                    "system. The malware attempted to encrypt reservation data, "
                    "guest information, and billing systems. Attack vector appears "
                    "to be a phishing email opened by housekeeping staff. Systems "
                    "have been isolated and are running on backup infrastructure."
                ),
                "metadata": {
                    "location": "IT Infrastructure - Multiple Systems",
                    "property_code": "IHCL_TAJ_MUMBAI_001",
                    "affected_systems": [
                        "hotel_management_system", 
                        "reservation_system", 
                        "billing_system",
                        "guest_services_portal"
                    ],
                    "business_impact": "Potential operation disruption, data encryption risk",
                    "reporting_system": "endpoint_detection_response",
                    "reported_by": "IT Operations Manager - Rajesh Gupta"
                },
                "expected_category": IncidentCategory.CYBER_SECURITY,
                "expected_priority": IncidentPriority.CRITICAL
            },
            
            "operational_security": {
                "title": "Security Guard Found Sleeping During Night Shift",
                "description": (
                    "Night audit manager discovered security guard sleeping at "
                    "the main entrance security desk during the 2:00 AM rounds. "
                    "CCTV footage shows the guard was asleep for approximately "
                    "45 minutes (1:30 AM - 2:15 AM). During this time, the main "
                    "entrance was unsupervised and emergency response capability "
                    "was compromised. This is the second incident for this employee."
                ),
                "metadata": {
                    "location": "Main Entrance - Security Desk",
                    "property_code": "IHCL_TAJ_MUMBAI_001",
                    "affected_employees": ["Security Guard - Ramesh Singh (ID: SEC_001789)"],
                    "affected_systems": ["physical_security", "cctv_monitoring"],
                    "business_impact": "Guest safety risk, security protocol violation",
                    "reporting_system": "night_audit_manager",
                    "reported_by": "Night Audit Manager - Deepak Verma"
                },
                "expected_category": IncidentCategory.OPERATIONAL_SECURITY,
                "expected_priority": IncidentPriority.MEDIUM
            }
        }
    
    async def initialize_agent(self) -> None:
        """Initialize the Security Triage Agent."""
        
        print("🔧 Initializing Security Incident Triage Agent...")
        
        # Check for API keys
        if not self.use_mock:
            api_key_found = bool(os.getenv("OPENAI_API_KEY")) or bool(os.getenv("ANTHROPIC_API_KEY"))
            if not api_key_found:
                print("⚠️  Warning: No API keys found. Running in mock mode.")
                self.use_mock = True
        
        # Create configuration
        config = SecurityTriageConfig(
            environment="development",
            debug_mode=True,
            log_level="INFO",
            property_type="luxury_resort",
            property_code="IHCL_TAJ_MUMBAI_001",
            guest_privacy_level="maximum",
            llm_model="gpt-4" if not self.use_mock else "mock",
            enable_metrics_collection=True,
            enable_safety_guardrails=True,
            enable_compliance_checks=True,
            enable_human_intervention=True
        )
        
        if self.use_mock:
            from tests.conftest import MockAgent
            self.agent = MockAgent(config)
            print("✅ Mock agent initialized (API keys not available)")
        else:
            self.agent = SecurityTriageAgent(config)
            await self.agent.initialize()
            print("✅ Production agent initialized successfully")
        
        print(f"🏨 Property: {config.property_code} ({config.property_type})")
        print(f"🔒 Privacy Level: {config.guest_privacy_level}")
        print(f"🛡️  Safety Guardrails: {'Enabled' if config.enable_safety_guardrails else 'Disabled'}")
        print(f"📋 Compliance Checks: {'Enabled' if config.enable_compliance_checks else 'Disabled'}")
        print()
    
    async def run_demo_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a specific demo scenario."""
        
        if scenario_name not in self.demo_scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.demo_scenarios[scenario_name]
        
        print(f"🎯 Running Scenario: {scenario_name.replace('_', ' ').title()}")
        print(f"📋 Title: {scenario['title']}")
        print(f"📝 Description: {scenario['description'][:100]}...")
        print()
        
        # Process the incident
        start_time = datetime.utcnow()
        
        try:
            result = await self.agent.process_incident(
                title=scenario["title"],
                description=scenario["description"],
                metadata=scenario["metadata"]
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            print("✅ Incident processed successfully!")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print()
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing incident: {e}")
            return {"error": str(e)}
    
    def display_results(self, result: Dict[str, Any]) -> None:
        """Display incident processing results."""
        
        if "error" in result:
            print(f"❌ Processing failed: {result['error']}")
            return
        
        print("📊 INCIDENT ANALYSIS RESULTS")
        print("=" * 50)
        
        # Basic information
        print(f"🆔 Incident ID: {result['incident_id']}")
        print(f"📅 Timestamp: {result['timestamp']}")
        print(f"✅ Status: {result['status']}")
        print()
        
        # Classification results
        if "classification" in result:
            classification = result["classification"]
            print("🏷️  CLASSIFICATION")
            print(f"   Category: {classification.get('category', 'Unknown')}")
            print(f"   Priority: {classification.get('priority', 'Unknown')}")
            print(f"   Confidence: {classification.get('confidence', 0):.2%}")
            print(f"   Risk Score: {classification.get('risk_score', 0):.1f}/10")
            print()
        
        # Response plan
        if "response_plan" in result and result["response_plan"]:
            response_plan = result["response_plan"]
            print("📋 RESPONSE PLAN")
            
            if response_plan.get("immediate_actions"):
                print("   🚨 Immediate Actions:")
                for i, action in enumerate(response_plan["immediate_actions"][:3], 1):
                    print(f"      {i}. {action}")
                if len(response_plan["immediate_actions"]) > 3:
                    print(f"      ... and {len(response_plan['immediate_actions']) - 3} more")
            
            if response_plan.get("notification_requirements"):
                print("   📢 Notifications Required:")
                for notification in response_plan["notification_requirements"][:3]:
                    print(f"      • {notification}")
            print()
        
        # Quality scores
        if "quality_scores" in result:
            quality = result["quality_scores"]
            print("🎯 QUALITY ASSESSMENT")
            print(f"   Overall Score: {quality.get('overall', 0):.2%}")
            print(f"   Response Completeness: {quality.get('response_completeness', 0):.2%}")
            print(f"   Safety Compliance: {quality.get('safety_compliance', 0):.2%}")
            print()
        
        # Evaluation results
        if "evaluation" in result:
            evaluation = result["evaluation"]
            print("📈 PERFORMANCE EVALUATION")
            print(f"   Grade: {evaluation.get('grade', 'N/A')}")
            print(f"   Overall Score: {evaluation.get('overall_score', 0):.2%}")
            print(f"   Compliance Status: {evaluation.get('compliance_status', 'Unknown')}")
            print(f"   Safety Status: {evaluation.get('safety_status', 'Unknown')}")
            
            if evaluation.get("strengths"):
                print("   ✅ Strengths:")
                for strength in evaluation["strengths"][:2]:
                    print(f"      • {strength}")
            
            if evaluation.get("recommendations"):
                print("   💡 Recommendations:")
                for rec in evaluation["recommendations"][:2]:
                    print(f"      • {rec}")
            print()
        
        # Processing metadata
        if "processing" in result:
            processing = result["processing"]
            print("⚙️  PROCESSING DETAILS")
            print(f"   Total Time: {processing.get('total_time_seconds', 0):.2f} seconds")
            print(f"   Steps Completed: {len(processing.get('completed_steps', []))}")
            print(f"   Human Interventions: {processing.get('human_interventions', 0)}")
            print(f"   Tools Used: {', '.join(processing.get('tool_results', []))}")
            print()
        
        # Historical insights
        if "historical_insights" in result and result["historical_insights"]:
            insights = result["historical_insights"]
            print("🔍 HISTORICAL INSIGHTS")
            print(f"   Similar Incidents Found: {insights.get('similar_incidents_found', 0)}")
            print(f"   Patterns Identified: {insights.get('patterns_identified', 0)}")
            if insights.get("recommendations"):
                print("   📚 Historical Recommendations:")
                for rec in insights["recommendations"]:
                    print(f"      • {rec}")
            print()
    
    async def run_performance_demo(self) -> None:
        """Demonstrate performance monitoring and benchmarking."""
        
        print("📊 PERFORMANCE MONITORING DEMO")
        print("=" * 50)
        
        if hasattr(self.agent, 'get_performance_dashboard'):
            dashboard = await self.agent.get_performance_dashboard(days=7)
            
            print("📈 Performance Dashboard (Last 7 Days)")
            print(f"   Active Incidents: {dashboard.get('active_incidents', 0)}")
            
            if "performance_metrics" in dashboard:
                perf = dashboard["performance_metrics"]
                print(f"   Automation Rate: {perf.get('automation_rate', 0):.1%}")
                print(f"   Escalation Rate: {perf.get('escalation_rate', 0):.1%}")
                print(f"   Avg Processing Time: {perf.get('avg_step_time', 0):.1f}s")
            
            if "benchmark_comparison" in dashboard:
                benchmark = dashboard["benchmark_comparison"]
                if "overall_assessment" in benchmark:
                    overall = benchmark["overall_assessment"]
                    print(f"   Industry Benchmark: {overall.get('performance_level', 'Unknown')}")
                    print(f"   Meets Standards: {overall.get('meets_industry_standards', False)}")
        else:
            print("   Performance monitoring not available in demo mode")
        
        print()
    
    async def interactive_mode(self) -> None:
        """Run interactive demo mode."""
        
        print("🎮 INTERACTIVE DEMO MODE")
        print("=" * 50)
        print("Available scenarios:")
        
        for i, (key, scenario) in enumerate(self.demo_scenarios.items(), 1):
            print(f"   {i}. {key.replace('_', ' ').title()}")
            print(f"      {scenario['title'][:60]}...")
        
        print("   0. Run all scenarios")
        print("   q. Quit")
        print()
        
        while True:
            try:
                choice = input("Select scenario (1-5, 0 for all, q to quit): ").strip().lower()
                
                if choice == 'q':
                    break
                elif choice == '0':
                    await self.run_all_scenarios()
                    break
                else:
                    scenario_num = int(choice)
                    if 1 <= scenario_num <= len(self.demo_scenarios):
                        scenario_key = list(self.demo_scenarios.keys())[scenario_num - 1]
                        result = await self.run_demo_scenario(scenario_key)
                        self.display_results(result)
                        
                        # Ask if user wants to continue
                        if input("\nRun another scenario? (y/n): ").strip().lower() != 'y':
                            break
                    else:
                        print("Invalid selection. Please try again.")
            
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")
            except KeyboardInterrupt:
                print("\n\nDemo interrupted by user.")
                break
    
    async def run_all_scenarios(self) -> None:
        """Run all demo scenarios sequentially."""
        
        print("🚀 RUNNING ALL DEMO SCENARIOS")
        print("=" * 50)
        
        results = {}
        
        for scenario_name in self.demo_scenarios.keys():
            print(f"\n{'='*20} {scenario_name.upper()} {'='*20}")
            
            try:
                result = await self.run_demo_scenario(scenario_name)
                results[scenario_name] = result
                self.display_results(result)
                
                # Brief pause between scenarios
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in scenario {scenario_name}: {e}")
                results[scenario_name] = {"error": str(e)}
        
        # Summary
        print(f"\n{'='*20} SUMMARY {'='*20}")
        successful = sum(1 for r in results.values() if "error" not in r)
        print(f"✅ Scenarios completed: {successful}/{len(results)}")
        
        if successful > 0:
            avg_quality = sum(
                r.get("quality_scores", {}).get("overall", 0) 
                for r in results.values() 
                if "error" not in r
            ) / successful
            
            print(f"📊 Average Quality Score: {avg_quality:.1%}")
        
        # Performance demo
        await self.run_performance_demo()
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.agent and hasattr(self.agent, 'cleanup'):
            await self.agent.cleanup()


async def main():
    """Main demo function."""
    
    parser = argparse.ArgumentParser(description="Security Incident Triage Agent Demo")
    parser.add_argument(
        "--scenario", 
        choices=["guest_access", "payment_fraud", "pii_breach", "cyber_security", "operational_security", "all"],
        help="Specific scenario to run"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--mock", 
        action="store_true",
        help="Use mock agent (no API calls)"
    )
    
    args = parser.parse_args()
    
    # Banner
    print("🛡️  SECURITY INCIDENT TRIAGE AGENT - DEMO")
    print("🏨 Hospitality Security Solutions for IHCL FlexiCore")
    print("=" * 60)
    print()
    
    demo = DemoRunner(use_mock=args.mock)
    
    try:
        await demo.initialize_agent()
        
        if args.interactive:
            await demo.interactive_mode()
        elif args.scenario:
            if args.scenario == "all":
                await demo.run_all_scenarios()
            else:
                result = await demo.run_demo_scenario(args.scenario)
                demo.display_results(result)
        else:
            # Default: run all scenarios
            await demo.run_all_scenarios()
        
        print("\n🎉 Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        if demo.logger:
            demo.logger.error(f"Demo error: {e}", exc_info=True)
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())