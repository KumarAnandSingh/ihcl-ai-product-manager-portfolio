"""
FastAPI middleware setup and configuration.
"""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from ..core.config import get_settings


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application."""
    
    settings = get_settings()
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not settings.is_production else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted hosts middleware for production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "api.yourdomain.com"]
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> Response:
        """Log all HTTP requests for audit trail."""
        
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        processing_time_ms = int(process_time * 1000)
        
        # Log to audit system
        if hasattr(request.app.state, 'audit_logger'):
            request.app.state.audit_logger.log_api_access(
                endpoint=str(request.url.path),
                method=request.method,
                response_code=response.status_code,
                processing_time_ms=processing_time_ms,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(processing_time_ms)
        
        return response
    
    # Security headers middleware
    @app.middleware("http")
    async def security_headers(request: Request, call_next: Callable) -> Response:
        """Add security headers to all responses."""
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response