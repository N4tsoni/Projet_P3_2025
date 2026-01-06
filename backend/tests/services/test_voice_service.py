"""
Tests for VoiceService.
"""
import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

from src.services.voice_service import VoiceService


@pytest.mark.asyncio
async def test_voice_service_process_success(mock_audio_file, mock_settings):
    """Test successful voice processing."""
    service = VoiceService()

    with patch('src.services.voice_service.transcribe_audio') as mock_stt, \
         patch('src.services.voice_service.get_agent') as mock_agent_getter, \
         patch('src.services.voice_service.synthesize_speech') as mock_tts:

        # Setup mocks
        mock_stt.return_value = "Bonjour Jarvis"
        
        mock_agent = AsyncMock()
        mock_agent.chat = AsyncMock(return_value="Bonjour! Comment puis-je vous aider?")
        mock_agent_getter.return_value = mock_agent

        mock_tts.return_value = None

        # Execute
        transcription, response, audio_url = await service.process_voice_input(mock_audio_file)

        # Assertions
        assert transcription == "Bonjour Jarvis"
        assert response == "Bonjour! Comment puis-je vous aider?"
        assert "/static/response_" in audio_url
        assert audio_url.endswith(".mp3")

        # Verify calls
        mock_stt.assert_called_once()
        mock_agent.chat.assert_called_once_with("Bonjour Jarvis")
        mock_tts.assert_called_once()


@pytest.mark.asyncio
async def test_voice_service_empty_transcription(mock_audio_file):
    """Test handling of empty transcription."""
    service = VoiceService()

    with patch('src.services.voice_service.transcribe_audio') as mock_stt:
        mock_stt.return_value = ""

        # Should raise ValueError
        with pytest.raises(ValueError, match="Aucune parole détectée"):
            await service.process_voice_input(mock_audio_file)


@pytest.mark.asyncio
async def test_voice_service_cleanup_on_error(mock_audio_file):
    """Test that temp files are cleaned up even on error."""
    service = VoiceService()

    with patch('src.services.voice_service.transcribe_audio') as mock_stt, \
         patch.object(service, '_cleanup_temp_file') as mock_cleanup:

        mock_stt.side_effect = Exception("STT failed")

        # Should raise exception but still cleanup
        with pytest.raises(Exception, match="STT failed"):
            await service.process_voice_input(mock_audio_file)

        # Cleanup should be called
        mock_cleanup.assert_called_once()
