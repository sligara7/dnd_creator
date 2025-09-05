import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from search_service.core.config import settings
from search_service.core.logging import log_analytics_event


class SearchAnalytics:
    """Search analytics handler"""

    def __init__(
        self,
        es_client: AsyncElasticsearch,
        redis_client: Redis,
        analytics_index: str = "search-analytics"
    ):
        self.es = es_client
        self.redis = redis_client
        self.analytics_index = analytics_index

    async def track_search_event(
        self,
        query: str,
        index_type: str,
        total_hits: int,
        took_ms: int,
        filters: Optional[Dict] = None,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Track search event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "index_type": index_type,
            "total_hits": total_hits,
            "took_ms": took_ms,
            "filters": filters or {},
            "user_id": str(user_id) if user_id else None,
            "session_id": session_id,
        }

        try:
            # Store event in Elasticsearch
            await self.es.index(
                index=self.analytics_index,
                document=event,
            )

            # Update query stats in Redis
            key_base = f"stats:query:{index_type}:"
            pipeline = self.redis.pipeline()

            # Increment query count
            pipeline.incr(f"{key_base}count")

            # Add to popular queries (sorted set)
            pipeline.zincrby(f"{key_base}popular", 1, query.lower())

            # Track response time
            pipeline.lpush(f"{key_base}times", took_ms)
            pipeline.ltrim(f"{key_base}times", 0, 999)  # Keep last 1000 times

            # Track zero results
            if total_hits == 0:
                pipeline.sadd(f"{key_base}zero_hits", query.lower())

            await pipeline.execute()

            log_analytics_event("search", event)
        except Exception as e:
            log_analytics_event("search", event, error=e)

    async def track_click_event(
        self,
        query: str,
        index_type: str,
        document_id: UUID,
        position: int,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Track result click event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "index_type": index_type,
            "document_id": str(document_id),
            "position": position,
            "user_id": str(user_id) if user_id else None,
            "session_id": session_id,
        }

        try:
            # Store event in Elasticsearch
            await self.es.index(
                index=self.analytics_index,
                document=event,
            )

            # Update click stats in Redis
            key_base = f"stats:clicks:{index_type}:"
            pipeline = self.redis.pipeline()

            # Track query-result pair
            click_key = f"{query.lower()}:{document_id}"
            pipeline.zincrby(f"{key_base}pairs", 1, click_key)

            # Track position stats
            pipeline.hincrby(f"{key_base}positions", str(position), 1)

            await pipeline.execute()

            log_analytics_event("click", event)
        except Exception as e:
            log_analytics_event("click", event, error=e)

    async def get_popular_queries(
        self,
        index_type: str,
        limit: int = 10,
        min_count: int = 2,
    ) -> List[Dict[str, float]]:
        """Get popular search queries"""
        key = f"stats:query:{index_type}:popular"
        try:
            results = await self.redis.zrevrangebyscore(
                key,
                min=min_count,
                max=float("inf"),
                start=0,
                num=limit,
                withscores=True,
            )
            return [
                {"query": query, "count": count}
                for query, count in results
            ]
        except Exception as e:
            log_analytics_event("get_popular", {"index_type": index_type}, error=e)
            return []

    async def get_zero_hit_queries(
        self,
        index_type: str,
    ) -> List[str]:
        """Get queries that returned no results"""
        key = f"stats:query:{index_type}:zero_hits"
        try:
            return await self.redis.smembers(key)
        except Exception as e:
            log_analytics_event(
                "get_zero_hits",
                {"index_type": index_type},
                error=e
            )
            return []

    async def get_performance_stats(
        self,
        index_type: str,
    ) -> Dict[str, float]:
        """Get search performance statistics"""
        key = f"stats:query:{index_type}:times"
        try:
            times = await self.redis.lrange(key, 0, -1)
            if not times:
                return {
                    "avg_time": 0,
                    "p95_time": 0,
                    "p99_time": 0,
                }

            times = [float(t) for t in times]
            times.sort()
            n = len(times)

            return {
                "avg_time": sum(times) / n,
                "p95_time": times[int(n * 0.95)],
                "p99_time": times[int(n * 0.99)],
            }
        except Exception as e:
            log_analytics_event(
                "get_performance",
                {"index_type": index_type},
                error=e
            )
            return {
                "avg_time": 0,
                "p95_time": 0,
                "p99_time": 0,
            }

    async def get_search_effectiveness(
        self,
        index_type: str,
        window_hours: int = 24,
    ) -> Dict[str, float]:
        """Get search effectiveness metrics"""
        try:
            # Query Elasticsearch for search events
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": f"now-{window_hours}h",
                                    }
                                }
                            },
                            {"term": {"index_type": index_type}},
                        ]
                    }
                },
                "aggs": {
                    "zero_hits": {
                        "filter": {"term": {"total_hits": 0}},
                    },
                    "avg_hits": {"avg": {"field": "total_hits"}},
                },
                "size": 0,
            }

            search_results = await self.es.search(
                index=self.analytics_index,
                body=search_query,
            )

            total_searches = search_results["hits"]["total"]["value"]
            if total_searches == 0:
                return {
                    "zero_hit_rate": 0,
                    "avg_hits": 0,
                    "success_rate": 0,
                }

            zero_hits = search_results["aggregations"]["zero_hits"]["doc_count"]
            avg_hits = search_results["aggregations"]["avg_hits"]["value"] or 0

            # Query Elasticsearch for click events
            click_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": f"now-{window_hours}h",
                                    }
                                }
                            },
                            {"term": {"index_type": index_type}},
                        ]
                    }
                },
                "size": 0,
            }

            click_results = await self.es.search(
                index=self.analytics_index,
                body=click_query,
            )

            total_clicks = click_results["hits"]["total"]["value"]

            return {
                "zero_hit_rate": zero_hits / total_searches,
                "avg_hits": avg_hits,
                "success_rate": total_clicks / total_searches,
            }
        except Exception as e:
            log_analytics_event(
                "get_effectiveness",
                {"index_type": index_type},
                error=e
            )
            return {
                "zero_hit_rate": 0,
                "avg_hits": 0,
                "success_rate": 0,
            }

    async def get_user_behavior(
        self,
        index_type: str,
        window_hours: int = 24,
    ) -> Dict[str, Any]:
        """Get user behavior analytics"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": f"now-{window_hours}h",
                                    }
                                }
                            },
                            {"term": {"index_type": index_type}},
                        ]
                    }
                },
                "aggs": {
                    "searches_per_user": {
                        "cardinality": {
                            "field": "user_id",
                        }
                    },
                    "searches_per_session": {
                        "cardinality": {
                            "field": "session_id",
                        }
                    },
                    "click_positions": {
                        "histogram": {
                            "field": "position",
                            "interval": 1,
                        }
                    },
                },
                "size": 0,
            }

            results = await self.es.search(
                index=self.analytics_index,
                body=query,
            )

            aggs = results["aggregations"]
            return {
                "searches_per_user": aggs["searches_per_user"]["value"],
                "searches_per_session": aggs["searches_per_session"]["value"],
                "click_positions": [
                    {
                        "position": bucket["key"],
                        "count": bucket["doc_count"],
                    }
                    for bucket in aggs["click_positions"]["buckets"]
                ],
            }
        except Exception as e:
            log_analytics_event(
                "get_user_behavior",
                {"index_type": index_type},
                error=e
            )
            return {
                "searches_per_user": 0,
                "searches_per_session": 0,
                "click_positions": [],
            }
