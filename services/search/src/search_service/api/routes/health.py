from typing import Dict, Any
from datetime import datetime
import psutil
import os
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from search_service.api.dependencies import get_db, get_es, get_cache
from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.clients.cache import CacheManager
from search_service.core.config import settings
from search_service.core.metrics import (
    es_health_gauge,
    es_nodes_gauge,
    es_shards_gauge,
    es_unassigned_shards_gauge,
    cache_keys_gauge,
    cache_memory_gauge,
    cache_clients_gauge,
    cache_hits_gauge,
    cache_misses_gauge,
    system_memory_usage,
    system_cpu_usage,
    system_open_files,
    system_connections,
    component_health,
)


router = APIRouter()


@router.get(
    "/health/live",
    summary="Liveness probe",
    description="Basic health check endpoint for liveness probe",
    response_model=Dict[str, Any],
)
async def liveness() -> Dict[str, Any]:
    """Simple liveness check"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
    }


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="Detailed health check endpoint for readiness probe",
    response_model=Dict[str, Any],
)
async def readiness(
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Check if service and dependencies are ready to handle traffic"""
    status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "components": {},
    }

    # Check Elasticsearch
    try:
        es_health = await es.health()
        status["components"]["elasticsearch"] = {
            "status": "ok",
            "details": {
                "cluster_name": es_health.get("cluster_name"),
                "status": es_health.get("status"),
                "number_of_nodes": es_health.get("number_of_nodes"),
                "active_shards": es_health.get("active_shards"),
                "unassigned_shards": es_health.get("unassigned_shards"),
                "timed_out": es_health.get("timed_out"),
            },
        }
    except Exception as e:
        status["components"]["elasticsearch"] = {
            "status": "error",
            "error": str(e),
        }
        status["status"] = "error"

    # Check Redis
    try:
        redis_health = await cache.health()
        redis_info = await cache.get_info()
        status["components"]["redis"] = {
            "status": "ok" if redis_health else "error",
            "details": {
                "version": redis_info.get("redis_version"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory": redis_info.get("used_memory_human"),
                "total_keys": redis_info.get("total_keys"),
            },
        }
    except Exception as e:
        status["components"]["redis"] = {
            "status": "error",
            "error": str(e),
        }
        status["status"] = "error"

    # Check database
    try:
        await db.execute("SELECT 1")
        status["components"]["database"] = {
            "status": "ok",
            "details": {
                "dialect": db.bind.dialect.name,
                "driver": db.bind.dialect.driver,
            },
        }
    except Exception as e:
        status["components"]["database"] = {
            "status": "error",
            "error": str(e),
        }
        status["status"] = "error"

    # Add system metrics
    try:
        process = psutil.Process(os.getpid())
        memory = process.memory_info()
        cpu_percent = process.cpu_percent(interval=1)
        open_files = len(process.open_files())
        connections = len(process.connections())

        # Add to status response
        status["system"] = {
            "memory": {
                "rss": memory.rss / 1024 / 1024,  # MB
                "vms": memory.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent(),
            },
            "cpu": {
                "percent": cpu_percent,
                "num_threads": process.num_threads(),
            },
            "open_files": open_files,
            "connections": connections,
        }

        # Update system metrics
        system_memory_usage.labels(type="rss").set(memory.rss)
        system_memory_usage.labels(type="vms").set(memory.vms)
        system_cpu_usage.set(cpu_percent)
        system_open_files.set(open_files)
        system_connections.set(connections)

    except Exception as e:
        status["system"] = {
            "status": "error",
            "error": str(e),
        }

    # Update component health metrics
    for component, health in status["components"].items():
        component_health.labels(component=component).set(
            1 if health["status"] == "ok" else 0
        )

    return status


@router.get(
    "/health/metrics",
    summary="Prometheus metrics",
    description="Metrics endpoint for Prometheus scraping",
)
async def metrics(
    es: ElasticsearchClient = Depends(get_es),
    cache: CacheManager = Depends(get_cache),
    response: Response = None,
) -> Response:
    """Return Prometheus metrics"""
    # Update search metrics
    try:
        # Elasticsearch metrics
        es_health = await es.health()
        if es_health:
            # Update cluster health metrics
            cluster_status = {
                "green": 2,
                "yellow": 1,
                "red": 0,
            }.get(es_health.get("status", "red"), 0)
            es_health_gauge.set(cluster_status)

            # Update node and shard metrics
            es_nodes_gauge.set(es_health.get("number_of_nodes", 0))
            es_shards_gauge.set(es_health.get("active_shards", 0))
            es_unassigned_shards_gauge.set(es_health.get("unassigned_shards", 0))

        # Cache metrics
        cache_stats = await cache.cache_stats()
        if cache_stats:
            cache_keys_gauge.set(cache_stats.get("keys", 0))
            cache_memory_gauge.set(cache_stats.get("memory_used_bytes", 0))
            cache_clients_gauge.set(cache_stats.get("connected_clients", 0))
            cache_hits_gauge.set(cache_stats.get("hits", 0))
            cache_misses_gauge.set(cache_stats.get("misses", 0))

    except Exception:
        pass  # Don't fail metric collection due to errors

    # Generate metrics
    metrics_data = generate_latest()
    
    # Set response headers
    response.headers["Content-Type"] = CONTENT_TYPE_LATEST
    response.body = metrics_data
    
    return response
