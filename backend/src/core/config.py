"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Jarvis Voice Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"

    # OpenRouter / LLM
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    LLM_MAX_TOKENS: int = 500
    LLM_TEMPERATURE: float = 0.7

    # Neo4j
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "graphrag2024"

    # Voice Settings
    STT_PROVIDER: str = "whisper-local"
    STT_MODEL: str = "base"
    TTS_PROVIDER: str = "edge-tts"
    TTS_VOICE: str = "fr-FR-DeniseNeural"

    # Groq (optional)
    GROQ_API_KEY: str = ""

    # Paths
    TEMP_DIR: str = "/app/data/temp"
    STATIC_DIR: str = "/app/static"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()
