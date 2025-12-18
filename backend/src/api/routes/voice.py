"""
Voice processing routes.
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException

from src.schemas.voice import VoiceProcessResponse
from src.controllers.voice_controller import VoiceController, get_voice_controller

router = APIRouter(prefix="/api/voice", tags=["Voice"])


@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice(
    audio: UploadFile = File(...),
    controller: VoiceController = Depends(get_voice_controller)
):
    """
    Process voice input through STT -> Agent -> TTS pipeline.

    Args:
        audio: Audio file (WAV, WebM, etc.)

    Returns:
        JSON with transcription, response text, and audio URL

    Raises:
        HTTPException: If processing fails
    """
    try:
        return await controller.process_voice(audio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
