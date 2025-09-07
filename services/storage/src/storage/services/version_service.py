"""Version Service for version control operations."""

from datetime import datetime
from typing import Dict, List, Optional, Any, BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.version import VersionRepository
from ..repositories.asset import AssetRepository
from ..integrations.s3_client import S3StorageClient
from ..models.version import AssetVersion
from ..utils.logging import get_logger

logger = get_logger(__name__)


class VersionService:
    """Service for version control operations."""
    
    def __init__(self, db: AsyncSession, s3_client: Optional[S3StorageClient] = None):
        """Initialize service with dependencies."""
        self.db = db
        self.version_repo = VersionRepository(db)
        self.asset_repo = AssetRepository(db)
        self.s3_client = s3_client or S3StorageClient()
    
    async def create_version(
        self,
        asset_id: UUID,
        s3_key: str,
        size: int,
        checksum: str,
        created_by: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssetVersion:
        """Create a new version for an asset."""
        try:
            # Get next version number
            version_number = await self.version_repo.get_next_version_number(asset_id)
            
            # Create version record
            version_data = {
                'asset_id': asset_id,
                'version_number': version_number,
                's3_key': s3_key,
                'size': size,
                'checksum': checksum,
                'created_by': created_by,
                'metadata': metadata or {}
            }
            
            version = await self.version_repo.create(version_data)
            await self.db.commit()
            
            logger.info(f"Created version {version_number} for asset {asset_id}")
            return version
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create version: {str(e)}")
            raise
    
    async def get_version(self, version_id: UUID) -> Optional[AssetVersion]:
        """Get a specific version by ID."""
        return await self.version_repo.get(version_id)
    
    async def get_version_by_number(
        self,
        asset_id: UUID,
        version_number: int
    ) -> Optional[AssetVersion]:
        """Get a specific version of an asset by version number."""
        return await self.version_repo.get_by_asset_and_number(asset_id, version_number)
    
    async def list_versions(
        self,
        asset_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[AssetVersion]:
        """List all versions of an asset."""
        return await self.version_repo.list_by_asset(asset_id, limit, offset)
    
    async def get_latest_version(self, asset_id: UUID) -> Optional[AssetVersion]:
        """Get the latest version of an asset."""
        return await self.version_repo.get_latest(asset_id)
    
    async def rollback_to_version(
        self,
        asset_id: UUID,
        version_number: int,
        created_by: UUID
    ) -> AssetVersion:
        """Rollback an asset to a specific version."""
        try:
            # Get the target version
            target_version = await self.version_repo.get_by_asset_and_number(
                asset_id, version_number
            )
            if not target_version:
                raise ValueError(f"Version {version_number} not found for asset {asset_id}")
            
            # Get the asset
            asset = await self.asset_repo.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Create a new version that's a copy of the target version
            new_version_number = await self.version_repo.get_next_version_number(asset_id)
            
            # Copy the S3 object to a new key
            new_s3_key = f"{target_version.s3_key}_rollback_v{new_version_number}"
            await self.s3_client.copy_object(target_version.s3_key, new_s3_key)
            
            # Create new version record
            version_data = {
                'asset_id': asset_id,
                'version_number': new_version_number,
                's3_key': new_s3_key,
                'size': target_version.size,
                'checksum': target_version.checksum,
                'created_by': created_by,
                'metadata': {
                    'rollback': True,
                    'rollback_from': version_number,
                    'rollback_at': datetime.utcnow().isoformat()
                }
            }
            
            new_version = await self.version_repo.create(version_data)
            
            # Update asset to point to new version
            await self.asset_repo.update(asset_id, {
                's3_key': new_s3_key,
                'size': target_version.size,
                'checksum': target_version.checksum,
                'current_version': new_version_number
            })
            
            await self.db.commit()
            
            logger.info(f"Rolled back asset {asset_id} to version {version_number}")
            return new_version
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to rollback version: {str(e)}")
            raise
    
    async def compare_versions(
        self,
        version_id1: UUID,
        version_id2: UUID
    ) -> Dict[str, Any]:
        """Compare two versions of an asset."""
        return await self.version_repo.compare_versions(version_id1, version_id2)
    
    async def delete_version(self, version_id: UUID) -> bool:
        """Soft delete a specific version."""
        try:
            success = await self.version_repo.soft_delete(version_id)
            if success:
                await self.db.commit()
                logger.info(f"Deleted version {version_id}")
            return success
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete version: {str(e)}")
            raise
    
    async def prune_old_versions(
        self,
        asset_id: UUID,
        keep_count: int = 10
    ) -> int:
        """Prune old versions of an asset, keeping the most recent ones."""
        try:
            pruned_count = await self.version_repo.prune_old_versions(
                asset_id, keep_count
            )
            
            if pruned_count > 0:
                await self.db.commit()
                logger.info(f"Pruned {pruned_count} old versions for asset {asset_id}")
            
            return pruned_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to prune versions: {str(e)}")
            raise
    
    async def download_version(
        self,
        version_id: UUID
    ) -> tuple[BinaryIO, Dict[str, Any]]:
        """Download a specific version of an asset."""
        try:
            version = await self.version_repo.get(version_id)
            if not version:
                raise ValueError(f"Version {version_id} not found")
            
            # Download from S3
            file_data = await self.s3_client.download(version.s3_key)
            
            # Get asset for metadata
            asset = await self.asset_repo.get(version.asset_id)
            
            metadata = {
                'version_id': str(version.id),
                'version_number': version.version_number,
                'asset_id': str(version.asset_id),
                'asset_name': asset.name if asset else 'unknown',
                'size': version.size,
                'checksum': version.checksum,
                'created_at': version.created_at.isoformat()
            }
            
            return file_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to download version {version_id}: {str(e)}")
            raise
    
    async def get_version_history(
        self,
        asset_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get the complete version history of an asset."""
        try:
            versions = await self.version_repo.list_by_asset(asset_id)
            
            history = []
            for version in versions:
                history.append({
                    'version_id': str(version.id),
                    'version_number': version.version_number,
                    'size': version.size,
                    'checksum': version.checksum,
                    'created_at': version.created_at.isoformat(),
                    'created_by': str(version.created_by),
                    'metadata': version.metadata
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get version history: {str(e)}")
            raise
    
    async def tag_version(
        self,
        version_id: UUID,
        tag: str,
        description: Optional[str] = None
    ) -> AssetVersion:
        """Tag a specific version for easy reference."""
        try:
            version = await self.version_repo.get(version_id)
            if not version:
                raise ValueError(f"Version {version_id} not found")
            
            # Update metadata with tag
            metadata = version.metadata or {}
            if 'tags' not in metadata:
                metadata['tags'] = []
            
            tag_entry = {
                'name': tag,
                'description': description,
                'tagged_at': datetime.utcnow().isoformat()
            }
            
            metadata['tags'].append(tag_entry)
            
            # Update version metadata in database
            # This would require an update method in version repo
            # For now, we'll store in metadata
            version.metadata = metadata
            await self.db.commit()
            
            logger.info(f"Tagged version {version_id} with '{tag}'")
            return version
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to tag version: {str(e)}")
            raise
