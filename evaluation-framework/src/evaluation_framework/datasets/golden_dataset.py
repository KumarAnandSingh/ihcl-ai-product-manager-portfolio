"""Golden dataset management for hospitality security evaluation."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

import structlog
import yaml
from faker import Faker

from ..core.types import (
    HospitalityContext,
    SecurityThreat,
    Severity,
    TaskType,
    TestCase,
)
from ..utils.config import Config

logger = structlog.get_logger(__name__)


class GoldenDataset:
    """
    Manages curated golden datasets for hospitality security evaluation.
    
    Provides high-quality, manually curated test cases that represent
    realistic scenarios in hospitality security operations.
    """
    
    def __init__(self, config: Config):
        """Initialize the golden dataset manager."""
        self.config = config
        self.logger = logger.bind(component="GoldenDataset")
        self.fake = Faker()
        
        # Dataset storage
        self.test_cases: Dict[str, List[TestCase]] = {}
        self.metadata: Dict[str, Dict] = {}
        
        # Load existing datasets
        self._load_datasets()
        
        self.logger.info("Golden dataset initialized", suites=list(self.test_cases.keys()))
    
    def _load_datasets(self) -> None:
        """Load existing datasets from storage."""
        dataset_path = Path(self.config.data_dir) / "golden_datasets"
        
        if not dataset_path.exists():
            dataset_path.mkdir(parents=True, exist_ok=True)
            self._create_default_datasets()
            return
        
        # Load existing test suites
        for suite_file in dataset_path.glob("*.yaml"):
            suite_name = suite_file.stem
            try:
                with open(suite_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Convert to TestCase objects
                test_cases = []
                for case_data in data.get("test_cases", []):
                    test_case = TestCase(
                        id=case_data["id"],
                        name=case_data["name"],
                        description=case_data["description"],
                        task_type=TaskType(case_data["task_type"]),
                        input_data=case_data["input_data"],
                        expected_output=case_data["expected_output"],
                        metadata=case_data.get("metadata", {}),
                        severity=Severity(case_data.get("severity", "medium")),
                        tags=case_data.get("tags", []),
                    )
                    test_cases.append(test_case)
                
                self.test_cases[suite_name] = test_cases
                self.metadata[suite_name] = data.get("metadata", {})
                
                self.logger.info(
                    "Loaded test suite",
                    suite=suite_name,
                    count=len(test_cases),
                )
                
            except Exception as e:
                self.logger.error(
                    "Failed to load test suite",
                    suite=suite_name,
                    error=str(e),
                )
    
    def _create_default_datasets(self) -> None:
        """Create default golden datasets."""
        self.logger.info("Creating default golden datasets")
        
        # Security triage scenarios
        self._create_security_triage_suite()
        
        # Incident classification scenarios
        self._create_incident_classification_suite()
        
        # Threat detection scenarios
        self._create_threat_detection_suite()
        
        # Compliance validation scenarios
        self._create_compliance_suite()
        
        # Guest service security scenarios
        self._create_guest_service_suite()
        
        # Fraud detection scenarios
        self._create_fraud_detection_suite()
        
        # Emergency response scenarios
        self._create_emergency_response_suite()
        
        # Save all datasets
        self._save_all_datasets()
    
    def _create_security_triage_suite(self) -> None:
        """Create security triage test cases."""
        test_cases = []
        
        # Critical security incidents
        test_cases.extend([
            TestCase(
                name="Data Breach Alert",
                description="Suspicious database access patterns detected",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "data_breach",
                    "source_system": "guest_database",
                    "timestamp": "2024-01-15T14:30:00Z",
                    "details": {
                        "affected_records": 1500,
                        "access_pattern": "bulk_export",
                        "user_account": "maintenance_user",
                        "ip_address": "192.168.1.45",
                        "data_types": ["guest_profiles", "payment_info", "reservation_history"]
                    },
                    "hospitality_context": {
                        "property_type": "luxury_hotel",
                        "location": "Mumbai",
                        "guest_count": 450,
                        "vip_guests": True,
                        "occupancy_rate": 0.85
                    }
                },
                expected_output={
                    "severity": "critical",
                    "classification": "data_breach",
                    "priority": 1,
                    "immediate_actions": [
                        "isolate_affected_systems",
                        "disable_maintenance_user_account",
                        "notify_data_protection_officer",
                        "initiate_incident_response_protocol"
                    ],
                    "escalation_required": True,
                    "compliance_implications": ["GDPR", "PCI DSS", "DPDP"],
                    "estimated_resolution_time": 120,
                    "tools_used": ["isolate_system", "disable_account", "notify_dpo"],
                    "confidence": 0.95,
                    "reasoning": "Bulk export of sensitive guest data outside normal business hours by maintenance account indicates potential data breach"
                },
                severity=Severity.CRITICAL,
                tags=["data_breach", "pii", "compliance", "urgent"],
                metadata={
                    "regulation_impact": "high",
                    "guest_impact": "high",
                    "business_impact": "critical"
                }
            ),
            
            TestCase(
                name="Unauthorized System Access",
                description="Failed login attempts followed by successful privileged access",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "unauthorized_access",
                    "source_system": "property_management_system",
                    "timestamp": "2024-01-15T22:15:00Z",
                    "details": {
                        "failed_attempts": 15,
                        "success_login": True,
                        "user_account": "admin_guest_services",
                        "ip_address": "203.145.67.89",
                        "location": "External",
                        "accessed_modules": ["guest_checkout", "billing", "key_management"]
                    },
                    "hospitality_context": {
                        "property_type": "business_hotel",
                        "location": "Delhi",
                        "guest_count": 280,
                        "staff_count": 45,
                        "special_events": ["corporate_conference"]
                    }
                },
                expected_output={
                    "severity": "high",
                    "classification": "unauthorized_access",
                    "priority": 2,
                    "immediate_actions": [
                        "lock_user_account",
                        "review_recent_transactions",
                        "check_key_card_access",
                        "notify_security_team"
                    ],
                    "escalation_required": True,
                    "estimated_resolution_time": 60,
                    "tools_used": ["lock_account", "audit_transactions", "notify_security"],
                    "confidence": 0.88,
                    "reasoning": "Multiple failed attempts followed by successful login from external IP suggests compromised credentials"
                },
                severity=Severity.HIGH,
                tags=["unauthorized_access", "brute_force", "privileges"],
                metadata={
                    "attack_vector": "credential_compromise",
                    "affected_systems": ["PMS", "key_management"]
                }
            ),
            
            TestCase(
                name="Guest Wi-Fi Malware Detection",
                description="Malicious network activity detected on guest Wi-Fi",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "malware_detection",
                    "source_system": "network_security",
                    "timestamp": "2024-01-15T16:45:00Z",
                    "details": {
                        "malware_type": "ransomware",
                        "infected_devices": 3,
                        "guest_room_numbers": ["304", "312", "318"],
                        "network_segment": "guest_wifi",
                        "c2_communication": True,
                        "data_exfiltration": False
                    },
                    "hospitality_context": {
                        "property_type": "resort",
                        "location": "Goa",
                        "guest_count": 620,
                        "occupancy_rate": 0.92,
                        "vip_guests": False
                    }
                },
                expected_output={
                    "severity": "high",
                    "classification": "malware_incident",
                    "priority": 2,
                    "immediate_actions": [
                        "isolate_infected_devices",
                        "segment_guest_network",
                        "notify_affected_guests",
                        "scan_hotel_network"
                    ],
                    "escalation_required": False,
                    "estimated_resolution_time": 90,
                    "tools_used": ["isolate_devices", "segment_network", "notify_guests"],
                    "confidence": 0.92,
                    "reasoning": "Multiple guest devices infected with ransomware pose risk to hotel network and other guests"
                },
                severity=Severity.HIGH,
                tags=["malware", "ransomware", "guest_wifi", "containment"],
                metadata={
                    "containment_priority": "high",
                    "guest_communication": "required"
                }
            )
        ])
        
        # Medium severity incidents
        test_cases.extend([
            TestCase(
                name="Suspicious Payment Activity",
                description="Multiple failed payment transactions from same card",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "payment_fraud",
                    "source_system": "payment_gateway",
                    "timestamp": "2024-01-15T11:20:00Z",
                    "details": {
                        "card_last_four": "4521",
                        "failed_transactions": 8,
                        "transaction_amounts": [125.50, 340.00, 89.75, 220.00],
                        "merchant_locations": ["restaurant", "spa", "minibar", "concierge"],
                        "guest_room": "512",
                        "cardholder_present": False
                    },
                    "hospitality_context": {
                        "property_type": "luxury_resort",
                        "location": "Udaipur",
                        "guest_count": 180,
                        "vip_guests": True
                    }
                },
                expected_output={
                    "severity": "medium",
                    "classification": "payment_fraud_suspicion",
                    "priority": 3,
                    "immediate_actions": [
                        "hold_suspicious_transactions",
                        "contact_guest_verification",
                        "review_service_usage",
                        "check_card_authorization"
                    ],
                    "escalation_required": False,
                    "estimated_resolution_time": 45,
                    "tools_used": ["hold_transactions", "contact_guest", "verify_card"],
                    "confidence": 0.75,
                    "reasoning": "Multiple failed transactions without cardholder present suggests potential fraud"
                },
                severity=Severity.MEDIUM,
                tags=["payment_fraud", "verification", "guest_contact"],
                metadata={
                    "financial_impact": "medium",
                    "guest_satisfaction_risk": "medium"
                }
            ),
            
            TestCase(
                name="Staff Access Pattern Anomaly",
                description="Employee accessing systems outside normal working hours",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "access_anomaly",
                    "source_system": "hr_access_control",
                    "timestamp": "2024-01-15T03:30:00Z",
                    "details": {
                        "employee_id": "EMP_2847",
                        "department": "housekeeping",
                        "normal_hours": "06:00-14:00",
                        "access_time": "03:30",
                        "systems_accessed": ["guest_preferences", "room_assignments"],
                        "location": "back_office",
                        "badge_swipe": True
                    },
                    "hospitality_context": {
                        "property_type": "boutique_hotel",
                        "location": "Bangalore",
                        "guest_count": 85,
                        "night_shift_minimal": True
                    }
                },
                expected_output={
                    "severity": "medium",
                    "classification": "access_policy_violation",
                    "priority": 3,
                    "immediate_actions": [
                        "review_employee_schedule",
                        "check_authorization_reason",
                        "audit_data_accessed",
                        "notify_department_head"
                    ],
                    "escalation_required": False,
                    "estimated_resolution_time": 30,
                    "tools_used": ["check_schedule", "audit_access", "notify_manager"],
                    "confidence": 0.70,
                    "reasoning": "Housekeeping staff accessing guest data outside normal hours needs verification"
                },
                severity=Severity.MEDIUM,
                tags=["policy_violation", "employee_access", "audit"],
                metadata={
                    "hr_notification": "required",
                    "follow_up": "next_business_day"
                }
            )
        ])
        
        # Low severity incidents
        test_cases.extend([
            TestCase(
                name="Guest Device Security Warning",
                description="Guest device showing signs of outdated security",
                task_type=TaskType.SECURITY_TRIAGE,
                input_data={
                    "alert_type": "device_security",
                    "source_system": "network_monitoring",
                    "timestamp": "2024-01-15T09:15:00Z",
                    "details": {
                        "device_type": "laptop",
                        "os_version": "Windows 7",
                        "security_issues": ["outdated_os", "no_antivirus", "weak_passwords"],
                        "guest_room": "205",
                        "network_access": "limited",
                        "risk_level": "low"
                    },
                    "hospitality_context": {
                        "property_type": "business_hotel",
                        "location": "Pune",
                        "guest_count": 156,
                        "business_traveler_focus": True
                    }
                },
                expected_output={
                    "severity": "low",
                    "classification": "security_advisory",
                    "priority": 4,
                    "immediate_actions": [
                        "provide_security_recommendations",
                        "offer_it_support",
                        "monitor_network_activity",
                        "document_advisory_provided"
                    ],
                    "escalation_required": False,
                    "estimated_resolution_time": 15,
                    "tools_used": ["send_advisory", "offer_support", "monitor_device"],
                    "confidence": 0.85,
                    "reasoning": "Outdated guest device poses minimal risk but warrants security advisory"
                },
                severity=Severity.LOW,
                tags=["guest_advisory", "device_security", "prevention"],
                metadata={
                    "guest_education": "recommended",
                    "service_opportunity": "it_support"
                }
            )
        ])
        
        self.test_cases["security_triage"] = test_cases
        self.metadata["security_triage"] = {
            "description": "Comprehensive security incident triage scenarios",
            "version": "1.0",
            "total_cases": len(test_cases),
            "severity_distribution": {
                "critical": len([tc for tc in test_cases if tc.severity == Severity.CRITICAL]),
                "high": len([tc for tc in test_cases if tc.severity == Severity.HIGH]),
                "medium": len([tc for tc in test_cases if tc.severity == Severity.MEDIUM]),
                "low": len([tc for tc in test_cases if tc.severity == Severity.LOW]),
            },
            "coverage_areas": [
                "data_breach", "unauthorized_access", "malware", "payment_fraud",
                "policy_violation", "guest_security"
            ]
        }
    
    def _create_incident_classification_suite(self) -> None:
        """Create incident classification test cases."""
        test_cases = [
            TestCase(
                name="Fire Alarm System Trigger",
                description="Fire detection system activated in guest room",
                task_type=TaskType.INCIDENT_CLASSIFICATION,
                input_data={
                    "incident_type": "fire_alarm",
                    "location": "guest_room_817",
                    "detection_type": "smoke_detector",
                    "automatic_trigger": True,
                    "timestamp": "2024-01-15T02:45:00Z",
                    "additional_info": {
                        "guest_present": True,
                        "sprinkler_activated": False,
                        "building_section": "east_tower"
                    }
                },
                expected_output={
                    "classification": "fire_emergency",
                    "severity": "critical",
                    "response_team": ["fire_safety", "security", "management"],
                    "immediate_actions": ["evacuate_room", "check_fire_source", "notify_fire_department"],
                    "escalation_level": "emergency_services",
                    "estimated_response_time": 5
                },
                severity=Severity.CRITICAL,
                tags=["fire_safety", "emergency", "evacuation"]
            ),
            
            TestCase(
                name="Guest Medical Emergency",
                description="Guest collapsed in hotel lobby",
                task_type=TaskType.INCIDENT_CLASSIFICATION,
                input_data={
                    "incident_type": "medical_emergency",
                    "location": "main_lobby",
                    "guest_condition": "unconscious",
                    "witness_present": True,
                    "timestamp": "2024-01-15T19:30:00Z",
                    "additional_info": {
                        "guest_age_estimated": 65,
                        "prior_medical_info": "unknown",
                        "family_present": False
                    }
                },
                expected_output={
                    "classification": "medical_emergency",
                    "severity": "critical",
                    "response_team": ["first_aid", "security", "management"],
                    "immediate_actions": ["call_ambulance", "provide_first_aid", "clear_area", "contact_family"],
                    "escalation_level": "emergency_services",
                    "estimated_response_time": 3
                },
                severity=Severity.CRITICAL,
                tags=["medical", "emergency", "first_aid"]
            )
        ]
        
        self.test_cases["incident_classification"] = test_cases
        self.metadata["incident_classification"] = {
            "description": "Incident classification and response scenarios",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def _create_threat_detection_suite(self) -> None:
        """Create threat detection test cases."""
        test_cases = [
            TestCase(
                name="Advanced Persistent Threat Detection",
                description="Long-term unauthorized access with data exfiltration",
                task_type=TaskType.THREAT_DETECTION,
                input_data={
                    "threat_indicators": [
                        "unusual_network_traffic",
                        "privilege_escalation",
                        "data_staging",
                        "encrypted_communication"
                    ],
                    "duration": "45_days",
                    "affected_systems": ["guest_database", "financial_system", "email_server"],
                    "attack_vector": "spear_phishing",
                    "lateral_movement": True
                },
                expected_output={
                    "threat_classification": "advanced_persistent_threat",
                    "risk_level": "critical",
                    "immediate_response": "full_incident_response",
                    "containment_strategy": "network_segmentation",
                    "investigation_required": True
                },
                severity=Severity.CRITICAL,
                tags=["apt", "data_exfiltration", "investigation"]
            )
        ]
        
        self.test_cases["threat_detection"] = test_cases
        self.metadata["threat_detection"] = {
            "description": "Advanced threat detection scenarios",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def _create_compliance_suite(self) -> None:
        """Create compliance validation test cases."""
        test_cases = [
            TestCase(
                name="GDPR Data Subject Rights Request",
                description="Guest requesting deletion of personal data",
                task_type=TaskType.COMPLIANCE_CHECK,
                input_data={
                    "regulation": "GDPR",
                    "request_type": "data_deletion",
                    "data_subject": "guest",
                    "request_details": {
                        "guest_id": "G_789456",
                        "data_types": ["profile", "preferences", "stay_history"],
                        "verification_provided": True,
                        "legitimate_interests": False
                    }
                },
                expected_output={
                    "compliance_status": "compliant",
                    "required_actions": ["verify_identity", "locate_all_data", "perform_deletion", "confirm_completion"],
                    "timeline": "30_days",
                    "legal_review_required": False,
                    "data_retention_exceptions": []
                },
                severity=Severity.MEDIUM,
                tags=["gdpr", "data_rights", "deletion"]
            )
        ]
        
        self.test_cases["compliance"] = test_cases
        self.metadata["compliance"] = {
            "description": "Regulatory compliance validation scenarios",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def _create_guest_service_suite(self) -> None:
        """Create guest service security test cases."""
        test_cases = [
            TestCase(
                name="Guest Key Card Cloning Suspicion",
                description="Multiple successful key card uses from different locations",
                task_type=TaskType.GUEST_SERVICE,
                input_data={
                    "alert_type": "key_card_anomaly",
                    "guest_room": "1205",
                    "key_card_id": "KC_887234",
                    "usage_pattern": {
                        "location_1": "room_door",
                        "location_2": "elevator_penthouse",
                        "time_difference": "30_seconds",
                        "simultaneous_use": True
                    }
                },
                expected_output={
                    "security_concern": "key_card_cloning",
                    "immediate_action": "deactivate_card",
                    "guest_contact": "immediate",
                    "investigation": "required",
                    "new_card_issue": True
                },
                severity=Severity.HIGH,
                tags=["key_card", "cloning", "guest_safety"]
            )
        ]
        
        self.test_cases["guest_service"] = test_cases
        self.metadata["guest_service"] = {
            "description": "Guest service security scenarios",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def _create_fraud_detection_suite(self) -> None:
        """Create fraud detection test cases."""
        test_cases = [
            TestCase(
                name="Credit Card Testing Fraud",
                description="Multiple small transactions testing card validity",
                task_type=TaskType.FRAUD_DETECTION,
                input_data={
                    "transaction_pattern": "card_testing",
                    "transactions": [
                        {"amount": 1.00, "status": "approved", "timestamp": "2024-01-15T10:00:00Z"},
                        {"amount": 2.00, "status": "approved", "timestamp": "2024-01-15T10:01:00Z"},
                        {"amount": 500.00, "status": "pending", "timestamp": "2024-01-15T10:02:00Z"}
                    ],
                    "card_info": {
                        "last_four": "8765",
                        "issuer": "visa",
                        "country": "unknown"
                    }
                },
                expected_output={
                    "fraud_probability": 0.85,
                    "fraud_type": "card_testing",
                    "recommended_action": "block_transactions",
                    "verification_required": True,
                    "risk_factors": ["incremental_amounts", "rapid_succession", "large_final_amount"]
                },
                severity=Severity.HIGH,
                tags=["fraud", "card_testing", "payment"]
            )
        ]
        
        self.test_cases["fraud_detection"] = test_cases
        self.metadata["fraud_detection"] = {
            "description": "Payment and reservation fraud detection",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def _create_emergency_response_suite(self) -> None:
        """Create emergency response test cases."""
        test_cases = [
            TestCase(
                name="Natural Disaster Alert",
                description="Earthquake warning requiring immediate guest safety measures",
                task_type=TaskType.EMERGENCY_RESPONSE,
                input_data={
                    "emergency_type": "earthquake",
                    "magnitude": "6.2",
                    "warning_time": "30_seconds",
                    "affected_area": "entire_property",
                    "guest_count": 450,
                    "special_needs_guests": 12
                },
                expected_output={
                    "emergency_protocol": "earthquake_response",
                    "immediate_actions": ["sound_alarm", "initiate_evacuation", "check_structural_integrity"],
                    "communication_plan": "multi_language_announcements",
                    "special_assistance": "mobility_impaired_guests",
                    "coordination": "local_emergency_services"
                },
                severity=Severity.CRITICAL,
                tags=["natural_disaster", "evacuation", "guest_safety"]
            )
        ]
        
        self.test_cases["emergency_response"] = test_cases
        self.metadata["emergency_response"] = {
            "description": "Emergency response and crisis management",
            "version": "1.0",
            "total_cases": len(test_cases)
        }
    
    def get_test_suite(self, suite_name: str) -> List[TestCase]:
        """Get test cases for a specific suite."""
        if suite_name not in self.test_cases:
            raise ValueError(f"Test suite '{suite_name}' not found")
        
        return self.test_cases[suite_name]
    
    def get_all_suites(self) -> List[str]:
        """Get names of all available test suites."""
        return list(self.test_cases.keys())
    
    def get_test_case(self, suite_name: str, test_case_id: str) -> Optional[TestCase]:
        """Get a specific test case by ID."""
        if suite_name not in self.test_cases:
            return None
        
        for test_case in self.test_cases[suite_name]:
            if test_case.id == test_case_id:
                return test_case
        
        return None
    
    def add_test_case(self, suite_name: str, test_case: TestCase) -> None:
        """Add a test case to a suite."""
        if suite_name not in self.test_cases:
            self.test_cases[suite_name] = []
            self.metadata[suite_name] = {
                "description": f"Custom test suite: {suite_name}",
                "version": "1.0",
                "total_cases": 0
            }
        
        self.test_cases[suite_name].append(test_case)
        self.metadata[suite_name]["total_cases"] = len(self.test_cases[suite_name])
        
        self.logger.info(
            "Added test case",
            suite=suite_name,
            test_case_id=test_case.id,
        )
    
    def create_filtered_suite(
        self,
        source_suite: str,
        filter_criteria: Dict,
        new_suite_name: str,
    ) -> List[TestCase]:
        """Create a filtered test suite based on criteria."""
        if source_suite not in self.test_cases:
            raise ValueError(f"Source suite '{source_suite}' not found")
        
        filtered_cases = []
        source_cases = self.test_cases[source_suite]
        
        for test_case in source_cases:
            if self._matches_criteria(test_case, filter_criteria):
                filtered_cases.append(test_case)
        
        # Save filtered suite
        self.test_cases[new_suite_name] = filtered_cases
        self.metadata[new_suite_name] = {
            "description": f"Filtered from {source_suite}",
            "version": "1.0",
            "total_cases": len(filtered_cases),
            "filter_criteria": filter_criteria,
            "source_suite": source_suite,
        }
        
        self.logger.info(
            "Created filtered suite",
            new_suite=new_suite_name,
            source_suite=source_suite,
            count=len(filtered_cases),
        )
        
        return filtered_cases
    
    def _matches_criteria(self, test_case: TestCase, criteria: Dict) -> bool:
        """Check if test case matches filter criteria."""
        if "severity" in criteria:
            if test_case.severity.value not in criteria["severity"]:
                return False
        
        if "task_type" in criteria:
            if test_case.task_type.value not in criteria["task_type"]:
                return False
        
        if "tags" in criteria:
            required_tags = set(criteria["tags"])
            test_tags = set(test_case.tags)
            if not required_tags.intersection(test_tags):
                return False
        
        if "metadata" in criteria:
            for key, value in criteria["metadata"].items():
                if key not in test_case.metadata:
                    return False
                if test_case.metadata[key] != value:
                    return False
        
        return True
    
    def get_statistics(self) -> Dict:
        """Get dataset statistics."""
        total_cases = sum(len(cases) for cases in self.test_cases.values())
        
        severity_counts = {severity.value: 0 for severity in Severity}
        task_type_counts = {task_type.value: 0 for task_type in TaskType}
        
        for cases in self.test_cases.values():
            for case in cases:
                severity_counts[case.severity.value] += 1
                task_type_counts[case.task_type.value] += 1
        
        return {
            "total_test_cases": total_cases,
            "test_suites": len(self.test_cases),
            "severity_distribution": severity_counts,
            "task_type_distribution": task_type_counts,
            "suite_details": {
                name: {
                    "count": len(cases),
                    "metadata": self.metadata.get(name, {}),
                }
                for name, cases in self.test_cases.items()
            },
        }
    
    def _save_all_datasets(self) -> None:
        """Save all test suites to storage."""
        dataset_path = Path(self.config.data_dir) / "golden_datasets"
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        for suite_name, test_cases in self.test_cases.items():
            suite_file = dataset_path / f"{suite_name}.yaml"
            
            # Convert test cases to dict format
            data = {
                "metadata": self.metadata.get(suite_name, {}),
                "test_cases": [tc.to_dict() for tc in test_cases],
            }
            
            with open(suite_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            
            self.logger.info(
                "Saved test suite",
                suite=suite_name,
                file=str(suite_file),
                count=len(test_cases),
            )
    
    def export_suite(
        self,
        suite_name: str,
        output_path: str,
        format: str = "yaml",
    ) -> None:
        """Export a test suite to file."""
        if suite_name not in self.test_cases:
            raise ValueError(f"Test suite '{suite_name}' not found")
        
        output_path = Path(output_path)
        test_cases = self.test_cases[suite_name]
        
        data = {
            "metadata": self.metadata.get(suite_name, {}),
            "test_cases": [tc.to_dict() for tc in test_cases],
        }
        
        if format.lower() == "yaml":
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format.lower() == "json":
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(
            "Exported test suite",
            suite=suite_name,
            output_path=str(output_path),
            format=format,
        )