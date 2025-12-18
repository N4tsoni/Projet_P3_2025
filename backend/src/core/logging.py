"""
Logging configuration using Loguru.
"""
import sys
from loguru import logger
from .config import get_settings


def setup_logging():
    """Configure Loguru logger."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Add file handler if in production
    if not settings.DEBUG:
        logger.add(
            "/app/logs/jarvis_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")
