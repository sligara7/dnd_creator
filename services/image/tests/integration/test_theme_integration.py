"""Integration tests for theme system."""

import pytest
import asyncio
from uuid import uuid4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_theme_application(
    theme_client,
    storage_client,
    test_theme_data,
    test_image_data,
):
    """Test theme application to images."""
    # Create theme and verify
    theme_id = test_theme_data["id"]
    await theme_client.create_theme(test_theme_data)
    
    # Create test image with theme
    image_id = str(uuid4())
    image_data = {
        **test_image_data["portrait"],
        "id": image_id,
        "theme_id": theme_id,
    }
    
    await storage_client.store_image(image_id, image_data)
    
    # Verify theme attributes are applied
    stored_image = await storage_client.get_image(image_id)
    assert stored_image["theme_id"] == theme_id
    assert "theme_attributes" in stored_image
    assert stored_image["theme_attributes"]["style"] == test_theme_data["style_attributes"]
    
    # Clean up
    await theme_client.delete_theme(theme_id)
    await storage_client.delete_image(image_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_theme_inheritance(
    theme_client,
    storage_client,
    test_theme_data,
    test_image_data,
):
    """Test theme inheritance and override behavior."""
    # Create parent theme
    parent_theme = {
        **test_theme_data,
        "id": "parent-theme",
        "name": "Parent Theme",
    }
    await theme_client.create_theme(parent_theme)
    
    # Create child theme inheriting from parent
    child_theme = {
        "id": "child-theme",
        "name": "Child Theme",
        "parent_id": "parent-theme",
        "style_attributes": {
            # Override some attributes
            "lighting": "soft",
            # Inherit other attributes
        },
    }
    await theme_client.create_theme(child_theme)
    
    # Create image with child theme
    image_id = str(uuid4())
    image_data = {
        **test_image_data["portrait"],
        "id": image_id,
        "theme_id": "child-theme",
    }
    
    await storage_client.store_image(image_id, image_data)
    
    # Verify theme inheritance
    stored_image = await storage_client.get_image(image_id)
    theme_attrs = stored_image["theme_attributes"]
    
    # Should have child's overridden attributes
    assert theme_attrs["style"]["lighting"] == "soft"
    
    # Should inherit parent's non-overridden attributes
    for key, value in parent_theme["style_attributes"].items():
        if key != "lighting":  # Skip overridden attribute
            assert theme_attrs["style"][key] == value
    
    # Clean up
    await theme_client.delete_theme("child-theme")
    await theme_client.delete_theme("parent-theme")
    await storage_client.delete_image(image_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_theme_bulk_update(
    theme_client,
    storage_client,
    test_theme_data,
    test_image_data,
):
    """Test bulk theme updates across multiple images."""
    theme_id = test_theme_data["id"]
    await theme_client.create_theme(test_theme_data)
    
    # Create multiple images with the same theme
    image_ids = []
    for _ in range(3):
        image_id = str(uuid4())
        image_data = {
            **test_image_data["portrait"],
            "id": image_id,
            "theme_id": theme_id,
        }
        await storage_client.store_image(image_id, image_data)
        image_ids.append(image_id)
    
    # Update theme
    updated_theme = {
        **test_theme_data,
        "style_attributes": {
            "lighting": "dramatic",
            "mood": "intense",
        },
    }
    await theme_client.update_theme(theme_id, updated_theme)
    
    # Wait briefly for updates to propagate
    await asyncio.sleep(1)
    
    # Verify all images were updated
    for image_id in image_ids:
        image = await storage_client.get_image(image_id)
        assert image["theme_attributes"]["style"]["lighting"] == "dramatic"
        assert image["theme_attributes"]["style"]["mood"] == "intense"
        assert "theme_updated_at" in image
    
    # Clean up
    await theme_client.delete_theme(theme_id)
    await storage_client.delete_images_bulk(image_ids)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_theme_validation(
    theme_client,
    storage_client,
    test_theme_data,
    test_image_data,
):
    """Test theme validation rules and constraints."""
    # Attempt to create invalid theme
    invalid_theme = {
        **test_theme_data,
        "style_attributes": {
            "invalid_attribute": "not_allowed",
            "lighting": "invalid_value",
        },
    }
    
    with pytest.raises(Exception) as exc_info:
        await theme_client.create_theme(invalid_theme)
    assert "validation error" in str(exc_info.value).lower()
    
    # Create valid theme
    theme_id = test_theme_data["id"]
    await theme_client.create_theme(test_theme_data)
    
    # Attempt to create image with invalid theme overrides
    image_id = str(uuid4())
    invalid_image = {
        **test_image_data["portrait"],
        "id": image_id,
        "theme_id": theme_id,
        "theme_overrides": {
            "invalid_override": "not_allowed",
        },
    }
    
    with pytest.raises(Exception) as exc_info:
        await storage_client.store_image(image_id, invalid_image)
    assert "theme validation" in str(exc_info.value).lower()
    
    # Clean up
    await theme_client.delete_theme(theme_id)