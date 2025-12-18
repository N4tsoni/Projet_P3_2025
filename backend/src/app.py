"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from src.core.config import get_settings
from src.core.logging import setup_logging
from src.middlewares.cors import add_cors_middleware
from src.middlewares.error_handler import add_error_handlers
from src.api.routes import health, voice, knowledge, langgraph


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    # Setup logging
    setup_logging()

    # Get settings
    settings = get_settings()

    # Create app
    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend API for Jarvis voice assistant with GraphRAG",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # Add middlewares
    add_cors_middleware(app)
    add_error_handlers(app)

    # Mount static files
    static_dir = Path(__file__).parent.parent.parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Include routers
    app.include_router(health.router)
    app.include_router(voice.router)
    app.include_router(knowledge.router)
    app.include_router(langgraph.router)

    # Root endpoint
    @app.get("/")
    async def root():
        """Serve the web interface or API info."""
        web_interface = static_dir / "index.html"
        if web_interface.exists():
            return FileResponse(web_interface)
        return {
            "message": f"{settings.APP_NAME} API",
            "status": "running",
            "version": settings.APP_VERSION,
        }

    return app


# Create app instance
app = create_app()
