"""
Health controller for application health checks.
"""
from src.schemas.health import HealthResponse, HealthDetailResponse
from src.core.config import get_settings


class HealthController:
    """Controller for health check operations."""

    def __init__(self):
        """Initialize health controller."""
        self.settings = get_settings()

    async def get_health(self) -> HealthResponse:
        """
        Get basic health status.

        Returns:
            HealthResponse with status information
        """
        return HealthResponse(
            status="healthy",
            service=self.settings.APP_NAME,
            version=self.settings.APP_VERSION,
        )

    async def get_health_detail(self) -> HealthDetailResponse:
        """
        Get detailed health status with all services.

        Returns:
            HealthDetailResponse with detailed information
        """
        # TODO: Check actual service statuses
        return HealthDetailResponse(
            status="healthy",
            service=self.settings.APP_NAME,
            version=self.settings.APP_VERSION,
            services={
                "neo4j": True,
                "whisper": True,
                "tts": True,
            }
        )


# Singleton instance
_health_controller: "HealthController" = None


def get_health_controller() -> HealthController:
    """
    Get health controller singleton.

    Returns:
        HealthController instance
    """
    global _health_controller

    if _health_controller is None:
        _health_controller = HealthController()

    return _health_controller
