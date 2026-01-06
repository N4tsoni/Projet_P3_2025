"""
Voice processing service - Business logic for voice pipeline.
Handles the complete flow: STT → Agent → TTS
"""
from pathlib import Path
from typing import Tuple
import uuid
from loguru import logger
from fastapi import UploadFile

from src.voice.stt import transcribe_audio
from src.voice.tts import synthesize_speech
from src.agents.jarvis_agent import get_agent
from src.core.config import get_settings


class VoiceService:
    """
    Service for processing voice input through the complete pipeline.
    """

    def __init__(self):
        self.settings = get_settings()

    async def process_voice_input(
        self,
        audio_file: UploadFile
    ) -> Tuple[str, str, str]:
        """
        Process voice input through the complete pipeline.

        Args:
            audio_file: Uploaded audio file

        Returns:
            Tuple of (transcription, agent_response, audio_url)

        Raises:
            ValueError: If transcription is empty
            Exception: If processing fails
        """
        logger.info(f"Processing voice input: {audio_file.filename}, type: {audio_file.content_type}")

        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Step 1: Save uploaded audio
        audio_path = await self._save_audio_file(audio_file, request_id)
        logger.info(f"Audio saved: {audio_path}")

        try:
            # Step 2: Speech-to-Text
            transcription = await self._transcribe(audio_path)

            # Step 3: Validate transcription
            if not transcription or len(transcription.strip()) == 0:
                logger.warning("Empty transcription - no speech detected")
                raise ValueError("Aucune parole détectée dans l'audio")

            # Step 4: Process with agent
            agent_response = await self._process_with_agent(transcription)

            # Step 5: Text-to-Speech
            audio_url = await self._synthesize_response(agent_response, request_id)

            # TODO: Step 6: Update knowledge graph

            logger.info(f"Voice processing complete: {request_id}")
            return transcription, agent_response, audio_url

        finally:
            # Clean up temporary input audio
            self._cleanup_temp_file(audio_path)

    async def _save_audio_file(self, audio_file: UploadFile, request_id: str) -> Path:
        """Save uploaded audio file to temporary directory."""
        audio_path = self.settings.temp_dir / f"input_{request_id}.webm"

        content = await audio_file.read()
        with open(audio_path, "wb") as f:
            f.write(content)

        logger.debug(f"Saved audio: size={len(content)} bytes, path={audio_path}")
        return audio_path

    async def _transcribe(self, audio_path: Path) -> str:
        """Transcribe audio to text using configured STT provider."""
        logger.info("Transcribing audio...")
        transcription = await transcribe_audio(audio_path, language="fr")
        logger.info(f"Transcription: {transcription}")
        return transcription

    async def _process_with_agent(self, transcription: str) -> str:
        """Process transcription with conversational agent."""
        logger.info("Processing with agent...")
        agent = get_agent()
        response = await agent.chat(transcription)
        logger.info(f"Agent response: {response}")
        return response

    async def _synthesize_response(self, text: str, request_id: str) -> str:
        """Synthesize text to speech and return URL."""
        logger.info("Synthesizing speech...")

        response_audio_path = self.settings.static_dir / f"response_{request_id}.mp3"
        await synthesize_speech(text, response_audio_path)

        audio_url = f"/static/response_{request_id}.mp3"
        logger.info(f"Audio response: {audio_url}")
        return audio_url

    def _cleanup_temp_file(self, file_path: Path):
        """Remove temporary file."""
        try:
            file_path.unlink(missing_ok=True)
            logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")


# Singleton instance
_voice_service: VoiceService | None = None


def get_voice_service() -> VoiceService:
    """
    Get or create the VoiceService singleton.

    Returns:
        VoiceService instance
    """
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
