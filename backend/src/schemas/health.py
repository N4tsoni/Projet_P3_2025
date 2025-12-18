"""
Health check schemas.
"""
from pydantic import BaseModel
from typing import Dict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class HealthDetailResponse(BaseModel):
    """Detailed health check response."""

    status: str
    service: str
    version: str
    services: Dict[str, bool]
