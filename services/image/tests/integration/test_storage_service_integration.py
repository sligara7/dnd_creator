"""Integration tests for storage service client."""

import pytest
from uuid import UUID

from image_service.domain.models import Image, ImageType, ImageSubtype
from image_service.integration.storage_service import StorageServiceClient


@pytest.fixture
async def storage_client() -> StorageServiceClient:
    """Create storage client for testing."""
    client = StorageServiceClient()
    await client.connect()
    yield client
    await client.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_get_image(storage_client: StorageServiceClient):
    """Test creating and retrieving an image."""
    # Create image
    created = await storage_client.create_image(
        type=ImageType.PORTRAIT,
        subtype=ImageSubtype.CHARACTER,
        name="Test Portrait",
        url="https://example.com/test.png",
        format="png",
        width=512,
        height=512,
        size=1024,
        theme="fantasy",
    )

    assert isinstance(created, Image)
    assert created.type == ImageType.PORTRAIT
    assert created.subtype == ImageSubtype.CHARACTER
    assert created.content.url == "https://example.com/test.png"
    assert created.metadata.theme == "fantasy"

    # Get image
    retrieved = await storage_client.get_image(created.id)
    assert isinstance(retrieved, Image)
    assert retrieved.id == created.id
    assert retrieved.type == created.type
    assert retrieved.metadata.theme == created.metadata.theme


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_images(storage_client: StorageServiceClient):
    """Test listing images with filters."""
    # Create test images
    for _ in range(3):
        await storage_client.create_image(
            type=ImageType.PORTRAIT,
            subtype=ImageSubtype.CHARACTER,
            name="Test Portrait",
            url="https://example.com/test.png",
            format="png",
            width=512,
            height=512,
            size=1024,
            theme="fantasy",
        )

    # List images with filter
    images = await storage_client.list_images(
        type=ImageType.PORTRAIT,
        theme="fantasy",
        skip=0,
        limit=10,
    )

    assert isinstance(images, list)
    assert len(images) > 0
    assert all(isinstance(img, Image) for img in images)
    assert all(img.type == ImageType.PORTRAIT for img in images)
    assert all(img.metadata.theme == "fantasy" for img in images)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_image(storage_client: StorageServiceClient):
    """Test deleting an image."""
    # Create image
    created = await storage_client.create_image(
        type=ImageType.PORTRAIT,
        subtype=ImageSubtype.CHARACTER,
        name="Test Portrait",
        url="https://example.com/test.png",
        format="png",
        width=512,
        height=512,
        size=1024,
        theme="fantasy",
    )

    # Delete image
    await storage_client.delete_image(created.id)

    # Verify deletion
    with pytest.raises(Exception):
        await storage_client.get_image(created.id)