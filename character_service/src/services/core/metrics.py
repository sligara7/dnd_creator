"""
Service metrics collection and monitoring.

This service handles collection and aggregation of various metrics including:
- System resource usage (CPU, memory)
- Database performance
- API request tracking
- Response timing
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from collections import defaultdict

from src.core.logging_config import get_logger
from src.core.config import settings

logger = get_logger(__name__)

# Constants for metrics collection
METRICS_RETENTION_DAYS = 7
METRICS_COLLECTION_INTERVAL = 60  # seconds
REQUEST_BUCKETS = [0.1, 0.5, 1.0, 2.0, 5.0]  # Latency buckets in seconds

class MetricsService:
    """Service for collecting and aggregating system metrics."""
    
    def __init__(self, db: Session):
        self.db = db
        self.requests = defaultdict(list)  # path -> [(timestamp, duration)]
        self.errors = defaultdict(list)    # path -> [(timestamp, error_type)]
        self._collection_task = None
    
    async def start_collection(self):
        """Start background metrics collection."""
        if self._collection_task is None:
            logger.info("starting_metrics_collection")
            self._collection_task = asyncio.create_task(self._collect_metrics())
    
    async def stop_collection(self):
        """Stop background metrics collection."""
        if self._collection_task is not None:
            logger.info("stopping_metrics_collection")
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None
    
    async def _collect_metrics(self):
        """Background task to collect metrics periodically."""
        while True:
            try:
                # Collect current metrics
                cpu_metrics = await self.get_cpu_metrics()
                memory_metrics = await self.get_memory_metrics()
                db_metrics = await self.get_db_metrics()
                
                # Store metrics (implement storage later)
                logger.info(
                    "metrics_collected",
                    cpu=cpu_metrics,
                    memory=memory_metrics,
                    database=db_metrics
                )
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error(
                    "metrics_collection_failed",
                    error=str(e),
                    error_type=type(e).__name__
                )
            
            # Wait for next collection interval
            await asyncio.sleep(METRICS_COLLECTION_INTERVAL)
    
    async def get_cpu_metrics(self) -> Dict[str, float]:
        """Get CPU usage metrics."""
        try:
            return {
                "usage_percent": psutil.cpu_percent(interval=1),
                "load_avg_1min": psutil.getloadavg()[0],
                "load_avg_5min": psutil.getloadavg()[1],
                "load_avg_15min": psutil.getloadavg()[2]
            }
        except Exception as e:
            logger.error(
                "cpu_metrics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "usage_percent": 0.0,
                "load_avg_1min": 0.0,
                "load_avg_5min": 0.0,
                "load_avg_15min": 0.0
            }
    
    async def get_memory_metrics(self) -> Dict[str, int]:
        """Get memory usage metrics."""
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent
            }
        except Exception as e:
            logger.error(
                "memory_metrics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "total": 0,
                "available": 0,
                "used": 0,
                "free": 0,
                "percent": 0
            }
    
    async def get_db_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            # Get connection pool stats
            pool_stats = await self._get_db_pool_stats()
            
            # Get query timing stats
            query_stats = await self._get_db_query_stats()
            
            return {
                "pool": pool_stats,
                "queries": query_stats
            }
        except Exception as e:
            logger.error(
                "db_metrics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "pool": {},
                "queries": {}
            }
    
    async def _get_db_pool_stats(self) -> Dict[str, int]:
        """Get database connection pool statistics."""
        try:
            # This will need to be customized based on your DB backend
            return {
                "size": self.db.bind.pool.size(),
                "checked_out": self.db.bind.pool.checkedout(),
                "overflow": self.db.bind.pool.overflow()
            }
        except Exception as e:
            logger.error(
                "db_pool_stats_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "size": 0,
                "checked_out": 0,
                "overflow": 0
            }
    
    async def _get_db_query_stats(self) -> Dict[str, Any]:
        """Get database query performance statistics."""
        try:
            # Example query to get table stats
            result = await self.db.execute(text("""
                SELECT schemaname, relname, n_live_tup, n_dead_tup
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 10
            """))
            
            table_stats = []
            for row in result:
                table_stats.append({
                    "schema": row.schemaname,
                    "table": row.relname,
                    "live_rows": row.n_live_tup,
                    "dead_rows": row.n_dead_tup
                })
            
            return {
                "table_stats": table_stats,
                "query_count": await self._get_query_count(),
                "slow_queries": await self._get_slow_queries()
            }
        except Exception as e:
            logger.error(
                "db_query_stats_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "table_stats": [],
                "query_count": 0,
                "slow_queries": []
            }
    
    async def _get_query_count(self) -> int:
        """Get total number of queries executed."""
        try:
            result = await self.db.execute(text("""
                SELECT COUNT(*) as count
                FROM pg_stat_statements
                WHERE userid = current_user
            """))
            row = await result.fetchone()
            return row.count if row else 0
        except Exception:
            return 0
    
    async def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get list of slow queries."""
        try:
            result = await self.db.execute(text("""
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements
                WHERE userid = current_user
                ORDER BY mean_time DESC
                LIMIT 5
            """))
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    "query": row.query,
                    "calls": row.calls,
                    "total_time": row.total_time,
                    "mean_time": row.mean_time
                })
            return slow_queries
        except Exception:
            return []
    
    def record_request(self, path: str, duration: float, error: Optional[str] = None):
        """Record an API request with its duration and optional error."""
        now = datetime.utcnow()
        
        # Record request timing
        self.requests[path].append((now, duration))
        
        # Record error if any
        if error:
            self.errors[path].append((now, error))
            logger.warning(
                "request_error",
                path=path,
                duration=duration,
                error=error
            )
        else:
            logger.info(
                "request_success",
                path=path,
                duration=duration
            )
    
    def get_request_metrics(self) -> Dict[str, Any]:
        """Get API request metrics aggregated by path."""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=METRICS_RETENTION_DAYS)
        metrics = {}
        
        for path, requests in self.requests.items():
            # Filter to recent requests
            recent = [(ts, dur) for ts, dur in requests if ts > cutoff]
            
            if not recent:
                continue
            
            # Calculate stats
            durations = [dur for _, dur in recent]
            error_count = len([err for ts, err in self.errors[path] if ts > cutoff])
            
            metrics[path] = {
                "count": len(recent),
                "error_count": error_count,
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_duration": sum(durations) / len(durations),
                "latency_buckets": self._calculate_latency_buckets(durations)
            }
        
        return metrics
    
    def _calculate_latency_buckets(self, durations: List[float]) -> Dict[str, int]:
        """Calculate latency distribution buckets."""
        buckets = {}
        for bucket in REQUEST_BUCKETS:
            count = len([d for d in durations if d <= bucket])
            buckets[f"le_{bucket}"] = count
        buckets["le_inf"] = len(durations)
        return buckets
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=METRICS_RETENTION_DAYS)
        
        for path in list(self.requests.keys()):
            self.requests[path] = [
                (ts, dur) for ts, dur in self.requests[path] 
                if ts > cutoff
            ]
            if not self.requests[path]:
                del self.requests[path]
        
        for path in list(self.errors.keys()):
            self.errors[path] = [
                (ts, err) for ts, err in self.errors[path]
                if ts > cutoff
            ]
            if not self.errors[path]:
                del self.errors[path]
