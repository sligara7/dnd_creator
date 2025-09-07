"""Search service for business logic orchestration"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from search_service.clients.cache import CacheClient
from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.clients.message_hub import MessageHubClient
from search_service.repositories.search import SearchRepository
from search_service.repositories.analytics import AnalyticsRepository
from search_service.core.config import settings
from search_service.core.exceptions import SearchServiceError


class SearchService:
    """Service for search operations"""

    def __init__(
        self,
        db: AsyncSession,
        es_client: ElasticsearchClient,
        cache_client: CacheClient,
        message_hub: MessageHubClient,
    ) -> None:
        """Initialize search service
        
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
        self.search_repo = SearchRepository(db, es_client)
        self.analytics_repo = AnalyticsRepository(db)

    async def search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = None,
        sort: Optional[List[Dict[str, Any]]] = None,
        source_fields: Optional[List[str]] = None,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Execute full-text search with caching and analytics
        
        Args:
            index: Index to search
            query: Search query
            filters: Optional filters
            page: Page number (1-based)
            page_size: Results per page
            sort: Sort criteria
            source_fields: Fields to return
            user_id: Optional user ID for analytics
            session_id: Optional session ID for analytics
            
        Returns:
            Search results with metadata
        """
        # Validate inputs
        if page < 1:
            raise SearchServiceError("Page must be >= 1", "invalid_page")
        
        page_size = page_size or settings.DEFAULT_PAGE_SIZE
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        
        # Check cache
        cache_key = self._generate_cache_key(
            "search", index, query, filters, page, page_size, sort
        )
        cached_result = await self.cache_client.get(cache_key)
        if cached_result:
            # Track cache hit
            await self.analytics_repo.track_event(
                "cache_hit",
                index,
                {"query": query, "cache_key": cache_key},
                session_id,
                user_id,
            )
            return cached_result
        
        # Execute search
        from_ = (page - 1) * page_size
        results = await self.search_repo.search(
            index=index,
            query=query,
            filters=filters,
            size=page_size,
            from_=from_,
            sort=sort,
            source_fields=source_fields,
            track_query=True,
        )
        
        # Process results
        processed_results = self._process_search_results(
            results, page, page_size
        )
        
        # Cache results
        await self.cache_client.set(
            cache_key,
            processed_results,
            ttl=settings.SEARCH_CACHE_TTL,
        )
        
        # Track search event
        await self.analytics_repo.track_event(
            "search",
            index,
            {
                "query": query,
                "filters": filters,
                "result_count": processed_results["total"],
                "page": page,
            },
            session_id,
            user_id,
        )
        
        # Publish event to Message Hub
        await self.message_hub.publish_event(
            "search.executed",
            {
                "index": index,
                "query": query,
                "result_count": processed_results["total"],
                "user_id": str(user_id) if user_id else None,
            }
        )
        
        return processed_results

    async def semantic_search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = None,
        min_score: float = 0.7,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Execute semantic/vector search
        
        Args:
            index: Index to search
            query: Search query
            filters: Optional filters
            size: Number of results
            min_score: Minimum similarity score
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            Search results with similarity scores
        """
        # Check cache
        cache_key = self._generate_cache_key(
            "semantic", index, query, filters, size, min_score
        )
        cached_result = await self.cache_client.get(cache_key)
        if cached_result:
            return cached_result
        
        # Execute semantic search
        results = await self.search_repo.semantic_search(
            index=index,
            query=query,
            filters=filters,
            size=size or settings.DEFAULT_PAGE_SIZE,
            min_score=min_score,
        )
        
        # Process results
        processed_results = self._process_search_results(results)
        
        # Cache results
        await self.cache_client.set(
            cache_key,
            processed_results,
            ttl=settings.SEMANTIC_CACHE_TTL,
        )
        
        # Track event
        await self.analytics_repo.track_event(
            "semantic_search",
            index,
            {
                "query": query,
                "result_count": processed_results["total"],
                "min_score": min_score,
            },
            session_id,
            user_id,
        )
        
        return processed_results

    async def suggest(
        self,
        index: str,
        query: str,
        size: int = 5,
    ) -> List[str]:
        """Get search suggestions
        
        Args:
            index: Index to search
            query: Partial query
            size: Number of suggestions
            
        Returns:
            List of suggestions
        """
        # Check cache
        cache_key = f"suggest:{index}:{query}"
        cached = await self.cache_client.get(cache_key)
        if cached:
            return cached
        
        # Get suggestions
        suggestions = await self.search_repo.suggest(
            index=index,
            query=query,
            size=size,
        )
        
        # Cache suggestions
        if suggestions:
            await self.cache_client.set(
                cache_key,
                suggestions,
                ttl=300,  # 5 minutes
            )
        
        return suggestions

    async def autocomplete(
        self,
        index: str,
        query: str,
        field: str = "name",
        size: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get autocomplete results
        
        Args:
            index: Index to search
            query: Partial query
            field: Field to search
            size: Number of results
            
        Returns:
            List of matching documents
        """
        # Check cache
        cache_key = f"autocomplete:{index}:{field}:{query}"
        cached = await self.cache_client.get(cache_key)
        if cached:
            return cached
        
        # Get autocomplete results
        results = await self.search_repo.autocomplete(
            index=index,
            query=query,
            field=field,
            size=size,
        )
        
        # Cache results
        if results:
            await self.cache_client.set(
                cache_key,
                results,
                ttl=300,  # 5 minutes
            )
        
        return results

    async def find_similar(
        self,
        index: str,
        document_id: str,
        fields: Optional[List[str]] = None,
        size: int = 10,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Find similar documents
        
        Args:
            index: Index to search
            document_id: Reference document ID
            fields: Fields to compare
            size: Number of results
            user_id: Optional user ID
            
        Returns:
            Similar documents
        """
        # Execute more-like-this search
        results = await self.search_repo.more_like_this(
            index=index,
            document_id=document_id,
            fields=fields,
            size=size,
        )
        
        # Process results
        processed_results = self._process_search_results(results)
        
        # Track event
        await self.analytics_repo.track_event(
            "find_similar",
            index,
            {
                "document_id": document_id,
                "result_count": processed_results["total"],
            },
            user_id=user_id,
        )
        
        return processed_results

    async def search_multi_index(
        self,
        indices: List[str],
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size_per_index: int = 10,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Search across multiple indices
        
        Args:
            indices: List of indices to search
            query: Search query
            filters: Optional filters
            size_per_index: Results per index
            user_id: Optional user ID
            
        Returns:
            Combined search results
        """
        # Execute searches in parallel
        import asyncio
        
        search_tasks = [
            self.search(
                index=index,
                query=query,
                filters=filters,
                page_size=size_per_index,
                user_id=user_id,
            )
            for index in indices
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results
        combined_results = {
            "query": query,
            "indices": {},
            "total": 0,
            "errors": [],
        }
        
        for index, result in zip(indices, results):
            if isinstance(result, Exception):
                combined_results["errors"].append({
                    "index": index,
                    "error": str(result),
                })
            else:
                combined_results["indices"][index] = result
                combined_results["total"] += result.get("total", 0)
        
        return combined_results

    async def track_click(
        self,
        query: str,
        document_id: str,
        index: str,
        position: int,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> None:
        """Track search result click
        
        Args:
            query: Original search query
            document_id: Clicked document ID
            index: Index name
            position: Position in results
            user_id: Optional user ID
            session_id: Optional session ID
        """
        await self.analytics_repo.track_click(
            query=query,
            document_id=document_id,
            index=index,
            position=position,
            session_id=session_id,
            user_id=user_id,
        )
        
        # Publish event
        await self.message_hub.publish_event(
            "search.click",
            {
                "query": query,
                "document_id": document_id,
                "index": index,
                "position": position,
                "user_id": str(user_id) if user_id else None,
            }
        )

    # Private helper methods
    
    def _generate_cache_key(self, *args) -> str:
        """Generate cache key from arguments
        
        Args:
            *args: Arguments to include in key
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        # Convert args to JSON string
        key_data = json.dumps(args, sort_keys=True, default=str)
        
        # Generate hash
        return f"search:{hashlib.md5(key_data.encode()).hexdigest()}"

    def _process_search_results(
        self,
        results: Dict[str, Any],
        page: int = 1,
        page_size: int = None,
    ) -> Dict[str, Any]:
        """Process Elasticsearch results
        
        Args:
            results: Raw Elasticsearch results
            page: Current page
            page_size: Results per page
            
        Returns:
            Processed results
        """
        hits = results.get("hits", {})
        total = hits.get("total", {}).get("value", 0)
        
        # Calculate pagination
        if page_size:
            total_pages = (total + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1
        else:
            total_pages = 1
            has_next = False
            has_prev = False
        
        # Format results
        return {
            "results": [
                {
                    "id": hit.get("_id"),
                    "score": hit.get("_score"),
                    "source": hit.get("_source"),
                    "highlight": hit.get("highlight"),
                }
                for hit in hits.get("hits", [])
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "aggregations": results.get("aggregations"),
        }
