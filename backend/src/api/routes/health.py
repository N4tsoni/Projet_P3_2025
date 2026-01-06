"""
Health check routes.
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

from src.models.responses import HealthResponse
from src.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/", include_in_schema=False)
async def root():
    """Serve the web interface or return API info."""
    settings = get_settings()
    web_interface = settings.static_dir / "index.html"

    if web_interface.exists():
        return FileResponse(web_interface)

    return {
        "message": "Jarvis Voice Assistant API",
        "status": "running",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version
    )


@router.get("/api/health", response_model=HealthResponse)
async def api_health_check():
    """API health check endpoint with sub-services status."""
    settings = get_settings()

    # TODO: Add actual health checks for Neo4j, etc.
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        services={
            "neo4j": True,  # TODO: Check actual Neo4j status
            "stt": True,
            "tts": True,
            "agent": True
        }
    )
