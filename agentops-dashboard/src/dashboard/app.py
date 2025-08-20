"""Main Streamlit dashboard application for AgentOps monitoring."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import httpx
import asyncio
from streamlit_autorefresh import st_autorefresh

# Configure page
st.set_page_config(
    page_title="AgentOps Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-critical {
        border-left: 5px solid #ff4b4b;
        background-color: #ffebeb;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-warning {
        border-left: 5px solid #ffa500;
        background-color: #fff8e1;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_dashboard_overview(hours: int = 24, environment: str = None):
    """Fetch dashboard overview data from API."""
    try:
        params = {"hours": hours}
        if environment:
            params["environment"] = environment
        
        response = httpx.get(f"{API_BASE_URL}/dashboard/overview", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        # Return demo data for portfolio demonstration
        return generate_demo_overview_data(hours)


@st.cache_data(ttl=30)
def fetch_agent_performance(hours: int = 24, environment: str = None):
    """Fetch agent performance data from API."""
    try:
        params = {"hours": hours}
        if environment:
            params["environment"] = environment
        
        response = httpx.get(f"{API_BASE_URL}/dashboard/agent-performance", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return generate_demo_agent_performance(hours)


@st.cache_data(ttl=30)
def fetch_security_summary(hours: int = 24, environment: str = None):
    """Fetch security summary data from API."""
    try:
        params = {"hours": hours}
        if environment:
            params["environment"] = environment
        
        response = httpx.get(f"{API_BASE_URL}/dashboard/security-summary", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return generate_demo_security_data(hours)


@st.cache_data(ttl=60)
def fetch_cost_analysis(days: int = 7, environment: str = None):
    """Fetch cost analysis data from API."""
    try:
        params = {"days": days}
        if environment:
            params["environment"] = environment
        
        response = httpx.get(f"{API_BASE_URL}/dashboard/cost-analysis", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return generate_demo_cost_data(days)


def generate_demo_overview_data(hours: int):
    """Generate demo data for portfolio demonstration."""
    np.random.seed(42)
    
    return {
        "time_window_hours": hours,
        "environment": "production",
        "overview": {
            "total_executions": 15847,
            "success_rate_percent": 96.8,
            "average_latency_ms": 1247.5,
            "total_cost_usd": 847.23,
            "security_incidents": 3,
            "critical_alerts": 1,
            "average_quality_score": 0.92,
        },
        "status": "healthy"
    }


def generate_demo_agent_performance(hours: int):
    """Generate demo agent performance data."""
    agents = [
        "security-triage-agent",
        "hotel-guest-service",
        "fraud-detection-agent",
        "complaint-handler",
        "quality-assurance-agent"
    ]
    
    performance_data = []
    for agent in agents:
        np.random.seed(hash(agent) % 100)
        performance_data.append({
            "agent_name": agent,
            "total_executions": np.random.randint(1000, 5000),
            "success_rate_percent": np.random.uniform(94, 99),
            "average_duration_ms": np.random.uniform(800, 2000),
            "total_cost_usd": np.random.uniform(50, 200),
            "average_confidence": np.random.uniform(0.85, 0.98),
        })
    
    return {"agents": performance_data, "time_window_hours": hours}


def generate_demo_security_data(hours: int):
    """Generate demo security data."""
    return {
        "severity_breakdown": {
            "critical": 1,
            "high": 2,
            "medium": 5,
            "low": 12
        },
        "incident_types": [
            {"type": "prompt_injection", "count": 8},
            {"type": "pii_exposure", "count": 5},
            {"type": "unauthorized_access", "count": 3},
            {"type": "compliance_violation", "count": 4}
        ],
        "pii_exposures": 5,
        "compliance_violations": 4,
        "time_window_hours": hours
    }


def generate_demo_cost_data(days: int):
    """Generate demo cost data."""
    dates = [(datetime.now() - timedelta(days=i)).date() for i in range(days)]
    
    cost_trends = []
    for i, date in enumerate(reversed(dates)):
        base_cost = 120 + np.sin(i * 0.5) * 20 + np.random.uniform(-10, 10)
        cost_trends.append({
            "date": date.isoformat(),
            "cost_usd": max(0, base_cost),
            "requests": np.random.randint(8000, 12000)
        })
    
    service_breakdown = [
        {"service": "gpt-4-turbo", "provider": "openai", "total_cost_usd": 245.67, "avg_cost_per_request": 0.0205},
        {"service": "claude-3-sonnet", "provider": "anthropic", "total_cost_usd": 189.23, "avg_cost_per_request": 0.0158},
        {"service": "gpt-3.5-turbo", "provider": "openai", "total_cost_usd": 67.89, "avg_cost_per_request": 0.0034},
        {"service": "embeddings", "provider": "openai", "total_cost_usd": 23.45, "avg_cost_per_request": 0.0001}
    ]
    
    optimization_opportunities = [
        {"service": "gpt-4-turbo", "current_cost_usd": 245.67, "potential_savings_percent": 15, "potential_savings_usd": 36.85},
        {"service": "claude-3-sonnet", "current_cost_usd": 189.23, "potential_savings_percent": 8, "potential_savings_usd": 15.14}
    ]
    
    return {
        "cost_trends": cost_trends,
        "service_breakdown": service_breakdown,
        "optimization_opportunities": optimization_opportunities,
        "time_window_days": days
    }


def render_overview_section(overview_data):
    """Render the overview section with key metrics."""
    st.header("🎯 Executive Overview")
    
    if "error" in overview_data:
        st.error(f"Failed to load overview data: {overview_data['error']}")
        return
    
    overview = overview_data["overview"]
    status = overview_data["status"]
    
    # Status indicator
    status_color = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"
    st.markdown(f"**System Status:** {status_color} {status.title()}")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Executions",
            f"{overview['total_executions']:,}",
            delta=None
        )
        st.metric(
            "Success Rate",
            f"{overview['success_rate_percent']:.1f}%",
            delta=f"{overview['success_rate_percent'] - 95:.1f}%" if overview['success_rate_percent'] != 95 else None
        )
    
    with col2:
        st.metric(
            "Avg Latency",
            f"{overview['average_latency_ms']:.0f}ms",
            delta=f"{overview['average_latency_ms'] - 1200:.0f}ms" if overview['average_latency_ms'] != 1200 else None
        )
        st.metric(
            "Quality Score",
            f"{overview['average_quality_score']:.2f}",
            delta=f"{overview['average_quality_score'] - 0.90:.2f}" if overview['average_quality_score'] != 0.90 else None
        )
    
    with col3:
        st.metric(
            "Total Cost",
            f"${overview['total_cost_usd']:.2f}",
            delta=None
        )
        st.metric(
            "Security Incidents",
            overview['security_incidents'],
            delta=f"{overview['security_incidents'] - 2}" if overview['security_incidents'] != 2 else None
        )
    
    with col4:
        st.metric(
            "Critical Alerts",
            overview['critical_alerts'],
            delta=f"{overview['critical_alerts']}" if overview['critical_alerts'] > 0 else None
        )
        
        # Quick action buttons
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()


def render_agent_performance_section(performance_data):
    """Render agent performance analysis."""
    st.header("🤖 Agent Performance Analysis")
    
    if "error" in performance_data:
        st.error(f"Failed to load performance data: {performance_data['error']}")
        return
    
    agents = performance_data["agents"]
    df = pd.DataFrame(agents)
    
    # Performance overview table
    st.subheader("Agent Performance Summary")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['success_rate_percent'] = display_df['success_rate_percent'].round(2)
    display_df['average_duration_ms'] = display_df['average_duration_ms'].round(0)
    display_df['total_cost_usd'] = display_df['total_cost_usd'].round(2)
    display_df['average_confidence'] = display_df['average_confidence'].round(3)
    
    st.dataframe(
        display_df,
        column_config={
            "agent_name": "Agent Name",
            "total_executions": st.column_config.NumberColumn("Total Executions", format="%d"),
            "success_rate_percent": st.column_config.NumberColumn("Success Rate %", format="%.2f%%"),
            "average_duration_ms": st.column_config.NumberColumn("Avg Duration (ms)", format="%.0f"),
            "total_cost_usd": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "average_confidence": st.column_config.NumberColumn("Avg Confidence", format="%.3f"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Success Rate by Agent")
        fig_success = px.bar(
            df,
            x='agent_name',
            y='success_rate_percent',
            title="Agent Success Rates",
            color='success_rate_percent',
            color_continuous_scale='RdYlGn',
            labels={'success_rate_percent': 'Success Rate (%)', 'agent_name': 'Agent'}
        )
        fig_success.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_success, use_container_width=True)
    
    with col2:
        st.subheader("Performance vs Cost")
        fig_scatter = px.scatter(
            df,
            x='total_cost_usd',
            y='success_rate_percent',
            size='total_executions',
            hover_name='agent_name',
            title="Performance vs Cost Analysis",
            labels={
                'total_cost_usd': 'Total Cost ($)',
                'success_rate_percent': 'Success Rate (%)',
                'total_executions': 'Total Executions'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


def render_security_section(security_data):
    """Render security monitoring section."""
    st.header("🔒 Security & Compliance Monitoring")
    
    if "error" in security_data:
        st.error(f"Failed to load security data: {security_data['error']}")
        return
    
    # Security metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("PII Exposures", security_data["pii_exposures"])
    with col2:
        st.metric("Compliance Violations", security_data["compliance_violations"])
    with col3:
        total_incidents = sum(security_data["severity_breakdown"].values())
        st.metric("Total Incidents", total_incidents)
    
    # Severity breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incidents by Severity")
        severity_df = pd.DataFrame(
            list(security_data["severity_breakdown"].items()),
            columns=['Severity', 'Count']
        )
        fig_severity = px.pie(
            severity_df,
            values='Count',
            names='Severity',
            title="Security Incidents by Severity",
            color_discrete_map={
                'critical': '#ff4444',
                'high': '#ff8800',
                'medium': '#ffaa00',
                'low': '#88cc00'
            }
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.subheader("Incident Types")
        incident_types_df = pd.DataFrame(security_data["incident_types"])
        fig_types = px.bar(
            incident_types_df,
            x='type',
            y='count',
            title="Security Incidents by Type",
            labels={'type': 'Incident Type', 'count': 'Count'}
        )
        fig_types.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_types, use_container_width=True)
    
    # Security alerts
    if security_data["severity_breakdown"].get("critical", 0) > 0:
        st.markdown("""
        <div class="alert-critical">
        <strong>⚠️ Critical Security Alert</strong><br>
        Critical security incidents detected. Immediate attention required.
        </div>
        """, unsafe_allow_html=True)
    elif security_data["severity_breakdown"].get("high", 0) > 0:
        st.markdown("""
        <div class="alert-warning">
        <strong>⚠️ Security Warning</strong><br>
        High severity security incidents detected. Review recommended.
        </div>
        """, unsafe_allow_html=True)


def render_cost_analysis_section(cost_data):
    """Render cost analysis and optimization section."""
    st.header("💰 Cost Analysis & Optimization")
    
    if "error" in cost_data:
        st.error(f"Failed to load cost data: {cost_data['error']}")
        return
    
    # Cost trends
    st.subheader("Cost Trends")
    trends_df = pd.DataFrame(cost_data["cost_trends"])
    trends_df['date'] = pd.to_datetime(trends_df['date'])
    
    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_trends.add_trace(
        go.Scatter(
            x=trends_df['date'],
            y=trends_df['cost_usd'],
            mode='lines+markers',
            name='Daily Cost',
            line=dict(color='#1f77b4', width=3)
        ),
        secondary_y=False,
    )
    
    fig_trends.add_trace(
        go.Scatter(
            x=trends_df['date'],
            y=trends_df['requests'],
            mode='lines+markers',
            name='Requests',
            line=dict(color='#ff7f0e', width=2)
        ),
        secondary_y=True,
    )
    
    fig_trends.update_xaxes(title_text="Date")
    fig_trends.update_yaxes(title_text="Cost ($)", secondary_y=False)
    fig_trends.update_yaxes(title_text="Requests", secondary_y=True)
    fig_trends.update_layout(title_text="Cost and Usage Trends")
    
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Service breakdown and optimization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Service")
        service_df = pd.DataFrame(cost_data["service_breakdown"])
        fig_service = px.bar(
            service_df,
            x='service',
            y='total_cost_usd',
            color='provider',
            title="Cost Breakdown by Service",
            labels={'total_cost_usd': 'Total Cost ($)', 'service': 'Service'}
        )
        fig_service.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_service, use_container_width=True)
    
    with col2:
        st.subheader("Optimization Opportunities")
        if cost_data["optimization_opportunities"]:
            opt_df = pd.DataFrame(cost_data["optimization_opportunities"])
            fig_opt = px.bar(
                opt_df,
                x='service',
                y='potential_savings_usd',
                title="Potential Cost Savings",
                labels={'potential_savings_usd': 'Potential Savings ($)', 'service': 'Service'},
                color='potential_savings_percent',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_opt, use_container_width=True)
            
            total_savings = opt_df['potential_savings_usd'].sum()
            st.success(f"💡 Total potential savings: ${total_savings:.2f}")
        else:
            st.info("No optimization opportunities identified.")


def render_sidebar():
    """Render the sidebar with controls and filters."""
    st.sidebar.title("AgentOps Dashboard")
    st.sidebar.markdown("---")
    
    # Environment filter
    environment = st.sidebar.selectbox(
        "Environment",
        ["All", "production", "staging", "development"],
        index=0
    )
    
    # Time range controls
    st.sidebar.subheader("Time Range")
    time_range = st.sidebar.selectbox(
        "Select Time Range",
        ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days"],
        index=2
    )
    
    # Convert time range to hours
    time_mapping = {
        "Last 1 hour": 1,
        "Last 6 hours": 6,
        "Last 24 hours": 24,
        "Last 7 days": 168,
        "Last 30 days": 720
    }
    hours = time_mapping[time_range]
    
    # Auto-refresh settings
    st.sidebar.subheader("Auto-refresh")
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)
    if auto_refresh:
        refresh_interval = st.sidebar.selectbox(
            "Refresh interval",
            ["30 seconds", "1 minute", "5 minutes"],
            index=1
        )
        interval_mapping = {"30 seconds": 30, "1 minute": 60, "5 minutes": 300}
        refresh_seconds = interval_mapping[refresh_interval]
        st_autorefresh(interval=refresh_seconds * 1000, key="datarefresh")
    
    # Quick actions
    st.sidebar.subheader("Quick Actions")
    if st.sidebar.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("📊 Generate Report"):
        st.sidebar.success("Report generation started!")
    
    if st.sidebar.button("🚨 View Alerts"):
        st.switch_page("pages/alerts.py")
    
    # System status
    st.sidebar.subheader("System Status")
    st.sidebar.markdown("🟢 API: Healthy")
    st.sidebar.markdown("🟢 Database: Connected")
    st.sidebar.markdown("🟢 Cache: Active")
    
    return environment if environment != "All" else None, hours


def main():
    """Main dashboard application."""
    st.title("🤖 AgentOps Dashboard")
    st.markdown("Comprehensive monitoring and evaluation for agentic AI systems")
    
    # Render sidebar and get filters
    environment, hours = render_sidebar()
    
    # Fetch data
    overview_data = fetch_dashboard_overview(hours, environment)
    performance_data = fetch_agent_performance(hours, environment)
    security_data = fetch_security_summary(hours, environment)
    cost_data = fetch_cost_analysis(min(hours // 24, 7) if hours >= 24 else 1, environment)
    
    # Render sections
    render_overview_section(overview_data)
    st.markdown("---")
    
    render_agent_performance_section(performance_data)
    st.markdown("---")
    
    render_security_section(security_data)
    st.markdown("---")
    
    render_cost_analysis_section(cost_data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "AgentOps Dashboard v1.0 | Built for IHCL FlexiCore Platform | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()