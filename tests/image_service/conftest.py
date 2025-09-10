"""
Image Service Test Fixtures

This module provides test fixtures specific to the Image Service.
"""

import pytest
import base64
from unittest.mock import MagicMock, patch
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import TestSessionManager, Base
from image_service.repositories.image_repository import ImageRepository
from image_service.services.image_service import ImageService
from image_service.core.image_generator import ImageGenerator
from image_service.core.map_generator import MapGenerator
from image_service.repositories.map_repository import MapRepository
from tests.image_service.mocks.mock_storage_repository_fixed2 import MockStorageRepository
from image_service.core.portrait_generator import PortraitGenerator

@pytest.fixture
async def db_manager() -> AsyncGenerator[TestSessionManager, None]:
    """Provide test database manager"""
    manager = TestSessionManager()
    await manager.init()

    try:
        # Create tables with explicit error handling
        async with manager.engine.begin() as conn:
            # First drop all tables to ensure clean state
            await conn.run_sync(Base.metadata.drop_all)
            # Then create all tables from current models
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating test database tables: {e}")
        raise

    yield manager
    await manager.cleanup()

@pytest.fixture
async def test_db(db_manager):
    """Provide test database session with transaction isolation"""
    async with db_manager.begin_nested() as session:
        yield session

@pytest.fixture
def mock_getimg_api():
    """Mock GetImg.AI API client"""
    with patch("image_service.core.getimg.GetImgClient") as mock:
        # Configure async return helper
        async def _async_return(value=None):
            return value
        
        # Configure async generate_image
        async def _generate_image(**kwargs):
            # Return a realistic mock response structure expected by callers
            return {
                "url": "http://mock.api/generated.png",
                "data": base64.b64encode(b"test").decode(),
                "metadata": {
                    "width": kwargs.get("width", 512),
                    "height": kwargs.get("height", 512),
                    "style": kwargs.get("style", "realistic"),
                    "prompt": kwargs.get("prompt", "")
                }
            }
        mock.generate_image = _generate_image

        # Configure async enhance_image
        async def _enhance_image(image_data: bytes):
            return image_data
        mock.enhance_image = _enhance_image

        yield mock

@pytest.fixture
def image_generator(mock_getimg_api):
    """Provide configured image generator"""
    return ImageGenerator(api_client=mock_getimg_api)

@pytest.fixture
def image_repository(test_db):
    """Provide image repository instance"""
    return ImageRepository(db=test_db)

@pytest.fixture
async def storage_repository() -> MockStorageRepository:
    """Create mock storage repository."""
    repository = MockStorageRepository()
    await repository.init()
    yield repository
    await repository.cleanup()

@pytest.fixture
def portrait_generator(mock_getimg_api):
    """Provide configured portrait generator"""
    return PortraitGenerator(api_client=mock_getimg_api)

@pytest.fixture
def image_service(
    image_repository,
    image_generator,
    mock_getimg_api,
    test_db,
    portrait_generator
):
    """Provide configured image service instance with map generation."""
    return ImageService(
        repository=image_repository,
        generator=image_generator,
        map_repository=MapRepository(db=test_db),
        map_generator=MapGenerator(api_client=mock_getimg_api),
        portrait_generator=portrait_generator
    )
