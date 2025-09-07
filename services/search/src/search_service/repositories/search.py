"""Search repository for Elasticsearch operations"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.models.database import SearchQuery, SearchSuggestion
from search_service.repositories.base import BaseRepository
from search_service.core.config import settings


class SearchRepository(BaseRepository[SearchQuery]):
    """Repository for search operations"""

    def __init__(self, db: AsyncSession, es_client: ElasticsearchClient) -> None:
        """Initialize search repository
        
        Args:
            db: Database session for metadata
            es_client: Elasticsearch client
        """
        super().__init__(db, SearchQuery)
        self.es_client = es_client

    async def search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = None,
        from_: int = None,
        sort: Optional[List[Dict[str, Any]]] = None,
        source_fields: Optional[List[str]] = None,
        track_query: bool = True,
    ) -> Dict[str, Any]:
        """Execute full-text search
        
        Args:
            index: Index to search
            query: Search query text
            filters: Optional filters to apply
            size: Number of results to return
            from_: Starting position for pagination
            sort: Sort criteria
            source_fields: Fields to return
            track_query: Whether to track query for analytics
            
        Returns:
            Search results with metadata
        """
        # Build Elasticsearch query
        es_query = self._build_query(query, filters)
        
        # Execute search
        import time
        start_time = time.time()
        
        results = await self.es_client.search(
            index=index,
            query=es_query,
            size=size or settings.DEFAULT_PAGE_SIZE,
            from_=from_ or 0,
            sort=sort,
            source=source_fields,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Track query if requested
        if track_query:
            await self._track_query(
                query=query,
                index=index,
                filters=filters,
                result_count=results.get("hits", {}).get("total", {}).get("value", 0),
                duration_ms=duration_ms,
            )
        
        return results

    async def semantic_search(
        self,
        index: str,
        query: str,
        vector_field: str = "embedding",
        filters: Optional[Dict[str, Any]] = None,
        size: int = None,
        min_score: float = 0.7,
    ) -> Dict[str, Any]:
        """Execute semantic/vector search
        
        Args:
            index: Index to search
            query: Search query text
            vector_field: Field containing document embeddings
            filters: Optional filters to apply
            size: Number of results to return
            min_score: Minimum similarity score
            
        Returns:
            Search results with similarity scores
        """
        # Generate query embedding (placeholder - would use actual embedding service)
        query_vector = await self._generate_embedding(query)
        
        # Build kNN search query
        es_query = {
            "knn": {
                vector_field: {
                    "vector": query_vector,
                    "k": size or settings.DEFAULT_PAGE_SIZE,
                }
            },
            "min_score": min_score,
        }
        
        if filters:
            es_query["filter"] = self._build_filters(filters)
        
        return await self.es_client.search(
            index=index,
            query={"bool": {"must": [es_query]}},
            size=size or settings.DEFAULT_PAGE_SIZE,
        )

    async def faceted_search(
        self,
        index: str,
        query: Optional[str] = None,
        facets: List[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10,
    ) -> Dict[str, Any]:
        """Execute faceted search with aggregations
        
        Args:
            index: Index to search
            query: Optional search query
            facets: Fields to generate facets for
            filters: Optional filters to apply
            size: Number of results per page
            
        Returns:
            Search results with facet counts
        """
        # Build query
        es_query = {}
        if query:
            es_query = self._build_query(query, filters)
        elif filters:
            es_query = {"bool": {"filter": self._build_filters(filters)}}
        else:
            es_query = {"match_all": {}}
        
        # Build aggregations
        aggs = {}
        if facets:
            for facet in facets:
                aggs[facet] = {
                    "terms": {
                        "field": facet,
                        "size": 20,  # Top 20 values per facet
                    }
                }
        
        # Execute search with aggregations
        body = {"query": es_query}
        if aggs:
            body["aggs"] = aggs
        
        return await self.es_client.search(
            index=index,
            query=es_query,
            size=size,
        )

    async def suggest(
        self,
        index: str,
        query: str,
        suggest_field: str = "name.suggest",
        size: int = 5,
    ) -> List[str]:
        """Get search suggestions
        
        Args:
            index: Index to search
            query: Partial query text
            suggest_field: Field configured for suggestions
            size: Number of suggestions to return
            
        Returns:
            List of suggested completions
        """
        body = {
            "suggest": {
                "text": query,
                "completion": {
                    "field": suggest_field,
                    "size": size,
                    "skip_duplicates": True,
                    "fuzzy": {
                        "fuzziness": "AUTO",
                    }
                }
            }
        }
        
        results = await self.es_client.client.search(
            index=settings.INDEX_PREFIX + index,
            body=body,
        )
        
        suggestions = []
        for suggestion in results.get("suggest", {}).get("completion", []):
            for option in suggestion.get("options", []):
                suggestions.append(option.get("text"))
        
        # Track suggestions
        if suggestions:
            for suggested in suggestions[:1]:  # Track top suggestion
                await self._track_suggestion(query, suggested, index)
        
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
            query: Partial query text
            field: Field to search
            size: Number of results to return
            
        Returns:
            List of matching documents
        """
        es_query = {
            "match_phrase_prefix": {
                field: {
                    "query": query,
                    "max_expansions": 50,
                }
            }
        }
        
        results = await self.es_client.search(
            index=index,
            query=es_query,
            size=size,
            source_fields=[field, "id"],
        )
        
        return [hit["_source"] for hit in results.get("hits", {}).get("hits", [])]

    async def more_like_this(
        self,
        index: str,
        document_id: str,
        fields: List[str] = None,
        size: int = 10,
        min_term_freq: int = 2,
        min_doc_freq: int = 5,
    ) -> Dict[str, Any]:
        """Find similar documents
        
        Args:
            index: Index to search
            document_id: ID of reference document
            fields: Fields to compare
            size: Number of similar documents to return
            min_term_freq: Minimum term frequency
            min_doc_freq: Minimum document frequency
            
        Returns:
            Similar documents
        """
        es_query = {
            "more_like_this": {
                "fields": fields or ["name", "description"],
                "like": [
                    {
                        "_index": settings.INDEX_PREFIX + index,
                        "_id": document_id,
                    }
                ],
                "min_term_freq": min_term_freq,
                "min_doc_freq": min_doc_freq,
                "max_query_terms": 12,
            }
        }
        
        return await self.es_client.search(
            index=index,
            query=es_query,
            size=size,
        )

    # Private helper methods
    
    def _build_query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build Elasticsearch query from text and filters
        
        Args:
            query: Search query text
            filters: Optional filters
            
        Returns:
            Elasticsearch query dict
        """
        # Multi-match query across relevant fields
        must = [{
            "multi_match": {
                "query": query,
                "fields": [
                    "name^3",  # Boost name field
                    "description^2",  # Boost description
                    "content",
                    "tags",
                ],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "minimum_should_match": settings.MINIMUM_SHOULD_MATCH,
            }
        }]
        
        # Add filters if provided
        filter_clauses = []
        if filters:
            filter_clauses = self._build_filters(filters)
        
        return {
            "bool": {
                "must": must,
                "filter": filter_clauses if filter_clauses else None,
            }
        }

    def _build_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build filter clauses from filter dict
        
        Args:
            filters: Filter conditions
            
        Returns:
            List of Elasticsearch filter clauses
        """
        filter_clauses = []
        
        for field, value in filters.items():
            if isinstance(value, dict):
                # Range query
                if any(k in value for k in ["gte", "gt", "lte", "lt"]):
                    filter_clauses.append({"range": {field: value}})
            elif isinstance(value, list):
                # Terms query for multiple values
                filter_clauses.append({"terms": {field: value}})
            else:
                # Term query for single value
                filter_clauses.append({"term": {field: value}})
        
        return filter_clauses

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Placeholder - would integrate with actual embedding service
        # For now, return a dummy vector
        import hashlib
        import struct
        
        # Generate deterministic vector from text hash
        hash_bytes = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(0, min(32, len(hash_bytes)), 4):
            value = struct.unpack('f', hash_bytes[i:i+4])[0]
            vector.append(value)
        
        # Normalize to unit length
        magnitude = sum(v**2 for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector

    async def _track_query(
        self,
        query: str,
        index: str,
        filters: Optional[Dict[str, Any]],
        result_count: int,
        duration_ms: int,
    ) -> None:
        """Track search query for analytics
        
        Args:
            query: Search query
            index: Index searched
            filters: Applied filters
            result_count: Number of results
            duration_ms: Query duration
        """
        search_query = SearchQuery(
            query=query,
            index=index,
            filters=filters,
            result_count={"total": result_count},
            duration_ms={"search": duration_ms},
            cache_hit=False,
        )
        
        self.db.add(search_query)
        await self.db.flush()

    async def _track_suggestion(
        self,
        original: str,
        suggested: str,
        index: str,
    ) -> None:
        """Track search suggestion
        
        Args:
            original: Original query
            suggested: Suggested query
            index: Index name
        """
        suggestion = SearchSuggestion(
            original_query=original,
            suggested_query=suggested,
            index=index,
            used=False,
        )
        
        self.db.add(suggestion)
        await self.db.flush()
