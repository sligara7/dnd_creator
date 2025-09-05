from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from search_service.api.dependencies import get_db, get_es, get_cache
from search_service.schemas.base import (
    SearchQuery,
    SearchResponse,
    SearchHit,
    SuggestQuery,
    SuggestResponse,
    IndexOperation,
    IndexResponse,
    BulkOperation,
    BulkResponse,
    ErrorResponse,
)
from search_service.core.exceptions import SearchServiceError
from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.clients.cache import CacheManager


# Create router
api_router = APIRouter()


@api_router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def search(
    query: SearchQuery,
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
) -> SearchResponse:
    """Perform search query"""
    # Try to get cached results
    if not query.explain:  # Don't cache explain queries
        cached_results = await cache.get_cached_search_results(query.dict())
        if cached_results:
            return SearchResponse(**cached_results)

    # Execute search
    results = await es.search(
        index_type=query.index_type,
        query=query.query,
        filters=query.filters,
        facets=query.facets,
        size=query.size,
        offset=query.offset,
        sort=query.sort,
        highlight=query.highlight,
        fuzzy=query.fuzzy,
        semantic=query.semantic,
        explain=query.explain,
    )

    # Cache results
    if not query.explain:
        await cache.cache_search_results(
            query.dict(),
            results,
            ttl=None  # Use default TTL
        )
        
    # Track query for analytics
    await cache.track_popular_queries(query.query, query.index_type)

    return SearchResponse(**results)


@api_router.post(
    "/search/multi",
    response_model=List[SearchResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def multi_search(
    queries: List[SearchQuery],
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
) -> List[SearchResponse]:
    """Perform multiple search queries"""
    responses = []
    for query in queries:
        # Try cache
        if not query.explain:
            cached_results = await cache.get_cached_search_results(query.dict())
            if cached_results:
                responses.append(SearchResponse(**cached_results))
                continue

        # Execute search
        results = await es.search(
            index_type=query.index_type,
            query=query.query,
            filters=query.filters,
            facets=query.facets,
            size=query.size,
            offset=query.offset,
            sort=query.sort,
            highlight=query.highlight,
            fuzzy=query.fuzzy,
            semantic=query.semantic,
            explain=query.explain,
        )

        # Cache results
        if not query.explain:
            await cache.cache_search_results(
                query.dict(),
                results,
                ttl=None
            )

        responses.append(SearchResponse(**results))

    return responses


@api_router.get(
    "/search/suggest",
    response_model=SuggestResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def suggest(
    query: SuggestQuery,
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
) -> SuggestResponse:
    """Get search suggestions"""
    # Try cache
    cached_suggestions = await cache.get_cached_suggestions(query.text)
    if cached_suggestions:
        return SuggestResponse(
            suggestions=cached_suggestions,
            took=0
        )

    # Get suggestions
    suggestions = await es.suggest(
        index_type=query.index_type,
        text=query.text,
        size=query.size,
        fuzzy=query.fuzzy,
    )

    # Cache suggestions
    await cache.cache_suggestions(
        query.text,
        suggestions,
        ttl=None
    )

    return SuggestResponse(
        suggestions=suggestions,
        took=0  # TODO: Add timing
    )


@api_router.get(
    "/search/autocomplete",
    response_model=List[str],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def autocomplete(
    text: str = Query(..., description="Text to autocomplete"),
    index_type: str = Query(..., description="Index type"),
    field: str = Query("name", description="Field to autocomplete"),
    size: int = Query(5, description="Number of suggestions"),
    es: ElasticsearchClient = Depends(get_es),
) -> List[str]:
    """Get autocompletion suggestions"""
    suggestions = await es.suggest(
        index_type=index_type,
        text=text,
        field=field,
        size=size,
    )
    return suggestions


@api_router.post(
    "/search/scroll",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def scroll_search(
    query: SearchQuery,
    scroll_id: Optional[str] = None,
    scroll_time: str = "1m",
    es: ElasticsearchClient = Depends(get_es),
) -> SearchResponse:
    """Search with scrolling for large result sets"""
    results = await es.scroll_search(
        index_type=query.index_type,
        query=query.query,
        filters=query.filters,
        scroll_id=scroll_id,
        scroll_time=scroll_time,
        size=query.size,
    )
    return SearchResponse(**results)


@api_router.post(
    "/indices/{name}",
    response_model=IndexResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def create_index(
    name: str,
    es: ElasticsearchClient = Depends(get_es),
) -> IndexResponse:
    """Create index"""
    result = await es.create_index(name)
    return IndexResponse(**result)


@api_router.delete(
    "/indices/{name}",
    response_model=IndexResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def delete_index(
    name: str,
    es: ElasticsearchClient = Depends(get_es),
) -> IndexResponse:
    """Delete index"""
    result = await es.delete_index(name)
    return IndexResponse(**result)


@api_router.post(
    "/documents",
    response_model=IndexResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def index_document(
    operation: IndexOperation,
    es: ElasticsearchClient = Depends(get_es),
) -> IndexResponse:
    """Index document"""
    if operation.operation not in ["create", "update", "delete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type"
        )

    if operation.operation == "create":
        result = await es.index_document(
            operation.index_type,
            operation.document_id,
            operation.document
        )
    elif operation.operation == "update":
        result = await es.update_document(
            operation.index_type,
            operation.document_id,
            operation.document
        )
    else:  # delete
        result = await es.delete_document(
            operation.index_type,
            operation.document_id
        )

    return IndexResponse(**result)


@api_router.post(
    "/documents/bulk",
    response_model=BulkResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def bulk_index(
    operation: BulkOperation,
    es: ElasticsearchClient = Depends(get_es),
) -> BulkResponse:
    """Bulk index documents"""
    documents = []
    for op in operation.operations:
        if not op.document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document missing for operation {op.operation}"
            )
        documents.append(op.document)

    result = await es.bulk_index(
        operation.operations[0].index_type,  # Use first operation's index type
        documents
    )
    return BulkResponse(**result)


# Health check routes
@api_router.get("/health/live")
async def liveness_check() -> dict:
    """Liveness probe"""
    return {"status": "ok"}


@api_router.get("/health/ready")
async def readiness_check(
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Readiness probe"""
    status = {
        "status": "ok",
        "components": {}
    }

    # Check Elasticsearch
    try:
        es_health = await es.health()
        status["components"]["elasticsearch"] = {
            "status": "ok",
            "details": es_health
        }
    except Exception as e:
        status["components"]["elasticsearch"] = {
            "status": "error",
            "error": str(e)
        }
        status["status"] = "error"

    # Check Redis
    try:
        redis_health = await cache.health()
        status["components"]["redis"] = {
            "status": "ok" if redis_health else "error"
        }
    except Exception as e:
        status["components"]["redis"] = {
            "status": "error",
            "error": str(e)
        }
        status["status"] = "error"

    # Check database
    try:
        await db.execute("SELECT 1")
        status["components"]["database"] = {
            "status": "ok"
        }
    except Exception as e:
        status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        status["status"] = "error"

    return status
