"""Tests for image storage repositories."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

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
from storage.repositories.image_storage import (
    ImageRepository,
    ImageOverlayRepository,
    MapGridRepository,
    GenerationTaskRepository,
    ThemeRepository,
    ThemeVariationRepository,
    StylePresetRepository,
    ThemeElementRepository,
)


@pytest.fixture
def image_data():
    """Create test image data."""
    return {
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


@pytest.fixture
def overlay_data():
    """Create test overlay data."""
    return {
        "type": "grid",
        "name": "Test Overlay",
        "description": "Test overlay description",
        "data": {"grid": "data"},
        "style": {"color": "red"},
    }


@pytest.fixture
def grid_data():
    """Create test grid data."""
    return {
        "enabled": True,
        "size": 50,
        "color": "#000000",
        "opacity": 0.5,
    }


@pytest.fixture
def task_data():
    """Create test task data."""
    return {
        "type": "image_generation",
        "status": "pending",
        "priority": 1,
        "params": {"prompt": "test prompt"},
    }


@pytest.fixture
def theme_data():
    """Create test theme data."""
    return {
        "name": "test_theme",
        "display_name": "Test Theme",
        "description": "Test theme description",
        "config": {"key": "value"},
        "variables": {"var": "value"},
        "prompts": {"prompt": "value"},
        "styles": {"style": "value"},
    }


@pytest.fixture
def variation_data():
    """Create test variation data."""
    return {
        "name": "test_variation",
        "display_name": "Test Variation",
        "description": "Test variation description",
        "config_override": {"key": "override"},
        "variable_override": {"var": "override"},
    }


@pytest.fixture
def preset_data():
    """Create test preset data."""
    return {
        "name": "test_preset",
        "display_name": "Test Preset",
        "description": "Test preset description",
        "category": "portraits",
        "config": {"key": "value"},
        "prompts": {"prompt": "value"},
        "compatibility": ["theme1", "theme2"],
    }


@pytest.fixture
def element_data():
    """Create test element data."""
    return {
        "category": "architecture",
        "name": "test_element",
        "display_name": "Test Element",
        "description": "Test element description",
        "config": {"key": "value"},
        "prompts": {"prompt": "value"},
        "compatibility": ["theme1", "theme2"],
    }


@pytest.mark.asyncio
async def test_image_repository(db_session, image_data):
    """Test image repository operations."""
    repo = ImageRepository(db_session)

    # Create image
    image = Image(**image_data)
    created_image = await repo.create(image)
    assert created_image.id is not None
    assert created_image.name == image_data["name"]

    # Get image
    fetched_image = await repo.get(created_image.id)
    assert fetched_image is not None
    assert fetched_image.id == created_image.id
    assert fetched_image.name == image_data["name"]

    # List images
    images = await repo.list(type=image_data["type"])
    assert len(images) == 1
    assert images[0].id == created_image.id

    # Update image
    created_image.name = "Updated Name"
    updated_image = await repo.update(created_image)
    assert updated_image.name == "Updated Name"

    # Delete image
    await repo.delete(created_image)
    deleted_image = await repo.get(created_image.id)
    assert deleted_image is None


@pytest.mark.asyncio
async def test_overlay_repository(db_session, image_data, overlay_data):
    """Test overlay repository operations."""
    # Create image first
    image = Image(**image_data)
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)

    repo = ImageOverlayRepository(db_session)

    # Create overlay
    overlay = ImageOverlay(image_id=image.id, **overlay_data)
    created_overlay = await repo.create(overlay)
    assert created_overlay.id is not None
    assert created_overlay.name == overlay_data["name"]

    # Get overlay
    fetched_overlay = await repo.get(created_overlay.id)
    assert fetched_overlay is not None
    assert fetched_overlay.id == created_overlay.id

    # List overlays
    overlays = await repo.list_by_image(image.id)
    assert len(overlays) == 1
    assert overlays[0].id == created_overlay.id

    # Update overlay
    created_overlay.name = "Updated Name"
    updated_overlay = await repo.update(created_overlay)
    assert updated_overlay.name == "Updated Name"

    # Delete overlay
    await repo.delete(created_overlay)
    deleted_overlay = await repo.get(created_overlay.id)
    assert deleted_overlay is None


@pytest.mark.asyncio
async def test_grid_repository(db_session, image_data, grid_data):
    """Test grid repository operations."""
    # Create image first
    image = Image(**image_data)
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)

    repo = MapGridRepository(db_session)

    # Create grid
    grid = MapGrid(image_id=image.id, **grid_data)
    created_grid = await repo.create(grid)
    assert created_grid.id is not None
    assert created_grid.size == grid_data["size"]

    # Get grid
    fetched_grid = await repo.get(created_grid.id)
    assert fetched_grid is not None
    assert fetched_grid.id == created_grid.id

    # Get by image
    image_grid = await repo.get_by_image(image.id)
    assert image_grid is not None
    assert image_grid.id == created_grid.id

    # Update grid
    created_grid.size = 75
    updated_grid = await repo.update(created_grid)
    assert updated_grid.size == 75

    # Delete grid
    await repo.delete(created_grid)
    deleted_grid = await repo.get(created_grid.id)
    assert deleted_grid is None


@pytest.mark.asyncio
async def test_task_repository(db_session, task_data):
    """Test generation task repository operations."""
    repo = GenerationTaskRepository(db_session)

    # Create task
    task = GenerationTask(**task_data)
    created_task = await repo.create(task)
    assert created_task.id is not None
    assert created_task.type == task_data["type"]

    # Get task
    fetched_task = await repo.get(created_task.id)
    assert fetched_task is not None
    assert fetched_task.id == created_task.id

    # List tasks
    tasks = await repo.list(status=task_data["status"])
    assert len(tasks) == 1
    assert tasks[0].id == created_task.id

    # Update task
    created_task.status = "running"
    updated_task = await repo.update(created_task)
    assert updated_task.status == "running"

    # Delete task
    await repo.delete(created_task)
    deleted_task = await repo.get(created_task.id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_theme_repository(db_session, theme_data):
    """Test theme repository operations."""
    repo = ThemeRepository(db_session)

    # Create theme
    theme = Theme(**theme_data)
    created_theme = await repo.create(theme)
    assert created_theme.id is not None
    assert created_theme.name == theme_data["name"]

    # Get theme
    fetched_theme = await repo.get(created_theme.id)
    assert fetched_theme is not None
    assert fetched_theme.id == created_theme.id

    # List themes
    themes = await repo.list()
    assert len(themes) == 1
    assert themes[0].id == created_theme.id

    # Update theme
    created_theme.display_name = "Updated Name"
    updated_theme = await repo.update(created_theme)
    assert updated_theme.display_name == "Updated Name"

    # Delete theme
    await repo.delete(created_theme)
    deleted_theme = await repo.get(created_theme.id)
    assert deleted_theme is None


@pytest.mark.asyncio
async def test_variation_repository(db_session, theme_data, variation_data):
    """Test theme variation repository operations."""
    # Create theme first
    theme = Theme(**theme_data)
    db_session.add(theme)
    await db_session.commit()
    await db_session.refresh(theme)

    repo = ThemeVariationRepository(db_session)

    # Create variation
    variation = ThemeVariation(theme_id=theme.id, **variation_data)
    created_variation = await repo.create(variation, theme.id)
    assert created_variation.id is not None
    assert created_variation.name == variation_data["name"]

    # Get variation
    fetched_variation = await repo.get(created_variation.id)
    assert fetched_variation is not None
    assert fetched_variation.id == created_variation.id

    # List variations
    variations = await repo.list_by_theme(theme.id)
    assert len(variations) == 1
    assert variations[0].id == created_variation.id

    # Update variation
    created_variation.display_name = "Updated Name"
    updated_variation = await repo.update(created_variation)
    assert updated_variation.display_name == "Updated Name"

    # Delete variation
    await repo.delete(created_variation)
    deleted_variation = await repo.get(created_variation.id)
    assert deleted_variation is None


@pytest.mark.asyncio
async def test_preset_repository(db_session, preset_data):
    """Test style preset repository operations."""
    repo = StylePresetRepository(db_session)

    # Create preset
    preset = StylePreset(**preset_data)
    created_preset = await repo.create(preset)
    assert created_preset.id is not None
    assert created_preset.name == preset_data["name"]

    # Get preset
    fetched_preset = await repo.get(created_preset.id)
    assert fetched_preset is not None
    assert fetched_preset.id == created_preset.id

    # List presets
    presets = await repo.list(category=preset_data["category"])
    assert len(presets) == 1
    assert presets[0].id == created_preset.id

    # Update preset
    created_preset.display_name = "Updated Name"
    updated_preset = await repo.update(created_preset)
    assert updated_preset.display_name == "Updated Name"

    # Delete preset
    await repo.delete(created_preset)
    deleted_preset = await repo.get(created_preset.id)
    assert deleted_preset is None


@pytest.mark.asyncio
async def test_element_repository(db_session, element_data):
    """Test theme element repository operations."""
    repo = ThemeElementRepository(db_session)

    # Create element
    element = ThemeElement(**element_data)
    created_element = await repo.create(element)
    assert created_element.id is not None
    assert created_element.name == element_data["name"]

    # Get element
    fetched_element = await repo.get(created_element.id)
    assert fetched_element is not None
    assert fetched_element.id == created_element.id

    # List elements
    elements = await repo.list(category=element_data["category"])
    assert len(elements) == 1
    assert elements[0].id == created_element.id

    # Update element
    created_element.display_name = "Updated Name"
    updated_element = await repo.update(created_element)
    assert updated_element.display_name == "Updated Name"

    # Delete element
    await repo.delete(created_element)
    deleted_element = await repo.get(created_element.id)
    assert deleted_element is None