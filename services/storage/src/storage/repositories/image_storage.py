"""Repositories for image storage service."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


class ImageRepository:
    """Repository for image operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, image: Image) -> Image:
        """Create new image."""
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get(self, image_id: UUID) -> Optional[Image]:
        """Get image by ID."""
        result = await self.db.execute(
            select(Image).where(
                Image.id == image_id,
                Image.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
        theme: Optional[str] = None,
    ) -> List[Image]:
        """List images with optional filters."""
        query = select(Image).where(Image.is_deleted == False)

        if type:
            query = query.where(Image.type == type)
        if theme:
            query = query.where(Image.theme == theme)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, image: Image) -> Image:
        """Update image."""
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def delete(self, image: Image) -> None:
        """Soft delete image."""
        image.is_deleted = True
        image.deleted_at = datetime.utcnow()
        await self.db.commit()


class ImageOverlayRepository:
    """Repository for image overlay operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, overlay: ImageOverlay) -> ImageOverlay:
        """Create new overlay."""
        self.db.add(overlay)
        await self.db.commit()
        await self.db.refresh(overlay)
        return overlay

    async def get(self, overlay_id: UUID) -> Optional[ImageOverlay]:
        """Get overlay by ID."""
        result = await self.db.execute(
            select(ImageOverlay).where(
                ImageOverlay.id == overlay_id,
                ImageOverlay.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_image(self, image_id: UUID) -> List[ImageOverlay]:
        """List overlays for an image."""
        result = await self.db.execute(
            select(ImageOverlay).where(
                ImageOverlay.image_id == image_id,
                ImageOverlay.is_deleted == False,
            )
        )
        return result.scalars().all()

    async def update(self, overlay: ImageOverlay) -> ImageOverlay:
        """Update overlay."""
        await self.db.commit()
        await self.db.refresh(overlay)
        return overlay

    async def delete(self, overlay: ImageOverlay) -> None:
        """Soft delete overlay."""
        overlay.is_deleted = True
        overlay.deleted_at = datetime.utcnow()
        await self.db.commit()


class MapGridRepository:
    """Repository for map grid operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, grid: MapGrid) -> MapGrid:
        """Create new grid."""
        self.db.add(grid)
        await self.db.commit()
        await self.db.refresh(grid)
        return grid

    async def get(self, grid_id: UUID) -> Optional[MapGrid]:
        """Get grid by ID."""
        result = await self.db.execute(
            select(MapGrid).where(
                MapGrid.id == grid_id,
                MapGrid.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_image(self, image_id: UUID) -> Optional[MapGrid]:
        """Get grid by image ID."""
        result = await self.db.execute(
            select(MapGrid).where(
                MapGrid.image_id == image_id,
                MapGrid.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, grid: MapGrid) -> MapGrid:
        """Update grid."""
        await self.db.commit()
        await self.db.refresh(grid)
        return grid

    async def delete(self, grid: MapGrid) -> None:
        """Soft delete grid."""
        grid.is_deleted = True
        grid.deleted_at = datetime.utcnow()
        await self.db.commit()


class GenerationTaskRepository:
    """Repository for generation task operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, task: GenerationTask) -> GenerationTask:
        """Create new task."""
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get(self, task_id: UUID) -> Optional[GenerationTask]:
        """Get task by ID."""
        result = await self.db.execute(
            select(GenerationTask).where(
                GenerationTask.id == task_id,
                GenerationTask.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[GenerationTask]:
        """List tasks with optional status filter."""
        query = select(GenerationTask).where(GenerationTask.is_deleted == False)

        if status:
            query = query.where(GenerationTask.status == status)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, task: GenerationTask) -> GenerationTask:
        """Update task."""
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: GenerationTask) -> None:
        """Soft delete task."""
        task.is_deleted = True
        task.deleted_at = datetime.utcnow()
        await self.db.commit()


class ThemeRepository:
    """Repository for theme operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, theme: Theme) -> Theme:
        """Create new theme."""
        self.db.add(theme)
        await self.db.commit()
        await self.db.refresh(theme)
        return theme

    async def get(self, theme_id: UUID) -> Optional[Theme]:
        """Get theme by ID."""
        result = await self.db.execute(
            select(Theme).where(
                Theme.id == theme_id,
                Theme.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Theme]:
        """List themes."""
        result = await self.db.execute(
            select(Theme)
            .where(Theme.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, theme: Theme) -> Theme:
        """Update theme."""
        await self.db.commit()
        await self.db.refresh(theme)
        return theme

    async def delete(self, theme: Theme) -> None:
        """Soft delete theme."""
        theme.is_deleted = True
        theme.deleted_at = datetime.utcnow()
        await self.db.commit()


class ThemeVariationRepository:
    """Repository for theme variation operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(
        self, variation: ThemeVariation, theme_id: UUID
    ) -> ThemeVariation:
        """Create new variation."""
        variation.theme_id = theme_id
        self.db.add(variation)
        await self.db.commit()
        await self.db.refresh(variation)
        return variation

    async def get(self, variation_id: UUID) -> Optional[ThemeVariation]:
        """Get variation by ID."""
        result = await self.db.execute(
            select(ThemeVariation).where(
                ThemeVariation.id == variation_id,
                ThemeVariation.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_theme(self, theme_id: UUID) -> List[ThemeVariation]:
        """List variations for a theme."""
        result = await self.db.execute(
            select(ThemeVariation).where(
                ThemeVariation.theme_id == theme_id,
                ThemeVariation.is_deleted == False,
            )
        )
        return result.scalars().all()

    async def update(self, variation: ThemeVariation) -> ThemeVariation:
        """Update variation."""
        await self.db.commit()
        await self.db.refresh(variation)
        return variation

    async def delete(self, variation: ThemeVariation) -> None:
        """Soft delete variation."""
        variation.is_deleted = True
        variation.deleted_at = datetime.utcnow()
        await self.db.commit()


class StylePresetRepository:
    """Repository for style preset operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, preset: StylePreset) -> StylePreset:
        """Create new preset."""
        self.db.add(preset)
        await self.db.commit()
        await self.db.refresh(preset)
        return preset

    async def get(self, preset_id: UUID) -> Optional[StylePreset]:
        """Get preset by ID."""
        result = await self.db.execute(
            select(StylePreset).where(
                StylePreset.id == preset_id,
                StylePreset.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, skip: int = 0, limit: int = 100, category: Optional[str] = None
    ) -> List[StylePreset]:
        """List presets with optional category filter."""
        query = select(StylePreset).where(StylePreset.is_deleted == False)

        if category:
            query = query.where(StylePreset.category == category)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, preset: StylePreset) -> StylePreset:
        """Update preset."""
        await self.db.commit()
        await self.db.refresh(preset)
        return preset

    async def delete(self, preset: StylePreset) -> None:
        """Soft delete preset."""
        preset.is_deleted = True
        preset.deleted_at = datetime.utcnow()
        await self.db.commit()


class ThemeElementRepository:
    """Repository for theme element operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, element: ThemeElement) -> ThemeElement:
        """Create new element."""
        self.db.add(element)
        await self.db.commit()
        await self.db.refresh(element)
        return element

    async def get(self, element_id: UUID) -> Optional[ThemeElement]:
        """Get element by ID."""
        result = await self.db.execute(
            select(ThemeElement).where(
                ThemeElement.id == element_id,
                ThemeElement.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, skip: int = 0, limit: int = 100, category: Optional[str] = None
    ) -> List[ThemeElement]:
        """List elements with optional category filter."""
        query = select(ThemeElement).where(ThemeElement.is_deleted == False)

        if category:
            query = query.where(ThemeElement.category == category)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, element: ThemeElement) -> ThemeElement:
        """Update element."""
        await self.db.commit()
        await self.db.refresh(element)
        return element

    async def delete(self, element: ThemeElement) -> None:
        """Soft delete element."""
        element.is_deleted = True
        element.deleted_at = datetime.utcnow()
        await self.db.commit()