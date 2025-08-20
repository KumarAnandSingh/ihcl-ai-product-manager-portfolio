# Hotel Operations Assistant

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

A comprehensive AI-powered hotel operations management system designed for luxury hospitality environments. Built for IHCL's FlexiCore platform, this system demonstrates advanced AI/ML engineering capabilities with domain expertise in hospitality operations.

## 🏨 Overview

The Hotel Operations Assistant is a production-ready system that handles:

- **Guest Services**: Room service, concierge, amenity requests
- **Complaint Management**: Service recovery, compensation, escalation
- **Security & Safety**: Access control, incident response, threat assessment  
- **Fraud Detection**: Payment monitoring, identity verification, risk assessment
- **Compliance Management**: DPDP Act 2023, GDPR, PCI DSS compliance
- **Incident Tracking**: Comprehensive audit trail and performance analytics

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │ Agent Coordinator│    │ Compliance Svc  │
│                 │    │                 │    │                 │
│ • REST Endpoints│    │ • Request Router│    │ • PII Protection│
│ • OpenAPI Docs  │    │ • Agent Manager │    │ • Audit Logging │
│ • Health Checks │    │ • Orchestration │    │ • Data Rights   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Specialized     │    │ Hotel Systems   │    │ Memory &        │
│ AI Agents       │    │ Integration     │    │ Analytics       │
│                 │    │                 │    │                 │
│ • Guest Service │    │ • PMS (Opera)   │    │ • Redis Cache   │
│ • Complaints    │    │ • POS Systems   │    │ • PostgreSQL    │
│ • Security      │    │ • CRM Platform  │    │ • Performance   │
│ • Fraud Detection│   │ • Security Sys  │    │ • Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### AI Agent Architecture

Each agent follows a specialized design pattern:

```python
@Agent(capabilities=[GUEST_SERVICE, INCIDENT_MANAGEMENT])
class GuestServiceAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Professional hotel guest service specialist..."
    
    async def process_request(self, request: str, context: AgentContext) -> AgentResponse:
        # 1. Classify request type
        # 2. Get guest context from hotel systems
        # 3. Generate LLM response with context
        # 4. Execute business logic actions
        # 5. Determine escalation needs
        # 6. Return structured response
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching and sessions)
- PostgreSQL (for persistent storage)
- OpenAI API key (for LLM integration)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ihcl-ai/hotel-ops-assistant.git
cd hotel-ops-assistant
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**
```bash
# Start the API server
hotel-ops-assistant run

# Or using uvicorn directly
uvicorn hotel_ops_assistant.api.main:create_app --factory --reload
```

5. **Access the application**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Interactive Demo: http://localhost:8000/demo/scenarios

## 📋 Key Features

### 🤖 AI-Powered Agents

**Guest Service Agent**
- Handles room service, housekeeping, amenity requests
- Personalizes responses based on guest profile and preferences
- Integrates with PMS, POS, and CRM systems
- Automatic escalation for VIP guests

**Complaint Handler Agent**
- De-escalation and service recovery expertise
- Compensation assessment within guidelines
- Sentiment analysis and escalation triggers
- Integration with incident management system

**Fraud Detection Agent**
- Real-time transaction monitoring
- Identity verification and document analysis
- Risk scoring with configurable thresholds
- Integration with security and compliance systems

**Security Agent**
- Access control and safety incident response
- Emergency protocol activation
- Integration with surveillance and alarm systems
- Threat assessment and escalation procedures

### 🛡️ Compliance & Privacy

**DPDP Act 2023 Compliance**
- Comprehensive PII encryption and masking
- Consent management and tracking
- Data minimization and purpose limitation
- Automated compliance scoring

**GDPR Implementation**
- Full data subject rights automation
- Cross-border transfer protection
- Lawful basis tracking and validation
- Right to be forgotten implementation

**PCI DSS Security**
- Payment data encryption and tokenization
- Access controls and monitoring
- Vulnerability management integration
- Compliance audit trails

### 📊 Operational Analytics

**Real-time Dashboards**
- Guest satisfaction metrics
- Incident resolution times
- Agent performance analytics
- Compliance score monitoring

**Audit & Compliance Reporting**
- Comprehensive audit trails
- Regulatory compliance reports
- PII access monitoring
- Security event tracking

## 🔧 Configuration

### Hotel Types

The system supports different hotel configurations:

```yaml
# Luxury Hotel Configuration
luxury:
  service_levels: ["premium", "concierge", "butler", "vip"]
  response_time_sla:
    complaints: 15  # minutes
    maintenance: 30
    security: 5
    concierge: 10
  
# Business Hotel Configuration  
business:
  service_levels: ["standard", "business", "premium"]
  response_time_sla:
    complaints: 30
    maintenance: 60
    security: 10
    concierge: 20
```

### Agent Capabilities

```python
# Configure agent routing
ROUTING_PATTERNS = {
    "complaint": {
        "keywords": ["complaint", "dissatisfied", "problem"],
        "agent": "complaint_handler",
        "priority": "high"
    },
    "security": {
        "keywords": ["security", "emergency", "theft"],
        "agent": "security",
        "priority": "urgent"
    }
}
```

## 📖 API Documentation

### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "message": "I need help with room service",
  "guest_id": "GUEST001",
  "room_number": "1205", 
  "language": "en",
  "priority": "medium",
  "context_data": {
    "loyalty_tier": "Gold",
    "vip_status": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "I'd be happy to help you with room service...",
  "session_id": "sess_123",
  "agent_id": "guest_service_agent",
  "actions_taken": [
    "room_service_request_created",
    "menu_provided"
  ],
  "escalation_required": false,
  "confidence_score": 0.92,
  "processing_time_ms": 1250
}
```

### Compliance Endpoints

```http
# Check DPDP compliance
POST /compliance/check
{
  "data": {"guest_name": "John Doe", "email": "john@example.com"},
  "operation": "guest_service",
  "framework": "dpdp_act_2023"
}

# Data subject rights request
POST /data-subject-request
{
  "request_type": "access",
  "subject_id": "GUEST001", 
  "subject_email": "guest@example.com"
}
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/hotel_ops_assistant --cov-report=html

# Run specific test categories
pytest tests/test_api.py::TestChatEndpoints -v
pytest tests/test_compliance.py -v
```

### Demo Scenarios

```bash
# Run interactive demo
python examples/demo_scenarios.py

# Test specific scenario category
hotel-ops-assistant demo

# Load test scenarios
python examples/load_test.py
```

## 🔒 Security

### PII Protection

```python
# Automatic PII detection and protection
pii_service = PIIProtectionService()

# Encrypt sensitive data for storage
protected_data = pii_service.protect_data(guest_data, "store")

# Mask data for display
masked_data = pii_service.protect_data(guest_data, "display")

# Decrypt for authorized access
decrypted_data = pii_service.unprotect_data(protected_data, user_id, "guest_service")
```

### Audit Logging

```python
# Comprehensive audit trail
audit_logger.log_guest_access(
    user_id="staff_123",
    guest_id="GUEST001", 
    action="profile_view",
    pii_involved=True
)

# Compliance reporting
compliance_report = audit_logger.generate_compliance_report(
    start_time=datetime.now() - timedelta(days=30),
    end_time=datetime.now()
)
```

## 📈 Performance

### Benchmarks

- **Response Time**: < 2 seconds average
- **Concurrent Users**: 100+ simultaneous sessions
- **Throughput**: 1000+ requests/minute
- **Availability**: 99.9% uptime target

### Monitoring

```python
# Performance metrics
GET /health
GET /audit/statistics
GET /agents/performance

# Real-time monitoring
GET /metrics  # Prometheus format
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build container
docker build -t hotel-ops-assistant .

# Run with environment
docker run -p 8000:8000 --env-file .env hotel-ops-assistant

# Docker Compose
docker-compose up -d
```

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: hotel-ops-assistant:latest
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests before submitting: `pytest`
5. Submit pull request with comprehensive description

### Code Standards

- **Type Hints**: All functions must have type annotations
- **Documentation**: Comprehensive docstrings for all public methods
- **Testing**: 90%+ code coverage required
- **Security**: All PII handling must be reviewed
- **Performance**: Response times < 2 seconds

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 IHCL FlexiCore Integration

This Hotel Operations Assistant demonstrates:

### Technical Excellence
- **Scalable Architecture**: Microservices with async processing
- **AI/ML Integration**: LangChain agents with domain expertise
- **Security First**: Comprehensive PII protection and compliance
- **Production Ready**: Full observability and monitoring

### Business Value
- **Guest Experience**: Personalized, 24/7 assistance
- **Operational Efficiency**: Automated incident management
- **Risk Management**: Proactive fraud detection
- **Regulatory Compliance**: Automated DPDP/GDPR compliance

### Innovation
- **Hospitality AI**: Domain-specific agent specialization
- **Contextual Intelligence**: Rich guest profile integration
- **Predictive Analytics**: Fraud pattern recognition
- **Compliance Automation**: Real-time privacy protection

---

**Built for IHCL FlexiCore Platform | AI Product Manager Portfolio**

*Demonstrating advanced AI/ML engineering capabilities in hospitality technology*