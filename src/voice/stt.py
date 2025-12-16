"""
Speech-to-Text module.
Supports multiple providers: Whisper (local), Groq, etc.
"""
import os
from pathlib import Path
from typing import Optional
from loguru import logger
import whisper


class STTProvider:
    """Base class for STT providers."""

    async def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text."""
        raise NotImplementedError


class WhisperLocalSTT(STTProvider):
    """
    Local Whisper STT using OpenAI's open-source model.
    Runs locally, no API key needed.
    """

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper model.

        Args:
            model_name: Model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Initializing Whisper model: {model_name}")

    def _load_model(self):
        """Lazy load the model."""
        if self.model is None:
            logger.info(f"Loading Whisper model '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")

    async def transcribe(self, audio_path: Path, language: str = "fr") -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file
            language: Language code (fr, en, etc.)

        Returns:
            Transcribed text
        """
        try:
            self._load_model()

            logger.info(f"Transcribing audio: {audio_path}")

            # Whisper transcribe is CPU-bound, but for now we'll run it directly
            # In production, consider running in a thread pool
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                fp16=False,  # Set to True if GPU available
            )

            text = result["text"].strip()
            logger.info(f"Transcription: {text}")

            return text

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise


class GroqSTT(STTProvider):
    """
    Groq STT using their Whisper API.
    Fast and has a generous free tier.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq STT.

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")

        logger.info("Initialized Groq STT")

    async def transcribe(self, audio_path: Path, language: str = "fr") -> str:
        """
        Transcribe audio using Groq API.

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Transcribed text
        """
        try:
            import httpx

            logger.info(f"Transcribing with Groq: {audio_path}")

            with open(audio_path, "rb") as audio_file:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        files={"file": audio_file},
                        data={
                            "model": "whisper-large-v3",
                            "language": language,
                        },
                    )

                    response.raise_for_status()
                    result = response.json()
                    text = result["text"].strip()

                    logger.info(f"Transcription: {text}")
                    return text

        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
            raise


def get_stt_provider() -> STTProvider:
    """
    Get STT provider based on configuration.

    Returns:
        Configured STT provider
    """
    provider_name = os.getenv("STT_PROVIDER", "whisper-local")

    if provider_name == "whisper-local":
        model_name = os.getenv("STT_MODEL", "base")
        return WhisperLocalSTT(model_name=model_name)

    elif provider_name == "groq":
        return GroqSTT()

    else:
        raise ValueError(f"Unknown STT provider: {provider_name}")


# Singleton instance
_stt_provider: Optional[STTProvider] = None


async def transcribe_audio(audio_path: Path, language: str = "fr") -> str:
    """
    Transcribe audio file to text using configured provider.

    Args:
        audio_path: Path to audio file
        language: Language code (default: fr)

    Returns:
        Transcribed text
    """
    global _stt_provider

    if _stt_provider is None:
        _stt_provider = get_stt_provider()

    return await _stt_provider.transcribe(audio_path, language=language)
