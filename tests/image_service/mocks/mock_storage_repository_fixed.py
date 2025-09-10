"""
Mock implementation of storage repository for testing.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID

from image_service.models.storage import (
    ImageFormat,
    ImageMetadata,
    ImageStorageMetadata,
    ImageUploadRequest,
    ImageUploadResponse,
    ImageDownloadResponse,
    ImageVersion,
    StorageLocation
)
from image_service.repositories.storage_repository import ImageStorageRepository, NotFoundError

class MockStorageRepository(ImageStorageRepository):
    """Mock implementation of storage repository for testing."""

    def __init__(self):
        """Initialize mock storage."""
        self.images: Dict[UUID, ImageStorageMetadata] = {}
        self.deleted_images: Set[UUID] = set()
        self.deleted_versions: Set[UUID] = set()

    async def init(self) -> None:
        """Initialize storage repository."""
        pass

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.images.clear()
        self.deleted_images.clear()
        self.deleted_versions.clear()

    async def create_upload_request(
        self, 
        request: ImageUploadRequest,
        expiration: timedelta = timedelta(minutes=15)
    ) -> ImageUploadResponse:
        """Create a mock upload request."""
        # Validate format
        if request.format.format not in ("PNG", "JPEG"):
            raise ValueError("Invalid image format")

        # Create storage location
        storage = StorageLocation(
            bucket="test-bucket",
            key=f"test/{request.image_id}.{request.format.format.lower()}",
            region="test-region-1",
            version_id=None  # Set when upload completed
        )

        # Create mock metadata
        metadata = ImageStorageMetadata(
            image_id=request.image_id,
            storage=storage,
            metadata=ImageMetadata(
                width=0,  # Will be updated on complete
                height=0,
                size_bytes=0,
                mime_type=f"image/{request.format.format.lower()}",
                checksum="pending",
                compression=request.format
            ),
            versions=[],
            current_version=None,
            tags=request.tags or {}
        )

        # Store initial metadata
        self.images[request.image_id] = metadata

        # Create mock upload response
        return ImageUploadResponse(
            storage_metadata=metadata,
            upload_url="http://mock-storage/upload",
            headers={
                "Authorization": "mock-auth-token",
                "Content-Type": metadata.metadata.mime_type
            }
        )

    async def complete_upload(
        self,
        image_id: UUID,
        version_id: UUID,
        metadata: ImageMetadata
    ) -> ImageStorageMetadata:
        """Complete a mock upload."""
        if image_id in self.deleted_images:
            raise NotFoundError(f"Image {image_id} not found")
        if version_id in self.deleted_versions:
            raise NotFoundError(f"Version {version_id} not found")

        # Get or create storage metadata
        storage_metadata = self.images.get(image_id)
        if not storage_metadata:
            # Create new storage metadata if not exists
            storage_metadata = ImageStorageMetadata(
                image_id=image_id,
                storage=StorageLocation(
                    bucket="test-bucket",
                    key=f"test/{image_id}.{metadata.mime_type.split('/')[-1]}",
                    region="test-region-1",
                    version_id=str(version_id)
                ),
                metadata=metadata,
                versions=[],
                current_version=None,
                tags={}
            )
            self.images[image_id] = storage_metadata
        
        # Create new version
        new_version = ImageVersion(
            version_id=version_id,
            parent_id=storage_metadata.current_version,
            metadata=metadata,
            created_at=datetime.utcnow()
        )

        # Update storage metadata
        storage_metadata.versions.append(new_version)
        storage_metadata.current_version = version_id
        storage_metadata.metadata = metadata
        storage_metadata.storage.version_id = str(version_id)

        return storage_metadata

    async def get_download_url(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None,
        expiration: timedelta = timedelta(minutes=15)
    ) -> ImageDownloadResponse:
        """Get a mock download URL."""
        if image_id in self.deleted_images:
            raise NotFoundError(f"Image {image_id} not found")

        storage_metadata = self.images.get(image_id)
        if not storage_metadata:
            raise NotFoundError(f"Image {image_id} not found")

        if version_id and str(version_id) != storage_metadata.storage.version_id:
            if version_id in self.deleted_versions:
                raise NotFoundError(f"Version {version_id} not found")

            # Find specific version
            version = next(
                (v for v in storage_metadata.versions if v.version_id == version_id),
                None
            )
            if not version:
                raise NotFoundError(f"Version {version_id} not found")

        return ImageDownloadResponse(
            storage_metadata=storage_metadata,
            download_url="http://mock-storage/download",
            headers={
                "Authorization": "mock-auth-token",
            },
            expiration=datetime.utcnow() + expiration
        )

    async def get_metadata(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None
    ) -> ImageStorageMetadata:
        """Get mock metadata."""
        if image_id in self.deleted_images:
            raise NotFoundError(f"Image {image_id} not found")

        metadata = self.images.get(image_id)
        if not metadata:
            raise NotFoundError(f"Image {image_id} not found")
        return metadata

    async def list_versions(
        self,
        image_id: UUID
    ) -> List[ImageVersion]:
        """List mock versions."""
        if image_id in self.deleted_images:
            raise NotFoundError(f"Image {image_id} not found")

        metadata = self.images.get(image_id)
        if not metadata:
            raise NotFoundError(f"Image {image_id} not found")

        # Filter out deleted versions
        return [
            v for v in metadata.versions 
            if v.version_id not in self.deleted_versions
        ]

    async def delete_image(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None
    ) -> None:
        """Delete mock image or version."""
        if image_id in self.deleted_images:
            raise NotFoundError(f"Image {image_id} not found")

        metadata = self.images.get(image_id)
        if not metadata:
            raise NotFoundError(f"Image {image_id} not found")

        if version_id:
            # Delete specific version
            version = next(
                (v for v in metadata.versions if v.version_id == version_id),
                None
            )
            if not version:
                raise NotFoundError(f"Version {version_id} not found")

            self.deleted_versions.add(version_id)

            # If current version deleted, set to previous
            if metadata.current_version == version_id:
                previous = next(
                    (v for v in reversed(metadata.versions)
                    if v.version_id not in self.deleted_versions
                    and v.version_id != version_id),
                    None
                )
                metadata.current_version = previous.version_id if previous else None
        else:
            # Delete entire image
            self.deleted_images.add(image_id)
            self.deleted_versions.update(v.version_id for v in metadata.versions)
