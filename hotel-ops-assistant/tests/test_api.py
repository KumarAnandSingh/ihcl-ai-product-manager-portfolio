"""
Comprehensive test suite for Hotel Operations Assistant API.
Tests all endpoints, agents, and core functionality.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
from httpx import AsyncClient

from hotel_ops_assistant.api.main import create_app
from hotel_ops_assistant.agents.base_agent import AgentContext
from hotel_ops_assistant.agents.agent_coordinator import AgentCoordinator
from hotel_ops_assistant.services.compliance_service import ComplianceService
from examples.demo_scenarios import DEMO_SCENARIOS, generate_test_data


@pytest.fixture
def app():
    """Create test application."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def agent_coordinator():
    """Create agent coordinator for testing."""
    return AgentCoordinator()


@pytest.fixture
def compliance_service():
    """Create compliance service for testing."""
    return ComplianceService()


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    async def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"
    
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        
        # Check required services
        services = data["services"]
        assert "agents" in services
        assert "compliance" in services
        assert "audit_logging" in services


@pytest.mark.asyncio
class TestChatEndpoints:
    """Test chat/conversation endpoints."""
    
    async def test_simple_chat_request(self, client):
        """Test basic chat functionality."""
        request_data = {
            "message": "Hello, I need help with room service",
            "guest_id": "TEST001",
            "room_number": "1001",
            "language": "en",
            "priority": "medium"
        }
        
        response = await client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "agent_id" in data
        assert "session_id" in data
        assert "confidence_score" in data
        assert data["confidence_score"] >= 0.0
        assert data["confidence_score"] <= 1.0
    
    async def test_chat_with_guest_context(self, client):
        """Test chat with rich guest context."""
        request_data = {
            "message": "I have a complaint about my room",
            "guest_id": "VIP001",
            "room_number": "2001",
            "language": "en",
            "priority": "high",
            "context_data": {
                "vip_status": True,
                "loyalty_tier": "Diamond",
                "total_stays": 25
            }
        }
        
        response = await client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "escalation_required" in data
        # VIP complaint should trigger escalation
        assert data["escalation_required"] is True
    
    async def test_security_incident_chat(self, client):
        """Test security incident handling."""
        request_data = {
            "message": "There's suspicious activity in the hallway and I'm concerned about safety",
            "guest_id": "GUEST123",
            "room_number": "1505", 
            "priority": "urgent"
        }
        
        response = await client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "security_agent"
        assert data["escalation_required"] is True
        assert len(data["actions_taken"]) > 0
    
    async def test_fraud_detection_chat(self, client):
        """Test fraud detection scenario."""
        request_data = {
            "message": "Multiple credit cards used by same guest in short timeframe - potential fraud",
            "guest_id": "FRAUD001",
            "priority": "critical",
            "context_data": {
                "fraud_indicators": ["multiple_cards", "high_velocity"],
                "risk_score": 85
            }
        }
        
        response = await client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "fraud_detection_agent"
        assert data["escalation_required"] is True


@pytest.mark.asyncio
class TestComplianceEndpoints:
    """Test compliance and privacy endpoints."""
    
    async def test_dpdp_compliance_check(self, client):
        """Test DPDP Act compliance checking."""
        request_data = {
            "data": {
                "guest_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "room_number": "101"
            },
            "operation": "guest_service",
            "framework": "dpdp_act_2023"
        }
        
        response = await client.post("/compliance/check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "check_id" in data
        assert "framework" in data
        assert "status" in data
        assert "score" in data
        assert data["framework"] == "dpdp_act_2023"
        assert 0 <= data["score"] <= 100
    
    async def test_gdpr_compliance_check(self, client):
        """Test GDPR compliance checking."""
        request_data = {
            "data": {
                "personal_data": True,
                "consent_given": True,
                "lawful_basis": "consent"
            },
            "operation": "data_processing",
            "framework": "gdpr"
        }
        
        response = await client.post("/compliance/check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["framework"] == "gdpr"
    
    async def test_compliance_dashboard(self, client):
        """Test compliance dashboard endpoint."""
        response = await client.get("/compliance/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overall_compliance_score" in data
        assert "compliance_by_framework" in data
        assert "pii_protection_enabled" in data
        assert "audit_logging_enabled" in data


@pytest.mark.asyncio
class TestAuditEndpoints:
    """Test audit and logging endpoints."""
    
    async def test_audit_events(self, client):
        """Test audit events retrieval."""
        response = await client.get("/audit/events?hours=1&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert "period_hours" in data
        assert isinstance(data["events"], list)
    
    async def test_audit_statistics(self, client):
        """Test audit statistics."""
        response = await client.get("/audit/statistics?hours=24")
        assert response.status_code == 200
        
        data = response.json()
        assert "period_hours" in data
        assert "total_events" in data
        assert "events_by_type" in data
        assert "events_by_severity" in data


@pytest.mark.asyncio
class TestAgentCoordinator:
    """Test agent coordination and routing."""
    
    async def test_guest_service_routing(self, agent_coordinator):
        """Test routing to guest service agent."""
        context = AgentContext(
            guest_id="TEST001",
            room_number="101"
        )
        
        response = await agent_coordinator.route_request(
            "I need help with room service", context
        )
        
        assert response.success is True
        assert response.data["routed_to_agent"] == "guest_service"
    
    async def test_complaint_routing(self, agent_coordinator):
        """Test routing to complaint handler."""
        context = AgentContext(
            guest_id="TEST002",
            room_number="102",
            priority="high"
        )
        
        response = await agent_coordinator.route_request(
            "I'm very unhappy with the service", context
        )
        
        assert response.success is True
        assert response.data["routed_to_agent"] == "complaint_handler"
        assert response.escalation_required is True
    
    async def test_security_routing(self, agent_coordinator):
        """Test routing to security agent."""
        context = AgentContext(
            guest_id="TEST003",
            room_number="103"
        )
        
        response = await agent_coordinator.route_request(
            "There's suspicious activity in my hallway", context
        )
        
        assert response.success is True
        assert response.data["routed_to_agent"] == "security"
    
    async def test_fraud_detection_routing(self, agent_coordinator):
        """Test routing to fraud detection agent."""
        context = AgentContext(
            guest_id="TEST004",
            context_data={"fraud_alert": True}
        )
        
        response = await agent_coordinator.route_request(
            "Suspicious payment activity detected", context
        )
        
        assert response.success is True
        assert response.data["routed_to_agent"] == "fraud_detection"


@pytest.mark.asyncio
class TestComplianceService:
    """Test compliance service functionality."""
    
    async def test_dpdp_compliance_check(self, compliance_service):
        """Test DPDP compliance checking."""
        test_data = {
            "guest_name": "Test Guest",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        
        result = await compliance_service.check_dpdp_compliance(test_data, "guest_service")
        
        assert result.framework.value == "dpdp_act_2023"
        assert result.status in ["compliant", "partially_compliant", "non_compliant"]
        assert 0 <= result.score <= 100
        assert isinstance(result.recommendations, list)
    
    async def test_pii_protection(self, compliance_service):
        """Test PII protection functionality."""
        test_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "credit_card": "4111111111111111"
        }
        
        # Test data protection
        protected_data = compliance_service.pii_protection.protect_data(test_data, "display")
        
        # Should mask sensitive information
        assert "*" in protected_data.get("email", "")
        assert "*" in protected_data.get("phone", "")
        if "credit_card" in protected_data:
            assert "*" in protected_data["credit_card"]
    
    async def test_consent_management(self, compliance_service):
        """Test consent recording and verification."""
        subject_id = "TEST_SUBJECT_001"
        purposes = ["guest_service", "marketing"]
        
        # Record consent
        compliance_service.record_consent(subject_id, purposes)
        
        # Verify consent
        consent_valid = await compliance_service.verify_consent(subject_id, "guest_service")
        assert consent_valid is True
        
        # Check unauthorized purpose
        consent_invalid = await compliance_service.verify_consent(subject_id, "data_analytics")
        assert consent_invalid is False


@pytest.mark.asyncio
class TestDemoScenarios:
    """Test all demo scenarios."""
    
    async def test_all_demo_scenarios(self, client):
        """Test all predefined demo scenarios."""
        test_data = generate_test_data()
        
        for scenario in test_data[:5]:  # Test first 5 scenarios
            request_data = {
                "message": scenario["message"],
                "guest_id": scenario["guest_id"],
                "room_number": scenario["room_number"],
                "language": scenario["language"],
                "priority": scenario["priority"],
                "context_data": scenario["context_data"]
            }
            
            response = await client.post("/chat", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "agent_id" in data
            assert "confidence_score" in data
    
    async def test_guest_service_scenarios(self, client):
        """Test guest service specific scenarios."""
        scenarios = DEMO_SCENARIOS["guest_service"]["scenarios"]
        
        for scenario in scenarios:
            request_data = {
                "message": scenario["guest_message"],
                **scenario["context"]
            }
            
            response = await client.post("/chat", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            # Should route to guest service for these scenarios
            assert data["agent_id"] == "guest_service_agent"
    
    async def test_complaint_scenarios(self, client):
        """Test complaint handling scenarios."""
        scenarios = DEMO_SCENARIOS["complaints"]["scenarios"]
        
        for scenario in scenarios:
            request_data = {
                "message": scenario["guest_message"],
                **scenario["context"]
            }
            
            response = await client.post("/chat", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            # Complaints should route to complaint handler
            assert data["agent_id"] == "complaint_handler_agent"
            # Complaints should typically require escalation
            assert data["escalation_required"] is True


@pytest.mark.asyncio
class TestPerformance:
    """Test performance and load characteristics."""
    
    async def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        
        async def make_request():
            request_data = {
                "message": "I need help with my room",
                "guest_id": f"LOAD_TEST_{datetime.now().timestamp()}",
                "room_number": "999"
            }
            response = await client.post("/chat", json=request_data)
            return response.status_code == 200
        
        # Run 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(results)
    
    async def test_response_time(self, client):
        """Test response time is reasonable."""
        start_time = datetime.now()
        
        request_data = {
            "message": "Quick test message",
            "guest_id": "PERF_TEST"
        }
        
        response = await client.post("/chat", json=request_data)
        end_time = datetime.now()
        
        assert response.status_code == 200
        
        # Response should be under 5 seconds
        response_time = (end_time - start_time).total_seconds()
        assert response_time < 5.0
        
        # Check if processing time is reported
        data = response.json()
        if "processing_time_ms" in data:
            assert data["processing_time_ms"] < 5000  # Under 5 seconds


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    async def test_invalid_chat_request(self, client):
        """Test handling of invalid chat requests."""
        # Empty message
        response = await client.post("/chat", json={"message": ""})
        assert response.status_code == 422  # Validation error
        
        # Missing required fields
        response = await client.post("/chat", json={})
        assert response.status_code == 422
    
    async def test_invalid_compliance_framework(self, client):
        """Test handling of invalid compliance framework."""
        request_data = {
            "data": {"test": "data"},
            "operation": "test",
            "framework": "invalid_framework"
        }
        
        response = await client.post("/compliance/check", json=request_data)
        assert response.status_code == 400
    
    async def test_malformed_json(self, client):
        """Test handling of malformed JSON."""
        response = await client.post(
            "/chat",
            content="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])