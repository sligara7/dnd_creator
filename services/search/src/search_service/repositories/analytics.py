"""Analytics repository for search analytics and metrics"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select, Integer, Float, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from search_service.models.database import (
    SearchAnalytics,
    SearchQuery,
    SearchSuggestion,
    CacheMetrics,
    SearchFailure,
)
from search_service.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[SearchAnalytics]):
    """Repository for search analytics operations"""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize analytics repository
        
        Args:
            db: Database session
        """
        super().__init__(db, SearchAnalytics)

    async def track_event(
        self,
        event_type: str,
        index: str,
        data: Dict[str, Any],
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> SearchAnalytics:
        """Track an analytics event
        
        Args:
            event_type: Type of event (search, click, etc.)
            index: Index name
            data: Event data
            session_id: Optional session ID
            user_id: Optional user ID
            
        Returns:
            Created analytics record
        """
        analytics = SearchAnalytics(
            event_type=event_type,
            index=index,
            data=data,
            session_id=session_id,
            user_id=user_id,
        )
        
        return await self.create(analytics)

    async def get_popular_queries(
        self,
        index: Optional[str] = None,
        days: int = 7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries
        
        Args:
            index: Optional index filter
            days: Number of days to look back
            limit: Number of results to return
            
        Returns:
            List of popular queries with counts
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            SearchQuery.query,
            func.count(SearchQuery.id).label("count"),
            func.avg(SearchQuery.duration_ms["search"].cast(Float)).label("avg_duration"),
        ).where(
            SearchQuery.created_at >= since,
            SearchQuery.is_deleted == False,
        )
        
        if index:
            query = query.where(SearchQuery.index == index)
        
        query = query.group_by(SearchQuery.query).order_by(
            func.count(SearchQuery.id).desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        
        return [
            {
                "query": row.query,
                "count": row.count,
                "avg_duration_ms": row.avg_duration,
            }
            for row in result
        ]

    async def get_failed_queries(
        self,
        index: Optional[str] = None,
        days: int = 1,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get failed search queries
        
        Args:
            index: Optional index filter
            days: Number of days to look back
            limit: Number of results to return
            
        Returns:
            List of failed queries
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        query = select(SearchFailure).where(
            SearchFailure.created_at >= since,
            SearchFailure.is_deleted == False,
        )
        
        if index:
            query = query.where(SearchFailure.index == index)
        
        query = query.order_by(SearchFailure.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        failures = result.scalars().all()
        
        return [
            {
                "query": f.query,
                "index": f.index,
                "error_type": f.error_type,
                "error_message": f.error_message,
                "timestamp": f.created_at.isoformat(),
            }
            for f in failures
        ]

    async def get_search_performance(
        self,
        index: Optional[str] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Get search performance metrics
        
        Args:
            index: Optional index filter
            hours: Number of hours to analyze
            
        Returns:
            Performance metrics
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(
            func.count(SearchQuery.id).label("total_queries"),
            func.avg(SearchQuery.duration_ms["search"].cast(Float)).label("avg_duration"),
            func.min(SearchQuery.duration_ms["search"].cast(Float)).label("min_duration"),
            func.max(SearchQuery.duration_ms["search"].cast(Float)).label("max_duration"),
            func.percentile_cont(0.5).within_group(
                SearchQuery.duration_ms["search"].cast(Float)
            ).label("median_duration"),
            func.percentile_cont(0.95).within_group(
                SearchQuery.duration_ms["search"].cast(Float)
            ).label("p95_duration"),
        ).where(
            SearchQuery.created_at >= since,
            SearchQuery.is_deleted == False,
        )
        
        if index:
            query = query.where(SearchQuery.index == index)
        
        result = await self.db.execute(query)
        row = result.one()
        
        return {
            "total_queries": row.total_queries or 0,
            "avg_duration_ms": row.avg_duration or 0,
            "min_duration_ms": row.min_duration or 0,
            "max_duration_ms": row.max_duration or 0,
            "median_duration_ms": row.median_duration or 0,
            "p95_duration_ms": row.p95_duration or 0,
        }

    async def get_cache_metrics(
        self,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Get cache performance metrics
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Cache metrics
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get cache hit rate from queries
        query = select(
            func.count(SearchQuery.id).label("total"),
            func.sum(func.cast(SearchQuery.cache_hit, Integer)).label("hits"),
        ).where(
            SearchQuery.created_at >= since,
            SearchQuery.is_deleted == False,
        )
        
        result = await self.db.execute(query)
        row = result.one()
        
        total = row.total or 0
        hits = row.hits or 0
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        # Get cache size metrics
        cache_query = select(
            func.sum(CacheMetrics.size_bytes["current"].cast(BigInteger)).label("total_size"),
            func.avg(CacheMetrics.latency_ms["get"].cast(Float)).label("avg_latency"),
        ).where(
            CacheMetrics.created_at >= since,
            CacheMetrics.is_deleted == False,
        )
        
        cache_result = await self.db.execute(cache_query)
        cache_row = cache_result.one()
        
        return {
            "hit_rate": hit_rate,
            "total_queries": total,
            "cache_hits": hits,
            "cache_misses": total - hits,
            "total_cache_size_bytes": cache_row.total_size or 0,
            "avg_cache_latency_ms": cache_row.avg_latency or 0,
        }

    async def get_suggestion_effectiveness(
        self,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get search suggestion effectiveness metrics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Suggestion metrics
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            func.count(SearchSuggestion.id).label("total_suggestions"),
            func.sum(func.cast(SearchSuggestion.used, Integer)).label("used_suggestions"),
        ).where(
            SearchSuggestion.created_at >= since,
            SearchSuggestion.is_deleted == False,
        )
        
        result = await self.db.execute(query)
        row = result.one()
        
        total = row.total_suggestions or 0
        used = row.used_suggestions or 0
        usage_rate = (used / total * 100) if total > 0 else 0
        
        return {
            "total_suggestions": total,
            "used_suggestions": used,
            "usage_rate": usage_rate,
        }

    async def get_index_usage(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get index usage statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of index usage stats
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            SearchQuery.index,
            func.count(SearchQuery.id).label("query_count"),
            func.avg(SearchQuery.result_count["total"].cast(Float)).label("avg_results"),
            func.avg(SearchQuery.duration_ms["search"].cast(Float)).label("avg_duration"),
        ).where(
            SearchQuery.created_at >= since,
            SearchQuery.is_deleted == False,
        ).group_by(
            SearchQuery.index
        ).order_by(
            func.count(SearchQuery.id).desc()
        )
        
        result = await self.db.execute(query)
        
        return [
            {
                "index": row.index,
                "query_count": row.query_count,
                "avg_results": row.avg_results or 0,
                "avg_duration_ms": row.avg_duration or 0,
            }
            for row in result
        ]

    async def get_user_search_history(
        self,
        user_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get user's search history
        
        Args:
            user_id: User ID
            limit: Number of results to return
            
        Returns:
            List of user's searches
        """
        query = select(
            SearchAnalytics
        ).where(
            SearchAnalytics.user_id == user_id,
            SearchAnalytics.event_type == "search",
            SearchAnalytics.is_deleted == False,
        ).order_by(
            SearchAnalytics.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        analytics = result.scalars().all()
        
        return [
            {
                "index": a.index,
                "query": a.data.get("query"),
                "results": a.data.get("result_count"),
                "timestamp": a.created_at.isoformat(),
            }
            for a in analytics
        ]

    async def track_click(
        self,
        query: str,
        document_id: str,
        index: str,
        position: int,
        session_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> SearchAnalytics:
        """Track search result click
        
        Args:
            query: Search query
            document_id: Clicked document ID
            index: Index name
            position: Position in results
            session_id: Optional session ID
            user_id: Optional user ID
            
        Returns:
            Created analytics record
        """
        return await self.track_event(
            event_type="click",
            index=index,
            data={
                "query": query,
                "document_id": document_id,
                "position": position,
            },
            session_id=session_id,
            user_id=user_id,
        )

    async def get_click_through_rate(
        self,
        index: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Calculate click-through rate
        
        Args:
            index: Optional index filter
            days: Number of days to analyze
            
        Returns:
            Click-through rate metrics
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Count searches
        search_query = select(
            func.count(SearchAnalytics.id)
        ).where(
            SearchAnalytics.event_type == "search",
            SearchAnalytics.created_at >= since,
            SearchAnalytics.is_deleted == False,
        )
        
        if index:
            search_query = search_query.where(SearchAnalytics.index == index)
        
        search_result = await self.db.execute(search_query)
        search_count = search_result.scalar() or 0
        
        # Count clicks
        click_query = select(
            func.count(SearchAnalytics.id)
        ).where(
            SearchAnalytics.event_type == "click",
            SearchAnalytics.created_at >= since,
            SearchAnalytics.is_deleted == False,
        )
        
        if index:
            click_query = click_query.where(SearchAnalytics.index == index)
        
        click_result = await self.db.execute(click_query)
        click_count = click_result.scalar() or 0
        
        ctr = (click_count / search_count * 100) if search_count > 0 else 0
        
        return {
            "search_count": search_count,
            "click_count": click_count,
            "click_through_rate": ctr,
        }
