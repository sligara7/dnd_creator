from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from search_service.analytics.search_analytics import SearchAnalytics
from search_service.api.dependencies import (
    get_db,
    get_es,
    get_cache,
)


router = APIRouter()


@router.get(
    "/analytics/queries/popular/{index_type}",
    response_model=List[Dict[str, float]],
    summary="Get popular search queries",
    description="Returns a list of popular search queries with their usage counts",
)
async def get_popular_queries(
    index_type: str,
    limit: int = Query(10, gt=0, le=100),
    min_count: int = Query(2, ge=1),
    analytics: SearchAnalytics = Depends(SearchAnalytics),
) -> List[Dict[str, float]]:
    return await analytics.get_popular_queries(
        index_type=index_type,
        limit=limit,
        min_count=min_count,
    )


@router.get(
    "/analytics/queries/zero-hits/{index_type}",
    response_model=List[str],
    summary="Get zero-hit queries",
    description="Returns a list of search queries that returned no results",
)
async def get_zero_hit_queries(
    index_type: str,
    analytics: SearchAnalytics = Depends(SearchAnalytics),
) -> List[str]:
    return await analytics.get_zero_hit_queries(index_type=index_type)


@router.get(
    "/analytics/performance/{index_type}",
    response_model=Dict[str, float],
    summary="Get performance statistics",
    description="Returns search performance statistics including average and percentile latencies",
)
async def get_performance_stats(
    index_type: str,
    analytics: SearchAnalytics = Depends(SearchAnalytics),
) -> Dict[str, float]:
    return await analytics.get_performance_stats(index_type=index_type)


@router.get(
    "/analytics/effectiveness/{index_type}",
    response_model=Dict[str, float],
    summary="Get search effectiveness metrics",
    description="Returns search effectiveness metrics including zero-hit rate and success rate",
)
async def get_search_effectiveness(
    index_type: str,
    window_hours: int = Query(24, gt=0, le=168),
    analytics: SearchAnalytics = Depends(SearchAnalytics),
) -> Dict[str, float]:
    return await analytics.get_search_effectiveness(
        index_type=index_type,
        window_hours=window_hours,
    )


@router.get(
    "/analytics/behavior/{index_type}",
    response_model=Dict,
    summary="Get user behavior analytics",
    description="Returns user behavior analytics including searches per user and click positions",
)
async def get_user_behavior(
    index_type: str,
    window_hours: int = Query(24, gt=0, le=168),
    analytics: SearchAnalytics = Depends(SearchAnalytics),
) -> Dict:
    return await analytics.get_user_behavior(
        index_type=index_type,
        window_hours=window_hours,
    )
