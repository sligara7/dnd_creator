"""Tests for image storage API endpoints."""

import json
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from storage.models.image_storage import (
    Image,
    ImageOverlay,
    MapGrid,
    GenerationTask,
    Theme,
    ThemeVariation,
    StylePreset,
    ThemeElement,
)


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application."""
    from storage.main import app
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_image(db_session) -> Image:
    """Create test image."""
    image = Image(
        type="portrait",
        subtype="character",
        name="Test Image",
        description="Test description",
        url="https://test.com/image.png",
        format="png",
        width=500,
        height=500,
        size=1024,
        theme="fantasy",
        style_data={"style": "realistic"},
        generation_params={"prompt": "test prompt"},
    )
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)
    return image


@pytest.fixture
async def test_overlay(db_session, test_image) -> ImageOverlay:
    """Create test overlay."""
    overlay = ImageOverlay(
        image_id=test_image.id,
        type="grid",
        name="Test Overlay",
        description="Test overlay description",
        data={"grid": "data"},
        style={"color": "red"},
    )
    db_session.add(overlay)
    await db_session.commit()
    await db_session.refresh(overlay)
    return overlay


@pytest.fixture
async def test_grid(db_session, test_image) -> MapGrid:
    """Create test grid."""
    grid = MapGrid(
        image_id=test_image.id,
        enabled=True,
        size=50,
        color="#000000",
        opacity=0.5,
    )
    db_session.add(grid)
    await db_session.commit()
    await db_session.refresh(grid)
    return grid


@pytest.fixture
async def test_task(db_session) -> GenerationTask:
    """Create test task."""
    task = GenerationTask(
        type="image_generation",
        status="pending",
        priority=1,
        params={"prompt": "test prompt"},
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def test_theme(db_session) -> Theme:
    """Create test theme."""
    theme = Theme(
        name="test_theme",
        display_name="Test Theme",
        description="Test theme description",
        config={"key": "value"},
        variables={"var": "value"},
        prompts={"prompt": "value"},
        styles={"style": "value"},
    )
    db_session.add(theme)
    await db_session.commit()
    await db_session.refresh(theme)
    return theme


@pytest.mark.asyncio
async def test_create_image(client: AsyncClient):
    """Test create image endpoint."""
    image_data = {
        "type": "portrait",
        "subtype": "character",
        "name": "Test Image",
        "description": "Test description",
        "url": "https://test.com/image.png",
        "format": "png",
        "width": 500,
        "height": 500,
        "size": 1024,
        "theme": "fantasy",
        "style_data": {"style": "realistic"},
        "generation_params": {"prompt": "test prompt"},
    }
    response = await client.post("/api/v2/image-storage/images", json=image_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == image_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_image(client: AsyncClient, test_image: Image):
    """Test get image endpoint."""
    response = await client.get(f"/api/v2/image-storage/images/{test_image.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_image.id)
    assert data["name"] == test_image.name


@pytest.mark.asyncio
async def test_list_images(client: AsyncClient, test_image: Image):
    """Test list images endpoint."""
    response = await client.get("/api/v2/image-storage/images")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_image.id)


@pytest.mark.asyncio
async def test_update_image(client: AsyncClient, test_image: Image):
    """Test update image endpoint."""
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
    }
    response = await client.put(
        f"/api/v2/image-storage/images/{test_image.id}",
        json=update_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_delete_image(client: AsyncClient, test_image: Image):
    """Test delete image endpoint."""
    response = await client.delete(f"/api/v2/image-storage/images/{test_image.id}")
    assert response.status_code == 200

    # Verify deletion
    response = await client.get(f"/api/v2/image-storage/images/{test_image.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_overlay(client: AsyncClient, test_image: Image):
    """Test create overlay endpoint."""
    overlay_data = {
        "image_id": str(test_image.id),
        "type": "grid",
        "name": "Test Overlay",
        "description": "Test description",
        "data": {"grid": "data"},
        "style": {"color": "red"},
    }
    response = await client.post("/api/v2/image-storage/overlays", json=overlay_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == overlay_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_overlay(client: AsyncClient, test_overlay: ImageOverlay):
    """Test get overlay endpoint."""
    response = await client.get(
        f"/api/v2/image-storage/overlays/{test_overlay.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_overlay.id)


@pytest.mark.asyncio
async def test_list_overlays(client: AsyncClient, test_image: Image, test_overlay: ImageOverlay):
    """Test list overlays endpoint."""
    response = await client.get(
        f"/api/v2/image-storage/images/{test_image.id}/overlays"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_overlay.id)


@pytest.mark.asyncio
async def test_create_grid(client: AsyncClient, test_image: Image):
    """Test create grid endpoint."""
    grid_data = {
        "image_id": str(test_image.id),
        "enabled": True,
        "size": 50,
        "color": "#000000",
        "opacity": 0.5,
    }
    response = await client.post("/api/v2/image-storage/grids", json=grid_data)
    assert response.status_code == 200
    data = response.json()
    assert data["size"] == grid_data["size"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_grid(client: AsyncClient, test_grid: MapGrid):
    """Test get grid endpoint."""
    response = await client.get(f"/api/v2/image-storage/grids/{test_grid.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_grid.id)


@pytest.mark.asyncio
async def test_get_image_grid(client: AsyncClient, test_image: Image, test_grid: MapGrid):
    """Test get image grid endpoint."""
    response = await client.get(
        f"/api/v2/image-storage/images/{test_image.id}/grid"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_grid.id)


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test create task endpoint."""
    task_data = {
        "type": "image_generation",
        "status": "pending",
        "priority": 1,
        "params": {"prompt": "test prompt"},
    }
    response = await client.post("/api/v2/image-storage/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == task_data["type"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, test_task: GenerationTask):
    """Test get task endpoint."""
    response = await client.get(f"/api/v2/image-storage/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_task.id)


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, test_task: GenerationTask):
    """Test list tasks endpoint."""
    response = await client.get("/api/v2/image-storage/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_task.id)


@pytest.mark.asyncio
async def test_create_theme(client: AsyncClient):
    """Test create theme endpoint."""
    theme_data = {
        "name": "test_theme",
        "display_name": "Test Theme",
        "description": "Test description",
        "config": {"key": "value"},
        "variables": {"var": "value"},
        "prompts": {"prompt": "value"},
        "styles": {"style": "value"},
    }
    response = await client.post("/api/v2/image-storage/themes", json=theme_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == theme_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_theme(client: AsyncClient, test_theme: Theme):
    """Test get theme endpoint."""
    response = await client.get(f"/api/v2/image-storage/themes/{test_theme.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_theme.id)


@pytest.mark.asyncio
async def test_list_themes(client: AsyncClient, test_theme: Theme):
    """Test list themes endpoint."""
    response = await client.get("/api/v2/image-storage/themes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_theme.id)


@pytest.mark.asyncio
async def test_create_theme_variation(client: AsyncClient, test_theme: Theme):
    """Test create theme variation endpoint."""
    variation_data = {
        "name": "test_variation",
        "display_name": "Test Variation",
        "description": "Test description",
        "config_override": {"key": "override"},
        "variable_override": {"var": "override"},
    }
    response = await client.post(
        f"/api/v2/image-storage/themes/{test_theme.id}/variations",
        json=variation_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == variation_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_variation(client: AsyncClient, test_theme: Theme):
    """Test get variation endpoint."""
    # Create variation first
    variation = ThemeVariation(
        theme_id=test_theme.id,
        name="test_variation",
        display_name="Test Variation",
        description="Test description",
        config_override={"key": "override"},
        variable_override={"var": "override"},
    )
    test_theme.variations.append(variation)
    response = await client.get(f"/api/v2/image-storage/variations/{variation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(variation.id)


@pytest.mark.asyncio
async def test_create_preset(client: AsyncClient):
    """Test create preset endpoint."""
    preset_data = {
        "name": "test_preset",
        "display_name": "Test Preset",
        "description": "Test description",
        "category": "portraits",
        "config": {"key": "value"},
        "prompts": {"prompt": "value"},
        "compatibility": ["theme1", "theme2"],
    }
    response = await client.post("/api/v2/image-storage/presets", json=preset_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == preset_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_preset(client: AsyncClient, db_session):
    """Test get preset endpoint."""
    # Create preset first
    preset = StylePreset(
        name="test_preset",
        display_name="Test Preset",
        description="Test description",
        category="portraits",
        config={"key": "value"},
        prompts={"prompt": "value"},
        compatibility=["theme1", "theme2"],
    )
    db_session.add(preset)
    await db_session.commit()
    await db_session.refresh(preset)

    response = await client.get(f"/api/v2/image-storage/presets/{preset.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(preset.id)


@pytest.mark.asyncio
async def test_list_presets(client: AsyncClient, db_session):
    """Test list presets endpoint."""
    # Create preset first
    preset = StylePreset(
        name="test_preset",
        display_name="Test Preset",
        description="Test description",
        category="portraits",
        config={"key": "value"},
        prompts={"prompt": "value"},
        compatibility=["theme1", "theme2"],
    )
    db_session.add(preset)
    await db_session.commit()
    await db_session.refresh(preset)

    response = await client.get("/api/v2/image-storage/presets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(preset.id)


@pytest.mark.asyncio
async def test_create_element(client: AsyncClient):
    """Test create element endpoint."""
    element_data = {
        "category": "architecture",
        "name": "test_element",
        "display_name": "Test Element",
        "description": "Test description",
        "config": {"key": "value"},
        "prompts": {"prompt": "value"},
        "compatibility": ["theme1", "theme2"],
    }
    response = await client.post("/api/v2/image-storage/elements", json=element_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == element_data["name"]
    assert UUID(data["id"])


@pytest.mark.asyncio
async def test_get_element(client: AsyncClient, db_session):
    """Test get element endpoint."""
    # Create element first
    element = ThemeElement(
        category="architecture",
        name="test_element",
        display_name="Test Element",
        description="Test description",
        config={"key": "value"},
        prompts={"prompt": "value"},
        compatibility=["theme1", "theme2"],
    )
    db_session.add(element)
    await db_session.commit()
    await db_session.refresh(element)

    response = await client.get(f"/api/v2/image-storage/elements/{element.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(element.id)


@pytest.mark.asyncio
async def test_list_elements(client: AsyncClient, db_session):
    """Test list elements endpoint."""
    # Create element first
    element = ThemeElement(
        category="architecture",
        name="test_element",
        display_name="Test Element",
        description="Test description",
        config={"key": "value"},
        prompts={"prompt": "value"},
        compatibility=["theme1", "theme2"],
    )
    db_session.add(element)
    await db_session.commit()
    await db_session.refresh(element)

    response = await client.get("/api/v2/image-storage/elements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(element.id)