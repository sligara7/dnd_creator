"""S3 storage service for image management."""
import hashlib
import io
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import aioboto3
from fastapi import UploadFile
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession

from image.core.config import get_settings
from image.core.metrics import (
    record_storage_operation,
    record_storage_size,
    record_upload_time,
    record_download_time
)
from image.models.storage import Image, ImageFormat, ImageType, StorageLocation
from image.repositories.image import ImageRepository

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing image storage in S3."""

    # Constants
    MULTIPART_THRESHOLD = 10 * 1024 * 1024  # 10MB
    MULTIPART_CHUNKSIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(
        self,
        session: AsyncSession,
        bucket_name: Optional[str] = None
    ) -> None:
        """Initialize the storage service.

        Args:
            session: Database session
            bucket_name: Optional S3 bucket name (default from settings)
        """
        self.session = session
        self.image_repo = ImageRepository(session)
        self.settings = get_settings()
        self.bucket_name = bucket_name or self.settings.s3_bucket_name
        self.session = aioboto3.Session()

    def _generate_storage_path(
        self,
        image_type: ImageType,
        created_at: datetime,
        image_id: UUID
    ) -> str:
        """Generate storage path for image.

        Args:
            image_type: Type of image
            created_at: Creation timestamp
            image_id: Image UUID

        Returns:
            S3 storage path
        """
        # Organization: type/year/month/uuid
        return f"{image_type.value}/{created_at.year}/{created_at.month:02d}/{image_id}"

    async def _compute_image_hash(self, file: UploadFile) -> str:
        """Compute content hash for image deduplication.

        Args:
            file: Image file to hash

        Returns:
            Content hash
        """
        hasher = hashlib.blake2b()
        chunk_size = 8192  # 8KB chunks

        # Reset file position
        await file.seek(0)

        # Read and hash chunks
        while chunk := await file.read(chunk_size):
            hasher.update(chunk)

        # Reset file position
        await file.seek(0)

        return hasher.hexdigest()

    async def _get_image_metadata(
        self,
        file: UploadFile
    ) -> Tuple[int, int, int, ImageFormat]:
        """Get image metadata.

        Args:
            file: Image file to analyze

        Returns:
            Tuple of (width, height, size_bytes, format)

        Raises:
            ValueError: If file is not a valid image
        """
        try:
            # Read image data
            await file.seek(0)
            content = await file.read()
            size_bytes = len(content)

            # Analyze with PIL
            with io.BytesIO(content) as buf:
                img = PILImage.open(buf)
                width, height = img.size
                format_str = img.format.lower()

            # Reset file position
            await file.seek(0)

            # Validate format
            try:
                image_format = ImageFormat(format_str)
            except ValueError:
                raise ValueError(f"Unsupported image format: {format_str}")

            return width, height, size_bytes, image_format

        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

    async def upload_image(
        self,
        file: UploadFile,
        image_type: ImageType,
        metadata: Optional[Dict] = None
    ) -> Image:
        """Upload new image to storage.

        Args:
            file: Image file to upload
            image_type: Type of image
            metadata: Optional metadata dict

        Returns:
            Created image record

        Raises:
            ValueError: If file is invalid
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Validate file size
            file_size = await file.seek(0, os.SEEK_END)
            if file_size > self.MAX_IMAGE_SIZE:
                raise ValueError(
                    f"File too large ({file_size} bytes). "
                    f"Maximum size is {self.MAX_IMAGE_SIZE} bytes."
                )
            await file.seek(0)

            # Get image metadata
            width, height, size_bytes, image_format = await self._get_image_metadata(file)

            # Compute content hash
            content_hash = await self._compute_image_hash(file)

            # Check for duplicates
            existing = await self.image_repo.get_by_content_hash(content_hash)
            if existing:
                # Create new version if duplicate
                image = await self.image_repo.create_version(
                    existing.id,
                    image_type=image_type,
                    metadata=metadata or {}
                )
                record_storage_operation("duplicate_detected")
                return image

            # Create image record
            image = await self.image_repo.create(
                type=image_type,
                format=image_format,
                content_hash=content_hash,
                size_bytes=size_bytes,
                width=width,
                height=height,
                location=StorageLocation.S3,
                storage_path=self._generate_storage_path(
                    image_type,
                    datetime.utcnow(),
                    image.id
                ),
                metadata=metadata or {}
            )

            # Upload to S3
            async with self.session.client("s3") as s3:
                if size_bytes > self.MULTIPART_THRESHOLD:
                    # Use multipart upload for large files
                    multipart_config = {
                        "PartSize": self.MULTIPART_CHUNKSIZE,
                        "Threshold": self.MULTIPART_THRESHOLD
                    }
                    await file.seek(0)
                    await s3.upload_fileobj(
                        file,
                        self.bucket_name,
                        image.storage_path,
                        Config=multipart_config
                    )
                else:
                    # Simple upload for small files
                    await file.seek(0)
                    await s3.upload_fileobj(
                        file,
                        self.bucket_name,
                        image.storage_path
                    )

            # Record metrics
            upload_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            record_upload_time(upload_time)
            record_storage_size(size_bytes)
            record_storage_operation("upload_success")

            return image

        except Exception as e:
            record_storage_operation("upload_error")
            logger.exception("Error uploading image")
            raise ValueError(f"Upload failed: {str(e)}")

    async def download_image(self, image_id: UUID) -> Tuple[bytes, Image]:
        """Download image from storage.

        Args:
            image_id: ID of image to download

        Returns:
            Tuple of (image_data, image_record)

        Raises:
            ValueError: If image not found or download fails
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Get image record
            image = await self.image_repo.get(image_id)
            if not image:
                raise ValueError(f"Image not found: {image_id}")

            # Create file buffer
            buffer = io.BytesIO()

            # Download from S3
            async with self.session.client("s3") as s3:
                if image.size_bytes > self.MULTIPART_THRESHOLD:
                    # Use multipart download for large files
                    multipart_config = {
                        "PartSize": self.MULTIPART_CHUNKSIZE,
                        "Threshold": self.MULTIPART_THRESHOLD
                    }
                    await s3.download_fileobj(
                        self.bucket_name,
                        image.storage_path,
                        buffer,
                        Config=multipart_config
                    )
                else:
                    # Simple download for small files
                    await s3.download_fileobj(
                        self.bucket_name,
                        image.storage_path,
                        buffer
                    )

            # Record metrics
            download_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            record_download_time(download_time)
            record_storage_operation("download_success")

            return buffer.getvalue(), image

        except Exception as e:
            record_storage_operation("download_error")
            logger.exception("Error downloading image")
            raise ValueError(f"Download failed: {str(e)}")

    async def delete_image(self, image_id: UUID) -> None:
        """Delete image from storage.

        Args:
            image_id: ID of image to delete

        Raises:
            ValueError: If image not found or deletion fails
        """
        try:
            # Get image record
            image = await self.image_repo.get(image_id)
            if not image:
                raise ValueError(f"Image not found: {image_id}")

            # Delete from S3
            async with self.session.client("s3") as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=image.storage_path
                )

            # Soft delete record
            await self.image_repo.soft_delete(image_id)

            # Record metrics
            record_storage_operation("delete_success")

        except Exception as e:
            record_storage_operation("delete_error")
            logger.exception("Error deleting image")
            raise ValueError(f"Deletion failed: {str(e)}")

    async def get_presigned_url(
        self,
        image_id: UUID,
        expires_in: int = 3600
    ) -> str:
        """Generate presigned URL for image access.

        Args:
            image_id: ID of image to access
            expires_in: URL expiration in seconds

        Returns:
            Presigned URL

        Raises:
            ValueError: If image not found
        """
        try:
            # Get image record
            image = await self.image_repo.get(image_id)
            if not image:
                raise ValueError(f"Image not found: {image_id}")

            # Generate URL
            async with self.session.client("s3") as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": image.storage_path
                    },
                    ExpiresIn=expires_in
                )

            # Record metrics
            record_storage_operation("presign_success")

            return url

        except Exception as e:
            record_storage_operation("presign_error")
            logger.exception("Error generating presigned URL")
            raise ValueError(f"URL generation failed: {str(e)}")

    async def list_images(
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
            List of image records
        """
        try:
            # Get images from database
            images = await self.image_repo.list(
                image_type=image_type,
                limit=limit,
                offset=offset
            )

            # Record metrics
            record_storage_operation("list_success")

            return images

        except Exception as e:
            record_storage_operation("list_error")
            logger.exception("Error listing images")
            raise ValueError(f"List operation failed: {str(e)}")
