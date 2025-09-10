"""
Portrait Generation Tests

Tests for the portrait generation functionality of the Image Service.
"""

import pytest
from uuid import UUID
from unittest.mock import MagicMock
from image_service.models.request import PortraitRequest
from image_service.models.image import Image
from image_service.core.exceptions import ImageGenerationError

@pytest.mark.asyncio
async def test_portrait_generation_basic(
    image_service,
    mock_getimg_api,
    test_character_data
):
    """Test basic portrait generation for a character"""
    # Prepare test data
    character_id = test_character_data["id"]
    request = PortraitRequest(
        character_id=character_id,
        style="realistic",
        description="A human fighter with plate armor",
        prompt_details={
            "gender": "male",
            "age": "middle-aged",
            "distinguishing_features": ["scar on left cheek", "weathered face"]
        }
    )
    
    # Configure mock response
    async def mock_generate(*args, **kwargs):
        return {
            "image_data": b"fake_image_bytes",
            "metadata": {
                "width": 512,
                "height": 512,
                "format": "PNG"
            }
        }
    mock_getimg_api.generate_image = MagicMock(side_effect=mock_generate)

    # Execute test
    result = await image_service.generate_portrait(request)

    # Verify result
    assert isinstance(result, Image)
    assert result.character_id == character_id
    assert result.width == 512
    assert result.height == 512
    assert result.format == "PNG"
    assert result.data == b"fake_image_bytes"

    # Verify API was called with correct parameters
    mock_getimg_api.generate_image.assert_called_once_with(
        style="realistic",
        description="A human fighter with plate armor",
        additional_details={
            "gender": "male",
            "age": "middle-aged",
            "distinguishing_features": ["scar on left cheek", "weathered face"]
        }
    )

@pytest.mark.asyncio
async def test_portrait_generation_api_error(
    image_service,
    mock_getimg_api
):
    """Test handling of API errors during portrait generation"""
    # Configure mock to raise an error
    mock_getimg_api.generate_image.side_effect = Exception("API Error")

    request = PortraitRequest(
        character_id=UUID("12345678-1234-5678-1234-567812345678"),
        style="realistic",
        description="A failed request"
    )

    # Verify error handling
    with pytest.raises(ImageGenerationError) as exc_info:
        await image_service.generate_portrait(request)
    
    assert str(exc_info.value) == "Failed to generate portrait: API Error"
