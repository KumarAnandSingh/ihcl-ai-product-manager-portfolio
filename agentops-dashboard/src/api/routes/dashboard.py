"""Dashboard aggregation API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ...utils.database import get_db_session
from ...models.agent_execution import AgentExecution
from ...models.evaluation_result import EvaluationResult
from ...models.security_incident import SecurityIncident
from ...models.cost_tracking import CostTracking
from ...models.performance_metric import PerformanceMetric
from ...models.alert import Alert

logger = structlog.get_logger()
router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    hours: int = Query(24, description="Hours to look back"),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get high-level dashboard overview metrics."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Base filters
    base_filters = [AgentExecution.start_time >= start_time]
    if environment:
        base_filters.append(AgentExecution.environment == environment)
    
    # Agent Execution Metrics
    exec_total = await session.execute(
        select(func.count(AgentExecution.execution_id))
        .where(and_(*base_filters))
    )
    total_executions = exec_total.scalar()
    
    exec_success = await session.execute(
        select(func.count(AgentExecution.execution_id))
        .where(and_(*base_filters, AgentExecution.success == True))
    )
    successful_executions = exec_success.scalar()
    
    # Cost Metrics
    cost_total = await session.execute(
        select(func.sum(AgentExecution.cost_usd))
        .where(and_(*base_filters))
    )
    total_cost = cost_total.scalar() or 0
    
    # Performance Metrics
    avg_latency = await session.execute(
        select(func.avg(AgentExecution.duration_ms))
        .where(and_(*base_filters))
    )
    average_latency = avg_latency.scalar() or 0
    
    # Security Incidents
    security_filters = [SecurityIncident.detected_at >= start_time]
    if environment:
        security_filters.append(SecurityIncident.environment == environment)
    
    security_incidents = await session.execute(
        select(func.count(SecurityIncident.incident_id))
        .where(and_(*security_filters))
    )
    total_incidents = security_incidents.scalar()
    
    # Critical Alerts
    alert_filters = [Alert.triggered_at >= start_time]
    if environment:
        alert_filters.append(Alert.environment == environment)
    
    critical_alerts = await session.execute(
        select(func.count(Alert.alert_id))
        .where(and_(*alert_filters, Alert.severity == 'critical'))
    )
    total_critical_alerts = critical_alerts.scalar()
    
    # Quality Metrics (from latest evaluations)
    eval_quality = await session.execute(
        select(func.avg(EvaluationResult.overall_score))
        .where(EvaluationResult.evaluation_time >= start_time)
    )
    average_quality_score = eval_quality.scalar() or 0
    
    # Calculate rates and percentages
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    return {
        "time_window_hours": hours,
        "environment": environment,
        "overview": {
            "total_executions": total_executions,
            "success_rate_percent": round(success_rate, 2),
            "average_latency_ms": round(average_latency, 2),
            "total_cost_usd": round(total_cost, 4),
            "security_incidents": total_incidents,
            "critical_alerts": total_critical_alerts,
            "average_quality_score": round(average_quality_score, 2),
        },
        "status": "healthy" if success_rate > 95 and total_critical_alerts == 0 else "degraded"
    }


@router.get("/agent-performance")
async def get_agent_performance_breakdown(
    hours: int = Query(24, description="Hours to look back"),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get performance breakdown by agent."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    base_filters = [AgentExecution.start_time >= start_time]
    if environment:
        base_filters.append(AgentExecution.environment == environment)
    
    # Agent performance metrics
    agent_stats = await session.execute(
        select(
            AgentExecution.agent_name,
            func.count(AgentExecution.execution_id).label('total_executions'),
            func.count(AgentExecution.execution_id).filter(
                AgentExecution.success == True
            ).label('successful_executions'),
            func.avg(AgentExecution.duration_ms).label('avg_duration'),
            func.sum(AgentExecution.cost_usd).label('total_cost'),
            func.avg(AgentExecution.confidence_score).label('avg_confidence'),
        )
        .where(and_(*base_filters))
        .group_by(AgentExecution.agent_name)
        .order_by(func.count(AgentExecution.execution_id).desc())
    )
    
    agent_performance = []
    for row in agent_stats:
        success_rate = (row.successful_executions / row.total_executions * 100) if row.total_executions > 0 else 0
        agent_performance.append({
            "agent_name": row.agent_name,
            "total_executions": row.total_executions,
            "success_rate_percent": round(success_rate, 2),
            "average_duration_ms": round(row.avg_duration or 0, 2),
            "total_cost_usd": round(row.total_cost or 0, 4),
            "average_confidence": round(row.avg_confidence or 0, 2),
        })
    
    return {
        "agents": agent_performance,
        "time_window_hours": hours,
    }


@router.get("/cost-analysis")
async def get_cost_analysis(
    days: int = Query(7, description="Days to look back"),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get detailed cost analysis."""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    # Daily cost trends
    cost_filters = [CostTracking.billing_date >= start_date]
    if environment:
        cost_filters.append(CostTracking.environment == environment)
    
    daily_costs = await session.execute(
        select(
            CostTracking.billing_date,
            func.sum(CostTracking.total_cost).label('daily_cost'),
            func.count(CostTracking.request_count).label('daily_requests'),
        )
        .where(and_(*cost_filters))
        .group_by(CostTracking.billing_date)
        .order_by(CostTracking.billing_date)
    )
    
    cost_trends = [
        {
            "date": row.billing_date.isoformat(),
            "cost_usd": round(row.daily_cost, 4),
            "requests": row.daily_requests,
        }
        for row in daily_costs
    ]
    
    # Cost by service
    service_costs = await session.execute(
        select(
            CostTracking.service_name,
            CostTracking.provider,
            func.sum(CostTracking.total_cost).label('total_cost'),
            func.avg(CostTracking.total_cost).label('avg_cost_per_request'),
        )
        .where(and_(*cost_filters))
        .group_by(CostTracking.service_name, CostTracking.provider)
        .order_by(func.sum(CostTracking.total_cost).desc())
    )
    
    service_breakdown = [
        {
            "service": row.service_name,
            "provider": row.provider,
            "total_cost_usd": round(row.total_cost, 4),
            "avg_cost_per_request": round(row.avg_cost_per_request, 6),
        }
        for row in service_costs
    ]
    
    # Optimization opportunities
    optimization_opportunities = await session.execute(
        select(
            CostTracking.service_name,
            func.sum(CostTracking.total_cost).label('current_cost'),
            func.avg(CostTracking.optimization_potential).label('avg_optimization'),
        )
        .where(
            and_(*cost_filters, CostTracking.optimization_potential > 0)
        )
        .group_by(CostTracking.service_name)
        .order_by(func.sum(CostTracking.total_cost).desc())
    )
    
    optimization_ops = [
        {
            "service": row.service_name,
            "current_cost_usd": round(row.current_cost, 4),
            "potential_savings_percent": round(row.avg_optimization, 2),
            "potential_savings_usd": round(row.current_cost * (row.avg_optimization / 100), 4),
        }
        for row in optimization_opportunities
    ]
    
    return {
        "cost_trends": cost_trends,
        "service_breakdown": service_breakdown,
        "optimization_opportunities": optimization_ops,
        "time_window_days": days,
    }


@router.get("/security-summary")
async def get_security_summary(
    hours: int = Query(24, description="Hours to look back"),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get security incident summary."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    security_filters = [SecurityIncident.detected_at >= start_time]
    if environment:
        security_filters.append(SecurityIncident.environment == environment)
    
    # Incident count by severity
    severity_counts = await session.execute(
        select(
            SecurityIncident.severity,
            func.count(SecurityIncident.incident_id).label('count')
        )
        .where(and_(*security_filters))
        .group_by(SecurityIncident.severity)
    )
    
    severity_breakdown = {row.severity: row.count for row in severity_counts}
    
    # Incident types
    type_counts = await session.execute(
        select(
            SecurityIncident.incident_type,
            func.count(SecurityIncident.incident_id).label('count')
        )
        .where(and_(*security_filters))
        .group_by(SecurityIncident.incident_type)
        .order_by(func.count(SecurityIncident.incident_id).desc())
    )
    
    incident_types = [
        {"type": row.incident_type, "count": row.count}
        for row in type_counts
    ]
    
    # Recent high-severity incidents
    recent_incidents = await session.execute(
        select(SecurityIncident)
        .where(
            and_(*security_filters, SecurityIncident.severity.in_(['critical', 'high']))
        )
        .order_by(SecurityIncident.detected_at.desc())
        .limit(10)
    )
    
    recent_incidents_list = [
        {
            "incident_id": incident.incident_id,
            "type": incident.incident_type,
            "severity": incident.severity,
            "title": incident.title,
            "detected_at": incident.detected_at.isoformat(),
            "status": incident.status,
        }
        for incident in recent_incidents.scalars()
    ]
    
    return {
        "severity_breakdown": severity_breakdown,
        "incident_types": incident_types,
        "recent_high_severity": recent_incidents_list,
        "time_window_hours": hours,
    }


@router.get("/quality-metrics")
async def get_quality_metrics(
    hours: int = Query(24, description="Hours to look back"),
    agent_name: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get quality and evaluation metrics."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    eval_filters = [EvaluationResult.evaluation_time >= start_time]
    if agent_name:
        # Join with executions to filter by agent
        exec_filters = [AgentExecution.agent_name == agent_name]
    
    # Overall quality scores
    quality_metrics = await session.execute(
        select(
            func.avg(EvaluationResult.overall_score).label('avg_overall'),
            func.avg(EvaluationResult.accuracy_score).label('avg_accuracy'),
            func.avg(EvaluationResult.safety_score).label('avg_safety'),
            func.avg(EvaluationResult.coherence_score).label('avg_coherence'),
            func.count(EvaluationResult.evaluation_id).label('total_evaluations'),
            func.count(EvaluationResult.evaluation_id).filter(
                EvaluationResult.passed == True
            ).label('passed_evaluations'),
        )
        .where(and_(*eval_filters))
    )
    
    quality_row = quality_metrics.first()
    pass_rate = (quality_row.passed_evaluations / quality_row.total_evaluations * 100) if quality_row.total_evaluations > 0 else 0
    
    # Quality trends by hour
    quality_trends = await session.execute(
        select(
            func.date_trunc('hour', EvaluationResult.evaluation_time).label('hour'),
            func.avg(EvaluationResult.overall_score).label('avg_score'),
            func.count(EvaluationResult.evaluation_id).label('eval_count'),
        )
        .where(and_(*eval_filters))
        .group_by(func.date_trunc('hour', EvaluationResult.evaluation_time))
        .order_by(func.date_trunc('hour', EvaluationResult.evaluation_time))
    )
    
    trends = [
        {
            "hour": row.hour.isoformat(),
            "average_score": round(row.avg_score, 2),
            "evaluation_count": row.eval_count,
        }
        for row in quality_trends
    ]
    
    return {
        "summary": {
            "average_overall_score": round(quality_row.avg_overall or 0, 2),
            "average_accuracy_score": round(quality_row.avg_accuracy or 0, 2),
            "average_safety_score": round(quality_row.avg_safety or 0, 2),
            "average_coherence_score": round(quality_row.avg_coherence or 0, 2),
            "total_evaluations": quality_row.total_evaluations,
            "pass_rate_percent": round(pass_rate, 2),
        },
        "trends": trends,
        "time_window_hours": hours,
    }