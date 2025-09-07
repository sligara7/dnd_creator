"""Asset Service for storage operations."""

import hashlib
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.asset import AssetRepository
from ..repositories.version import VersionRepository
from ..integrations.s3_client import S3StorageClient
from ..models.asset import Asset, AssetType
from ..models.version import AssetVersion
from ..core.config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AssetService:
    """Service for asset management operations."""
    
    def __init__(self, db: AsyncSession, s3_client: Optional[S3StorageClient] = None):
        """Initialize service with dependencies."""
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.version_repo = VersionRepository(db)
        self.s3_client = s3_client or S3StorageClient()
    
    async def upload_asset(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: str,
        service: str,
        owner_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        asset_type: Optional[AssetType] = None
    ) -> Asset:
        """Upload a new asset with deduplication."""
        try:
            # Read file data
            file_bytes = file_data.read()
            file_size = len(file_bytes)
            
            # Calculate checksum for deduplication
            checksum = hashlib.sha256(file_bytes).hexdigest()
            
            # Check for existing asset with same checksum
            existing_asset = await self.asset_repo.get_by_checksum(checksum)
            if existing_asset:
                logger.info(f"Asset already exists with checksum {checksum}")
                # Update metadata if different owner/service
                if existing_asset.owner_id != owner_id or existing_asset.service != service:
                    # Create a reference rather than duplicate
                    metadata = metadata or {}
                    metadata['original_asset_id'] = str(existing_asset.id)
                    metadata['deduplicated'] = True
                
                return existing_asset
            
            # Generate S3 key
            s3_key = self._generate_s3_key(service, owner_id, filename)
            
            # Upload to S3
            s3_url = await self.s3_client.upload(
                key=s3_key,
                data=io.BytesIO(file_bytes),
                content_type=content_type,
                metadata={
                    'service': service,
                    'owner_id': str(owner_id),
                    'checksum': checksum
                }
            )
            
            # Determine asset type
            if not asset_type:
                asset_type = self._determine_asset_type(content_type)
            
            # Create asset record
            asset_data = {
                'name': filename,
                'service': service,
                'owner_id': owner_id,
                'asset_type': asset_type,
                's3_key': s3_key,
                's3_url': s3_url,
                'size': file_size,
                'content_type': content_type,
                'checksum': checksum,
                'tags': tags or [],
                'metadata': metadata or {}
            }
            
            asset = await self.asset_repo.create(asset_data)
            
            # Create initial version
            version_data = {
                'asset_id': asset.id,
                'version_number': 1,
                's3_key': s3_key,
                'size': file_size,
                'checksum': checksum,
                'created_by': owner_id,
                'metadata': {'initial': True}
            }
            
            await self.version_repo.create(version_data)
            await self.db.commit()
            
            logger.info(f"Successfully uploaded asset {asset.id}")
            return asset
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to upload asset: {str(e)}")
            raise
    
    async def download_asset(
        self,
        asset_id: UUID,
        version: Optional[int] = None
    ) -> Tuple[BinaryIO, Dict[str, Any]]:
        """Download an asset."""
        try:
            # Get asset
            asset = await self.asset_repo.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Determine which version to download
            if version:
                version_obj = await self.version_repo.get_by_asset_and_number(
                    asset_id, version
                )
                if not version_obj:
                    raise ValueError(f"Version {version} not found for asset {asset_id}")
                s3_key = version_obj.s3_key
            else:
                s3_key = asset.s3_key
            
            # Download from S3
            file_data = await self.s3_client.download(s3_key)
            
            # Prepare metadata
            metadata = {
                'filename': asset.name,
                'content_type': asset.content_type,
                'size': asset.size,
                'checksum': asset.checksum,
                'version': version or 'latest'
            }
            
            logger.info(f"Downloaded asset {asset_id} (version: {version or 'latest'})")
            return file_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to download asset {asset_id}: {str(e)}")
            raise
    
    async def update_asset(
        self,
        asset_id: UUID,
        file_data: Optional[BinaryIO] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[UUID] = None
    ) -> Asset:
        """Update an asset, creating a new version if file changes."""
        try:
            # Get existing asset
            asset = await self.asset_repo.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            updates = {}
            
            # Handle file update (creates new version)
            if file_data:
                file_bytes = file_data.read()
                file_size = len(file_bytes)
                checksum = hashlib.sha256(file_bytes).hexdigest()
                
                # Only create new version if content changed
                if checksum != asset.checksum:
                    # Get next version number
                    version_number = await self.version_repo.get_next_version_number(asset_id)
                    
                    # Generate new S3 key for version
                    s3_key = self._generate_versioned_s3_key(
                        asset.service,
                        asset.owner_id,
                        asset.name,
                        version_number
                    )
                    
                    # Upload new version to S3
                    s3_url = await self.s3_client.upload(
                        key=s3_key,
                        data=io.BytesIO(file_bytes),
                        content_type=asset.content_type,
                        metadata={
                            'service': asset.service,
                            'owner_id': str(asset.owner_id),
                            'checksum': checksum,
                            'version': str(version_number)
                        }
                    )
                    
                    # Create version record
                    version_data = {
                        'asset_id': asset_id,
                        'version_number': version_number,
                        's3_key': s3_key,
                        'size': file_size,
                        'checksum': checksum,
                        'created_by': created_by or asset.owner_id,
                        'metadata': {'updated': True}
                    }
                    
                    await self.version_repo.create(version_data)
                    
                    # Update asset with new file info
                    updates['s3_key'] = s3_key
                    updates['s3_url'] = s3_url
                    updates['size'] = file_size
                    updates['checksum'] = checksum
                    updates['current_version'] = version_number
            
            # Update metadata
            if metadata is not None:
                current_metadata = asset.metadata or {}
                current_metadata.update(metadata)
                updates['metadata'] = current_metadata
            
            # Update tags
            if tags is not None:
                updates['tags'] = tags
            
            # Apply updates
            if updates:
                asset = await self.asset_repo.update(asset_id, updates)
                await self.db.commit()
            
            logger.info(f"Updated asset {asset_id}")
            return asset
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update asset {asset_id}: {str(e)}")
            raise
    
    async def delete_asset(
        self,
        asset_id: UUID,
        hard_delete: bool = False
    ) -> bool:
        """Delete an asset (soft delete by default)."""
        try:
            if hard_delete:
                # Get asset for S3 cleanup
                asset = await self.asset_repo.get(asset_id, include_deleted=True)
                if not asset:
                    return False
                
                # Delete from S3
                await self.s3_client.delete(asset.s3_key)
                
                # Delete all version files from S3
                versions = await self.version_repo.list_by_asset(asset_id)
                for version in versions:
                    if version.s3_key != asset.s3_key:  # Don't delete twice
                        await self.s3_client.delete(version.s3_key)
                
                # Hard delete from database
                # This would require a hard_delete method in repository
                # For now, we'll use soft delete
                success = await self.asset_repo.soft_delete(asset_id)
            else:
                # Soft delete
                success = await self.asset_repo.soft_delete(asset_id)
            
            if success:
                await self.db.commit()
                logger.info(f"Deleted asset {asset_id} (hard: {hard_delete})")
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete asset {asset_id}: {str(e)}")
            raise
    
    async def restore_asset(self, asset_id: UUID) -> Optional[Asset]:
        """Restore a soft-deleted asset."""
        try:
            asset = await self.asset_repo.restore(asset_id)
            if asset:
                await self.db.commit()
                logger.info(f"Restored asset {asset_id}")
            return asset
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to restore asset {asset_id}: {str(e)}")
            raise
    
    async def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        """Get asset by ID."""
        return await self.asset_repo.get(asset_id)
    
    async def list_assets(
        self,
        service: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        asset_type: Optional[AssetType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Asset]:
        """List assets with filters."""
        return await self.asset_repo.list(
            service=service,
            owner_id=owner_id,
            asset_type=asset_type,
            tags=tags,
            limit=limit,
            offset=offset
        )
    
    async def search_assets(
        self,
        query: str,
        service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Asset]:
        """Search assets by name or metadata."""
        return await self.asset_repo.search(
            query_str=query,
            service=service,
            limit=limit,
            offset=offset
        )
    
    async def get_storage_stats(
        self,
        service: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get storage statistics."""
        return await self.asset_repo.get_storage_stats(service)
    
    async def bulk_upload(
        self,
        files: List[Tuple[BinaryIO, str, str]],
        service: str,
        owner_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> List[Asset]:
        """Bulk upload multiple assets."""
        try:
            assets = []
            
            for file_data, filename, content_type in files:
                asset = await self.upload_asset(
                    file_data=file_data,
                    filename=filename,
                    content_type=content_type,
                    service=service,
                    owner_id=owner_id,
                    metadata=metadata,
                    tags=tags
                )
                assets.append(asset)
            
            logger.info(f"Bulk uploaded {len(assets)} assets")
            return assets
            
        except Exception as e:
            logger.error(f"Failed to bulk upload assets: {str(e)}")
            raise
    
    async def bulk_delete(
        self,
        asset_ids: List[UUID],
        hard_delete: bool = False
    ) -> int:
        """Bulk delete multiple assets."""
        try:
            if hard_delete:
                # Delete S3 objects for each asset
                for asset_id in asset_ids:
                    asset = await self.asset_repo.get(asset_id, include_deleted=True)
                    if asset:
                        await self.s3_client.delete(asset.s3_key)
            
            # Perform bulk soft delete
            deleted_count = await self.asset_repo.bulk_delete(asset_ids)
            
            if deleted_count > 0:
                await self.db.commit()
                logger.info(f"Bulk deleted {deleted_count} assets")
            
            return deleted_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to bulk delete assets: {str(e)}")
            raise
    
    async def get_presigned_url(
        self,
        asset_id: UUID,
        expiration: int = 3600
    ) -> str:
        """Generate a presigned URL for direct asset access."""
        try:
            asset = await self.asset_repo.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            url = await self.s3_client.generate_presigned_url(
                key=asset.s3_key,
                expiration=expiration
            )
            
            logger.debug(f"Generated presigned URL for asset {asset_id}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def _generate_s3_key(
        self,
        service: str,
        owner_id: UUID,
        filename: str
    ) -> str:
        """Generate S3 key for an asset."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = uuid4().hex[:8]
        return f"{service}/{owner_id}/{timestamp}/{unique_id}_{filename}"
    
    def _generate_versioned_s3_key(
        self,
        service: str,
        owner_id: UUID,
        filename: str,
        version: int
    ) -> str:
        """Generate S3 key for a versioned asset."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = uuid4().hex[:8]
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            versioned_name = f"{name}_v{version}.{ext}"
        else:
            versioned_name = f"{filename}_v{version}"
        return f"{service}/{owner_id}/{timestamp}/{unique_id}_{versioned_name}"
    
    def _determine_asset_type(self, content_type: str) -> AssetType:
        """Determine asset type from content type."""
        if content_type.startswith('image/'):
            return AssetType.IMAGE
        elif content_type == 'application/pdf':
            return AssetType.DOCUMENT
        elif content_type.startswith('audio/'):
            return AssetType.AUDIO
        elif content_type.startswith('video/'):
            return AssetType.VIDEO
        elif content_type in ['application/zip', 'application/x-tar', 'application/gzip']:
            return AssetType.ARCHIVE
        else:
            return AssetType.OTHER
