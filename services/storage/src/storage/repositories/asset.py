"""Asset Repository for storage service."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.asset import Asset, AssetType
from ..models.version import AssetVersion
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AssetRepository:
    """Repository for asset operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, asset_data: Dict[str, Any]) -> Asset:
        """Create a new asset."""
        try:
            asset = Asset(**asset_data)
            self.db.add(asset)
            await self.db.flush()
            await self.db.refresh(asset)
            logger.info(f"Created asset with ID: {asset.id}")
            return asset
        except Exception as e:
            logger.error(f"Failed to create asset: {str(e)}")
            raise
    
    async def get(self, asset_id: UUID, include_deleted: bool = False) -> Optional[Asset]:
        """Get asset by ID."""
        try:
            query = select(Asset).where(Asset.id == asset_id)
            
            if not include_deleted:
                query = query.where(Asset.is_deleted == False)
            
            # Include versions relationship
            query = query.options(selectinload(Asset.versions))
            
            result = await self.db.execute(query)
            asset = result.scalar_one_or_none()
            
            if asset:
                logger.debug(f"Retrieved asset: {asset_id}")
            else:
                logger.warning(f"Asset not found: {asset_id}")
            
            return asset
        except Exception as e:
            logger.error(f"Failed to get asset {asset_id}: {str(e)}")
            raise
    
    async def get_by_checksum(self, checksum: str, include_deleted: bool = False) -> Optional[Asset]:
        """Get asset by checksum for deduplication."""
        try:
            query = select(Asset).where(Asset.checksum == checksum)
            
            if not include_deleted:
                query = query.where(Asset.is_deleted == False)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get asset by checksum: {str(e)}")
            raise
    
    async def list(
        self,
        service: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        asset_type: Optional[AssetType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Asset]:
        """List assets with filters."""
        try:
            query = select(Asset)
            
            # Apply filters
            conditions = []
            
            if not include_deleted:
                conditions.append(Asset.is_deleted == False)
            
            if service:
                conditions.append(Asset.service == service)
            
            if owner_id:
                conditions.append(Asset.owner_id == owner_id)
            
            if asset_type:
                conditions.append(Asset.asset_type == asset_type)
            
            if tags:
                # Check if any of the provided tags are in the asset's tags
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(Asset.tags.contains([tag]))
                conditions.append(or_(*tag_conditions))
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Order by creation date
            query = query.order_by(Asset.created_at.desc())
            
            result = await self.db.execute(query)
            assets = result.scalars().all()
            
            logger.debug(f"Listed {len(assets)} assets with filters")
            return assets
        except Exception as e:
            logger.error(f"Failed to list assets: {str(e)}")
            raise
    
    async def update(self, asset_id: UUID, updates: Dict[str, Any]) -> Optional[Asset]:
        """Update an asset."""
        try:
            # Don't allow updating certain fields
            protected_fields = ['id', 'created_at', 'checksum', 's3_key']
            for field in protected_fields:
                updates.pop(field, None)
            
            # Update timestamp
            updates['updated_at'] = datetime.utcnow()
            
            query = (
                update(Asset)
                .where(Asset.id == asset_id, Asset.is_deleted == False)
                .values(**updates)
                .returning(Asset)
            )
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_asset = result.scalar_one_or_none()
            
            if updated_asset:
                logger.info(f"Updated asset: {asset_id}")
            else:
                logger.warning(f"Asset not found for update: {asset_id}")
            
            return updated_asset
        except Exception as e:
            logger.error(f"Failed to update asset {asset_id}: {str(e)}")
            raise
    
    async def soft_delete(self, asset_id: UUID) -> bool:
        """Soft delete an asset."""
        try:
            query = (
                update(Asset)
                .where(Asset.id == asset_id, Asset.is_deleted == False)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            
            result = await self.db.execute(query)
            success = result.rowcount > 0
            
            if success:
                logger.info(f"Soft deleted asset: {asset_id}")
            else:
                logger.warning(f"Asset not found for deletion: {asset_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to delete asset {asset_id}: {str(e)}")
            raise
    
    async def restore(self, asset_id: UUID) -> Optional[Asset]:
        """Restore a soft-deleted asset."""
        try:
            query = (
                update(Asset)
                .where(Asset.id == asset_id, Asset.is_deleted == True)
                .values(
                    is_deleted=False,
                    deleted_at=None,
                    updated_at=datetime.utcnow()
                )
                .returning(Asset)
            )
            
            result = await self.db.execute(query)
            restored_asset = result.scalar_one_or_none()
            
            if restored_asset:
                logger.info(f"Restored asset: {asset_id}")
            else:
                logger.warning(f"Asset not found for restoration: {asset_id}")
            
            return restored_asset
        except Exception as e:
            logger.error(f"Failed to restore asset {asset_id}: {str(e)}")
            raise
    
    async def get_storage_stats(self, service: Optional[str] = None) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            # Base query
            query = select(
                func.count(Asset.id).label('total_count'),
                func.sum(Asset.size).label('total_size'),
                func.avg(Asset.size).label('avg_size')
            ).where(Asset.is_deleted == False)
            
            if service:
                query = query.where(Asset.service == service)
            
            result = await self.db.execute(query)
            row = result.one()
            
            # Get breakdown by type
            type_query = select(
                Asset.asset_type,
                func.count(Asset.id).label('count'),
                func.sum(Asset.size).label('size')
            ).where(Asset.is_deleted == False)
            
            if service:
                type_query = type_query.where(Asset.service == service)
            
            type_query = type_query.group_by(Asset.asset_type)
            
            type_result = await self.db.execute(type_query)
            type_breakdown = [
                {
                    'type': row.asset_type.value if row.asset_type else 'unknown',
                    'count': row.count,
                    'size': row.size or 0
                }
                for row in type_result
            ]
            
            stats = {
                'total_count': row.total_count or 0,
                'total_size': row.total_size or 0,
                'average_size': float(row.avg_size) if row.avg_size else 0,
                'type_breakdown': type_breakdown
            }
            
            logger.debug(f"Generated storage stats for service: {service}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            raise
    
    async def bulk_create(self, assets_data: List[Dict[str, Any]]) -> List[Asset]:
        """Create multiple assets in a single transaction."""
        try:
            assets = [Asset(**data) for data in assets_data]
            self.db.add_all(assets)
            await self.db.flush()
            
            # Refresh all assets to get generated fields
            for asset in assets:
                await self.db.refresh(asset)
            
            logger.info(f"Bulk created {len(assets)} assets")
            return assets
        except Exception as e:
            logger.error(f"Failed to bulk create assets: {str(e)}")
            raise
    
    async def bulk_delete(self, asset_ids: List[UUID]) -> int:
        """Soft delete multiple assets."""
        try:
            query = (
                update(Asset)
                .where(Asset.id.in_(asset_ids), Asset.is_deleted == False)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            
            result = await self.db.execute(query)
            deleted_count = result.rowcount
            
            logger.info(f"Bulk deleted {deleted_count} assets")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to bulk delete assets: {str(e)}")
            raise
    
    async def search(
        self,
        query_str: str,
        service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Asset]:
        """Search assets by name or metadata."""
        try:
            # Search in name and metadata fields
            search_query = select(Asset).where(
                and_(
                    Asset.is_deleted == False,
                    or_(
                        Asset.name.ilike(f"%{query_str}%"),
                        Asset.metadata.op('@>')({f'search': query_str})
                    )
                )
            )
            
            if service:
                search_query = search_query.where(Asset.service == service)
            
            search_query = search_query.limit(limit).offset(offset)
            search_query = search_query.order_by(Asset.created_at.desc())
            
            result = await self.db.execute(search_query)
            assets = result.scalars().all()
            
            logger.debug(f"Search returned {len(assets)} assets for query: {query_str}")
            return assets
        except Exception as e:
            logger.error(f"Failed to search assets: {str(e)}")
            raise
