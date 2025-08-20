"""
Demo scenarios for Hotel Operations Assistant.
Provides realistic test cases for different operational scenarios.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

# Demo scenarios organized by category
DEMO_SCENARIOS = {
    "guest_service": {
        "description": "General guest service requests and inquiries",
        "scenarios": [
            {
                "title": "Room Service Request",
                "guest_message": "I'd like to order dinner to my room. Do you have any vegetarian options available?",
                "context": {
                    "guest_id": "GUEST001",
                    "room_number": "1205",
                    "language": "en",
                    "priority": "medium",
                    "context_data": {
                        "guest_preferences": {"dietary": "vegetarian"},
                        "loyalty_tier": "Gold"
                    }
                },
                "expected_actions": ["room_service_request_created", "menu_provided", "dietary_preferences_noted"]
            },
            {
                "title": "Spa Booking",
                "guest_message": "Can you help me book a spa appointment for tomorrow afternoon? I'm interested in a relaxing massage.",
                "context": {
                    "guest_id": "GUEST002", 
                    "room_number": "808",
                    "language": "en",
                    "priority": "low",
                    "context_data": {
                        "loyalty_tier": "Platinum",
                        "previous_spa_visits": 3
                    }
                },
                "expected_actions": ["spa_availability_checked", "appointment_booking_initiated"]
            },
            {
                "title": "Hotel Information Request",
                "guest_message": "What time does the gym close? Also, do you have a business center?",
                "context": {
                    "guest_id": "GUEST003",
                    "room_number": "1510",
                    "language": "en",
                    "priority": "low"
                },
                "expected_actions": ["facility_information_provided", "business_center_details_shared"]
            },
            {
                "title": "Late Checkout Request",
                "guest_message": "I have a late flight today. Is it possible to get a late checkout until 3 PM?",
                "context": {
                    "guest_id": "GUEST004",
                    "room_number": "720",
                    "language": "en",
                    "priority": "medium",
                    "context_data": {
                        "checkout_date": "2024-01-20",
                        "loyalty_tier": "Diamond"
                    }
                },
                "expected_actions": ["late_checkout_request_processed", "room_availability_checked"]
            }
        ]
    },
    
    "complaints": {
        "description": "Guest complaints requiring service recovery",
        "scenarios": [
            {
                "title": "Room Cleanliness Issue",
                "guest_message": "I'm very disappointed. My room hasn't been cleaned properly - there are towels on the floor and the bathroom is dirty. This is not what I expect from a luxury hotel.",
                "context": {
                    "guest_id": "GUEST005",
                    "room_number": "1102",
                    "language": "en", 
                    "priority": "high",
                    "context_data": {
                        "loyalty_tier": "Platinum",
                        "vip_status": True,
                        "total_stays": 15
                    }
                },
                "expected_actions": ["immediate_housekeeping_dispatched", "apology_issued", "compensation_offered", "incident_created"]
            },
            {
                "title": "Staff Behavior Complaint",
                "guest_message": "The staff at your restaurant was extremely rude to me tonight. They made me wait 30 minutes for a table despite having a reservation, and when I complained, they were dismissive. I'm considering posting a review about this.",
                "context": {
                    "guest_id": "GUEST006",
                    "room_number": "305",
                    "language": "en",
                    "priority": "urgent",
                    "context_data": {
                        "loyalty_tier": "Gold",
                        "restaurant_reservation_time": "19:30",
                        "complaint_time": "21:15"
                    }
                },
                "expected_actions": ["management_notified", "restaurant_manager_contacted", "service_recovery_plan", "escalation_triggered"]
            },
            {
                "title": "Billing Dispute",
                "guest_message": "I've been charged for services I didn't use. There are charges for minibar items that I never touched, and a spa treatment I didn't book. Please fix this immediately.",
                "context": {
                    "guest_id": "GUEST007",
                    "room_number": "1420",
                    "language": "en",
                    "priority": "high",
                    "context_data": {
                        "disputed_charges": ["minibar", "spa_treatment"],
                        "total_disputed_amount": 8500
                    }
                },
                "expected_actions": ["billing_review_initiated", "disputed_charges_investigated", "folio_adjustment_prepared"]
            },
            {
                "title": "Noise Complaint",
                "guest_message": "There's construction noise that started at 6 AM outside my window. I couldn't sleep and have an important meeting today. This is completely unacceptable.",
                "context": {
                    "guest_id": "GUEST008",
                    "room_number": "203",
                    "language": "en",
                    "priority": "high",
                    "context_data": {
                        "business_traveler": True,
                        "important_meeting": True,
                        "noise_start_time": "06:00"
                    }
                },
                "expected_actions": ["room_relocation_offered", "construction_team_notified", "compensation_provided", "future_booking_notes_updated"]
            }
        ]
    },
    
    "security": {
        "description": "Security and safety related incidents",
        "scenarios": [
            {
                "title": "Access Card Issue", 
                "guest_message": "My key card stopped working and I can't get into my room. I've been trying for 10 minutes and I'm getting frustrated.",
                "context": {
                    "guest_id": "GUEST009",
                    "room_number": "925",
                    "language": "en",
                    "priority": "high"
                },
                "expected_actions": ["security_team_dispatched", "new_key_card_prepared", "access_logs_checked"]
            },
            {
                "title": "Suspicious Activity",
                "guest_message": "I saw someone suspicious hanging around the 15th floor for the past hour. They don't seem to be a guest and are looking into rooms. I'm concerned about security.",
                "context": {
                    "guest_id": "GUEST010",
                    "room_number": "1501",
                    "language": "en",
                    "priority": "urgent",
                    "context_data": {
                        "location": "15th_floor",
                        "suspicious_person_description": "male, 30s, no room key visible"
                    }
                },
                "expected_actions": ["security_patrol_dispatched", "surveillance_review_initiated", "floor_security_increased"]
            },
            {
                "title": "Lost Property",
                "guest_message": "I think I lost my wallet somewhere in the hotel lobby area. It has my credit cards and ID. Can you help me find it?",
                "context": {
                    "guest_id": "GUEST011",
                    "room_number": "412",
                    "language": "en",
                    "priority": "medium",
                    "context_data": {
                        "lost_item": "wallet",
                        "last_seen_location": "lobby",
                        "contains": ["credit_cards", "id", "cash"]
                    }
                },
                "expected_actions": ["lost_and_found_checked", "security_review_cctv", "incident_report_created"]
            },
            {
                "title": "Safety Concern",
                "guest_message": "There's a smell of gas in the hallway on my floor. I'm worried about a gas leak. This could be dangerous.",
                "context": {
                    "guest_id": "GUEST012",
                    "room_number": "607",
                    "language": "en",
                    "priority": "critical",
                    "context_data": {
                        "floor": "6th",
                        "potential_hazard": "gas_leak",
                        "safety_risk": True
                    }
                },
                "expected_actions": ["emergency_protocol_activated", "maintenance_team_urgent_dispatch", "floor_evacuation_considered", "utilities_company_contacted"]
            }
        ]
    },
    
    "fraud_detection": {
        "description": "Fraud detection and security monitoring scenarios",
        "scenarios": [
            {
                "title": "Multiple Credit Cards",
                "guest_message": "Guest GUEST013 has used 4 different credit cards in the last 2 hours for various transactions totaling ₹45,000. This seems unusual.",
                "context": {
                    "guest_id": "GUEST013",
                    "room_number": "1050",
                    "language": "en",
                    "priority": "urgent",
                    "context_data": {
                        "transaction_count": 4,
                        "card_count": 4,
                        "total_amount": 45000,
                        "timeframe": "2_hours",
                        "fraud_indicators": ["multiple_cards", "high_velocity"]
                    }
                },
                "expected_actions": ["fraud_analysis_initiated", "transactions_reviewed", "additional_verification_required", "security_hold_placed"]
            },
            {
                "title": "Identity Verification Issue",
                "guest_message": "The ID documents provided by guest GUEST014 don't match the credit card name, and the photo looks suspicious. Need immediate verification.",
                "context": {
                    "guest_id": "GUEST014",
                    "room_number": "318",
                    "language": "en",
                    "priority": "critical",
                    "context_data": {
                        "document_mismatch": True,
                        "photo_suspicious": True,
                        "fraud_risk": "high",
                        "verification_failed": True
                    }
                },
                "expected_actions": ["identity_verification_escalated", "law_enforcement_contacted", "account_frozen", "manager_notified"]
            },
            {
                "title": "Suspicious Payment Pattern",
                "guest_message": "Foreign credit card from high-risk country used for ₹75,000 transaction. Guest has no previous stay history with us.",
                "context": {
                    "guest_id": "GUEST015",
                    "room_number": "2105",
                    "language": "en",
                    "priority": "high",
                    "context_data": {
                        "foreign_card": True,
                        "high_risk_country": True,
                        "high_amount": 75000,
                        "new_guest": True,
                        "fraud_score": 85
                    }
                },
                "expected_actions": ["enhanced_verification_required", "bank_authorization_checked", "transaction_monitoring_increased"]
            },
            {
                "title": "Unauthorized Access Pattern",
                "guest_message": "Room 1205 has had 15 failed access attempts in the last hour from different devices. This is highly unusual and may indicate unauthorized access attempts.",
                "context": {
                    "guest_id": "GUEST016",
                    "room_number": "1205",
                    "language": "en",
                    "priority": "urgent",
                    "context_data": {
                        "failed_attempts": 15,
                        "timeframe": "1_hour",
                        "multiple_devices": True,
                        "access_anomaly": True
                    }
                },
                "expected_actions": ["access_logs_analyzed", "room_security_enhanced", "guest_contacted_for_verification", "potential_breach_investigated"]
            }
        ]
    }
}


async def run_demo_scenario(scenario_category: str, scenario_index: int = 0):
    """Run a specific demo scenario."""
    
    if scenario_category not in DEMO_SCENARIOS:
        print(f"Unknown scenario category: {scenario_category}")
        return
    
    category_data = DEMO_SCENARIOS[scenario_category]
    scenarios = category_data["scenarios"]
    
    if scenario_index >= len(scenarios):
        print(f"Scenario index {scenario_index} out of range for category {scenario_category}")
        return
    
    scenario = scenarios[scenario_index]
    
    print(f"\n{'='*60}")
    print(f"DEMO SCENARIO: {scenario['title']}")
    print(f"Category: {scenario_category.upper()}")
    print(f"{'='*60}")
    
    print(f"\nGuest Message:")
    print(f'"{scenario["guest_message"]}"')
    
    print(f"\nContext:")
    for key, value in scenario["context"].items():
        print(f"  {key}: {value}")
    
    print(f"\nExpected Actions:")
    for action in scenario["expected_actions"]:
        print(f"  • {action}")
    
    print(f"\n{'='*60}")
    
    # Here you would integrate with the actual agent coordinator
    # For demo purposes, we'll simulate the response
    
    print("\n[SIMULATED AGENT RESPONSE]")
    print("Agent: Processing your request...")
    print("Agent: I understand your concern and I'm taking immediate action to resolve this.")
    print("Actions taken:")
    for action in scenario["expected_actions"]:
        print(f"  ✓ {action.replace('_', ' ').title()}")
    
    return scenario


async def run_all_scenarios():
    """Run all demo scenarios."""
    
    print("\n" + "="*80)
    print("HOTEL OPERATIONS ASSISTANT - COMPREHENSIVE DEMO")
    print("="*80)
    
    for category, data in DEMO_SCENARIOS.items():
        print(f"\n\n{category.upper()} SCENARIOS")
        print("-" * 50)
        print(f"Description: {data['description']}")
        
        for i, scenario in enumerate(data["scenarios"]):
            print(f"\n{i+1}. {scenario['title']}")
            print(f"   Message: {scenario['guest_message'][:100]}...")
            
        # Run first scenario from each category
        print(f"\nRunning first scenario from {category}...")
        await run_demo_scenario(category, 0)
        
        # Wait for user input to continue
        input("\nPress Enter to continue to next category...")


def get_scenario_by_category(category: str) -> List[Dict]:
    """Get all scenarios for a specific category."""
    return DEMO_SCENARIOS.get(category, {}).get("scenarios", [])


def get_all_categories() -> List[str]:
    """Get all available scenario categories."""
    return list(DEMO_SCENARIOS.keys())


def generate_test_data():
    """Generate test data for API testing."""
    
    test_requests = []
    
    for category, data in DEMO_SCENARIOS.items():
        for scenario in data["scenarios"]:
            test_request = {
                "message": scenario["guest_message"],
                "guest_id": scenario["context"].get("guest_id"),
                "room_number": scenario["context"].get("room_number"),
                "language": scenario["context"].get("language", "en"),
                "priority": scenario["context"].get("priority", "medium"),
                "context_data": scenario["context"].get("context_data", {}),
                "expected_category": category,
                "expected_actions": scenario["expected_actions"]
            }
            test_requests.append(test_request)
    
    return test_requests


if __name__ == "__main__":
    print("Hotel Operations Assistant Demo Scenarios")
    print("Available categories:", ", ".join(get_all_categories()))
    
    # Run interactive demo
    asyncio.run(run_all_scenarios())