"""Main FastAPI application for AgentOps Dashboard API."""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from typing import List, Optional
import uvicorn

from ..utils.database import get_db_session, init_db
from ..utils.config import get_settings
from .routes import (
    executions_router,
    evaluations_router,
    security_router,
    costs_router,
    performance_router,
    alerts_router,
    audit_router,
    dashboard_router,
)

# Configure structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AgentOps Dashboard API")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down AgentOps Dashboard API")


# Create FastAPI application
app = FastAPI(
    title="AgentOps Dashboard API",
    description="Comprehensive monitoring and evaluation API for agentic AI systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error("Unhandled exception", exc_info=exc, request=str(request))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agentops-dashboard-api"}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check database connection
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")


# Include routers
app.include_router(
    executions_router,
    prefix="/api/v1/executions",
    tags=["Agent Executions"]
)

app.include_router(
    evaluations_router,
    prefix="/api/v1/evaluations",
    tags=["Evaluations"]
)

app.include_router(
    security_router,
    prefix="/api/v1/security",
    tags=["Security"]
)

app.include_router(
    costs_router,
    prefix="/api/v1/costs",
    tags=["Cost Tracking"]
)

app.include_router(
    performance_router,
    prefix="/api/v1/performance",
    tags=["Performance Metrics"]
)

app.include_router(
    alerts_router,
    prefix="/api/v1/alerts",
    tags=["Alerts"]
)

app.include_router(
    audit_router,
    prefix="/api/v1/audit",
    tags=["Audit Logs"]
)

app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "AgentOps Dashboard API",
        "version": "1.0.0",
        "description": "Comprehensive monitoring and evaluation API for agentic AI systems",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


def main():
    """Main entry point for running the API server."""
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()