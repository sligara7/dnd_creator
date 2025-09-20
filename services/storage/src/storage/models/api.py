"""API models for storage service."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from .asset import AssetType


class UploadRequest(BaseModel):
    """Request model for asset upload."""
    filename: str = Field(..., description="Original filename of the asset")
    content_type: str = Field(..., description="MIME type of the asset")
    service: str = Field(..., description="Service identifier requesting storage")
    owner_id: UUID = Field(..., description="ID of the asset owner")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the asset")
    tags: Optional[List[str]] = Field(None, description="Optional tags for the asset")
    asset_type: Optional[AssetType] = Field(None, description="Type of asset, inferred from content_type if not provided")


class BulkUploadRequest(BaseModel):
    """Request model for bulk asset upload."""
    files: List[UploadRequest] = Field(..., description="List of files to upload", min_items=1)
    service: str = Field(..., description="Service identifier requesting storage")
    owner_id: UUID = Field(..., description="ID of the assets owner")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for all assets")
    tags: Optional[List[str]] = Field(None, description="Optional tags for all assets")


class UpdateAssetRequest(BaseModel):
    """Request model for asset update."""
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata for the asset")
    tags: Optional[List[str]] = Field(None, description="Updated tags for the asset")
    created_by: Optional[UUID] = Field(None, description="ID of user performing the update")


class AssetResponse(BaseModel):
    """Response model for asset details."""
    id: UUID = Field(..., description="Unique identifier of the asset")
    name: str = Field(..., description="Asset filename")
    service: str = Field(..., description="Service identifier that owns the asset")
    owner_id: UUID = Field(..., description="ID of the asset owner")
    asset_type: AssetType = Field(..., description="Type of asset")
    s3_key: str = Field(..., description="S3 storage key")
    s3_url: HttpUrl = Field(..., description="Full S3 URL")
    size: int = Field(..., description="Size in bytes")
    content_type: str = Field(..., description="MIME type")
    checksum: str = Field(..., description="SHA256 checksum")
    current_version: int = Field(..., description="Current version number")
    tags: List[str] = Field(default_factory=list, description="Asset tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Asset metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Soft delete status")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp if deleted")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True


class AssetListResponse(BaseModel):
    """Response model for asset list operations."""
    items: List[AssetResponse] = Field(..., description="List of assets")
    total: int = Field(..., description="Total number of assets matching query")
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Offset from start of results")


class PresignedUrlResponse(BaseModel):
    """Response model for presigned URL generation."""
    url: HttpUrl = Field(..., description="Presigned URL for direct asset access")
    expires_at: datetime = Field(..., description="URL expiration timestamp")


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics."""
    total_assets: int = Field(..., description="Total number of assets")
    total_size: int = Field(..., description="Total size in bytes")
    asset_types: Dict[AssetType, int] = Field(..., description="Count by asset type")
    service_stats: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Stats by service if specified")