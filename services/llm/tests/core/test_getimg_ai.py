"""Tests for GetImg.AI service integration."""
import base64
from io import BytesIO
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from PIL import Image

from llm_service.core.config import Settings
from llm_service.core.exceptions import ImageGenerationError
from llm_service.services.getimg_ai import GetImgAIClient
from llm_service.core.cache import RateLimiter
from llm_service.schemas.image import (
    ImageModelConfig,
    ImageParameters,
    ImageSize,
    ImageToImageRequest,
    TextToImageRequest,
)


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        GETIMG_API_KEY="test-key",
        GETIMG_MAX_RETRIES=2,
        GETIMG_TIMEOUT=30,
    )


@pytest.fixture
def mock_rate_limiter():
    """Create mock rate limiter."""
    rate_limiter = MagicMock(spec=RateLimiter)
    rate_limiter.check_image_limit = AsyncMock()
    return rate_limiter


@pytest.fixture
def mock_client():
    """Create mock HTTPX client."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock(spec=AsyncClient)
        mock.return_value = client
        yield client


@pytest.fixture
def getimg_service(settings, mock_rate_limiter, mock_client):
    """Create GetImg.AI service instance."""
    service = GetImgAIClient(settings, mock_rate_limiter)
    service.client = mock_client
    return service


@pytest.fixture
def mock_image():
    """Create a mock image for testing."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@pytest.mark.asyncio
async def test_generate_image_success(getimg_service, mock_client, mock_rate_limiter):
    """Test successful image generation."""
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "image": "base64_image_data",
    }
    mock_client.post.return_value = mock_response

    # Create request
    request = TextToImageRequest(
        prompt="Test prompt",
        model=ImageModelConfig(
            name="stable-diffusion-v1-5",
            steps=30,
            cfg_scale=7.5,
        ),
        size=ImageSize(width=512, height=512),
        parameters=ImageParameters(
            negative_prompt="bad quality",
            style_preset="anime",
        ),
    )

    # Generate image
    image_data = await getimg_service.generate_image(request)

    # Verify response
    assert image_data == "base64_image_data"

    # Verify rate limit check
    mock_rate_limiter.check_image_limit.assert_called_once_with("text_to_image")

    # Verify request
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "/text-to-image"
    assert call_args[1]["json"]["prompt"] == "Test prompt"
    assert call_args[1]["json"]["steps"] == 30
    assert call_args[1]["json"]["cfg_scale"] == 7.5
    assert call_args[1]["json"]["negative_prompt"] == "bad quality"
    assert call_args[1]["json"]["style_preset"] == "anime"


@pytest.mark.asyncio
async def test_transform_image_success(getimg_service, mock_client, mock_rate_limiter, mock_image):
    """Test successful image transformation."""
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "image": "transformed_base64_data",
    }
    mock_client.post.return_value = mock_response

    # Create request
    request = ImageToImageRequest(
        source_image=mock_image,
        prompt="Transform test",
        model=ImageModelConfig(
            name="stable-diffusion-v1-5",
            steps=30,
            cfg_scale=7.5,
        ),
        parameters=ImageParameters(
            style_preset="digital-art",
        ),
        strength=0.8,
    )

    # Transform image
    image_data = await getimg_service.transform_image(request)

    # Verify response
    assert image_data == "transformed_base64_data"

    # Verify rate limit check
    mock_rate_limiter.check_image_limit.assert_called_once_with("image_to_image")

    # Verify request
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "/image-to-image"
    assert call_args[1]["json"]["image"] == mock_image
    assert call_args[1]["json"]["prompt"] == "Transform test"
    assert call_args[1]["json"]["strength"] == 0.8


@pytest.mark.asyncio
async def test_enhance_faces_success(getimg_service, mock_client, mock_image):
    """Test successful face enhancement."""
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "image": "enhanced_base64_data",
    }
    mock_client.post.return_value = mock_response

    # Enhance faces
    image_data = await getimg_service.enhance_faces(mock_image)

    # Verify response
    assert image_data == "enhanced_base64_data"

    # Verify request
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "/face-enhance"
    assert call_args[1]["json"]["image"] == mock_image


@pytest.mark.asyncio
async def test_api_error_handling(getimg_service, mock_client, mock_rate_limiter):
    """Test handling of API errors."""
    # Prepare mock error response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": "Test error",
    }
    mock_client.post.return_value = mock_response

    # Create request
    request = TextToImageRequest(
        prompt="Test prompt",
        model=ImageModelConfig(name="stable-diffusion-v1-5"),
        size=ImageSize(width=512, height=512),
        parameters=ImageParameters(),
    )

    # Verify error handling
    with pytest.raises(ImageGenerationError) as exc_info:
        await getimg_service.generate_image(request)

    assert "API error" in str(exc_info.value)
    assert mock_client.post.call_count == getimg_service.settings.GETIMG_MAX_RETRIES


@pytest.mark.asyncio
async def test_rate_limit_handling(getimg_service, mock_client, mock_rate_limiter):
    """Test handling of rate limit errors."""
    # Make rate limiter raise error
    mock_rate_limiter.check_image_limit.side_effect = Exception("Rate limit exceeded")

    # Create request
    request = TextToImageRequest(
        prompt="Test prompt",
        model=ImageModelConfig(name="stable-diffusion-v1-5"),
        size=ImageSize(width=512, height=512),
        parameters=ImageParameters(),
    )

    # Verify rate limit handling
    with pytest.raises(Exception) as exc_info:
        await getimg_service.generate_image(request)

    assert "Rate limit exceeded" in str(exc_info.value)
    mock_client.post.assert_not_called()


def test_invalid_base64_image(getimg_service):
    """Test handling of invalid base64 image data."""
    with pytest.raises(ValueError) as exc_info:
        getimg_service._validate_base64_image("invalid_data")

    assert "Invalid base64 image data" in str(exc_info.value)


def test_create_thumbnail(getimg_service, mock_image):
    """Test thumbnail creation."""
    # Create thumbnail
    thumbnail = getimg_service.create_thumbnail(mock_image)

    # Verify thumbnail is valid base64
    try:
        img_data = base64.b64decode(thumbnail)
        img = Image.open(BytesIO(img_data))
        assert img.size == (256, 256)  # Default thumbnail size
        assert img.mode == "RGB"
    except Exception as e:
        pytest.fail(f"Invalid thumbnail generated: {e}")
