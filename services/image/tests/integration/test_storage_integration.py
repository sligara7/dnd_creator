"""Integration tests for storage service interaction."""

import pytest
from uuid import uuid4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_image_storage_lifecycle(
    storage_client,
    test_image_data,
):
    """Test complete lifecycle of image storage operations."""
    # Create test image data
    image_id = str(uuid4())
    image_data = test_image_data["portrait"]
    image_data["id"] = image_id

    # Store image
    await storage_client.store_image(image_id, image_data)

    # Verify retrieval
    stored_image = await storage_client.get_image(image_id)
    assert stored_image["id"] == image_id
    assert stored_image["theme_id"] == image_data["theme_id"]

    # Update metadata
    updated_data = {**image_data, "style": {"lighting": "bright"}}
    await storage_client.update_image(image_id, updated_data)

    # Verify update
    updated_image = await storage_client.get_image(image_id)
    assert updated_image["style"]["lighting"] == "bright"

    # Delete image
    await storage_client.delete_image(image_id)

    # Verify deletion
    with pytest.raises(Exception):
        await storage_client.get_image(image_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_bulk_storage_operations(
    storage_client,
    test_image_data,
):
    """Test bulk image storage operations."""
    # Create multiple test images
    image_ids = [str(uuid4()) for _ in range(3)]
    images = []
    for idx, image_id in enumerate(image_ids):
        image_data = {
            **test_image_data["portrait"],
            "id": image_id,
            "character_id": f"test-char-{idx}",
        }
        images.append(image_data)

    # Store images in bulk
    await storage_client.store_images_bulk(images)

    # Verify bulk retrieval
    stored_images = await storage_client.get_images_bulk(image_ids)
    assert len(stored_images) == len(image_ids)
    assert all(img["id"] in image_ids for img in stored_images)

    # Clean up
    await storage_client.delete_images_bulk(image_ids)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_image_version_control(
    storage_client,
    test_image_data,
):
    """Test image version control operations."""
    # Create initial version
    image_id = str(uuid4())
    initial_data = test_image_data["portrait"]
    initial_data["id"] = image_id
    
    await storage_client.store_image(image_id, initial_data)
    
    # Create new version
    updated_data = {
        **initial_data,
        "style": {"lighting": "bright", "background": "forest"},
    }
    await storage_client.create_image_version(image_id, updated_data)
    
    # Get version history
    versions = await storage_client.get_image_versions(image_id)
    assert len(versions) == 2
    
    # Revert to original version
    await storage_client.revert_image_version(image_id, versions[0]["version_id"])
    
    # Verify reversion
    current = await storage_client.get_image(image_id)
    assert current["style"]["lighting"] == initial_data["style"]["lighting"]
    
    # Clean up
    await storage_client.delete_image(image_id)