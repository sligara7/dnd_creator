"""Script to migrate data from image service to storage service."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.dialects.postgresql import insert

from storage.core.database import DatabaseManager
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URLs
IMAGE_DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/image_db"  # Configure as needed
STORAGE_DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/storage_db"  # Configure as needed

# Batch size for processing
BATCH_SIZE = 100


async def get_source_session() -> AsyncSession:
    """Get session for source database."""
    engine = create_async_engine(IMAGE_DB_URL)
    async_session = AsyncSession(engine)
    return async_session


async def get_target_session() -> AsyncSession:
    """Get session for target database."""
    db_manager = DatabaseManager(STORAGE_DB_URL)
    await db_manager.init()
    return await db_manager.get_session().__aenter__()


async def migrate_images(
    source_session: AsyncSession, target_session: AsyncSession
) -> Dict[UUID, UUID]:
    """Migrate images from source to target database."""
    logger.info("Starting image migration...")
    
    # Dictionary to store old ID to new ID mappings
    id_map = {}
    
    offset = 0
    while True:
        # Fetch batch of images
        query = select(Image).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        images = result.scalars().all()
        
        if not images:
            break
            
        # Process batch
        for image in images:
            # Create new image record
            new_image = Image(
                id=image.id,  # Preserve original ID
                type=image.type,
                subtype=image.subtype,
                name=image.name,
                description=image.description,
                url=image.url,
                format=image.format,
                width=image.width,
                height=image.height,
                size=image.size,
                theme=image.theme,
                style_data=image.style_data,
                generation_params=image.generation_params,
                source_id=image.source_id,
                source_type=image.source_type,
                created_at=image.created_at,
                updated_at=image.updated_at,
                deleted_at=image.deleted_at,
                is_deleted=image.is_deleted,
            )
            target_session.add(new_image)
            id_map[image.id] = new_image.id
            
        # Commit batch
        await target_session.commit()
        logger.info(f"Migrated {len(images)} images")
        offset += BATCH_SIZE
    
    return id_map


async def migrate_overlays(
    source_session: AsyncSession,
    target_session: AsyncSession,
    image_id_map: Dict[UUID, UUID],
) -> None:
    """Migrate image overlays."""
    logger.info("Starting overlay migration...")
    
    offset = 0
    while True:
        query = select(ImageOverlay).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        overlays = result.scalars().all()
        
        if not overlays:
            break
            
        for overlay in overlays:
            # Skip if parent image wasn't migrated
            if overlay.image_id not in image_id_map:
                logger.warning(f"Skipping orphaned overlay {overlay.id}")
                continue
                
            new_overlay = ImageOverlay(
                id=overlay.id,  # Preserve original ID
                image_id=image_id_map[overlay.image_id],
                type=overlay.type,
                name=overlay.name,
                description=overlay.description,
                data=overlay.data,
                style=overlay.style,
                created_at=overlay.created_at,
                updated_at=overlay.updated_at,
                deleted_at=overlay.deleted_at,
                is_deleted=overlay.is_deleted,
            )
            target_session.add(new_overlay)
            
        await target_session.commit()
        logger.info(f"Migrated {len(overlays)} overlays")
        offset += BATCH_SIZE


async def migrate_grids(
    source_session: AsyncSession,
    target_session: AsyncSession,
    image_id_map: Dict[UUID, UUID],
) -> None:
    """Migrate map grids."""
    logger.info("Starting grid migration...")
    
    offset = 0
    while True:
        query = select(MapGrid).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        grids = result.scalars().all()
        
        if not grids:
            break
            
        for grid in grids:
            # Skip if parent image wasn't migrated
            if grid.image_id not in image_id_map:
                logger.warning(f"Skipping orphaned grid {grid.id}")
                continue
                
            new_grid = MapGrid(
                id=grid.id,  # Preserve original ID
                image_id=image_id_map[grid.image_id],
                enabled=grid.enabled,
                size=grid.size,
                color=grid.color,
                opacity=grid.opacity,
                created_at=grid.created_at,
                updated_at=grid.updated_at,
                deleted_at=grid.deleted_at,
                is_deleted=grid.is_deleted,
            )
            target_session.add(new_grid)
            
        await target_session.commit()
        logger.info(f"Migrated {len(grids)} grids")
        offset += BATCH_SIZE


async def migrate_generation_tasks(
    source_session: AsyncSession, target_session: AsyncSession
) -> None:
    """Migrate generation tasks."""
    logger.info("Starting generation task migration...")
    
    offset = 0
    while True:
        query = select(GenerationTask).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        tasks = result.scalars().all()
        
        if not tasks:
            break
            
        for task in tasks:
            new_task = GenerationTask(
                id=task.id,  # Preserve original ID
                type=task.type,
                status=task.status,
                priority=task.priority,
                params=task.params,
                result=task.result,
                attempts=task.attempts,
                last_error=task.last_error,
                last_attempt=task.last_attempt,
                retry_count=task.retry_count,
                max_retries=task.max_retries,
                retry_delay=task.retry_delay,
                created_at=task.created_at,
                updated_at=task.updated_at,
                deleted_at=task.deleted_at,
                is_deleted=task.is_deleted,
            )
            target_session.add(new_task)
            
        await target_session.commit()
        logger.info(f"Migrated {len(tasks)} generation tasks")
        offset += BATCH_SIZE


async def migrate_themes_and_related(
    source_session: AsyncSession, target_session: AsyncSession
) -> None:
    """Migrate themes and related data (variations, presets, elements)."""
    logger.info("Starting theme migration...")
    
    # First migrate themes
    theme_id_map = {}
    offset = 0
    while True:
        query = select(Theme).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        themes = result.scalars().all()
        
        if not themes:
            break
            
        for theme in themes:
            new_theme = Theme(
                id=theme.id,  # Preserve original ID
                name=theme.name,
                display_name=theme.display_name,
                description=theme.description,
                config=theme.config,
                variables=theme.variables,
                prompts=theme.prompts,
                styles=theme.styles,
                created_at=theme.created_at,
                updated_at=theme.updated_at,
                deleted_at=theme.deleted_at,
                is_deleted=theme.is_deleted,
            )
            target_session.add(new_theme)
            theme_id_map[theme.id] = new_theme.id
            
        await target_session.commit()
        logger.info(f"Migrated {len(themes)} themes")
        offset += BATCH_SIZE
        
    # Then migrate theme variations
    logger.info("Starting theme variation migration...")
    offset = 0
    while True:
        query = select(ThemeVariation).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        variations = result.scalars().all()
        
        if not variations:
            break
            
        for variation in variations:
            # Skip if parent theme wasn't migrated
            if variation.theme_id not in theme_id_map:
                logger.warning(f"Skipping orphaned variation {variation.id}")
                continue
                
            new_variation = ThemeVariation(
                id=variation.id,  # Preserve original ID
                theme_id=theme_id_map[variation.theme_id],
                name=variation.name,
                display_name=variation.display_name,
                description=variation.description,
                config_override=variation.config_override,
                variable_override=variation.variable_override,
                created_at=variation.created_at,
                updated_at=variation.updated_at,
                deleted_at=variation.deleted_at,
                is_deleted=variation.is_deleted,
            )
            target_session.add(new_variation)
            
        await target_session.commit()
        logger.info(f"Migrated {len(variations)} theme variations")
        offset += BATCH_SIZE
        
    # Migrate style presets
    logger.info("Starting style preset migration...")
    offset = 0
    while True:
        query = select(StylePreset).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        presets = result.scalars().all()
        
        if not presets:
            break
            
        for preset in presets:
            new_preset = StylePreset(
                id=preset.id,  # Preserve original ID
                name=preset.name,
                display_name=preset.display_name,
                description=preset.description,
                category=preset.category,
                config=preset.config,
                prompts=preset.prompts,
                compatibility=preset.compatibility,
                created_at=preset.created_at,
                updated_at=preset.updated_at,
                deleted_at=preset.deleted_at,
                is_deleted=preset.is_deleted,
            )
            target_session.add(new_preset)
            
        await target_session.commit()
        logger.info(f"Migrated {len(presets)} style presets")
        offset += BATCH_SIZE
        
    # Finally migrate theme elements
    logger.info("Starting theme element migration...")
    offset = 0
    while True:
        query = select(ThemeElement).offset(offset).limit(BATCH_SIZE)
        result = await source_session.execute(query)
        elements = result.scalars().all()
        
        if not elements:
            break
            
        for element in elements:
            new_element = ThemeElement(
                id=element.id,  # Preserve original ID
                category=element.category,
                name=element.name,
                display_name=element.display_name,
                description=element.description,
                config=element.config,
                prompts=element.prompts,
                compatibility=element.compatibility,
                created_at=element.created_at,
                updated_at=element.updated_at,
                deleted_at=element.deleted_at,
                is_deleted=element.is_deleted,
            )
            target_session.add(new_element)
            
        await target_session.commit()
        logger.info(f"Migrated {len(elements)} theme elements")
        offset += BATCH_SIZE


async def main():
    """Main migration function."""
    logger.info("Starting database migration...")
    
    # Get database sessions
    source_session = await get_source_session()
    target_session = await get_target_session()
    
    try:
        # Migrate all data
        image_id_map = await migrate_images(source_session, target_session)
        await migrate_overlays(source_session, target_session, image_id_map)
        await migrate_grids(source_session, target_session, image_id_map)
        await migrate_generation_tasks(source_session, target_session)
        await migrate_themes_and_related(source_session, target_session)
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
        
    finally:
        await source_session.close()
        await target_session.close()


if __name__ == "__main__":
    asyncio.run(main())