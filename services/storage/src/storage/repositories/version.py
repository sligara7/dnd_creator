"""Version Repository for storage service."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy import select, update, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.version import AssetVersion
from ..utils.logging import get_logger

logger = get_logger(__name__)


class VersionRepository:
    """Repository for version control operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, version_data: Dict[str, Any]) -> AssetVersion:
        """Create a new version."""
        try:
            version = AssetVersion(**version_data)
            self.db.add(version)
            await self.db.flush()
            await self.db.refresh(version)
            logger.info(f"Created version {version.version_number} for asset {version.asset_id}")
            return version
        except Exception as e:
            logger.error(f"Failed to create version: {str(e)}")
            raise
    
    async def get(self, version_id: UUID) -> Optional[AssetVersion]:
        """Get version by ID."""
        try:
            query = select(AssetVersion).where(
                AssetVersion.id == version_id,
                AssetVersion.is_deleted == False
            )
            result = await self.db.execute(query)
            version = result.scalar_one_or_none()
            
            if version:
                logger.debug(f"Retrieved version: {version_id}")
            else:
                logger.warning(f"Version not found: {version_id}")
            
            return version
        except Exception as e:
            logger.error(f"Failed to get version {version_id}: {str(e)}")
            raise
    
    async def get_by_asset_and_number(
        self, 
        asset_id: UUID, 
        version_number: int
    ) -> Optional[AssetVersion]:
        """Get specific version of an asset."""
        try:
            query = select(AssetVersion).where(
                and_(
                    AssetVersion.asset_id == asset_id,
                    AssetVersion.version_number == version_number,
                    AssetVersion.is_deleted == False
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get version: {str(e)}")
            raise
    
    async def list_by_asset(
        self,
        asset_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[AssetVersion]:
        """List all versions of an asset."""
        try:
            query = select(AssetVersion).where(
                and_(
                    AssetVersion.asset_id == asset_id,
                    AssetVersion.is_deleted == False
                )
            ).order_by(desc(AssetVersion.version_number))
            
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            versions = result.scalars().all()
            
            logger.debug(f"Listed {len(versions)} versions for asset {asset_id}")
            return versions
        except Exception as e:
            logger.error(f"Failed to list versions: {str(e)}")
            raise
    
    async def get_latest(self, asset_id: UUID) -> Optional[AssetVersion]:
        """Get the latest version of an asset."""
        try:
            query = select(AssetVersion).where(
                and_(
                    AssetVersion.asset_id == asset_id,
                    AssetVersion.is_deleted == False
                )
            ).order_by(desc(AssetVersion.version_number)).limit(1)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get latest version: {str(e)}")
            raise
    
    async def get_next_version_number(self, asset_id: UUID) -> int:
        """Get the next version number for an asset."""
        try:
            query = select(func.max(AssetVersion.version_number)).where(
                AssetVersion.asset_id == asset_id
            )
            result = await self.db.execute(query)
            max_version = result.scalar()
            return (max_version or 0) + 1
        except Exception as e:
            logger.error(f"Failed to get next version number: {str(e)}")
            raise
    
    async def soft_delete(self, version_id: UUID) -> bool:
        """Soft delete a version."""
        try:
            query = (
                update(AssetVersion)
                .where(
                    AssetVersion.id == version_id,
                    AssetVersion.is_deleted == False
                )
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            
            result = await self.db.execute(query)
            success = result.rowcount > 0
            
            if success:
                logger.info(f"Soft deleted version: {version_id}")
            else:
                logger.warning(f"Version not found for deletion: {version_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to delete version {version_id}: {str(e)}")
            raise
    
    async def prune_old_versions(
        self,
        asset_id: UUID,
        keep_count: int = 10
    ) -> int:
        """Prune old versions, keeping the most recent ones."""
        try:
            # Get versions to keep
            keep_query = select(AssetVersion.id).where(
                and_(
                    AssetVersion.asset_id == asset_id,
                    AssetVersion.is_deleted == False
                )
            ).order_by(desc(AssetVersion.version_number)).limit(keep_count)
            
            keep_result = await self.db.execute(keep_query)
            keep_ids = [row[0] for row in keep_result]
            
            if not keep_ids:
                return 0
            
            # Soft delete older versions
            delete_query = (
                update(AssetVersion)
                .where(
                    and_(
                        AssetVersion.asset_id == asset_id,
                        AssetVersion.id.notin_(keep_ids),
                        AssetVersion.is_deleted == False
                    )
                )
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            
            result = await self.db.execute(delete_query)
            pruned_count = result.rowcount
            
            if pruned_count > 0:
                logger.info(f"Pruned {pruned_count} old versions for asset {asset_id}")
            
            return pruned_count
        except Exception as e:
            logger.error(f"Failed to prune versions: {str(e)}")
            raise
    
    async def compare_versions(
        self,
        version_id1: UUID,
        version_id2: UUID
    ) -> Dict[str, Any]:
        """Compare two versions."""
        try:
            v1 = await self.get(version_id1)
            v2 = await self.get(version_id2)
            
            if not v1 or not v2:
                raise ValueError("One or both versions not found")
            
            comparison = {
                'version_1': {
                    'id': v1.id,
                    'version_number': v1.version_number,
                    'size': v1.size,
                    'checksum': v1.checksum,
                    'created_at': v1.created_at
                },
                'version_2': {
                    'id': v2.id,
                    'version_number': v2.version_number,
                    'size': v2.size,
                    'checksum': v2.checksum,
                    'created_at': v2.created_at
                },
                'differences': {
                    'size_diff': v2.size - v1.size,
                    'checksum_changed': v1.checksum != v2.checksum,
                    'metadata_changes': self._compare_metadata(v1.metadata, v2.metadata)
                }
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Failed to compare versions: {str(e)}")
            raise
    
    def _compare_metadata(self, meta1: Dict, meta2: Dict) -> Dict[str, Any]:
        """Compare metadata between versions."""
        added_keys = set(meta2.keys()) - set(meta1.keys())
        removed_keys = set(meta1.keys()) - set(meta2.keys())
        common_keys = set(meta1.keys()) & set(meta2.keys())
        
        changed = {}
        for key in common_keys:
            if meta1[key] != meta2[key]:
                changed[key] = {
                    'old': meta1[key],
                    'new': meta2[key]
                }
        
        return {
            'added': list(added_keys),
            'removed': list(removed_keys),
            'changed': changed
        }
