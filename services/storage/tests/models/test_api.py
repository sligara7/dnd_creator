"""Tests for API models."""

from datetime import datetime, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError

from storage.models.api import (
    UploadRequest, BulkUploadRequest, UpdateAssetRequest,
    AssetResponse, AssetListResponse, PresignedUrlResponse,
    StorageStatsResponse
)
from storage.models.asset import AssetType


def test_upload_request():
    """Test UploadRequest model."""
    # Test valid data
    data = {
        "filename": "test.png",
        "content_type": "image/png",
        "service": "test_service",
        "owner_id": str(uuid4()),
        "metadata": {"test": "data"},
        "tags": ["test", "png"],
        "asset_type": "IMAGE"
    }
    request = UploadRequest(**data)
    assert request.filename == data["filename"]
    assert request.content_type == data["content_type"]
    assert request.service == data["service"]
    assert str(request.owner_id) == data["owner_id"]
    assert request.metadata == data["metadata"]
    assert request.tags == data["tags"]
    assert request.asset_type == AssetType.IMAGE

    # Test optional fields
    data = {
        "filename": "test.png",
        "content_type": "image/png",
        "service": "test_service",
        "owner_id": str(uuid4())
    }
    request = UploadRequest(**data)
    assert request.metadata is None
    assert request.tags is None
    assert request.asset_type is None

    # Test validation errors
    with pytest.raises(ValidationError):
        UploadRequest()  # Missing required fields

    with pytest.raises(ValidationError):
        UploadRequest(
            filename="test.png",
            content_type="image/png",
            service="test_service",
            owner_id="invalid-uuid"
        )


def test_bulk_upload_request():
    """Test BulkUploadRequest model."""
    # Test valid data
    data = {
        "files": [
            {
                "filename": "test1.png",
                "content_type": "image/png",
                "metadata": {"test": 1}
            },
            {
                "filename": "test2.jpg",
                "content_type": "image/jpeg",
                "tags": ["test"]
            }
        ],
        "service": "test_service",
        "owner_id": str(uuid4()),
        "metadata": {"batch": "test"},
        "tags": ["bulk", "test"]
    }
    request = BulkUploadRequest(**data)
    assert len(request.files) == 2
    assert request.service == data["service"]
    assert str(request.owner_id) == data["owner_id"]
    assert request.metadata == data["metadata"]
    assert request.tags == data["tags"]

    # Test validation errors
    with pytest.raises(ValidationError):
        BulkUploadRequest(
            files=[],  # Empty list
            service="test_service",
            owner_id=str(uuid4())
        )


def test_update_asset_request():
    """Test UpdateAssetRequest model."""
    # Test valid data
    data = {
        "metadata": {"updated": "data"},
        "tags": ["updated", "test"],
        "created_by": str(uuid4())
    }
    request = UpdateAssetRequest(**data)
    assert request.metadata == data["metadata"]
    assert request.tags == data["tags"]
    assert str(request.created_by) == data["created_by"]

    # Test optional fields
    request = UpdateAssetRequest()
    assert request.metadata is None
    assert request.tags is None
    assert request.created_by is None

    # Test validation error
    with pytest.raises(ValidationError):
        UpdateAssetRequest(created_by="invalid-uuid")


def test_asset_response():
    """Test AssetResponse model."""
    # Test valid data
    now = datetime.now(timezone.utc)
    data = {
        "id": str(uuid4()),
        "name": "test.png",
        "service": "test_service",
        "owner_id": str(uuid4()),
        "asset_type": "IMAGE",
        "s3_key": "test/123/test.png",
        "s3_url": "https://storage.test.com/test.png",
        "size": 1024,
        "content_type": "image/png",
        "checksum": "sha256:123",
        "current_version": 1,
        "tags": ["test"],
        "metadata": {"test": "data"},
        "created_at": now,
        "updated_at": now,
        "is_deleted": False,
        "deleted_at": None
    }
    response = AssetResponse(**data)
    assert str(response.id) == data["id"]
    assert response.name == data["name"]
    assert response.service == data["service"]
    assert response.asset_type == AssetType.IMAGE
    assert response.size == data["size"]
    assert response.tags == data["tags"]
    assert response.metadata == data["metadata"]
    assert response.is_deleted == data["is_deleted"]
    assert response.deleted_at == data["deleted_at"]


def test_asset_list_response():
    """Test AssetListResponse model."""
    # Test valid data
    asset_data = {
        "id": str(uuid4()),
        "name": "test.png",
        "service": "test_service",
        "owner_id": str(uuid4()),
        "asset_type": "IMAGE",
        "s3_key": "test/123/test.png",
        "s3_url": "https://storage.test.com/test.png",
        "size": 1024,
        "content_type": "image/png",
        "checksum": "sha256:123",
        "current_version": 1,
        "tags": ["test"],
        "metadata": {"test": "data"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_deleted": False,
        "deleted_at": None
    }
    data = {
        "items": [asset_data],
        "total": 1,
        "limit": 100,
        "offset": 0
    }
    response = AssetListResponse(**data)
    assert len(response.items) == 1
    assert response.total == data["total"]
    assert response.limit == data["limit"]
    assert response.offset == data["offset"]


def test_presigned_url_response():
    """Test PresignedUrlResponse model."""
    # Test valid data
    data = {
        "url": "https://storage.test.com/presigned/test.png",
        "expires_at": datetime.now(timezone.utc)
    }
    response = PresignedUrlResponse(**data)
    assert str(response.url) == data["url"]
    assert response.expires_at == data["expires_at"]

    # Test validation error
    with pytest.raises(ValidationError):
        PresignedUrlResponse(
            url="invalid-url",
            expires_at=datetime.now(timezone.utc)
        )


def test_storage_stats_response():
    """Test StorageStatsResponse model."""
    # Test valid data
    data = {
        "total_assets": 100,
        "total_size": 1024 * 1024,
        "asset_types": {
            "IMAGE": 50,
            "DOCUMENT": 30,
            "AUDIO": 20
        },
        "service_stats": {
            "test_service": {
                "total_assets": 100,
                "total_size": 1024 * 1024
            }
        }
    }
    response = StorageStatsResponse(**data)
    assert response.total_assets == data["total_assets"]
    assert response.total_size == data["total_size"]
    assert response.asset_types == data["asset_types"]
    assert response.service_stats == data["service_stats"]