"""Cost tracking API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...utils.database import get_db_session

router = APIRouter()

@router.get("/summary")
async def get_cost_summary(
    days: int = Query(7, description="Days to look back"),
    session: AsyncSession = Depends(get_db_session)
):
    """Get cost summary."""
    return {"message": "Cost summary endpoint - implementation in progress"}