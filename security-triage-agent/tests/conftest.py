"""
Pytest configuration and shared fixtures for testing.

Provides test fixtures, mock configurations, and test data
for comprehensive testing of the Security Triage Agent.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.security_triage_agent.core.state import IncidentState, IncidentCategory, IncidentPriority
from src.security_triage_agent.utils.config import SecurityTriageConfig
from src.security_triage_agent.memory.persistent_storage import PersistentStorage
from src.security_triage_agent.memory.session_manager import SessionManager
from src.security_triage_agent.evaluation.metrics_tracker import MetricsTracker


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration."""
    config = SecurityTriageConfig(
        environment="testing",
        debug_mode=True,
        log_level="DEBUG",
        database_path=str(temp_dir / "test_incidents.db"),
        checkpoint_db_path=str(temp_dir / "test_checkpoints.db"),
        redis_url="redis://localhost:6379/1",  # Use different DB for tests
        data_directory=str(temp_dir / "data"),
        log_directory=str(temp_dir / "logs"),
        llm_model="gpt-3.5-turbo",  # Use cheaper model for tests
        enable_metrics_collection=True,
        enable_safety_guardrails=True,
        enable_compliance_checks=True
    )
    return config


@pytest.fixture
async def storage(test_config):
    """Create test persistent storage."""
    storage = PersistentStorage(test_config.database_path)
    await storage.initialize()
    yield storage


@pytest.fixture
async def session_manager(test_config):
    """Create test session manager."""
    session_manager = SessionManager(
        redis_url=test_config.redis_url,
        session_ttl_hours=1  # Short TTL for tests
    )
    await session_manager.initialize()
    yield session_manager
    await session_manager.close()


@pytest.fixture
async def metrics_tracker(storage):
    """Create test metrics tracker."""
    tracker = MetricsTracker(storage)
    yield tracker


@pytest.fixture
def mock_llm():
    """Create mock LLM for testing."""
    llm = AsyncMock()
    
    # Mock responses for different tools
    llm.ainvoke.return_value = Mock(
        content='{"category": "guest_access", "confidence": 0.9, "reasoning": "Test classification"}'
    )
    
    return llm


@pytest.fixture
def sample_incident_state():
    """Create sample incident state for testing."""
    return IncidentState(
        incident_id="test_incident_001",
        title="Unauthorized Guest Access",
        description="Guest reported accessing room after checkout using old key card",
        category=IncidentCategory.GUEST_ACCESS,
        severity=IncidentPriority.HIGH
    )


@pytest.fixture
def guest_access_incident():
    """Sample guest access incident."""
    return {
        "title": "Unauthorized Room Access After Checkout",
        "description": (
            "Guest John Smith (Room 1205) reported that he was able to access "
            "his hotel room using his key card even after checking out at 11:00 AM. "
            "The incident was discovered when the new guest for that room complained "
            "about someone being in their assigned room at 3:00 PM."
        ),
        "metadata": {
            "location": "Floor 12, Room 1205",
            "property_code": "HOTEL_001",
            "affected_guests": ["john.smith@email.com", "new.guest@email.com"],
            "affected_systems": ["key_card_system", "room_access_control"],
            "business_impact": "Guest satisfaction impact, potential security breach",
            "reporting_system": "front_desk",
            "reported_by": "Front Desk Manager"
        }
    }


@pytest.fixture
def payment_fraud_incident():
    """Sample payment fraud incident."""
    return {
        "title": "Suspicious Credit Card Transactions",
        "description": (
            "Multiple credit card transactions flagged by payment processor "
            "showing unusual patterns. Transactions totaling $15,000 across "
            "5 different cards within 30 minutes at restaurant and spa. "
            "All transactions processed through terminal ID: POS_REST_001."
        ),
        "metadata": {
            "location": "Restaurant - Main Dining",
            "property_code": "HOTEL_001",
            "affected_systems": ["pos_system", "payment_processor"],
            "estimated_cost": 15000.0,
            "business_impact": "Potential financial loss, payment processor investigation",
            "reporting_system": "payment_monitoring",
            "reported_by": "Finance Manager"
        }
    }


@pytest.fixture
def pii_breach_incident():
    """Sample PII breach incident."""
    return {
        "title": "Customer Database Access Logs Show Unauthorized Access",
        "description": (
            "System administrator discovered unauthorized access to guest database "
            "containing personal information including names, addresses, phone numbers, "
            "and email addresses of approximately 500 guests. Access occurred between "
            "2:00 AM and 2:15 AM using suspended employee credentials."
        ),
        "metadata": {
            "location": "Data Center - Server Room",
            "property_code": "HOTEL_001",
            "affected_guests": ["500+ guest records"],
            "affected_systems": ["guest_database", "crm_system"],
            "business_impact": "Data privacy violation, potential regulatory breach",
            "reporting_system": "security_monitoring",
            "reported_by": "IT Security Manager"
        }
    }


@pytest.fixture
def cyber_security_incident():
    """Sample cybersecurity incident."""
    return {
        "title": "Malware Detected on Hotel Management System",
        "description": (
            "Antivirus software detected and quarantined suspicious files on "
            "the main hotel management system. Initial analysis suggests potential "
            "ransomware attempting to encrypt reservation and billing data. "
            "System has been isolated as a precautionary measure."
        ),
        "metadata": {
            "location": "IT Server Room",
            "property_code": "HOTEL_001",
            "affected_systems": ["hotel_management_system", "reservation_system", "billing_system"],
            "business_impact": "Potential operation disruption, data encryption risk",
            "reporting_system": "antivirus_monitoring",
            "reported_by": "IT Operations Manager"
        }
    }


@pytest.fixture
def incident_test_cases(guest_access_incident, payment_fraud_incident, pii_breach_incident, cyber_security_incident):
    """Collection of test incident cases."""
    return {
        "guest_access": guest_access_incident,
        "payment_fraud": payment_fraud_incident,
        "pii_breach": pii_breach_incident,
        "cyber_security": cyber_security_incident
    }


@pytest.fixture
def mock_compliance_result():
    """Mock compliance check result."""
    return {
        "framework_checks": {
            "dpdp": True,
            "pci_dss": True
        },
        "violations": [],
        "recommendations": ["Ensure timely notification", "Document all actions"],
        "requires_legal_review": False,
        "requires_regulatory_notification": False,
        "notification_deadlines": {},
        "documentation_requirements": ["incident_report", "action_log"],
        "risk_mitigation_actions": ["update_access_controls", "staff_training"]
    }


@pytest.fixture
def mock_safety_result():
    """Mock safety check result."""
    return {
        "passed": True,
        "overall_risk_level": "medium",
        "violations": [],
        "content_flags": [],
        "requires_human_review": False,
        "review_reason": "",
        "risk_factors": [],
        "recommendations": ["Monitor for similar incidents", "Review security procedures"]
    }


@pytest.fixture
def mock_classification_result():
    """Mock classification result."""
    return {
        "category": "guest_access",
        "confidence": 0.95,
        "reasoning": "Incident involves unauthorized access to guest room using key card after checkout",
        "alternative_categories": ["operational_security"],
        "extracted_entities": {
            "room_numbers": ["1205"],
            "guest_names": ["John Smith"],
            "systems": ["key_card_system"]
        },
        "severity_indicators": ["unauthorized_access", "guest_privacy"]
    }


class MockAgent:
    """Mock agent for testing without full initialization."""
    
    def __init__(self, config):
        self.config = config
        self.is_initialized = True
        self.active_incidents = {}
    
    async def process_incident(self, title, description, metadata=None, user_context=None):
        """Mock incident processing."""
        incident_id = f"mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "incident_id": incident_id,
            "title": title,
            "status": "completed",
            "classification": {
                "category": "guest_access",
                "priority": "high",
                "confidence": 0.9,
                "risk_score": 7.5
            },
            "quality_scores": {
                "overall": 0.85,
                "response_completeness": 0.9,
                "safety_compliance": 0.95
            },
            "evaluation": {
                "overall_score": 0.87,
                "grade": "B",
                "compliance_status": "compliant",
                "safety_status": "safe"
            }
        }


@pytest.fixture
def mock_agent(test_config):
    """Create mock agent for testing."""
    return MockAgent(test_config)