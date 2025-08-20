"""Security incident tracking API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ...utils.database import get_db_session
from ...models.security_incident import SecurityIncident
from ...schemas.security_schemas import (
    SecurityIncidentCreate,
    SecurityIncidentUpdate,
    SecurityIncidentResponse,
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/incidents", response_model=SecurityIncidentResponse)
async def create_security_incident(
    incident: SecurityIncidentCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new security incident."""
    try:
        db_incident = SecurityIncident(**incident.model_dump())
        session.add(db_incident)
        await session.commit()
        await session.refresh(db_incident)
        
        # Trigger immediate alerting for critical/high severity
        if db_incident.severity in ['critical', 'high']:
            background_tasks.add_task(trigger_security_alerts, db_incident.incident_id)
        
        logger.warning(
            "Security incident created",
            incident_id=db_incident.incident_id,
            severity=db_incident.severity,
            type=db_incident.incident_type
        )
        
        return SecurityIncidentResponse.model_validate(db_incident)
    except Exception as e:
        logger.error("Failed to create security incident", error=str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create security incident")


@router.get("/incidents", response_model=List[SecurityIncidentResponse])
async def list_security_incidents(
    severity: Optional[str] = Query(None),
    incident_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    hours: int = Query(24, description="Hours to look back"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """List security incidents with filtering."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(SecurityIncident).where(
        SecurityIncident.detected_at >= start_time
    )
    
    # Apply filters
    if severity:
        query = query.where(SecurityIncident.severity == severity)
    if incident_type:
        query = query.where(SecurityIncident.incident_type == incident_type)
    if status:
        query = query.where(SecurityIncident.status == status)
    if environment:
        query = query.where(SecurityIncident.environment == environment)
    
    query = query.order_by(SecurityIncident.detected_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    incidents = result.scalars().all()
    
    return [SecurityIncidentResponse.model_validate(incident) for incident in incidents]


@router.get("/incidents/{incident_id}", response_model=SecurityIncidentResponse)
async def get_security_incident(
    incident_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific security incident."""
    result = await session.execute(
        select(SecurityIncident).where(SecurityIncident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Security incident not found")
    
    return SecurityIncidentResponse.model_validate(incident)


@router.put("/incidents/{incident_id}", response_model=SecurityIncidentResponse)
async def update_security_incident(
    incident_id: str,
    incident_update: SecurityIncidentUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a security incident."""
    result = await session.execute(
        select(SecurityIncident).where(SecurityIncident.incident_id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Security incident not found")
    
    update_data = incident_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    await session.commit()
    await session.refresh(incident)
    
    logger.info("Security incident updated", incident_id=incident_id)
    return SecurityIncidentResponse.model_validate(incident)


@router.get("/dashboard/summary")
async def get_security_dashboard_summary(
    hours: int = Query(24, description="Hours to look back"),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get security dashboard summary."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    base_filters = [SecurityIncident.detected_at >= start_time]
    if environment:
        base_filters.append(SecurityIncident.environment == environment)
    
    # Total incidents by severity
    severity_stats = await session.execute(
        select(
            SecurityIncident.severity,
            func.count(SecurityIncident.incident_id).label('count')
        )
        .where(and_(*base_filters))
        .group_by(SecurityIncident.severity)
    )
    
    severity_counts = {row.severity: row.count for row in severity_stats}
    
    # Incident types
    type_stats = await session.execute(
        select(
            SecurityIncident.incident_type,
            func.count(SecurityIncident.incident_id).label('count')
        )
        .where(and_(*base_filters))
        .group_by(SecurityIncident.incident_type)
        .order_by(func.count(SecurityIncident.incident_id).desc())
        .limit(10)
    )
    
    top_incident_types = [
        {"type": row.incident_type, "count": row.count}
        for row in type_stats
    ]
    
    # PII exposure incidents
    pii_incidents = await session.execute(
        select(func.count(SecurityIncident.incident_id))
        .where(and_(*base_filters, SecurityIncident.pii_exposed == True))
    )
    pii_count = pii_incidents.scalar()
    
    # Compliance violations
    compliance_incidents = await session.execute(
        select(func.count(SecurityIncident.incident_id))
        .where(and_(*base_filters, SecurityIncident.compliance_violation == True))
    )
    compliance_count = compliance_incidents.scalar()
    
    # Resolution metrics
    resolved_incidents = await session.execute(
        select(
            func.count(SecurityIncident.incident_id).label('total_resolved'),
            func.avg(
                func.extract('epoch', SecurityIncident.resolution_time - SecurityIncident.detected_at)
            ).label('avg_resolution_time')
        )
        .where(
            and_(*base_filters, SecurityIncident.status == 'resolved')
        )
    )
    
    resolution_stats = resolved_incidents.first()
    
    return {
        "severity_breakdown": severity_counts,
        "top_incident_types": top_incident_types,
        "pii_exposures": pii_count,
        "compliance_violations": compliance_count,
        "resolution_metrics": {
            "total_resolved": resolution_stats.total_resolved or 0,
            "average_resolution_time_minutes": round((resolution_stats.avg_resolution_time or 0) / 60, 2)
        },
        "time_window_hours": hours
    }


async def trigger_security_alerts(incident_id: str):
    """Background task to trigger security alerts."""
    logger.critical("High severity security incident detected", incident_id=incident_id)
    # Implementation would integrate with alerting systems like PagerDuty, Slack, etc.