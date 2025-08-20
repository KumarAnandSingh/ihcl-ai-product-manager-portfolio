"""Performance metrics API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from ...utils.database import get_db_session

router = APIRouter()

@router.get("/summary")
async def get_performance_summary(
    hours: int = Query(24, description="Hours to look back"),
    session: AsyncSession = Depends(get_db_session)
):
    """Get performance summary."""
    return {"message": "Performance summary endpoint - implementation in progress"}