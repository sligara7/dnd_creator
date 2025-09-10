"""
Image storage models.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

class ImageFormat(BaseModel):
    """Image format and compression settings."""
    format: str = Field(..., description="Image format (PNG, JPEG, WebP)")
    quality: Optional[int] = Field(None, ge=1, le=100, description="Compression quality (1-100)")
    progressive: bool = Field(False, description="Use progressive encoding")
    lossless: bool = Field(True, description="Use lossless compression")

class ImageMetadata(BaseModel):
    """Image metadata."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    size_bytes: int = Field(..., description="Size in bytes")
    mime_type: str = Field(..., description="MIME type")
    checksum: str = Field(..., description="Image data checksum")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    compression: Optional[ImageFormat] = None

class ImageVersion(BaseModel):
    """Image version information."""
    version_id: UUID = Field(..., description="Version identifier")
    parent_id: Optional[UUID] = Field(None, description="Parent version ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: ImageMetadata = Field(..., description="Version metadata")
    tags: Dict[str, str] = Field(default_factory=dict)

class StorageLocation(BaseModel):
    """Storage location information."""
    bucket: str = Field(..., description="Storage bucket name")
    key: str = Field(..., description="Storage object key")
    region: Optional[str] = Field(None, description="Storage region")
    version_id: Optional[str] = Field(None, description="Storage version ID")

class ImageStorageMetadata(BaseModel):
    """Complete storage metadata for an image."""
    image_id: UUID = Field(..., description="Image identifier")
    character_id: Optional[UUID] = Field(None, description="Associated character ID")
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign ID")
    encounter_id: Optional[UUID] = Field(None, description="Associated encounter ID")
    current_version: Optional[UUID] = Field(None, description="Current version ID")
    versions: List[ImageVersion] = Field(default_factory=list)
    storage: StorageLocation = Field(..., description="Storage location")
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: ImageMetadata = Field(..., description="Image metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ImageUploadRequest(BaseModel):
    """Request to upload an image."""
    image_id: UUID = Field(..., description="Image identifier")
    character_id: Optional[UUID] = Field(None, description="Associated character ID")
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign ID")
    encounter_id: Optional[UUID] = Field(None, description="Associated encounter ID")
    format: ImageFormat = Field(..., description="Image format settings")
    tags: Dict[str, str] = Field(default_factory=dict)

class ImageUploadResponse(BaseModel):
    """Response from image upload."""
    storage_metadata: ImageStorageMetadata = Field(..., description="Storage metadata")
    upload_url: str = Field(..., description="Pre-signed upload URL")
    headers: Dict[str, str] = Field(..., description="Headers for upload")

class ImageDownloadResponse(BaseModel):
    """Response for image download."""
    storage_metadata: ImageStorageMetadata = Field(..., description="Storage metadata")
    download_url: str = Field(..., description="Pre-signed download URL")
    headers: Dict[str, str] = Field(..., description="Headers for download")
    expiration: datetime = Field(..., description="URL expiration time")
