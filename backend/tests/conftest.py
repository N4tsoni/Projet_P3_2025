"""
Pytest configuration and fixtures.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

from src.core.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Settings()
    settings.temp_dir = Path("/tmp/jarvis_test")
    settings.static_dir = Path("/tmp/jarvis_test/static")
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    settings.static_dir.mkdir(parents=True, exist_ok=True)
    return settings


@pytest.fixture
def mock_audio_file():
    """Mock UploadFile for testing."""
    mock = AsyncMock()
    mock.filename = "test_audio.webm"
    mock.content_type = "audio/webm"
    mock.read = AsyncMock(return_value=b"fake_audio_content")
    return mock


@pytest.fixture
def api_client():
    """FastAPI test client."""
    from src.api.main import app
    return TestClient(app)
