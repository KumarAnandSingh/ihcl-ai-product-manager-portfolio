"""API routes for AgentOps Dashboard."""

from .executions import router as executions_router
from .evaluations import router as evaluations_router
from .security import router as security_router
from .costs import router as costs_router
from .performance import router as performance_router
from .alerts import router as alerts_router
from .audit import router as audit_router
from .dashboard import router as dashboard_router

__all__ = [
    "executions_router",
    "evaluations_router",
    "security_router",
    "costs_router",
    "performance_router",
    "alerts_router",
    "audit_router",
    "dashboard_router",
]