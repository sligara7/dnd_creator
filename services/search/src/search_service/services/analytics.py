"""Analytics service for search analytics operations"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from search_service.clients.cache import CacheClient
from search_service.clients.message_hub import MessageHubClient
from search_service.repositories.analytics import AnalyticsRepository
from search_service.models.database import SearchHistory, SearchPerformance
from search_service.core.config import settings
from search_service.core.exceptions import SearchServiceError


class AnalyticsService:
    """Service for search analytics operations"""

    def __init__(
        self,
        db: AsyncSession,
        cache_client: CacheClient,
        message_hub: MessageHubClient,
    ) -> None:
        """Initialize analytics service
        
        Args:
            db: Database session
            cache_client: Cache client
            message_hub: Message hub client
        """
        self.db = db
        self.cache_client = cache_client
        self.message_hub = message_hub
        self.analytics_repo = AnalyticsRepository(db)

    async def track_search_query(
        self,
        query: str,
        index: str,
        result_count: int,
        took_ms: int,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> bool:
        """Track search query for analytics
        
        Args:
            query: Search query text
            index: Index searched
            result_count: Number of results returned
            took_ms: Query execution time in milliseconds
            filters: Optional filters applied
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            True if tracked successfully
        """
        try:
            # Create search history entry
            search_history = SearchHistory(
                query=query,
                index=index,
                result_count=result_count,
                filters=filters or {},
                metadata={
                    "took_ms": took_ms,
                    "has_filters": bool(filters),
                },
                user_id=user_id,
                session_id=session_id,
            )
            
            await self.analytics_repo.create(search_history)
            
            # Update popular queries cache
            await self._update_popular_queries_cache(query, index)
            
            # Track performance metrics
            await self._track_performance_metrics(
                index=index,
                took_ms=took_ms,
                result_count=result_count,
            )
            
            return True
            
        except Exception as e:
            # Log error but don't fail the search
            print(f"Error tracking search query: {str(e)}")
            return False

    async def track_click(
        self,
        document_id: str,
        query: str,
        index: str,
        position: int,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> bool:
        """Track document click for click-through rate analysis
        
        Args:
            document_id: ID of clicked document
            query: Search query that led to the click
            index: Index the document belongs to
            position: Position in search results
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            True if tracked successfully
        """
        try:
            # Track click event
            await self.analytics_repo.track_event(
                event_type="search_click",
                index=index,
                metadata={
                    "document_id": document_id,
                    "query": query,
                    "position": position,
                },
                session_id=session_id,
                user_id=user_id,
            )
            
            # Update click-through rate metrics
            await self._update_ctr_metrics(query, index, position)
            
            # Publish event
            await self.message_hub.publish_event(
                "analytics.click_tracked",
                {
                    "document_id": document_id,
                    "query": query,
                    "index": index,
                    "position": position,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Error tracking click: {str(e)}")
            return False

    async def get_popular_queries(
        self,
        index: Optional[str] = None,
        limit: int = 10,
        time_range: Optional[int] = 24,  # hours
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries
        
        Args:
            index: Optional index to filter by
            limit: Number of queries to return
            time_range: Time range in hours (None for all time)
            
        Returns:
            List of popular queries with counts
        """
        try:
            # Check cache first
            cache_key = f"popular_queries:{index or 'all'}:{time_range or 'all'}:{limit}"
            cached_result = await self.cache_client.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build query
            query = select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
                func.avg(SearchHistory.result_count).label("avg_results"),
            ).where(
                SearchHistory.is_deleted == False
            )
            
            # Add filters
            if index:
                query = query.where(SearchHistory.index == index)
            
            if time_range:
                cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
                query = query.where(SearchHistory.created_at >= cutoff_time)
            
            # Group and order
            query = query.group_by(SearchHistory.query).order_by(
                desc("count")
            ).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            rows = result.all()
            
            # Format results
            popular_queries = [
                {
                    "query": row.query,
                    "count": row.count,
                    "avg_results": float(row.avg_results) if row.avg_results else 0,
                }
                for row in rows
            ]
            
            # Cache results
            await self.cache_client.set(
                cache_key,
                popular_queries,
                ttl=settings.ANALYTICS_CACHE_TTL,
            )
            
            return popular_queries
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting popular queries: {str(e)}",
                "popular_queries_error"
            )

    async def get_search_performance(
        self,
        index: Optional[str] = None,
        time_range: Optional[int] = 24,  # hours
    ) -> Dict[str, Any]:
        """Get search performance metrics
        
        Args:
            index: Optional index to filter by
            time_range: Time range in hours
            
        Returns:
            Performance metrics
        """
        try:
            # Check cache
            cache_key = f"search_performance:{index or 'all'}:{time_range or 'all'}"
            cached_result = await self.cache_client.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build query
            query = select(SearchPerformance).where(
                SearchPerformance.is_deleted == False
            )
            
            # Add filters
            if index:
                query = query.where(SearchPerformance.index == index)
            
            if time_range:
                cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
                query = query.where(SearchPerformance.timestamp >= cutoff_time)
            
            # Execute query
            result = await self.db.execute(query)
            metrics = result.scalars().all()
            
            if not metrics:
                return {
                    "avg_response_time_ms": 0,
                    "total_queries": 0,
                    "cache_hit_rate": 0,
                    "avg_result_count": 0,
                }
            
            # Calculate aggregates
            total_queries = len(metrics)
            avg_response_time = sum(m.response_time for m in metrics) / total_queries
            cache_hits = sum(1 for m in metrics if m.metadata.get("cache_hit"))
            cache_hit_rate = (cache_hits / total_queries) * 100 if total_queries > 0 else 0
            
            # Get result counts from metadata
            result_counts = [
                m.metadata.get("result_count", 0) 
                for m in metrics 
                if "result_count" in m.metadata
            ]
            avg_result_count = sum(result_counts) / len(result_counts) if result_counts else 0
            
            performance_data = {
                "avg_response_time_ms": round(avg_response_time, 2),
                "total_queries": total_queries,
                "cache_hit_rate": round(cache_hit_rate, 2),
                "avg_result_count": round(avg_result_count, 2),
                "index": index or "all",
                "time_range_hours": time_range or "all",
            }
            
            # Cache results
            await self.cache_client.set(
                cache_key,
                performance_data,
                ttl=settings.ANALYTICS_CACHE_TTL,
            )
            
            return performance_data
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting search performance: {str(e)}",
                "performance_metrics_error"
            )

    async def get_zero_result_queries(
        self,
        index: Optional[str] = None,
        limit: int = 10,
        time_range: Optional[int] = 24,  # hours
    ) -> List[Dict[str, Any]]:
        """Get queries that returned zero results
        
        Args:
            index: Optional index to filter by
            limit: Number of queries to return
            time_range: Time range in hours
            
        Returns:
            List of zero-result queries
        """
        try:
            # Build query
            query = select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
                func.max(SearchHistory.created_at).label("last_searched"),
            ).where(
                and_(
                    SearchHistory.is_deleted == False,
                    SearchHistory.result_count == 0,
                )
            )
            
            # Add filters
            if index:
                query = query.where(SearchHistory.index == index)
            
            if time_range:
                cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
                query = query.where(SearchHistory.created_at >= cutoff_time)
            
            # Group and order
            query = query.group_by(SearchHistory.query).order_by(
                desc("count")
            ).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            rows = result.all()
            
            # Format results
            zero_result_queries = [
                {
                    "query": row.query,
                    "count": row.count,
                    "last_searched": row.last_searched.isoformat() if row.last_searched else None,
                }
                for row in rows
            ]
            
            return zero_result_queries
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting zero result queries: {str(e)}",
                "zero_result_queries_error"
            )

    async def get_click_through_rate(
        self,
        index: Optional[str] = None,
        time_range: Optional[int] = 24,  # hours
    ) -> Dict[str, Any]:
        """Get click-through rate metrics
        
        Args:
            index: Optional index to filter by
            time_range: Time range in hours
            
        Returns:
            Click-through rate metrics
        """
        try:
            # Get search and click counts
            search_count = await self._get_search_count(index, time_range)
            click_count = await self._get_click_count(index, time_range)
            
            # Calculate CTR
            ctr = (click_count / search_count * 100) if search_count > 0 else 0
            
            # Get position-based CTR
            position_ctr = await self._get_position_ctr(index, time_range)
            
            return {
                "overall_ctr": round(ctr, 2),
                "total_searches": search_count,
                "total_clicks": click_count,
                "position_ctr": position_ctr,
                "index": index or "all",
                "time_range_hours": time_range or "all",
            }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting click-through rate: {str(e)}",
                "ctr_metrics_error"
            )

    async def get_query_suggestions(
        self,
        partial_query: str,
        index: Optional[str] = None,
        limit: int = 5,
    ) -> List[str]:
        """Get query suggestions based on search history
        
        Args:
            partial_query: Partial query to get suggestions for
            index: Optional index to filter by
            limit: Number of suggestions to return
            
        Returns:
            List of query suggestions
        """
        try:
            # Check cache
            cache_key = f"suggestions:{partial_query}:{index or 'all'}:{limit}"
            cached_result = await self.cache_client.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build query
            query = select(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count"),
            ).where(
                and_(
                    SearchHistory.is_deleted == False,
                    SearchHistory.query.ilike(f"{partial_query}%"),
                    SearchHistory.result_count > 0,  # Only suggest queries with results
                )
            )
            
            # Add index filter
            if index:
                query = query.where(SearchHistory.index == index)
            
            # Group and order by popularity
            query = query.group_by(SearchHistory.query).order_by(
                desc("count")
            ).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            rows = result.all()
            
            # Extract suggestions
            suggestions = [row.query for row in rows]
            
            # Cache results
            await self.cache_client.set(
                cache_key,
                suggestions,
                ttl=300,  # 5 minutes
            )
            
            return suggestions
            
        except Exception as e:
            raise SearchServiceError(
                f"Error getting query suggestions: {str(e)}",
                "query_suggestions_error"
            )

    async def export_analytics(
        self,
        index: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export analytics data
        
        Args:
            index: Optional index to filter by
            start_date: Start date for export
            end_date: End date for export
            format: Export format (json, csv)
            
        Returns:
            Exported data or export metadata
        """
        try:
            # Build query
            query = select(SearchHistory).where(
                SearchHistory.is_deleted == False
            )
            
            # Add filters
            if index:
                query = query.where(SearchHistory.index == index)
            
            if start_date:
                query = query.where(SearchHistory.created_at >= start_date)
            
            if end_date:
                query = query.where(SearchHistory.created_at <= end_date)
            
            # Execute query
            result = await self.db.execute(query)
            search_history = result.scalars().all()
            
            # Format data
            export_data = []
            for entry in search_history:
                export_data.append({
                    "query": entry.query,
                    "index": entry.index,
                    "result_count": entry.result_count,
                    "timestamp": entry.created_at.isoformat(),
                    "filters": entry.filters,
                    "user_id": str(entry.user_id) if entry.user_id else None,
                    "session_id": str(entry.session_id) if entry.session_id else None,
                })
            
            # Handle different formats
            if format == "csv":
                # Convert to CSV format (simplified)
                import csv
                import io
                
                output = io.StringIO()
                if export_data:
                    writer = csv.DictWriter(
                        output,
                        fieldnames=export_data[0].keys()
                    )
                    writer.writeheader()
                    writer.writerows(export_data)
                
                return {
                    "format": "csv",
                    "data": output.getvalue(),
                    "row_count": len(export_data),
                }
            else:
                return {
                    "format": "json",
                    "data": export_data,
                    "row_count": len(export_data),
                }
            
        except Exception as e:
            raise SearchServiceError(
                f"Error exporting analytics: {str(e)}",
                "export_analytics_error"
            )

    # Private helper methods

    async def _update_popular_queries_cache(
        self,
        query: str,
        index: str,
    ) -> None:
        """Update popular queries cache"""
        cache_key = f"query_count:{index}:{query}"
        count = await self.cache_client.get(cache_key) or 0
        await self.cache_client.set(cache_key, count + 1, ttl=3600)

    async def _track_performance_metrics(
        self,
        index: str,
        took_ms: int,
        result_count: int,
    ) -> None:
        """Track performance metrics"""
        performance = SearchPerformance(
            index=index,
            response_time=took_ms,
            metadata={
                "result_count": result_count,
                "timestamp": datetime.utcnow().isoformat(),
            },
            timestamp=datetime.utcnow(),
        )
        await self.analytics_repo.create(performance)

    async def _update_ctr_metrics(
        self,
        query: str,
        index: str,
        position: int,
    ) -> None:
        """Update click-through rate metrics"""
        cache_key = f"ctr:{index}:{query}:{position}"
        clicks = await self.cache_client.get(cache_key) or 0
        await self.cache_client.set(cache_key, clicks + 1, ttl=3600)

    async def _get_search_count(
        self,
        index: Optional[str],
        time_range: Optional[int],
    ) -> int:
        """Get total search count"""
        query = select(func.count(SearchHistory.id)).where(
            SearchHistory.is_deleted == False
        )
        
        if index:
            query = query.where(SearchHistory.index == index)
        
        if time_range:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            query = query.where(SearchHistory.created_at >= cutoff_time)
        
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_click_count(
        self,
        index: Optional[str],
        time_range: Optional[int],
    ) -> int:
        """Get total click count from events"""
        # This would query an events table if we had one
        # For now, return a simulated value
        cache_key = f"click_count:{index or 'all'}:{time_range or 'all'}"
        return await self.cache_client.get(cache_key) or 0

    async def _get_position_ctr(
        self,
        index: Optional[str],
        time_range: Optional[int],
    ) -> Dict[int, float]:
        """Get CTR by position"""
        # Simplified implementation
        return {
            1: 30.0,  # Position 1: 30% CTR
            2: 15.0,  # Position 2: 15% CTR
            3: 10.0,  # Position 3: 10% CTR
            4: 7.0,   # Position 4: 7% CTR
            5: 5.0,   # Position 5: 5% CTR
        }
