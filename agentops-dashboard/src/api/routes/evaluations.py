"""Evaluation result tracking API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...utils.database import get_db_session
from ...models.evaluation_result import EvaluationResult
from ...schemas.evaluation_schemas import (
    EvaluationResultCreate,
    EvaluationResultResponse,
)

router = APIRouter()


@router.post("/", response_model=EvaluationResultResponse)
async def create_evaluation_result(
    evaluation: EvaluationResultCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new evaluation result."""
    db_evaluation = EvaluationResult(**evaluation.model_dump())
    session.add(db_evaluation)
    await session.commit()
    await session.refresh(db_evaluation)
    
    return EvaluationResultResponse.model_validate(db_evaluation)


@router.get("/", response_model=List[EvaluationResultResponse])
async def list_evaluation_results(
    evaluator_name: Optional[str] = Query(None),
    test_suite: Optional[str] = Query(None),
    passed: Optional[bool] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """List evaluation results with filtering."""
    query = select(EvaluationResult)
    
    if evaluator_name:
        query = query.where(EvaluationResult.evaluator_name == evaluator_name)
    if test_suite:
        query = query.where(EvaluationResult.test_suite == test_suite)
    if passed is not None:
        query = query.where(EvaluationResult.passed == passed)
    
    query = query.order_by(EvaluationResult.evaluation_time.desc())
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    evaluations = result.scalars().all()
    
    return [EvaluationResultResponse.model_validate(eval) for eval in evaluations]


@router.get("/summary/quality-trends")
async def get_quality_trends(
    hours: int = Query(24, description="Hours to look back"),
    test_suite: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Get quality score trends over time."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    base_filters = [EvaluationResult.evaluation_time >= start_time]
    if test_suite:
        base_filters.append(EvaluationResult.test_suite == test_suite)
    
    # Hourly trends
    hourly_trends = await session.execute(
        select(
            func.date_trunc('hour', EvaluationResult.evaluation_time).label('hour'),
            func.avg(EvaluationResult.overall_score).label('avg_overall'),
            func.avg(EvaluationResult.accuracy_score).label('avg_accuracy'),
            func.avg(EvaluationResult.safety_score).label('avg_safety'),
            func.count(EvaluationResult.evaluation_id).label('eval_count'),
            func.count(EvaluationResult.evaluation_id).filter(
                EvaluationResult.passed == True
            ).label('passed_count')
        )
        .where(and_(*base_filters))
        .group_by(func.date_trunc('hour', EvaluationResult.evaluation_time))
        .order_by(func.date_trunc('hour', EvaluationResult.evaluation_time))
    )
    
    trends = []
    for row in hourly_trends:
        pass_rate = (row.passed_count / row.eval_count * 100) if row.eval_count > 0 else 0
        trends.append({
            "hour": row.hour.isoformat(),
            "average_overall_score": round(row.avg_overall or 0, 2),
            "average_accuracy_score": round(row.avg_accuracy or 0, 2),
            "average_safety_score": round(row.avg_safety or 0, 2),
            "evaluation_count": row.eval_count,
            "pass_rate_percent": round(pass_rate, 2)
        })
    
    return {"trends": trends, "time_window_hours": hours}


@router.get("/summary/test-suite-performance")
async def get_test_suite_performance(
    hours: int = Query(168, description="Hours to look back (default 1 week)"),
    session: AsyncSession = Depends(get_db_session)
):
    """Get performance breakdown by test suite."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    suite_performance = await session.execute(
        select(
            EvaluationResult.test_suite,
            func.count(EvaluationResult.evaluation_id).label('total_evaluations'),
            func.count(EvaluationResult.evaluation_id).filter(
                EvaluationResult.passed == True
            ).label('passed_evaluations'),
            func.avg(EvaluationResult.overall_score).label('avg_score'),
            func.avg(EvaluationResult.accuracy_score).label('avg_accuracy'),
            func.avg(EvaluationResult.safety_score).label('avg_safety'),
            func.count(EvaluationResult.evaluation_id).filter(
                EvaluationResult.hallucination_detected == True
            ).label('hallucination_count'),
        )
        .where(EvaluationResult.evaluation_time >= start_time)
        .group_by(EvaluationResult.test_suite)
        .order_by(func.count(EvaluationResult.evaluation_id).desc())
    )
    
    suite_stats = []
    for row in suite_performance:
        pass_rate = (row.passed_evaluations / row.total_evaluations * 100) if row.total_evaluations > 0 else 0
        hallucination_rate = (row.hallucination_count / row.total_evaluations * 100) if row.total_evaluations > 0 else 0
        
        suite_stats.append({
            "test_suite": row.test_suite,
            "total_evaluations": row.total_evaluations,
            "pass_rate_percent": round(pass_rate, 2),
            "average_score": round(row.avg_score or 0, 2),
            "average_accuracy": round(row.avg_accuracy or 0, 2),
            "average_safety": round(row.avg_safety or 0, 2),
            "hallucination_rate_percent": round(hallucination_rate, 2),
        })
    
    return {"test_suites": suite_stats, "time_window_hours": hours}