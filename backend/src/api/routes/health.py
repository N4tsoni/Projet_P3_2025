"""
Health check routes.
"""
from fastapi import APIRouter, Depends

from src.schemas.health import HealthResponse, HealthDetailResponse
from src.controllers.health_controller import HealthController, get_health_controller

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    controller: HealthController = Depends(get_health_controller)
):
    """
    Basic health check endpoint.

    Returns:
        Health status
    """
    return await controller.get_health()


@router.get("/api/health", response_model=HealthDetailResponse)
async def api_health_check(
    controller: HealthController = Depends(get_health_controller)
):
    """
    Detailed health check endpoint with all services status.

    Returns:
        Detailed health status
    """
    return await controller.get_health_detail()
