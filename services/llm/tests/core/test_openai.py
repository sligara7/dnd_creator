"""Tests for OpenAI service integration."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from llm_service.core.config import Settings
from llm_service.core.exceptions import ContentGenerationError
from llm_service.services.openai import OpenAIService


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        OPENAI_API_KEY="test-key",
        OPENAI_MAX_RETRIES=2,
        OPENAI_TIMEOUT=30,
        OPENAI_MODEL="gpt-4",
    )


@pytest.fixture
def mock_client():
    """Create mock HTTPX client."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock(spec=AsyncClient)
        mock.return_value = client
        yield client


@pytest.fixture
def openai_service(settings, mock_client):
    """Create OpenAI service instance."""
    service = OpenAIService(settings)
    service.client = mock_client
    return service


@pytest.mark.asyncio
async def test_generate_text_success(openai_service, mock_client):
    """Test successful text generation."""
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"text": "Generated text"}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }
    mock_client.post.return_value = mock_response

    # Generate text
    text, usage = await openai_service.generate_text(
        prompt="Test prompt",
        max_tokens=100,
        temperature=0.7,
    )

    # Verify response
    assert text == "Generated text"
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30

    # Verify request
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0].endswith("/completions")
    assert call_args[1]["json"]["prompt"] == "Test prompt"
    assert call_args[1]["json"]["max_tokens"] == 100
    assert call_args[1]["json"]["temperature"] == 0.7


@pytest.mark.asyncio
async def test_generate_text_api_error(openai_service, mock_client):
    """Test handling of API errors."""
    # Prepare mock error response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": {"message": "Test error"},
    }
    mock_client.post.return_value = mock_response

    # Verify error handling
    with pytest.raises(ContentGenerationError) as exc_info:
        await openai_service.generate_text("Test prompt")

    assert "API error" in str(exc_info.value)
    assert mock_client.post.call_count == openai_service.settings.OPENAI_MAX_RETRIES


@pytest.mark.asyncio
async def test_generate_text_rate_limit(openai_service, mock_client):
    """Test handling of rate limit errors."""
    # Prepare mock rate limit response
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": {"message": "Rate limit exceeded"},
    }
    mock_client.post.return_value = mock_response

    # Verify rate limit handling
    with pytest.raises(ContentGenerationError) as exc_info:
        await openai_service.generate_text("Test prompt")

    assert "rate limit" in str(exc_info.value).lower()
    assert mock_client.post.call_count == openai_service.settings.OPENAI_MAX_RETRIES


@pytest.mark.asyncio
async def test_generate_text_timeout(openai_service, mock_client):
    """Test handling of timeout errors."""
    # Make client raise timeout error
    mock_client.post.side_effect = TimeoutError("Request timed out")

    # Verify timeout handling
    with pytest.raises(ContentGenerationError) as exc_info:
        await openai_service.generate_text("Test prompt")

    assert "timed out" in str(exc_info.value)
    assert mock_client.post.call_count == openai_service.settings.OPENAI_MAX_RETRIES
