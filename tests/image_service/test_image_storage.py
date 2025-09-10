"""
Tests for image storage functionality.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import hashlib
import os
from unittest.mock import MagicMock

from image_service.models.storage import (
    ImageFormat,
    ImageMetadata,
    ImageVersion,
    StorageLocation,
    ImageStorageMetadata,
    ImageUploadRequest,
    ImageUploadResponse,
    ImageDownloadResponse
)
from image_service.repositories.storage_repository import NotFoundError

@pytest.fixture
def test_image_data() -> bytes:
    """Generate test image data."""
    # Create a small test pattern
    data = bytearray()
    for i in range(256):
        data.extend([i % 256] * 256)  # 64KB test pattern
    return bytes(data)

@pytest.fixture
def test_image_format() -> ImageFormat:
    """Create test image format."""
    return ImageFormat(
        format="PNG",
        quality=None,  # Lossless
        progressive=False,
        lossless=True
    )

@pytest.fixture
def test_image_metadata(test_image_data: bytes, test_image_format: ImageFormat) -> ImageMetadata:
    """Create test image metadata."""
    return ImageMetadata(
        width=256,
        height=256,
        size_bytes=len(test_image_data),
        mime_type="image/png",
        checksum=hashlib.sha256(test_image_data).hexdigest(),
        compression=test_image_format
    )

@pytest.fixture
def test_storage_location() -> StorageLocation:
    """Create test storage location."""
    return StorageLocation(
        bucket="test-bucket",
        key="test/image.png",
        region="test-region-1",
        version_id="test-version-1"
    )

@pytest.mark.asyncio
class TestImageStorage:
    async def test_create_upload_request(
        self,
        storage_repository,
        test_image_format: ImageFormat
    ):
        """Test creating an upload request."""
        # Prepare test data
        image_id = uuid4()
        request = ImageUploadRequest(
            image_id=image_id,
            format=test_image_format,
            tags={"purpose": "test"}
        )
        
        # Create upload request
        response = await storage_repository.create_upload_request(request)
        
        # Verify response
        assert isinstance(response, ImageUploadResponse)
        assert response.storage_metadata.image_id == image_id
        assert response.storage_metadata.storage.bucket == "test-bucket"
        assert "test" in response.storage_metadata.storage.key
        assert response.upload_url.startswith("http")
        assert "Authorization" in response.headers

    async def test_complete_upload(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test completing an upload."""
        # Prepare test data
        image_id = uuid4()
        version_id = uuid4()
        
        # Complete upload
        metadata = await storage_repository.complete_upload(
            image_id=image_id,
            version_id=version_id,
            metadata=test_image_metadata
        )
        
        # Verify metadata
        assert isinstance(metadata, ImageStorageMetadata)
        assert metadata.image_id == image_id
        assert metadata.current_version == version_id
        assert len(metadata.versions) == 1
        assert metadata.versions[0].version_id == version_id
        assert metadata.versions[0].metadata == test_image_metadata

    async def test_download_url(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test getting a download URL."""
        # Prepare test data
        image_id = uuid4()
        version_id = uuid4()
        await storage_repository.complete_upload(
            image_id=image_id,
            version_id=version_id,
            metadata=test_image_metadata
        )
        
        # Get download URL
        response = await storage_repository.get_download_url(
            image_id=image_id,
            version_id=version_id
        )
        
        # Verify response
        assert isinstance(response, ImageDownloadResponse)
        assert response.storage_metadata.image_id == image_id
        assert response.download_url.startswith("http")
        assert "Authorization" in response.headers
        assert response.expiration > datetime.utcnow()

    async def test_list_versions(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test listing image versions."""
        # Prepare test data
        image_id = uuid4()
        version_ids = [uuid4(), uuid4(), uuid4()]
        
        # Create multiple versions
        for version_id in version_ids:
            await storage_repository.complete_upload(
                image_id=image_id,
                version_id=version_id,
                metadata=test_image_metadata
            )
        
        # List versions
        versions = await storage_repository.list_versions(image_id)
        
        # Verify versions
        assert len(versions) == len(version_ids)
        assert all(isinstance(v, ImageVersion) for v in versions)
        assert all(v.version_id in version_ids for v in versions)
        assert all(v.metadata == test_image_metadata for v in versions)

    async def test_delete_image(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test deleting an image."""
        # Prepare test data
        image_id = uuid4()
        version_id = uuid4()
        await storage_repository.complete_upload(
            image_id=image_id,
            version_id=version_id,
            metadata=test_image_metadata
        )
        
        # Delete image
        await storage_repository.delete_image(image_id)
        
        # Verify deletion
        with pytest.raises(NotFoundError):
            await storage_repository.get_metadata(image_id)

    async def test_delete_version(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test deleting a specific version."""
        # Prepare test data
        image_id = uuid4()
        version_ids = [uuid4(), uuid4()]
        
        # Create multiple versions
        for version_id in version_ids:
            await storage_repository.complete_upload(
                image_id=image_id,
                version_id=version_id,
                metadata=test_image_metadata
            )
        
        # Delete first version
        await storage_repository.delete_image(
            image_id=image_id,
            version_id=version_ids[0]
        )
        
        # Verify remaining version
        versions = await storage_repository.list_versions(image_id)
        assert len(versions) == 1
        assert versions[0].version_id == version_ids[1]

    async def test_invalid_format(
        self,
        storage_repository
    ):
        """Test handling invalid image format."""
        # Prepare test data with invalid format
        request = ImageUploadRequest(
            image_id=uuid4(),
            format=ImageFormat(
                format="INVALID",
                lossless=True
            )
        )
        
        # Verify error handling
        with pytest.raises(ValueError) as exc_info:
            await storage_repository.create_upload_request(request)
        assert "Invalid image format" in str(exc_info.value)

    async def test_not_found_errors(
        self,
        storage_repository
    ):
        """Test handling not found errors."""
        image_id = uuid4()
        version_id = uuid4()

        # Add version to deleted versions
        storage_repository.deleted_versions.add(version_id)
        
        # Test various not found scenarios
        with pytest.raises(NotFoundError):
            await storage_repository.get_metadata(image_id)
        
        with pytest.raises(NotFoundError):
            await storage_repository.get_download_url(image_id)
        
        with pytest.raises(NotFoundError):
            await storage_repository.list_versions(image_id)
        
        with pytest.raises(NotFoundError):
            await storage_repository.delete_image(image_id)
        
        with pytest.raises(NotFoundError):
            await storage_repository.complete_upload(
                image_id=image_id,
                version_id=version_id,
                metadata=ImageMetadata(
                    width=100,
                    height=100,
                    size_bytes=10000,
                    mime_type="image/png",
                    checksum="test"
                )
            )

@pytest.mark.asyncio
class TestImageStorageOptimization:
    async def test_compression_settings(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test image compression settings."""
        # Test lossy compression
        format_lossy = ImageFormat(
            format="JPEG",
            quality=85,
            progressive=True,
            lossless=False
        )
        
        # Create upload request with lossy format
        request = ImageUploadRequest(
            image_id=uuid4(),
            format=format_lossy
        )
        
        response = await storage_repository.create_upload_request(request)
        assert response.storage_metadata.metadata.compression == format_lossy
        
        # Test lossless compression
        format_lossless = ImageFormat(
            format="PNG",
            lossless=True
        )
        
        request = ImageUploadRequest(
            image_id=uuid4(),
            format=format_lossless
        )
        
        response = await storage_repository.create_upload_request(request)
        assert response.storage_metadata.metadata.compression == format_lossless

    async def test_versioning(
        self,
        storage_repository,
        test_image_metadata: ImageMetadata
    ):
        """Test image versioning."""
        image_id = uuid4()
        parent_id = None
        version_chain = []
        
        # Create version chain
        for i in range(3):
            version_id = uuid4()
            version_chain.append(version_id)
            
            # Update metadata for each version
            new_metadata = ImageMetadata(
                width=test_image_metadata.width,
                height=test_image_metadata.height,
                size_bytes=test_image_metadata.size_bytes,
                mime_type=test_image_metadata.mime_type,
                checksum=test_image_metadata.checksum,
                created_at=datetime.utcnow() + timedelta(minutes=i),
                compression=test_image_metadata.compression
            )
            
            # Complete upload with parent reference
            result = await storage_repository.complete_upload(
                image_id=image_id,
                version_id=version_id,
                metadata=new_metadata
            )
            
            if parent_id:
                version = next(
                    v for v in result.versions 
                    if v.version_id == version_id
                )
                assert version.parent_id == parent_id
            
            parent_id = version_id
        
        # Verify version chain
        versions = await storage_repository.list_versions(image_id)
        assert len(versions) == 3
        
        for i, version in enumerate(versions):
            if i > 0:
                assert version.parent_id == version_chain[i - 1]
            else:
                assert version.parent_id is None
