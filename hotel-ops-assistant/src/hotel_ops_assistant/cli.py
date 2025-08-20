"""
Command Line Interface for Hotel Operations Assistant.
Provides CLI commands for running the application and management tasks.
"""

import asyncio
import typer
from typing import Optional

from .api.main import create_app
from .core.config import get_settings

app = typer.Typer(
    name="hotel-ops-assistant",
    help="Hotel Operations Assistant CLI"
)


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    workers: int = typer.Option(1, help="Number of worker processes"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    log_level: str = typer.Option("info", help="Log level")
):
    """Run the Hotel Operations Assistant API server."""
    
    import uvicorn
    
    uvicorn.run(
        "hotel_ops_assistant.api.main:create_app",
        factory=True,
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level=log_level
    )


@app.command()
def health():
    """Check application health."""
    
    async def check_health():
        settings = get_settings()
        
        typer.echo(f"Hotel Operations Assistant v{settings.app_version}")
        typer.echo(f"Environment: {settings.environment}")
        typer.echo(f"Debug mode: {settings.debug}")
        typer.echo(f"PII Protection: {'Enabled' if settings.enable_pii_protection else 'Disabled'}")
        typer.echo(f"Audit Logging: {'Enabled' if settings.enable_audit_logging else 'Disabled'}")
        typer.echo("Status: Ready")
    
    asyncio.run(check_health())


@app.command()
def demo():
    """Run demo scenarios."""
    
    typer.echo("Hotel Operations Assistant Demo")
    typer.echo("=" * 40)
    
    scenarios = [
        "Guest Service: 'I need room service for dinner'",
        "Complaint: 'My room hasn't been cleaned'", 
        "Security: 'I can't access my room'",
        "Fraud Detection: 'Multiple cards used by same guest'"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        typer.echo(f"{i}. {scenario}")
    
    typer.echo("\nUse the API endpoints to test these scenarios.")
    typer.echo("Start the server with: hotel-ops-assistant run")
    typer.echo("Then visit: http://localhost:8000/docs")


@app.command()
def compliance_check():
    """Run compliance self-check."""
    
    async def run_compliance_check():
        from .services.compliance_service import ComplianceService
        
        compliance_service = ComplianceService()
        
        # Sample data for compliance check
        test_data = {
            "guest_name": "John Doe",
            "email": "john@example.com", 
            "phone": "+1234567890",
            "room_number": "101"
        }
        
        # Run DPDP compliance check
        result = await compliance_service.check_dpdp_compliance(test_data, "guest_service")
        
        typer.echo(f"Compliance Check Results:")
        typer.echo(f"Framework: {result.framework.value}")
        typer.echo(f"Status: {result.status.value}")
        typer.echo(f"Score: {result.score}/100")
        
        if result.recommendations:
            typer.echo("\nRecommendations:")
            for rec in result.recommendations:
                typer.echo(f"- {rec}")
    
    asyncio.run(run_compliance_check())


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()