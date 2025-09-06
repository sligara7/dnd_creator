"""Tests for content validation service."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.config import Settings
from llm_service.core.exceptions import ValidationError
from llm_service.core.cache import RateLimiter
from llm_service.services.openai import OpenAIService
from llm_service.services.validation_service import (
    ValidationService,
    ContentValidation,
)


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
def mock_openai():
    """Create mock OpenAI service."""
    service = MagicMock(spec=OpenAIService)
    service.generate_text = AsyncMock()
    return service


@pytest.fixture
def mock_rate_limiter():
    """Create mock rate limiter."""
    rate_limiter = MagicMock(spec=RateLimiter)
    rate_limiter.check_text_limit = AsyncMock()
    return rate_limiter


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def validation_service(settings, mock_openai, mock_rate_limiter, mock_db):
    """Create validation service instance."""
    return ValidationService(settings, mock_openai, mock_rate_limiter, mock_db)


@pytest.fixture
def mock_validation_response():
    """Create mock validation response."""
    class MockCompletion:
        text = """\
{
    "is_valid": true,
    "score": 0.85,
    "issues": [
        {
            "category": "theme",
            "severity": "warning",
            "description": "Theme could be stronger",
            "impact": "medium"
        }
    ],
    "suggestions": [
        "Enhance theme elements",
        "Add more details"
    ]
}"""
        choices = [MagicMock(text=text)]

    return MockCompletion()


@pytest.mark.asyncio
async def test_validate_character_content(
    validation_service, mock_openai, mock_rate_limiter, mock_validation_response
):
    """Test character content validation."""
    # Set up mock response
    mock_openai.generate_text.return_value = mock_validation_response

    # Create test data
    content_id = uuid.uuid4()
    content = "Test character content"
    content_type = "character_backstory"
    parameters = {
        "character_class": "Wizard",
        "level": 5,
        "theme": "dark fantasy",
    }

    # Validate content
    result = await validation_service.validate_character_content(
        content=content,
        content_type=content_type,
        character_id=content_id,
        parameters=parameters,
    )

    # Verify result
    assert isinstance(result, ContentValidation)
    assert result.is_valid is True
    assert result.score == 0.85
    assert len(result.issues) == 1
    assert result.issues[0]["category"] == "theme"
    assert len(result.suggestions) == 2

    # Verify rate limit check
    mock_rate_limiter.check_text_limit.assert_called_once_with("validation")

    # Verify OpenAI call
    mock_openai.generate_text.assert_called_once()
    call_args = mock_openai.generate_text.call_args
    assert "content_type" in call_args[1]["prompt"]
    assert "D&D 5e" in call_args[1]["prompt"]
    assert call_args[1]["max_tokens"] == 1000
    assert call_args[1]["temperature"] == 0.3


@pytest.mark.asyncio
async def test_validate_theme_consistency(
    validation_service, mock_openai, mock_rate_limiter, mock_validation_response
):
    """Test theme consistency validation."""
    # Set up mock response
    mock_openai.generate_text.return_value = mock_validation_response

    # Create test data
    content_id = uuid.uuid4()
    content = "Test themed content"
    theme_context = {
        "style": "dark fantasy",
        "tone": "gritty",
        "details": "Gothic horror elements",
    }
    content_type = "narrative"

    # Validate theme
    result = await validation_service.validate_theme_consistency(
        content=content,
        theme_context=theme_context,
        content_type=content_type,
        content_id=content_id,
    )

    # Verify result
    assert isinstance(result, ContentValidation)
    assert result.is_valid is True
    assert result.score == 0.85
    assert len(result.issues) == 1
    assert len(result.suggestions) == 2

    # Verify rate limit check
    mock_rate_limiter.check_text_limit.assert_called_once_with("validation")

    # Verify OpenAI call
    mock_openai.generate_text.assert_called_once()
    call_args = mock_openai.generate_text.call_args
    assert "Theme Context" in call_args[1]["prompt"]
    assert "style consistency" in call_args[1]["prompt"].lower()
    assert call_args[1]["temperature"] == 0.3


@pytest.mark.asyncio
async def test_validate_image_quality(
    validation_service, mock_openai, mock_rate_limiter, mock_validation_response
):
    """Test image quality validation."""
    # Set up mock response
    mock_openai.generate_text.return_value = mock_validation_response

    # Create test data
    image_id = uuid.uuid4()
    image_data = "base64_image_data"
    prompt = "Test prompt"
    parameters = {
        "style": "fantasy art",
        "quality": "high",
    }
    image_type = "character_portrait"

    # Validate image
    result = await validation_service.validate_image_quality(
        image_data=image_data,
        prompt=prompt,
        parameters=parameters,
        image_type=image_type,
        image_id=image_id,
    )

    # Verify result
    assert isinstance(result, ContentValidation)
    assert result.is_valid is True
    assert result.score == 0.85
    assert len(result.issues) == 1
    assert len(result.suggestions) == 2

    # Verify rate limit check
    mock_rate_limiter.check_text_limit.assert_called_once_with("validation")

    # Verify OpenAI call
    mock_openai.generate_text.assert_called_once()
    call_args = mock_openai.generate_text.call_args
    assert "image" in call_args[1]["prompt"].lower()
    assert "visual quality" in call_args[1]["prompt"].lower()
    assert call_args[1]["temperature"] == 0.3


@pytest.mark.asyncio
async def test_validation_error_handling(validation_service, mock_openai, mock_rate_limiter):
    """Test validation error handling."""
    # Make OpenAI service raise error
    mock_openai.generate_text.side_effect = Exception("API error")

    # Create test data
    content_id = uuid.uuid4()
    content = "Test content"
    content_type = "backstory"
    parameters = {"theme": "fantasy"}

    # Verify error handling
    with pytest.raises(ValidationError) as exc_info:
        await validation_service.validate_character_content(
            content=content,
            content_type=content_type,
            character_id=content_id,
            parameters=parameters,
        )

    assert "Content validation failed" in str(exc_info.value)
    assert "API error" in str(exc_info.value)

    # Verify rate limit check was called
    mock_rate_limiter.check_text_limit.assert_called_once_with("validation")
