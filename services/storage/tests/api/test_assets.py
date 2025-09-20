"""Tests for asset management API endpoints."""

import io
import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from storage.models.api import AssetResponse
from storage.models.asset import Asset, AssetType


def create_test_file() -> tuple[io.BytesIO, str, str]:
    """Create a test file for upload."""
    file_content = b"test file content"
    return io.BytesIO(file_content), "test.txt", "text/plain"


@pytest.mark.asyncio
async def test_upload_asset(test_client: AsyncClient):
    """Test upload asset endpoint."""
    file, filename, content_type = create_test_file()
    owner_id = str(uuid4())
    metadata = {"test": "data"}
    tags = ["test", "file"]

    files = {
        "file": (filename, file, content_type),
        "filename": (None, filename),
        "content_type": (None, content_type),
        "service": (None, "test_service"),
        "owner_id": (None, owner_id),
        "metadata": (None, json.dumps(metadata)),
        "tags": (None, json.dumps(tags))
    }

    response = await test_client.post("/assets/upload", files=files)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == filename
    assert data["content_type"] == content_type
    assert data["service"] == "test_service"
    assert data["owner_id"] == owner_id
    assert data["metadata"] == metadata
    assert data["tags"] == tags


@pytest.mark.asyncio
async def test_upload_asset_validation_error(test_client: AsyncClient):
    """Test upload asset endpoint with invalid data."""
    # Missing required fields
    files = {
        "file": ("test.txt", io.BytesIO(b"test"), "text/plain")
    }

    response = await test_client.post("/assets/upload", files=files)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_bulk_upload(test_client: AsyncClient):
    """Test bulk upload endpoint."""
    owner_id = str(uuid4())
    files = [create_test_file(), create_test_file()]
    
    file_data = {
        "files": [
            {"filename": "test1.txt", "content_type": "text/plain"},
            {"filename": "test2.txt", "content_type": "text/plain"}
        ],
        "service": "test_service",
        "owner_id": owner_id,
        "metadata": {"batch": "test"},
        "tags": ["test", "bulk"]
    }

    upload_files = {
        f"files.{i}": (file[0], file[1], file[2])
        for i, file in enumerate(files)
    }

    response = await test_client.post(
        "/assets/bulk-upload",
        files=upload_files,
        data={"request": json.dumps(file_data)}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 2
    for asset in data:
        assert asset["service"] == "test_service"
        assert asset["owner_id"] == owner_id


@pytest.mark.asyncio
async def test_get_asset(test_client: AsyncClient, db_asset: Asset):
    """Test get asset endpoint."""
    response = await test_client.get(f"/assets/{db_asset.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(db_asset.id)
    assert data["name"] == db_asset.name
    assert data["service"] == db_asset.service


@pytest.mark.asyncio
async def test_get_asset_not_found(test_client: AsyncClient):
    """Test get asset endpoint with non-existent asset."""
    response = await test_client.get(f"/assets/{uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "message" in data
    assert "Asset not found" in data["message"]


@pytest.mark.asyncio
async def test_update_asset(test_client: AsyncClient, db_asset: Asset):
    """Test update asset endpoint."""
    update_data = {
        "metadata": {"updated": "data"},
        "tags": ["updated", "test"],
        "created_by": str(uuid4())
    }

    response = await test_client.put(
        f"/assets/{db_asset.id}",
        json=update_data
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(db_asset.id)
    assert data["metadata"] == update_data["metadata"]
    assert data["tags"] == update_data["tags"]


@pytest.mark.asyncio
async def test_delete_asset(test_client: AsyncClient, db_asset: Asset):
    """Test delete asset endpoint."""
    response = await test_client.delete(f"/assets/{db_asset.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify asset is deleted
    get_response = await test_client.get(f"/assets/{db_asset.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_assets(test_client: AsyncClient, db_asset: Asset):
    """Test list assets endpoint."""
    response = await test_client.get("/assets")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any(item["id"] == str(db_asset.id) for item in data["items"])


@pytest.mark.asyncio
async def test_list_assets_with_filters(test_client: AsyncClient, db_asset: Asset):
    """Test list assets endpoint with filters."""
    response = await test_client.get(
        "/assets",
        params={
            "service": db_asset.service,
            "asset_type": db_asset.asset_type.value,
            "tags": db_asset.tags
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 1
    assert any(item["id"] == str(db_asset.id) for item in data["items"])


@pytest.mark.asyncio
async def test_search_assets(test_client: AsyncClient, db_asset: Asset):
    """Test search assets endpoint."""
    response = await test_client.get(
        "/assets",
        params={"search": db_asset.name}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 1
    assert any(item["id"] == str(db_asset.id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_presigned_url(test_client: AsyncClient, db_asset: Asset):
    """Test get presigned URL endpoint."""
    response = await test_client.get(
        f"/assets/{db_asset.id}/presigned-url",
        params={"expiration": 3600}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_get_storage_stats(test_client: AsyncClient, db_asset: Asset):
    """Test get storage statistics endpoint."""
    response = await test_client.get("/assets/stats")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_assets" in data
    assert "total_size" in data
    assert "asset_types" in data


@pytest.mark.asyncio
async def test_validation_errors(test_client: AsyncClient):
    """Test various validation error scenarios."""
    # Invalid UUID
    response = await test_client.get("/assets/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid page parameters
    response = await test_client.get("/assets", params={"limit": 0})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await test_client.get("/assets", params={"offset": -1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid expiration for presigned URL
    response = await test_client.get(
        f"/assets/{uuid4()}/presigned-url",
        params={"expiration": 30}  # Too short
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY