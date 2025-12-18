"""
Voice controller for voice processing operations.
"""
from pathlib import Path
import uuid
from fastapi import UploadFile
from loguru import logger

from src.schemas.voice import VoiceProcessResponse
from src.services.voice.stt_service import get_stt_service
from src.services.voice.tts_service import get_tts_service
from src.services.agent_service import get_agent_service
from src.services.langgraph_service import get_langgraph_service
from src.core.config import get_settings


class VoiceController:
    """Controller for voice processing operations."""

    def __init__(self):
        """Initialize voice controller."""
        self.settings = get_settings()
        self.stt_service = get_stt_service()
        self.tts_service = get_tts_service()
        # Use LangGraph by default, fallback to old agent if needed
        self.use_langgraph = True
        self.langgraph_service = get_langgraph_service()
        self.agent_service = get_agent_service()  # Backup

    async def process_voice(self, audio: UploadFile) -> VoiceProcessResponse:
        """
        Process voice input through STT -> Agent -> TTS pipeline.

        Args:
            audio: Uploaded audio file

        Returns:
            VoiceProcessResponse with transcription, response, and audio URL
        """
        logger.info(f"Processing voice file: {audio.filename}, type: {audio.content_type}")

        # Step 1: Save uploaded audio
        temp_dir = Path(self.settings.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)

        request_id = str(uuid.uuid4())[:8]
        audio_path = temp_dir / f"input_{request_id}.webm"

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        logger.info(f"Saved audio to {audio_path}, size: {len(content)} bytes")

        try:
            # Step 2: Speech-to-Text
            logger.info("Step 1/3: Transcribing audio...")
            transcription = await self.stt_service.transcribe(audio_path, language="fr")
            logger.info(f"Transcription: {transcription}")

            # Step 3: Agent processes the message
            logger.info("Step 2/3: Processing with agent...")

            if self.use_langgraph:
                logger.info("Using LangGraph agent")
                agent_response = await self.langgraph_service.process_message(transcription)
            else:
                logger.info("Using legacy agent")
                agent_response = await self.agent_service.process_message(transcription)

            logger.info(f"Agent response: {agent_response}")

            # Step 4: Text-to-Speech
            logger.info("Step 3/3: Synthesizing speech...")
            static_dir = Path(self.settings.STATIC_DIR)
            static_dir.mkdir(parents=True, exist_ok=True)

            response_audio_path = static_dir / f"response_{request_id}.mp3"
            await self.tts_service.synthesize(agent_response, response_audio_path)

            response_audio_url = f"/static/response_{request_id}.mp3"
            logger.info(f"Audio response URL: {response_audio_url}")

            # Step 5: TODO - Update knowledge graph with conversation

            # Clean up input audio
            audio_path.unlink(missing_ok=True)

            return VoiceProcessResponse(
                success=True,
                transcription=transcription,
                response=agent_response,
                audio_url=response_audio_url,
            )

        except Exception as e:
            # Clean up on error
            audio_path.unlink(missing_ok=True)
            raise


# Singleton instance
_voice_controller: "VoiceController" = None


def get_voice_controller() -> VoiceController:
    """
    Get voice controller singleton.

    Returns:
        VoiceController instance
    """
    global _voice_controller

    if _voice_controller is None:
        _voice_controller = VoiceController()

    return _voice_controller
