"""Repository for image database operations."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from image.models.storage import Image, ImageType


class ImageRepository:
    """Repository for image database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    def get_query(self) -> Select:
        """Get base query for images.

        Returns:
            SQLAlchemy select query
        """
        return select(Image).where(Image.is_deleted == False)

    async def create(
        self,
        type: ImageType,
        format: str,
        content_hash: str,
        size_bytes: int,
        width: int,
        height: int,
        location: str,
        storage_path: str,
        metadata: Optional[Dict] = None,
        theme: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        source_id: Optional[UUID] = None,
        source_type: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        cdn_url: Optional[str] = None,
        version: int = 1
    ) -> Image:
        """Create new image record.

        Args:
            type: Image type
            format: Image format
            content_hash: Content hash for deduplication
            size_bytes: Size in bytes
            width: Image width in pixels
            height: Image height in pixels
            location: Storage location
            storage_path: Path in storage
            metadata: Optional metadata dict
            theme: Optional theme name
            cache_ttl: Optional cache TTL
            source_id: Optional source ID
            source_type: Optional source type
            parent_id: Optional parent image ID
            tags: Optional list of tags
            cdn_url: Optional CDN URL
            version: Version number

        Returns:
            Created image record
        """
        image = Image(
            type=type,
            format=format,
            content_hash=content_hash,
            size_bytes=size_bytes,
            width=width,
            height=height,
            location=location,
            storage_path=storage_path,
            metadata=metadata or {},
            theme=theme,
            cache_ttl=cache_ttl,
            source_id=source_id,
            source_type=source_type,
            parent_id=parent_id,
            tags=tags or [],
            cdn_url=cdn_url,
            version=version
        )
        self.session.add(image)
        await self.session.commit()
        return image

    async def create_version(
        self,
        parent_id: UUID,
        image_type: ImageType,
        metadata: Optional[Dict] = None
    ) -> Image:
        """Create new version of existing image.

        Args:
            parent_id: ID of parent image
            image_type: Image type for new version
            metadata: Optional metadata dict

        Returns:
            Created image version

        Raises:
            ValueError: If parent image not found
        """
        # Get parent image
        parent = await self.get(parent_id)
        if not parent:
            raise ValueError(f"Parent image not found: {parent_id}")

        # Create new version
        version = await self.create(
            type=image_type,
            format=parent.format,
            content_hash=parent.content_hash,
            size_bytes=parent.size_bytes,
            width=parent.width,
            height=parent.height,
            location=parent.location,
            storage_path=parent.storage_path,  # Share storage
            metadata=metadata or {},
            theme=parent.theme,
            parent_id=parent_id,
            version=parent.version + 1
        )
        return version

    async def get(self, image_id: UUID) -> Optional[Image]:
        """Get image by ID.

        Args:
            image_id: Image ID

        Returns:
            Image if found, otherwise None
        """
        query = self.get_query().where(Image.id == image_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_content_hash(self, content_hash: str) -> Optional[Image]:
        """Get image by content hash.

        Args:
            content_hash: Content hash to find

        Returns:
            Image if found, otherwise None
        """
        query = (
            self.get_query()
            .where(Image.content_hash == content_hash)
            .order_by(Image.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(
        self,
        image_type: Optional[ImageType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Image]:
        """List images with optional filtering.

        Args:
            image_type: Optional type filter
            limit: Maximum number of records
            offset: Pagination offset

        Returns:
            List of images
        """
        query = self.get_query()
        if image_type:
            query = query.where(Image.type == image_type)
        query = query.order_by(Image.created_at.desc())
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        image_id: UUID,
        theme: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        cdn_url: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> Optional[Image]:
        """Update image record.

        Args:
            image_id: ID of image to update
            theme: Optional new theme
            metadata: Optional new metadata
            tags: Optional new tags
            cdn_url: Optional new CDN URL
            cache_ttl: Optional new cache TTL

        Returns:
            Updated image if found, otherwise None
        """
        # Build update values
        values = {}
        if theme is not None:
            values["theme"] = theme
        if metadata is not None:
            values["metadata"] = metadata
        if tags is not None:
            values["tags"] = tags
        if cdn_url is not None:
            values["cdn_url"] = cdn_url
        if cache_ttl is not None:
            values["cache_ttl"] = cache_ttl
        if values:
            values["updated_at"] = datetime.utcnow()

        # Update image
        if values:
            query = (
                update(Image)
                .where(Image.id == image_id)
                .values(**values)
                .returning(Image)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none()
        return None

    async def soft_delete(self, image_id: UUID) -> bool:
        """Soft delete image.

        Args:
            image_id: ID of image to delete

        Returns:
            True if image was found and deleted
        """
        # Update image
        query = (
            update(Image)
            .where(Image.id == image_id, Image.is_deleted == False)
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow()
            )
            .returning(Image.id)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none() is not None

    async def count(self, image_type: Optional[ImageType] = None) -> int:
        """Count total non-deleted images.

        Args:
            image_type: Optional type filter

        Returns:
            Total number of images
        """
        query = select(sa.func.count(Image.id)).where(Image.is_deleted == False)
        if image_type:
            query = query.where(Image.type == image_type)
        result = await self.session.execute(query)
        return result.scalar_one()
