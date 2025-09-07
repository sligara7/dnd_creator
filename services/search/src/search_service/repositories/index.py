"""Index repository for Elasticsearch index management"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.models.database import IndexMetadata
from search_service.repositories.base import BaseRepository
from search_service.core.config import settings


class IndexRepository(BaseRepository[IndexMetadata]):
    """Repository for index management operations"""

    def __init__(self, db: AsyncSession, es_client: ElasticsearchClient) -> None:
        """Initialize index repository
        
        Args:
            db: Database session for metadata
            es_client: Elasticsearch client
        """
        super().__init__(db, IndexMetadata)
        self.es_client = es_client

    async def create_index(
        self,
        index_name: str,
        mappings: Optional[Dict[str, Any]] = None,
        settings_override: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create new index with mappings
        
        Args:
            index_name: Name of the index
            mappings: Index mappings configuration
            settings_override: Optional settings to override defaults
            
        Returns:
            True if created successfully
        """
        # Use predefined mappings if not provided
        if not mappings and index_name in settings.INDEX_MAPPINGS:
            mappings = settings.INDEX_MAPPINGS[index_name]
        
        # Create index in Elasticsearch
        await self.es_client.create_index(index_name, mappings or {})
        
        # Store metadata in database
        metadata = IndexMetadata(
            index=index_name,
            document_count={"total": 0},
            last_refresh=datetime.utcnow(),
            settings=settings_override or {},
            mappings=mappings or {},
            stats={
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
            },
        )
        
        await self.create(metadata)
        return True

    async def delete_index(self, index_name: str) -> bool:
        """Delete index and its metadata
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if deleted successfully
        """
        # Delete from Elasticsearch
        await self.es_client.delete_index(index_name)
        
        # Soft delete metadata
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.index == index_name,
            IndexMetadata.is_deleted == False
        )
        result = await self.db.execute(query)
        metadata = result.scalar_one_or_none()
        
        if metadata:
            await self.soft_delete(metadata.id)
        
        return True

    async def update_mappings(
        self,
        index_name: str,
        mappings: Dict[str, Any],
    ) -> bool:
        """Update index mappings
        
        Args:
            index_name: Name of the index
            mappings: New mappings to add
            
        Returns:
            True if updated successfully
        """
        # Update mappings in Elasticsearch
        await self.es_client.client.indices.put_mapping(
            index=settings.INDEX_PREFIX + index_name,
            body=mappings,
        )
        
        # Update metadata
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.index == index_name,
            IndexMetadata.is_deleted == False
        )
        result = await self.db.execute(query)
        metadata = result.scalar_one_or_none()
        
        if metadata:
            # Merge new mappings with existing
            existing_mappings = metadata.mappings or {}
            existing_mappings.update(mappings)
            
            await self.update(
                metadata.id,
                {"mappings": existing_mappings}
            )
        
        return True

    async def refresh_index(self, index_name: str) -> bool:
        """Refresh index to make recent changes searchable
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if refreshed successfully
        """
        # Refresh in Elasticsearch
        await self.es_client.client.indices.refresh(
            index=settings.INDEX_PREFIX + index_name
        )
        
        # Update last refresh time
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.index == index_name,
            IndexMetadata.is_deleted == False
        )
        result = await self.db.execute(query)
        metadata = result.scalar_one_or_none()
        
        if metadata:
            await self.update(
                metadata.id,
                {"last_refresh": datetime.utcnow()}
            )
        
        return True

    async def optimize_index(
        self,
        index_name: str,
        max_num_segments: int = 1,
    ) -> bool:
        """Optimize index by merging segments
        
        Args:
            index_name: Name of the index
            max_num_segments: Target number of segments
            
        Returns:
            True if optimized successfully
        """
        # Force merge in Elasticsearch
        await self.es_client.client.indices.forcemerge(
            index=settings.INDEX_PREFIX + index_name,
            max_num_segments=max_num_segments,
        )
        
        # Update stats
        await self._update_index_stats(index_name)
        
        return True

    async def reindex(
        self,
        source_index: str,
        target_index: str,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Reindex documents from source to target
        
        Args:
            source_index: Source index name
            target_index: Target index name
            query: Optional query to filter documents
            
        Returns:
            Reindex operation results
        """
        body = {
            "source": {
                "index": settings.INDEX_PREFIX + source_index,
            },
            "dest": {
                "index": settings.INDEX_PREFIX + target_index,
            }
        }
        
        if query:
            body["source"]["query"] = query
        
        result = await self.es_client.client.reindex(body=body)
        
        # Update metadata for target index
        await self._update_index_stats(target_index)
        
        return result

    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get index statistics
        
        Args:
            index_name: Name of the index
            
        Returns:
            Index statistics
        """
        stats = await self.es_client.client.indices.stats(
            index=settings.INDEX_PREFIX + index_name
        )
        
        # Update stored stats
        await self._update_index_stats(index_name, stats)
        
        return stats

    async def list_indices(
        self,
        pattern: str = "*",
        include_system: bool = False,
    ) -> List[Dict[str, Any]]:
        """List all indices matching pattern
        
        Args:
            pattern: Index name pattern
            include_system: Whether to include system indices
            
        Returns:
            List of index information
        """
        # Get indices from Elasticsearch
        indices = await self.es_client.client.cat.indices(
            index=settings.INDEX_PREFIX + pattern,
            format="json",
        )
        
        # Filter system indices if requested
        if not include_system:
            indices = [
                idx for idx in indices
                if not idx["index"].startswith(".")
            ]
        
        # Get metadata from database
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.is_deleted == False
        )
        result = await self.db.execute(query)
        metadata_map = {
            m.index: m for m in result.scalars().all()
        }
        
        # Combine information
        for idx in indices:
            index_name = idx["index"].replace(settings.INDEX_PREFIX, "")
            if index_name in metadata_map:
                idx["metadata"] = metadata_map[index_name]
        
        return indices

    async def analyze_text(
        self,
        index_name: str,
        text: str,
        analyzer: str = "standard",
    ) -> List[Dict[str, Any]]:
        """Analyze text using index analyzer
        
        Args:
            index_name: Name of the index
            text: Text to analyze
            analyzer: Analyzer to use
            
        Returns:
            List of tokens
        """
        result = await self.es_client.client.indices.analyze(
            index=settings.INDEX_PREFIX + index_name,
            body={
                "text": text,
                "analyzer": analyzer,
            }
        )
        
        return result.get("tokens", [])

    async def backup_index(
        self,
        index_name: str,
        repository: str = "backup_repo",
        snapshot_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create index backup snapshot
        
        Args:
            index_name: Name of the index
            repository: Snapshot repository name
            snapshot_name: Name for the snapshot
            
        Returns:
            Snapshot creation result
        """
        if not snapshot_name:
            snapshot_name = f"{index_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        result = await self.es_client.client.snapshot.create(
            repository=repository,
            snapshot=snapshot_name,
            body={
                "indices": settings.INDEX_PREFIX + index_name,
                "include_global_state": False,
            }
        )
        
        # Update metadata with backup info
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.index == index_name,
            IndexMetadata.is_deleted == False
        )
        result_db = await self.db.execute(query)
        metadata = result_db.scalar_one_or_none()
        
        if metadata:
            stats = metadata.stats or {}
            stats["last_backup"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "snapshot": snapshot_name,
                "repository": repository,
            }
            await self.update(metadata.id, {"stats": stats})
        
        return result

    async def restore_index(
        self,
        snapshot_name: str,
        repository: str = "backup_repo",
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Restore index from snapshot
        
        Args:
            snapshot_name: Name of the snapshot
            repository: Snapshot repository name
            index_name: Optional new name for restored index
            
        Returns:
            Restore operation result
        """
        body = {
            "include_global_state": False,
        }
        
        if index_name:
            body["rename_pattern"] = "(.+)"
            body["rename_replacement"] = settings.INDEX_PREFIX + index_name
        
        result = await self.es_client.client.snapshot.restore(
            repository=repository,
            snapshot=snapshot_name,
            body=body,
        )
        
        return result

    # Private helper methods
    
    async def _update_index_stats(
        self,
        index_name: str,
        stats: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update stored index statistics
        
        Args:
            index_name: Name of the index
            stats: Optional stats to store
        """
        if not stats:
            stats = await self.es_client.client.indices.stats(
                index=settings.INDEX_PREFIX + index_name
            )
        
        # Extract relevant stats
        index_stats = stats.get("indices", {}).get(
            settings.INDEX_PREFIX + index_name, {}
        )
        
        doc_count = index_stats.get("primaries", {}).get("docs", {}).get("count", 0)
        store_size = index_stats.get("primaries", {}).get("store", {}).get("size_in_bytes", 0)
        
        # Update metadata
        from sqlalchemy import select
        query = select(IndexMetadata).where(
            IndexMetadata.index == index_name,
            IndexMetadata.is_deleted == False
        )
        result = await self.db.execute(query)
        metadata = result.scalar_one_or_none()
        
        if metadata:
            await self.update(
                metadata.id,
                {
                    "document_count": {"total": doc_count},
                    "stats": {
                        "doc_count": doc_count,
                        "store_size_bytes": store_size,
                        "last_updated": datetime.utcnow().isoformat(),
                    }
                }
            )
