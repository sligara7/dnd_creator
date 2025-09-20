"""Asset management API endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import json

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from storage.core.database import get_db
from storage.core.exceptions import AssetNotFoundException, ValidationError
from storage.models.api import (
    AssetResponse, AssetListResponse, PresignedUrlResponse,
    StorageStatsResponse, UploadRequest, BulkUploadRequest, UpdateAssetRequest
)
from storage.models.asset import AssetType
from storage.services.asset_service import AssetService
from storage.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def get_asset_service(db: AsyncSession = Depends(get_db)) -> AssetService:
    """Dependency to get the asset service."""
    return AssetService(db)


@router.post("/upload",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    description="Upload a new asset.",
    tags=["Assets"])
async def upload_asset(
    file: UploadFile = File(...),
    filename: str = Form(...),
    content_type: str = Form(...),
    service: str = Form(...),
    owner_id: UUID = Form(...),
    metadata: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    asset_type: Optional[AssetType] = Form(None),
    asset_service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """Upload a new asset."""
    try:
        # Convert form data to proper types
        metadata_dict = json.loads(metadata) if metadata else None
        tags_list = json.loads(tags) if tags else None

        # Create asset
        asset = await asset_service.upload_asset(
            file_data=file.file,
            filename=filename,
            content_type=content_type,
            service=service,
            owner_id=owner_id,
            metadata=metadata_dict,
            tags=tags_list,
            asset_type=asset_type
        )
        return asset

    except Exception as e:
        logger.error(f"Failed to upload asset: {str(e)}")
        raise ValidationError("Failed to upload asset", {"error": str(e)})


@router.post("/bulk-upload",
    response_model=list[AssetResponse],
    status_code=status.HTTP_201_CREATED,
    description="Upload multiple assets in a single request.",
    tags=["Assets"])
async def bulk_upload(
    files: list[UploadFile] = File(...),
    request: BulkUploadRequest = Body(...),
    asset_service: AssetService = Depends(get_asset_service)
) -> list[AssetResponse]:
    """Upload multiple assets."""
    try:
        # Validate request
        if len(files) != len(request.files):
            raise ValidationError(
                "Number of files doesn't match request data",
                {"files_count": len(files), "request_count": len(request.files)}
            )

        # Process uploads
        file_tuples = [
            (file.file, file_req.filename, file_req.content_type)
            for file, file_req in zip(files, request.files)
        ]

        assets = await asset_service.bulk_upload(
            files=file_tuples,
            service=request.service,
            owner_id=request.owner_id,
            metadata=request.metadata,
            tags=request.tags
        )
        return assets

    except Exception as e:
        logger.error(f"Failed to bulk upload assets: {str(e)}")
        raise ValidationError("Failed to bulk upload assets", {"error": str(e)})


@router.get("/{asset_id}",
    response_model=AssetResponse,
    description="Get asset details by ID.",
    tags=["Assets"])
async def get_asset(
    asset_id: UUID,
    asset_service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """Get asset details."""
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise AssetNotFoundException(str(asset_id))
    return asset


@router.get("/{asset_id}/download",
    description="Download an asset file.",
    tags=["Assets"])
async def download_asset(
    asset_id: UUID,
    version: Optional[int] = None,
    asset_service: AssetService = Depends(get_asset_service)
):
    """Download asset file."""
    try:
        file_data, metadata = await asset_service.download_asset(asset_id, version)

        return StreamingResponse(
            file_data,
            media_type=metadata["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{metadata["filename"]}"',
                "Content-Length": str(metadata["size"]),
                "X-Checksum": metadata["checksum"],
                "X-Version": str(metadata["version"])
            }
        )

    except Exception as e:
        logger.error(f"Failed to download asset: {str(e)}")
        raise ValidationError("Failed to download asset", {"error": str(e)})


@router.put("/{asset_id}",
    response_model=AssetResponse,
    description="Update an asset.",
    tags=["Assets"])
async def update_asset(
    asset_id: UUID,
    file: Optional[UploadFile] = None,
    request: UpdateAssetRequest = Body(...),
    asset_service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """Update asset metadata and optionally the file."""
    try:
        file_data = file.file if file else None
        asset = await asset_service.update_asset(
            asset_id=asset_id,
            file_data=file_data,
            metadata=request.metadata,
            tags=request.tags,
            created_by=request.created_by
        )
        if not asset:
            raise AssetNotFoundException(str(asset_id))
        return asset

    except Exception as e:
        logger.error(f"Failed to update asset: {str(e)}")
        raise ValidationError("Failed to update asset", {"error": str(e)})


@router.delete("/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an asset.",
    tags=["Assets"])
async def delete_asset(
    asset_id: UUID,
    hard_delete: bool = Query(False, description="If true, permanently deletes the asset"),
    asset_service: AssetService = Depends(get_asset_service)
):
    """Delete an asset."""
    success = await asset_service.delete_asset(asset_id, hard_delete)
    if not success:
        raise AssetNotFoundException(str(asset_id))


@router.get("",
    response_model=AssetListResponse,
    description="List or search assets.",
    tags=["Assets"])
async def list_assets(
    service: Optional[str] = None,
    owner_id: Optional[UUID] = None,
    asset_type: Optional[AssetType] = None,
    tags: Optional[list[str]] = Query(None),
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    asset_service: AssetService = Depends(get_asset_service)
) -> AssetListResponse:
    """List or search assets."""
    try:
        if search:
            assets = await asset_service.search_assets(
                query=search,
                service=service,
                limit=limit,
                offset=offset
            )
        else:
            assets = await asset_service.list_assets(
                service=service,
                owner_id=owner_id,
                asset_type=asset_type,
                tags=tags,
                limit=limit,
                offset=offset
            )

        total = len(assets)  # In real implementation, get total from service
        
        return AssetListResponse(
            items=assets,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to list assets: {str(e)}")
        raise ValidationError("Failed to list assets", {"error": str(e)})


@router.get("/{asset_id}/presigned-url",
    response_model=PresignedUrlResponse,
    description="Generate a presigned URL for direct asset access.",
    tags=["Assets"])
async def get_presigned_url(
    asset_id: UUID,
    expiration: int = Query(3600, ge=60, le=86400),
    asset_service: AssetService = Depends(get_asset_service)
) -> PresignedUrlResponse:
    """Generate presigned URL."""
    try:
        url = await asset_service.get_presigned_url(asset_id, expiration)
        expires_at = datetime.utcnow() + timedelta(seconds=expiration)

        return PresignedUrlResponse(
            url=url,
            expires_at=expires_at
        )

    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise ValidationError("Failed to generate presigned URL", {"error": str(e)})


@router.get("/stats",
    response_model=StorageStatsResponse,
    description="Get storage statistics.",
    tags=["Assets"])
async def get_storage_stats(
    service: Optional[str] = None,
    asset_service: AssetService = Depends(get_asset_service)
) -> StorageStatsResponse:
    """Get storage statistics."""
    try:
        stats = await asset_service.get_storage_stats(service)
        return StorageStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get storage stats: {str(e)}")
        raise ValidationError("Failed to get storage stats", {"error": str(e)})
