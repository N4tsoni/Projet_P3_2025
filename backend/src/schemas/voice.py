"""
Voice processing schemas.
"""
from pydantic import BaseModel


class VoiceProcessResponse(BaseModel):
    """Response from voice processing."""

    success: bool
    transcription: str
    response: str
    audio_url: str
