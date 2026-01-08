"""
Voice processing routes.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from src.models.responses import VoiceProcessResponse, ErrorResponse
from src.models.requests import TextMessageRequest
from src.services.voice_service import get_voice_service
from src.core.database import get_db

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice(
    audio: UploadFile = File(...),
    conversation_id: Optional[str] = Query(None, description="Conversation ID to add this interaction to"),
    db: Session = Depends(get_db),
):
    """
    Process voice input through the complete pipeline: STT → Agent → TTS.

    Args:
        audio: Audio file (WAV, WebM, MP3, etc.)
        conversation_id: Optional conversation ID to persist this interaction

    Returns:
        VoiceProcessResponse with transcription, response, and audio URL

    Raises:
        HTTPException: If processing fails
    """
    try:
        voice_service = get_voice_service()
        transcription, response, audio_url = await voice_service.process_voice_input(
            audio, conversation_id=conversation_id, db=db
        )

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


@router.post("/text", response_model=VoiceProcessResponse)
async def process_text(
    request: TextMessageRequest,
    db: Session = Depends(get_db),
):
    """
    Process text message directly (without voice input).

    Args:
        request: TextMessageRequest with text and optional conversation_id

    Returns:
        VoiceProcessResponse with the text, response, and audio URL

    Raises:
        HTTPException: If processing fails
    """
    try:
        voice_service = get_voice_service()
        text, response, audio_url = await voice_service.process_text_input(
            request.text, conversation_id=request.conversation_id, db=db
        )

        return VoiceProcessResponse(
            success=True,
            transcription=text,
            response=response,
            audio_url=audio_url
        )

    except ValueError as e:
        # Empty text or validation error
        logger.warning(f"Validation error: {e}")
        return ErrorResponse(
            error=str(e),
            transcription="",
            response=""
        )

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
