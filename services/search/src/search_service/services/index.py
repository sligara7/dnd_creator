"""Index service for index management operations"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from search_service.clients.cache import CacheClient
from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.clients.message_hub import MessageHubClient
from search_service.repositories.index import IndexRepository
from search_service.repositories.analytics import AnalyticsRepository
from search_service.core.config import settings
from search_service.core.exceptions import SearchServiceError


class IndexService:
    """Service for index management operations"""

    def __init__(
        self,
        db: AsyncSession,
        es_client: ElasticsearchClient,
        cache_client: CacheClient,
        message_hub: MessageHubClient,
    ) -> None:
        """Initialize index service
        
        Args:
            db: Database session
            es_client: Elasticsearch client
            cache_client: Cache client
            message_hub: Message hub client
        """
        self.db = db
        self.es_client = es_client
        self.cache_client = cache_client
        self.message_hub = message_hub
        self.index_repo = IndexRepository(db, es_client)
        self.analytics_repo = AnalyticsRepository(db)

    async def create_index(
        self,
        index_name: str,
        mappings: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create new index with mappings and settings
        
        Args:
            index_name: Name of the index to create
            mappings: Optional mappings configuration
            settings: Optional index settings
            user_id: Optional user ID for tracking
            
        Returns:
            Index creation result
        """
        try:
            # Create index
            success = await self.index_repo.create_index(
                index_name=index_name,
                mappings=mappings,
                settings_override=settings,
            )
            
            if not success:
                raise SearchServiceError(
                    f"Failed to create index: {index_name}",
                    "index_creation_failed"
                )
            
            # Invalidate cached index list
            await self.cache_client.delete_pattern("indices:*")
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_created",
                index=index_name,
                metadata={
                    "has_mappings": bool(mappings),
                    "has_settings": bool(settings),
                },
                user_id=user_id,
            )
            
            # Publish event
            await self.message_hub.publish_event(
                "index.created",
                {
                    "index": index_name,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return {
                "success": True,
                "index": index_name,
                "message": f"Index '{index_name}' created successfully"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error creating index: {str(e)}",
                "index_creation_error"
            )

    async def delete_index(
        self,
        index_name: str,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Delete index and its metadata
        
        Args:
            index_name: Name of the index to delete
            user_id: Optional user ID for tracking
            
        Returns:
            Deletion result
        """
        try:
            # Delete index
            success = await self.index_repo.delete_index(index_name)
            
            if not success:
                raise SearchServiceError(
                    f"Failed to delete index: {index_name}",
                    "index_deletion_failed"
                )
            
            # Invalidate caches
            await self.cache_client.delete_pattern(f"index:{index_name}:*")
            await self.cache_client.delete_pattern("indices:*")
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_deleted",
                index=index_name,
                metadata={},
                user_id=user_id,
            )
            
            # Publish event
            await self.message_hub.publish_event(
                "index.deleted",
                {
                    "index": index_name,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return {
                "success": True,
                "index": index_name,
                "message": f"Index '{index_name}' deleted successfully"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error deleting index: {str(e)}",
                "index_deletion_error"
            )

    async def update_mappings(
        self,
        index_name: str,
        mappings: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Update index mappings
        
        Args:
            index_name: Name of the index
            mappings: New mappings to add
            user_id: Optional user ID for tracking
            
        Returns:
            Update result
        """
        try:
            # Update mappings
            success = await self.index_repo.update_mappings(
                index_name=index_name,
                mappings=mappings,
            )
            
            if not success:
                raise SearchServiceError(
                    f"Failed to update mappings for index: {index_name}",
                    "mapping_update_failed"
                )
            
            # Invalidate index cache
            await self.cache_client.delete_pattern(f"index:{index_name}:*")
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="mappings_updated",
                index=index_name,
                metadata={
                    "fields_added": len(mappings.get("properties", {})),
                },
                user_id=user_id,
            )
            
            # Publish event
            await self.message_hub.publish_event(
                "index.mappings_updated",
                {
                    "index": index_name,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return {
                "success": True,
                "index": index_name,
                "message": f"Mappings updated for index '{index_name}'"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error updating mappings: {str(e)}",
                "mapping_update_error"
            )

    async def refresh_index(
        self,
        index_name: str,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Refresh index to make recent changes searchable
        
        Args:
            index_name: Name of the index to refresh
            user_id: Optional user ID for tracking
            
        Returns:
            Refresh result
        """
        try:
            # Refresh index
            success = await self.index_repo.refresh_index(index_name)
            
            if not success:
                raise SearchServiceError(
                    f"Failed to refresh index: {index_name}",
                    "index_refresh_failed"
                )
            
            # Invalidate search caches for this index
            await self.cache_client.delete_pattern(f"search:{index_name}:*")
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_refreshed",
                index=index_name,
                metadata={},
                user_id=user_id,
            )
            
            return {
                "success": True,
                "index": index_name,
                "message": f"Index '{index_name}' refreshed successfully"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error refreshing index: {str(e)}",
                "index_refresh_error"
            )

    async def optimize_index(
        self,
        index_name: str,
        max_num_segments: int = 1,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Optimize index by merging segments
        
        Args:
            index_name: Name of the index to optimize
            max_num_segments: Target number of segments
            user_id: Optional user ID for tracking
            
        Returns:
            Optimization result
        """
        try:
            # Optimize index
            success = await self.index_repo.optimize_index(
                index_name=index_name,
                max_num_segments=max_num_segments,
            )
            
            if not success:
                raise SearchServiceError(
                    f"Failed to optimize index: {index_name}",
                    "index_optimization_failed"
                )
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_optimized",
                index=index_name,
                metadata={
                    "max_num_segments": max_num_segments,
                },
                user_id=user_id,
            )
            
            # Publish event
            await self.message_hub.publish_event(
                "index.optimized",
                {
                    "index": index_name,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return {
                "success": True,
                "index": index_name,
                "message": f"Index '{index_name}' optimized successfully"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error optimizing index: {str(e)}",
                "index_optimization_error"
            )

    async def reindex(
        self,
        source_index: str,
        target_index: str,
        query: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Reindex documents from source to target
        
        Args:
            source_index: Source index name
            target_index: Target index name
            query: Optional query to filter documents
            user_id: Optional user ID for tracking
            
        Returns:
            Reindex result with statistics
        """
        try:
            # Perform reindex
            result = await self.index_repo.reindex(
                source_index=source_index,
                target_index=target_index,
                query=query,
            )
            
            # Invalidate caches for both indices
            await self.cache_client.delete_pattern(f"index:{source_index}:*")
            await self.cache_client.delete_pattern(f"index:{target_index}:*")
            await self.cache_client.delete_pattern(f"search:{source_index}:*")
            await self.cache_client.delete_pattern(f"search:{target_index}:*")
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_reindexed",
                index=source_index,
                metadata={
                    "target_index": target_index,
                    "documents_copied": result.get("total", 0),
                    "has_query": bool(query),
                },
                user_id=user_id,
            )
            
            # Publish event
            await self.message_hub.publish_event(
                "index.reindexed",
                {
                    "source_index": source_index,
                    "target_index": target_index,
                    "documents_copied": result.get("total", 0),
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return {
                "success": True,
                "source_index": source_index,
                "target_index": target_index,
                "documents_copied": result.get("total", 0),
                "took_ms": result.get("took", 0),
                "message": f"Reindexed {result.get('total', 0)} documents from '{source_index}' to '{target_index}'"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error reindexing: {str(e)}",
                "reindex_error"
            )

    async def analyze_text(
        self,
        index_name: str,
        text: str,
        analyzer: Optional[str] = None,
        field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze text using index analyzers
        
        Args:
            index_name: Name of the index
            text: Text to analyze
            analyzer: Optional analyzer name
            field: Optional field to use analyzer from
            
        Returns:
            Analysis result with tokens
        """
        try:
            # Perform analysis
            body = {"text": text}
            if analyzer:
                body["analyzer"] = analyzer
            elif field:
                body["field"] = field
            
            result = await self.es_client.client.indices.analyze(
                index=settings.INDEX_PREFIX + index_name,
                body=body
            )
            
            # Extract tokens
            tokens = [
                {
                    "token": token["token"],
                    "position": token["position"],
                    "start_offset": token["start_offset"],
                    "end_offset": token["end_offset"],
                    "type": token.get("type", "word"),
                }
                for token in result.get("tokens", [])
            ]
            
            return {
                "success": True,
                "index": index_name,
                "text": text,
                "analyzer": analyzer or "default",
                "tokens": tokens,
                "token_count": len(tokens),
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error analyzing text: {str(e)}",
                "text_analysis_error"
            )

    async def get_index_stats(
        self,
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get index statistics
        
        Args:
            index_name: Optional specific index name, or all indices
            
        Returns:
            Index statistics
        """
        try:
            # Get stats from Elasticsearch
            index_pattern = settings.INDEX_PREFIX + (index_name or "*")
            stats = await self.es_client.client.indices.stats(index=index_pattern)
            
            # Process stats
            indices_stats = {}
            for idx, idx_stats in stats.get("indices", {}).items():
                # Remove prefix from index name
                clean_name = idx.replace(settings.INDEX_PREFIX, "")
                indices_stats[clean_name] = {
                    "document_count": idx_stats["primaries"]["docs"]["count"],
                    "deleted_docs": idx_stats["primaries"]["docs"]["deleted"],
                    "size_bytes": idx_stats["primaries"]["store"]["size_in_bytes"],
                    "segments": idx_stats["primaries"]["segments"]["count"],
                    "search_queries": idx_stats["primaries"]["search"]["query_total"],
                    "search_time_ms": idx_stats["primaries"]["search"]["query_time_in_millis"],
                }
            
            return {
                "success": True,
                "indices": indices_stats,
                "total_indices": len(indices_stats),
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting index stats: {str(e)}",
                "index_stats_error"
            )

    async def backup_index(
        self,
        index_name: str,
        repository: str = "backup_repo",
        snapshot_name: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create backup snapshot of index
        
        Args:
            index_name: Name of the index to backup
            repository: Snapshot repository name
            snapshot_name: Optional snapshot name
            user_id: Optional user ID for tracking
            
        Returns:
            Backup result
        """
        try:
            from datetime import datetime
            
            # Generate snapshot name if not provided
            if not snapshot_name:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                snapshot_name = f"{index_name}_{timestamp}"
            
            # Create snapshot
            await self.es_client.client.snapshot.create(
                repository=repository,
                snapshot=snapshot_name,
                body={
                    "indices": settings.INDEX_PREFIX + index_name,
                    "include_global_state": False,
                }
            )
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_backed_up",
                index=index_name,
                metadata={
                    "repository": repository,
                    "snapshot": snapshot_name,
                },
                user_id=user_id,
            )
            
            return {
                "success": True,
                "index": index_name,
                "repository": repository,
                "snapshot": snapshot_name,
                "message": f"Index '{index_name}' backed up to snapshot '{snapshot_name}'"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error backing up index: {str(e)}",
                "index_backup_error"
            )

    async def restore_index(
        self,
        snapshot_name: str,
        repository: str = "backup_repo",
        index_name: Optional[str] = None,
        rename_pattern: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Restore index from backup snapshot
        
        Args:
            snapshot_name: Name of the snapshot
            repository: Snapshot repository name
            index_name: Optional specific index to restore
            rename_pattern: Optional rename pattern
            user_id: Optional user ID for tracking
            
        Returns:
            Restore result
        """
        try:
            # Restore snapshot
            body = {"include_global_state": False}
            if index_name:
                body["indices"] = settings.INDEX_PREFIX + index_name
            if rename_pattern:
                body["rename_pattern"] = "(.+)"
                body["rename_replacement"] = rename_pattern + "_$1"
            
            await self.es_client.client.snapshot.restore(
                repository=repository,
                snapshot=snapshot_name,
                body=body
            )
            
            # Track event
            await self.analytics_repo.track_event(
                event_type="index_restored",
                index=index_name or "all",
                metadata={
                    "repository": repository,
                    "snapshot": snapshot_name,
                    "renamed": bool(rename_pattern),
                },
                user_id=user_id,
            )
            
            return {
                "success": True,
                "snapshot": snapshot_name,
                "repository": repository,
                "index": index_name or "all",
                "message": f"Index restored from snapshot '{snapshot_name}'"
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error restoring index: {str(e)}",
                "index_restore_error"
            )
