"""
FastAPI application for Jarvis voice assistant.
Refactored with Layered Architecture.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.core.config import get_settings
from src.api.routes import voice_router, knowledge_router, health_router

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Jarvis voice assistant with GraphRAG and Layered Architecture",
    version=settings.app_version,
    debug=settings.debug,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Include routers
app.include_router(health_router)  # Health checks at root level
app.include_router(voice_router)  # /api/voice/*
app.include_router(knowledge_router)  # /api/knowledge/*


@app.on_event("startup")
async def startup_event():
    """Application startup - Initialize services."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"STT Provider: {settings.stt_provider}")
    logger.info(f"TTS Provider: {settings.tts_provider}")
    logger.info(f"LLM Model: {settings.openrouter_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown - Cleanup resources."""
    logger.info("Shutting down Jarvis backend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
