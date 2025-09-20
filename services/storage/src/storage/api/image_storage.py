"""API endpoints for image storage service."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storage.core.database import get_db
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
from storage.schemas.image_storage import (
    ImageCreate,
    ImageResponse,
    ImageUpdate,
    ImageOverlayCreate,
    ImageOverlayResponse,
    ImageOverlayUpdate,
    MapGridCreate,
    MapGridResponse,
    MapGridUpdate,
    GenerationTaskCreate,
    GenerationTaskResponse,
    GenerationTaskUpdate,
    ThemeCreate,
    ThemeResponse,
    ThemeUpdate,
    ThemeVariationCreate,
    ThemeVariationResponse,
    ThemeVariationUpdate,
    StylePresetCreate,
    StylePresetResponse,
    StylePresetUpdate,
    ThemeElementCreate,
    ThemeElementResponse,
    ThemeElementUpdate,
)

router = APIRouter(prefix="/api/v2/image-storage", tags=["image-storage"])


# Image endpoints

@router.post("/images", response_model=ImageResponse)
async def create_image(
    image: ImageCreate, db: AsyncSession = Depends(get_db)
) -> ImageResponse:
    """Create new image."""
    db_image = Image(**image.dict())
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    return db_image


@router.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: UUID, db: AsyncSession = Depends(get_db)
) -> ImageResponse:
    """Get image by ID."""
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.is_deleted == False
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.put("/images/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: UUID, image: ImageUpdate, db: AsyncSession = Depends(get_db)
) -> ImageResponse:
    """Update image."""
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.is_deleted == False
        )
    )
    db_image = result.scalar_one_or_none()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    for field, value in image.dict(exclude_unset=True).items():
        setattr(db_image, field, value)

    await db.commit()
    await db.refresh(db_image)
    return db_image


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: UUID, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Soft delete image."""
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.is_deleted == False
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image.is_deleted = True
    image.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Image deleted"}


@router.get("/images", response_model=List[ImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    theme: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[ImageResponse]:
    """List images with optional filters."""
    query = select(Image).where(Image.is_deleted == False)
    
    if type:
        query = query.where(Image.type == type)
    if theme:
        query = query.where(Image.theme == theme)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Image overlay endpoints

@router.post("/overlays", response_model=ImageOverlayResponse)
async def create_overlay(
    overlay: ImageOverlayCreate, db: AsyncSession = Depends(get_db)
) -> ImageOverlayResponse:
    """Create new image overlay."""
    db_overlay = ImageOverlay(**overlay.dict())
    db.add(db_overlay)
    await db.commit()
    await db.refresh(db_overlay)
    return db_overlay


@router.get("/overlays/{overlay_id}", response_model=ImageOverlayResponse)
async def get_overlay(
    overlay_id: UUID, db: AsyncSession = Depends(get_db)
) -> ImageOverlayResponse:
    """Get overlay by ID."""
    result = await db.execute(
        select(ImageOverlay).where(
            ImageOverlay.id == overlay_id,
            ImageOverlay.is_deleted == False
        )
    )
    overlay = result.scalar_one_or_none()
    if not overlay:
        raise HTTPException(status_code=404, detail="Overlay not found")
    return overlay


@router.get("/images/{image_id}/overlays", response_model=List[ImageOverlayResponse])
async def list_image_overlays(
    image_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[ImageOverlayResponse]:
    """List overlays for an image."""
    result = await db.execute(
        select(ImageOverlay).where(
            ImageOverlay.image_id == image_id,
            ImageOverlay.is_deleted == False
        )
    )
    return result.scalars().all()


# Map grid endpoints

@router.post("/grids", response_model=MapGridResponse)
async def create_grid(
    grid: MapGridCreate, db: AsyncSession = Depends(get_db)
) -> MapGridResponse:
    """Create new map grid."""
    db_grid = MapGrid(**grid.dict())
    db.add(db_grid)
    await db.commit()
    await db.refresh(db_grid)
    return db_grid


@router.get("/grids/{grid_id}", response_model=MapGridResponse)
async def get_grid(
    grid_id: UUID, db: AsyncSession = Depends(get_db)
) -> MapGridResponse:
    """Get grid by ID."""
    result = await db.execute(
        select(MapGrid).where(
            MapGrid.id == grid_id,
            MapGrid.is_deleted == False
        )
    )
    grid = result.scalar_one_or_none()
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid


@router.get("/images/{image_id}/grid", response_model=MapGridResponse)
async def get_image_grid(
    image_id: UUID, db: AsyncSession = Depends(get_db)
) -> MapGridResponse:
    """Get grid for an image."""
    result = await db.execute(
        select(MapGrid).where(
            MapGrid.image_id == image_id,
            MapGrid.is_deleted == False
        )
    )
    grid = result.scalar_one_or_none()
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid


# Generation task endpoints

@router.post("/tasks", response_model=GenerationTaskResponse)
async def create_task(
    task: GenerationTaskCreate, db: AsyncSession = Depends(get_db)
) -> GenerationTaskResponse:
    """Create new generation task."""
    db_task = GenerationTask(**task.dict())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.get("/tasks/{task_id}", response_model=GenerationTaskResponse)
async def get_task(
    task_id: UUID, db: AsyncSession = Depends(get_db)
) -> GenerationTaskResponse:
    """Get task by ID."""
    result = await db.execute(
        select(GenerationTask).where(
            GenerationTask.id == task_id,
            GenerationTask.is_deleted == False
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks", response_model=List[GenerationTaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[GenerationTaskResponse]:
    """List generation tasks with optional filters."""
    query = select(GenerationTask).where(GenerationTask.is_deleted == False)
    
    if status:
        query = query.where(GenerationTask.status == status)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Theme endpoints

@router.post("/themes", response_model=ThemeResponse)
async def create_theme(
    theme: ThemeCreate, db: AsyncSession = Depends(get_db)
) -> ThemeResponse:
    """Create new theme."""
    db_theme = Theme(**theme.dict())
    db.add(db_theme)
    await db.commit()
    await db.refresh(db_theme)
    return db_theme


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: UUID, db: AsyncSession = Depends(get_db)
) -> ThemeResponse:
    """Get theme by ID."""
    result = await db.execute(
        select(Theme).where(
            Theme.id == theme_id,
            Theme.is_deleted == False
        )
    )
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme


@router.get("/themes", response_model=List[ThemeResponse])
async def list_themes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[ThemeResponse]:
    """List all themes."""
    result = await db.execute(
        select(Theme)
        .where(Theme.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# Theme variation endpoints

@router.post("/themes/{theme_id}/variations", response_model=ThemeVariationResponse)
async def create_theme_variation(
    theme_id: UUID,
    variation: ThemeVariationCreate,
    db: AsyncSession = Depends(get_db),
) -> ThemeVariationResponse:
    """Create new theme variation."""
    # Verify theme exists
    result = await db.execute(
        select(Theme).where(
            Theme.id == theme_id,
            Theme.is_deleted == False
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Theme not found")

    db_variation = ThemeVariation(**variation.dict(), theme_id=theme_id)
    db.add(db_variation)
    await db.commit()
    await db.refresh(db_variation)
    return db_variation


@router.get("/variations/{variation_id}", response_model=ThemeVariationResponse)
async def get_variation(
    variation_id: UUID, db: AsyncSession = Depends(get_db)
) -> ThemeVariationResponse:
    """Get variation by ID."""
    result = await db.execute(
        select(ThemeVariation).where(
            ThemeVariation.id == variation_id,
            ThemeVariation.is_deleted == False
        )
    )
    variation = result.scalar_one_or_none()
    if not variation:
        raise HTTPException(status_code=404, detail="Variation not found")
    return variation


# Style preset endpoints

@router.post("/presets", response_model=StylePresetResponse)
async def create_preset(
    preset: StylePresetCreate, db: AsyncSession = Depends(get_db)
) -> StylePresetResponse:
    """Create new style preset."""
    db_preset = StylePreset(**preset.dict())
    db.add(db_preset)
    await db.commit()
    await db.refresh(db_preset)
    return db_preset


@router.get("/presets/{preset_id}", response_model=StylePresetResponse)
async def get_preset(
    preset_id: UUID, db: AsyncSession = Depends(get_db)
) -> StylePresetResponse:
    """Get preset by ID."""
    result = await db.execute(
        select(StylePreset).where(
            StylePreset.id == preset_id,
            StylePreset.is_deleted == False
        )
    )
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.get("/presets", response_model=List[StylePresetResponse])
async def list_presets(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[StylePresetResponse]:
    """List style presets with optional category filter."""
    query = select(StylePreset).where(StylePreset.is_deleted == False)
    
    if category:
        query = query.where(StylePreset.category == category)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Theme element endpoints

@router.post("/elements", response_model=ThemeElementResponse)
async def create_element(
    element: ThemeElementCreate, db: AsyncSession = Depends(get_db)
) -> ThemeElementResponse:
    """Create new theme element."""
    db_element = ThemeElement(**element.dict())
    db.add(db_element)
    await db.commit()
    await db.refresh(db_element)
    return db_element


@router.get("/elements/{element_id}", response_model=ThemeElementResponse)
async def get_element(
    element_id: UUID, db: AsyncSession = Depends(get_db)
) -> ThemeElementResponse:
    """Get element by ID."""
    result = await db.execute(
        select(ThemeElement).where(
            ThemeElement.id == element_id,
            ThemeElement.is_deleted == False
        )
    )
    element = result.scalar_one_or_none()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.get("/elements", response_model=List[ThemeElementResponse])
async def list_elements(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[ThemeElementResponse]:
    """List theme elements with optional category filter."""
    query = select(ThemeElement).where(ThemeElement.is_deleted == False)
    
    if category:
        query = query.where(ThemeElement.category == category)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()