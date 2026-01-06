"""
Voice processing routes.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger

from src.models.responses import VoiceProcessResponse, ErrorResponse
from src.services.voice_service import get_voice_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice(audio: UploadFile = File(...)):
    """
    Process voice input through the complete pipeline: STT → Agent → TTS.

    Args:
        audio: Audio file (WAV, WebM, MP3, etc.)

    Returns:
        VoiceProcessResponse with transcription, response, and audio URL

    Raises:
        HTTPException: If processing fails
    """
    try:
        voice_service = get_voice_service()
        transcription, response, audio_url = await voice_service.process_voice_input(audio)

        return VoiceProcessResponse(
            success=True,
            transcription=transcription,
            response=response,
            audio_url=audio_url
        )

    except ValueError as e:
        # Empty transcription or validation error
        logger.warning(f"Validation error: {e}")
        return ErrorResponse(
            error=str(e),
            transcription="",
            response=""
        )

    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
