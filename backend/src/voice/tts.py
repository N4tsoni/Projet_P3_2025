"""
Text-to-Speech module.
Supports multiple providers: Edge TTS (free), Coqui, ElevenLabs, etc.
"""
import os
from pathlib import Path
from typing import Optional
from loguru import logger
import edge_tts
import asyncio


class TTSProvider:
    """Base class for TTS providers."""

    async def synthesize(self, text: str, output_path: Path) -> Path:
        """Synthesize speech from text."""
        raise NotImplementedError


class EdgeTTSProvider(TTSProvider):
    """
    Microsoft Edge TTS.
    Free, unlimited, good quality voices.
    """

    def __init__(self, voice: str = "fr-FR-DeniseNeural"):
        """
        Initialize Edge TTS.

        Args:
            voice: Voice ID to use
                   French: fr-FR-DeniseNeural (female), fr-FR-HenriNeural (male)
                   English: en-US-AriaNeural, en-US-GuyNeural
        """
        self.voice = voice
        logger.info(f"Initialized Edge TTS with voice: {voice}")

    async def synthesize(self, text: str, output_path: Path) -> Path:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Where to save audio file

        Returns:
            Path to generated audio file
        """
        try:
            logger.info(f"Synthesizing: {text[:50]}...")

            # Create communicate object
            communicate = edge_tts.Communicate(text, self.voice)

            # Generate audio
            await communicate.save(str(output_path))

            logger.info(f"Audio saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise


class CoquiTTSProvider(TTSProvider):
    """
    Coqui TTS - Local, open-source TTS.
    Requires more setup but runs locally.
    """

    def __init__(self, model_name: str = "tts_models/fr/css10/vits"):
        """
        Initialize Coqui TTS.

        Args:
            model_name: Model to use
        """
        self.model_name = model_name
        self.tts = None
        logger.info(f"Initializing Coqui TTS: {model_name}")

    def _load_model(self):
        """Lazy load the model."""
        if self.tts is None:
            from TTS.api import TTS

            logger.info("Loading Coqui TTS model...")
            self.tts = TTS(model_name=self.model_name)
            logger.info("Coqui TTS model loaded")

    async def synthesize(self, text: str, output_path: Path) -> Path:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Where to save audio file

        Returns:
            Path to generated audio file
        """
        try:
            self._load_model()

            logger.info(f"Synthesizing: {text[:50]}...")

            # TTS is CPU-bound, run in thread pool in production
            self.tts.tts_to_file(text=text, file_path=str(output_path))

            logger.info(f"Audio saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            raise


def get_tts_provider() -> TTSProvider:
    """
    Get TTS provider based on configuration.

    Returns:
        Configured TTS provider
    """
    provider_name = os.getenv("TTS_PROVIDER", "edge-tts")

    if provider_name in ["edge-tts", "edge"]:
        voice = os.getenv("TTS_VOICE", "fr-FR-DeniseNeural")
        return EdgeTTSProvider(voice=voice)

    elif provider_name in ["coqui-local", "coqui"]:
        model = os.getenv("TTS_MODEL", "tts_models/fr/css10/vits")
        return CoquiTTSProvider(model_name=model)

    else:
        raise ValueError(f"Unknown TTS provider: {provider_name}")


# Singleton instance
_tts_provider: Optional[TTSProvider] = None


async def synthesize_speech(text: str, output_path: Path) -> Path:
    """
    Synthesize speech from text using configured provider.

    Args:
        text: Text to synthesize
        output_path: Where to save audio file

    Returns:
        Path to generated audio file
    """
    global _tts_provider

    if _tts_provider is None:
        _tts_provider = get_tts_provider()

    return await _tts_provider.synthesize(text, output_path)
