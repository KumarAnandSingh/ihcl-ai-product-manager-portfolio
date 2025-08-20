# AgentOps Dashboard

A comprehensive monitoring and evaluation platform for agentic AI systems in production. Built for enterprise-scale AI operations with advanced security, compliance, and cost optimization features.

![AgentOps Dashboard](docs/images/dashboard-overview.png)

## 🎯 Overview

AgentOps Dashboard provides end-to-end monitoring, evaluation, and optimization for AI agent systems. Designed specifically for IHCL's FlexiCore security platform, it delivers enterprise-grade observability with real-time alerting, comprehensive security monitoring, and intelligent cost optimization.

### Key Features

- **Real-Time Monitoring**: Live performance metrics, latency tracking, and SLA monitoring
- **Security & Compliance**: Advanced threat detection, PII exposure alerts, compliance violation tracking
- **Cost Intelligence**: Multi-model cost tracking, optimization recommendations, budget management
- **Quality Assurance**: Automated evaluation frameworks, A/B testing, hallucination detection
- **Advanced Analytics**: Trend analysis, anomaly detection, predictive insights
- **Enterprise Integration**: Slack/PagerDuty alerting, audit logging, role-based access

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for development)
- PostgreSQL 15+ (if running locally)
- Redis 7+ (if running locally)

### Option 1: Docker Compose (Recommended)

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd agentops-dashboard
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start All Services**
   ```bash
   docker-compose up -d
   ```

3. **Access the Dashboard**
   - Main Dashboard: http://localhost:8501
   - API Documentation: http://localhost:8000/docs
   - Grafana Analytics: http://localhost:3000 (admin/admin123)
   - Prometheus Metrics: http://localhost:9090

### Option 2: Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Services**
   ```bash
   # Terminal 1: Start API
   python -m uvicorn src.api.main:app --reload --port 8000
   
   # Terminal 2: Start Dashboard
   streamlit run src/dashboard/app.py --server.port 8501
   ```

3. **Generate Demo Data**
   ```bash
   python demo_data/generate_demo_data.py
   ```

## 📊 Dashboard Components

### Executive Overview
- **System Health**: Real-time status indicators and SLA tracking
- **Key Performance Indicators**: Success rates, latency, cost, and quality metrics
- **Security Posture**: Active incidents, compliance status, threat detection
- **Quick Actions**: Force refresh, alert management, report generation

### Agent Performance Analysis
- **Performance Metrics**: Success rates, latency distribution, efficiency scores
- **Agent Comparison**: Side-by-side performance analysis across different agents
- **Trend Analysis**: Historical performance trends and anomaly detection
- **Tool Usage Analytics**: Tool call success rates and optimization opportunities

### Security & Compliance Monitoring
- **Incident Management**: Real-time security incident tracking and response
- **Threat Intelligence**: Advanced threat detection and analysis
- **Compliance Dashboard**: Regulatory compliance monitoring (GDPR, CCPA, SOX)
- **PII Protection**: Data exposure detection and remediation workflows

### Cost Intelligence
- **Cost Breakdown**: Detailed cost analysis by service, model, and team
- **Optimization Engine**: AI-powered cost reduction recommendations
- **Budget Management**: Budget tracking, alerts, and forecasting
- **ROI Analysis**: Business value and return on investment calculations

### Quality Assurance
- **Evaluation Results**: Comprehensive quality metrics and scoring
- **A/B Testing**: Model comparison and performance benchmarking
- **Hallucination Detection**: Advanced content validation and fact-checking
- **Human Feedback Integration**: Quality ratings and improvement tracking

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   PostgreSQL    │
│   Dashboard     │◄──►│      API        │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │     Redis       │    │   Prometheus    │
│  Load Balancer  │    │     Cache       │    │    Metrics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Grafana      │    │     Celery      │    │   AlertManager  │
│   Dashboards    │    │    Workers      │    │   & Notifications│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Data Ingestion**: Agent execution data flows through FastAPI endpoints
2. **Real-time Processing**: Immediate evaluation and alerting via background workers
3. **Storage**: Structured data storage in PostgreSQL with Redis caching
4. **Analytics**: Real-time metrics collection and trend analysis
5. **Visualization**: Multi-layered dashboards for different stakeholder needs
6. **Alerting**: Intelligent notification routing based on severity and context

## 🔧 Configuration

### Environment Variables

```bash
# Core Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://host:port/db
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Alerting
SLACK_WEBHOOK_URL=your-slack-webhook
PAGERDUTY_API_KEY=your-pagerduty-key

# Features
ENABLE_REAL_TIME_ALERTS=true
ENABLE_COST_OPTIMIZATION=true
ENABLE_ADVANCED_ANALYTICS=true
```

### Alert Configuration

```python
# Custom alert conditions
AlertCondition(
    name="High Latency Alert",
    alert_type=AlertType.PERFORMANCE,
    severity=AlertSeverity.HIGH,
    condition_func=lambda data: data.get("duration_ms", 0) > 5000,
    message_template="Agent {agent_name} execution took {duration_ms}ms",
    threshold_value=5000.0,
    cooldown_minutes=5
)
```

## 📈 Monitoring & Alerting

### Alert Types

- **Performance Alerts**: Latency, throughput, error rates, SLA breaches
- **Security Alerts**: Threat detection, PII exposure, compliance violations
- **Cost Alerts**: Budget thresholds, cost anomalies, optimization opportunities
- **Quality Alerts**: Low scores, hallucinations, bias detection
- **System Alerts**: Infrastructure issues, service availability

### Notification Channels

- **Slack**: Real-time team notifications with rich formatting
- **Email**: Detailed incident reports and summaries
- **PagerDuty**: Critical incident escalation and on-call management
- **Webhooks**: Custom integrations with external systems

### SLA Monitoring

- **Availability**: 99.9% uptime target with automated failover
- **Latency**: P95 response time < 2 seconds
- **Accuracy**: Quality score > 0.85 for production agents
- **Security**: Zero tolerance for critical security incidents

## 🛡️ Security Features

### Data Protection
- **Encryption**: End-to-end encryption for sensitive data
- **Access Control**: Role-based permissions and audit logging
- **PII Detection**: Automated scanning and redaction capabilities
- **Compliance**: GDPR, CCPA, SOX compliance monitoring

### Threat Detection
- **Prompt Injection**: Advanced detection of malicious prompts
- **Data Exfiltration**: Monitoring for unauthorized data access
- **Anomaly Detection**: ML-based behavioral analysis
- **Incident Response**: Automated response workflows

## 💰 Cost Optimization

### Cost Tracking
- **Multi-Model Support**: OpenAI, Anthropic, AWS, Azure, GCP
- **Granular Billing**: Per-request, per-token, and per-user tracking
- **Budget Management**: Department and project-level budgets
- **Forecasting**: Predictive cost modeling and trend analysis

### Optimization Engine
- **Model Selection**: Intelligent routing to cost-effective models
- **Caching Strategies**: Response caching and deduplication
- **Batch Processing**: Efficient request batching and scheduling
- **Resource Scaling**: Dynamic scaling based on demand

## 🔬 Evaluation Framework

### Automated Evaluation
- **Quality Metrics**: Accuracy, relevance, coherence, completeness
- **Safety Scoring**: Bias detection, toxicity analysis, safety validation
- **Performance Evaluation**: Latency, efficiency, resource utilization
- **Business Metrics**: Task completion, user satisfaction, ROI

### A/B Testing
- **Model Comparison**: Head-to-head performance analysis
- **Statistical Significance**: Robust statistical testing framework
- **Gradual Rollout**: Safe deployment with automatic rollback
- **Performance Tracking**: Real-time experiment monitoring

## 📚 API Documentation

### Core Endpoints

```bash
# Agent Executions
POST /api/v1/executions          # Create execution record
GET  /api/v1/executions          # List executions with filtering
GET  /api/v1/executions/{id}     # Get specific execution
PUT  /api/v1/executions/{id}     # Update execution

# Security Incidents
POST /api/v1/security/incidents  # Create security incident
GET  /api/v1/security/incidents  # List incidents
PUT  /api/v1/security/incidents/{id} # Update incident

# Evaluations
POST /api/v1/evaluations         # Create evaluation result
GET  /api/v1/evaluations         # List evaluation results
GET  /api/v1/evaluations/summary # Get evaluation summary

# Dashboard Data
GET  /api/v1/dashboard/overview  # Executive overview metrics
GET  /api/v1/dashboard/agent-performance # Agent performance data
GET  /api/v1/dashboard/cost-analysis    # Cost analysis data
```

### Authentication

```python
# API Key Authentication
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
```

## 🚀 Deployment

### Production Deployment

1. **Infrastructure Setup**
   ```bash
   # Deploy with Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   
   # Or use Kubernetes
   kubectl apply -f k8s/
   ```

2. **SSL Configuration**
   ```bash
   # Generate SSL certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout config/nginx/ssl/key.pem \
     -out config/nginx/ssl/cert.pem
   ```

3. **Database Migration**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple API and dashboard instances behind load balancer
- **Database Scaling**: Read replicas and connection pooling
- **Cache Optimization**: Redis clustering and cache warming
- **Background Processing**: Celery worker scaling based on queue depth

## 🤝 Integration Examples

### Agent Integration

```python
import httpx
from datetime import datetime

# Track agent execution
async def track_execution(agent_name: str, execution_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/executions",
            headers={"Authorization": "Bearer your-api-key"},
            json={
                "execution_id": "exec_123",
                "agent_name": agent_name,
                "agent_type": "security",
                "start_time": datetime.utcnow().isoformat(),
                **execution_data
            }
        )
        return response.json()
```

### Security Monitoring

```python
# Report security incident
async def report_security_incident(incident_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/security/incidents",
            headers={"Authorization": "Bearer your-api-key"},
            json={
                "incident_id": "sec_456",
                "incident_type": "prompt_injection",
                "severity": "high",
                "detected_at": datetime.utcnow().isoformat(),
                **incident_data
            }
        )
        return response.json()
```

## 🔍 Troubleshooting

### Common Issues

1. **Dashboard Not Loading**
   ```bash
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs dashboard
   ```

2. **Database Connection Issues**
   ```bash
   # Verify database connectivity
   docker-compose exec postgres pg_isready
   
   # Check environment variables
   docker-compose exec api printenv | grep DATABASE
   ```

3. **High Memory Usage**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Adjust memory limits in docker-compose.yml
   ```

### Performance Optimization

- **Database Indexing**: Ensure proper indexes on frequently queried columns
- **Cache Warming**: Implement cache warming strategies for frequently accessed data
- **Query Optimization**: Use database query analysis tools to optimize slow queries
- **Background Processing**: Offload heavy processing to background workers

## 📊 Metrics & KPIs

### Business Metrics
- **Agent Availability**: 99.9% uptime target
- **Response Time**: P95 < 2 seconds
- **Quality Score**: Average > 0.85
- **Cost Efficiency**: 15% cost reduction YoY
- **Security Posture**: Zero critical incidents

### Technical Metrics
- **Throughput**: Requests per second
- **Error Rates**: 4xx and 5xx error percentages
- **Resource Utilization**: CPU, memory, disk usage
- **Cache Hit Rates**: Redis cache effectiveness
- **Database Performance**: Query execution times

## 🏆 Portfolio Highlights

This AgentOps Dashboard demonstrates advanced capabilities in:

- **Enterprise AI Operations**: Production-grade monitoring and management
- **Security Excellence**: Comprehensive threat detection and compliance
- **Cost Intelligence**: AI-powered optimization and budget management
- **Quality Assurance**: Automated evaluation and continuous improvement
- **System Architecture**: Scalable, resilient, and maintainable design
- **Business Impact**: Measurable improvements in efficiency and security

## 📞 Support

For technical support or questions:

- **Email**: priya.singh@ihcl.com
- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/agentops-dashboard/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for IHCL FlexiCore Security Platform**

*Demonstrating enterprise-grade AI operations and security monitoring capabilities*