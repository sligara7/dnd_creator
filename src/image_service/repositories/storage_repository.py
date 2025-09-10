"""
Storage repository interface and implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, BinaryIO
import hashlib
import mimetypes
from uuid import UUID, uuid4

from ..models.storage import (
    ImageFormat,
    ImageMetadata,
    ImageVersion,
    StorageLocation,
    ImageStorageMetadata,
    ImageUploadRequest,
    ImageUploadResponse,
    ImageDownloadResponse
)

class ImageStorageRepository(ABC):
    """Abstract base class for image storage repositories."""

    @abstractmethod
    async def init(self) -> None:
        """Initialize the storage repository."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up storage repository resources."""
        pass

    @abstractmethod
    async def create_upload_request(
        self,
        request: ImageUploadRequest,
        expiration: timedelta = timedelta(minutes=15)
    ) -> ImageUploadResponse:
        """Create a pre-signed upload URL for an image.
        
        Args:
            request: Upload request details
            expiration: URL expiration time
            
        Returns:
            Upload response with URL and metadata
            
        Raises:
            ValueError: If request is invalid
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def complete_upload(
        self,
        image_id: UUID,
        version_id: UUID,
        metadata: ImageMetadata
    ) -> ImageStorageMetadata:
        """Complete an image upload.
        
        Args:
            image_id: Image identifier
            version_id: Version identifier
            metadata: Image metadata
            
        Returns:
            Complete storage metadata
            
        Raises:
            ValueError: If metadata is invalid
            StorageError: If storage operation fails
            NotFoundError: If image or version not found
        """
        pass

    @abstractmethod
    async def get_download_url(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None,
        expiration: timedelta = timedelta(minutes=15)
    ) -> ImageDownloadResponse:
        """Get a pre-signed download URL for an image.
        
        Args:
            image_id: Image identifier
            version_id: Optional specific version to download
            expiration: URL expiration time
            
        Returns:
            Download response with URL and metadata
            
        Raises:
            NotFoundError: If image or version not found
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def delete_image(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None
    ) -> None:
        """Delete an image or specific version.
        
        Args:
            image_id: Image identifier
            version_id: Optional specific version to delete
            
        Raises:
            NotFoundError: If image or version not found
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def list_versions(
        self,
        image_id: UUID
    ) -> List[ImageVersion]:
        """List all versions of an image.
        
        Args:
            image_id: Image identifier
            
        Returns:
            List of image versions
            
        Raises:
            NotFoundError: If image not found
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def get_metadata(
        self,
        image_id: UUID,
        version_id: Optional[UUID] = None
    ) -> ImageStorageMetadata:
        """Get storage metadata for an image.
        
        Args:
            image_id: Image identifier
            version_id: Optional specific version to get metadata for
            
        Returns:
            Image storage metadata
            
        Raises:
            NotFoundError: If image or version not found
            StorageError: If storage operation fails
        """
        pass

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of image data.
        
        Args:
            data: Raw image bytes
            
        Returns:
            Hex-encoded checksum
        """
        return hashlib.sha256(data).hexdigest()

    def _get_mime_type(self, format: str) -> str:
        """Get MIME type for image format.
        
        Args:
            format: Image format string
            
        Returns:
            MIME type string
            
        Raises:
            ValueError: If format is invalid
        """
        mime_type = mimetypes.guess_type(f"image.{format.lower()}")[0]
        if not mime_type:
            raise ValueError(f"Invalid image format: {format}")
        return mime_type

class StorageError(Exception):
    """Base class for storage errors."""
    pass

class NotFoundError(StorageError):
    """Raised when a requested resource is not found."""
    pass
