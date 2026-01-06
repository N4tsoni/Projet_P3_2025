"""
API Routes - Import all routers here.
"""
from .voice import router as voice_router
from .knowledge import router as knowledge_router
from .health import router as health_router

__all__ = ["voice_router", "knowledge_router", "health_router"]
