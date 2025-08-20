"""Agent execution tracking API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ...utils.database import get_db_session
from ...models.agent_execution import AgentExecution
from ...schemas.execution_schemas import (
    ExecutionCreate,
    ExecutionUpdate,
    ExecutionResponse,
    ExecutionSummary,
    ExecutionFilters,
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution: ExecutionCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new agent execution record."""
    try:
        db_execution = AgentExecution(**execution.model_dump())
        session.add(db_execution)
        await session.commit()
        await session.refresh(db_execution)
        
        # Background task for real-time analytics
        background_tasks.add_task(process_execution_analytics, db_execution.execution_id)
        
        logger.info("Execution created", execution_id=db_execution.execution_id)
        return ExecutionResponse.model_validate(db_execution)
    except Exception as e:
        logger.error("Failed to create execution", error=str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create execution")


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific execution by ID."""
    result = await session.execute(
        select(AgentExecution).where(AgentExecution.execution_id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return ExecutionResponse.model_validate(execution)


@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    agent_name: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """List executions with optional filtering."""
    query = select(AgentExecution)
    
    # Apply filters
    filters = []
    if agent_name:
        filters.append(AgentExecution.agent_name == agent_name)
    if environment:
        filters.append(AgentExecution.environment == environment)
    if status:
        filters.append(AgentExecution.status == status)
    if start_time:
        filters.append(AgentExecution.start_time >= start_time)
    if end_time:
        filters.append(AgentExecution.start_time <= end_time)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(AgentExecution.start_time.desc())
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    executions = result.scalars().all()
    
    return [ExecutionResponse.model_validate(exec) for exec in executions]


@router.put("/{execution_id}", response_model=ExecutionResponse)
async def update_execution(
    execution_id: str,
    execution_update: ExecutionUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update an existing execution."""
    result = await session.execute(
        select(AgentExecution).where(AgentExecution.execution_id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    update_data = execution_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(execution, field, value)
    
    await session.commit()
    await session.refresh(execution)
    
    logger.info("Execution updated", execution_id=execution_id)
    return ExecutionResponse.model_validate(execution)


@router.get("/summary/stats", response_model=Dict[str, Any])
async def get_execution_stats(
    hours: int = Query(24, description="Hours to look back"),
    agent_name: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get execution statistics for the dashboard."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    base_query = select(AgentExecution).where(
        AgentExecution.start_time >= start_time
    )
    
    # Apply filters
    if agent_name:
        base_query = base_query.where(AgentExecution.agent_name == agent_name)
    if environment:
        base_query = base_query.where(AgentExecution.environment == environment)
    
    # Total executions
    total_result = await session.execute(
        select(func.count(AgentExecution.execution_id)).select_from(base_query.subquery())
    )
    total_executions = total_result.scalar()
    
    # Success rate
    success_result = await session.execute(
        select(func.count(AgentExecution.execution_id)).select_from(
            base_query.where(AgentExecution.success == True).subquery()
        )
    )
    successful_executions = success_result.scalar()
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    # Average duration
    avg_duration_result = await session.execute(
        select(func.avg(AgentExecution.duration_ms)).select_from(base_query.subquery())
    )
    avg_duration = avg_duration_result.scalar() or 0
    
    # Cost summary
    cost_result = await session.execute(
        select(func.sum(AgentExecution.cost_usd)).select_from(base_query.subquery())
    )
    total_cost = cost_result.scalar() or 0
    
    # Error distribution
    error_result = await session.execute(
        select(
            AgentExecution.error_type,
            func.count(AgentExecution.execution_id).label('count')
        ).select_from(
            base_query.where(AgentExecution.success == False).subquery()
        ).group_by(AgentExecution.error_type)
    )
    error_distribution = {row.error_type or 'unknown': row.count for row in error_result}
    
    return {
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "success_rate_percent": round(success_rate, 2),
        "average_duration_ms": round(avg_duration, 2),
        "total_cost_usd": round(total_cost, 4),
        "error_distribution": error_distribution,
        "time_window_hours": hours,
    }


@router.get("/trends/hourly", response_model=List[Dict[str, Any]])
async def get_hourly_trends(
    hours: int = Query(24, description="Hours to look back"),
    agent_name: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get hourly execution trends."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(
        func.date_trunc('hour', AgentExecution.start_time).label('hour'),
        func.count(AgentExecution.execution_id).label('total'),
        func.count(AgentExecution.execution_id).filter(
            AgentExecution.success == True
        ).label('successful'),
        func.avg(AgentExecution.duration_ms).label('avg_duration'),
        func.sum(AgentExecution.cost_usd).label('total_cost')
    ).where(
        AgentExecution.start_time >= start_time
    )
    
    if agent_name:
        query = query.where(AgentExecution.agent_name == agent_name)
    
    query = query.group_by(func.date_trunc('hour', AgentExecution.start_time))
    query = query.order_by(func.date_trunc('hour', AgentExecution.start_time))
    
    result = await session.execute(query)
    trends = []
    
    for row in result:
        success_rate = (row.successful / row.total * 100) if row.total > 0 else 0
        trends.append({
            "hour": row.hour.isoformat(),
            "total_executions": row.total,
            "successful_executions": row.successful,
            "success_rate_percent": round(success_rate, 2),
            "average_duration_ms": round(row.avg_duration or 0, 2),
            "total_cost_usd": round(row.total_cost or 0, 4),
        })
    
    return trends


async def process_execution_analytics(execution_id: str):
    """Background task to process execution analytics."""
    # This would trigger real-time analytics processing
    # For now, just log the event
    logger.info("Processing execution analytics", execution_id=execution_id)