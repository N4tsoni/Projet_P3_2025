"""
Configuration settings for Jarvis backend.
Centralizes all environment variables and app settings.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Jarvis Voice Assistant API"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # API
    api_port: int = int(os.getenv("API_PORT", "8000"))
    cors_origins: list[str] = ["*"]  # In production, specify actual origins

    # OpenRouter (LLM)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # OpenAI (for Graphiti embeddings via OpenRouter)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    # Neo4j
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "graphrag2024")

    # Voice Settings
    stt_provider: str = os.getenv("STT_PROVIDER", "groq")  # whisper or groq
    stt_model: str = os.getenv("STT_MODEL", "base")  # For Whisper local
    tts_provider: str = os.getenv("TTS_PROVIDER", "edge")  # edge or coqui
    tts_voice: str = os.getenv("TTS_VOICE", "fr-FR-DeniseNeural")

    # Groq API
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    temp_dir: Path = data_dir / "temp"
    static_dir: Path = base_dir / "static"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the Settings singleton.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
