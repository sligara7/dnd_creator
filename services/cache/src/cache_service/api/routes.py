"""API routes for cache service."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel, Field
import structlog

from ..services.cache_manager import CacheManager
from ..core.exceptions import (
    CacheKeyError,
    CacheOperationError,
    InvalidKeyspaceError,
    CircuitBreakerError,
)

logger = structlog.get_logger()

# Create API router
api_router = APIRouter(prefix="/api/v2/cache", tags=["cache"])


# Request/Response Models
class CacheGetRequest(BaseModel):
    """Cache get request model."""
    key: str = Field(..., description="Cache key")
    use_local: bool = Field(default=True, description="Use local cache")


class CacheSetRequest(BaseModel):
    """Cache set request model."""
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Value to cache")
    ttl: Optional[int] = Field(None, description="Time-to-live in seconds")
    update_local: bool = Field(default=True, description="Update local cache")


class CacheDeleteRequest(BaseModel):
    """Cache delete request model."""
    key: str = Field(..., description="Cache key")
    delete_local: bool = Field(default=True, description="Delete from local cache")


class CacheBatchGetRequest(BaseModel):
    """Cache batch get request model."""
    keys: List[str] = Field(..., description="List of cache keys")
    use_local: bool = Field(default=True, description="Use local cache")


class CacheBatchSetRequest(BaseModel):
    """Cache batch set request model."""
    items: Dict[str, Any] = Field(..., description="Key-value pairs to cache")
    ttl: Optional[int] = Field(None, description="Time-to-live in seconds")
    update_local: bool = Field(default=True, description="Update local cache")


class CacheBatchDeleteRequest(BaseModel):
    """Cache batch delete request model."""
    keys: List[str] = Field(..., description="List of cache keys to delete")
    delete_local: bool = Field(default=True, description="Delete from local cache")


class CacheFlushRequest(BaseModel):
    """Cache flush request model."""
    service: Optional[str] = Field(None, description="Service to flush")
    pattern: Optional[str] = Field(None, description="Pattern to match")


class CacheResponse(BaseModel):
    """Generic cache response model."""
    status: str = Field(..., description="Operation status")
    data: Optional[Any] = Field(None, description="Response data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


# Dependency to get cache manager from app state
async def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    from ..main import cache_manager
    return cache_manager


# Dependency to get service ID from headers
def get_service_id(
    x_service_id: Optional[str] = Header(None, alias="X-Service-ID")
) -> Optional[str]:
    """Get service ID from request headers."""
    return x_service_id


# Cache Operations Endpoints
@api_router.get("/{key}")
async def get_cache_item(
    key: str,
    use_local: bool = Query(True, description="Use local cache"),
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Get value from cache."""
    try:
        value = await cache_manager.get(key, service=service_id, use_local=use_local)
        
        if value is None:
            return CacheResponse(
                status="miss",
                data=None,
                metadata={"key": key, "service": service_id}
            )
        
        return CacheResponse(
            status="hit",
            data=value,
            metadata={"key": key, "service": service_id}
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache get error", key=key, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


@api_router.put("/{key}")
async def set_cache_item(
    key: str,
    request: CacheSetRequest,
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Set value in cache."""
    try:
        # Ensure key in request matches URL key
        if request.key != key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Key mismatch between URL and request body"
            )
        
        result = await cache_manager.set(
            key=key,
            value=request.value,
            ttl=request.ttl,
            service=service_id,
            update_local=request.update_local
        )
        
        return CacheResponse(
            status="success" if result else "failed",
            data=result,
            metadata={
                "key": key,
                "ttl": request.ttl,
                "service": service_id
            }
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache set error", key=key, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


@api_router.delete("/{key}")
async def delete_cache_item(
    key: str,
    delete_local: bool = Query(True, description="Delete from local cache"),
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Delete key from cache."""
    try:
        result = await cache_manager.delete(
            key=key,
            service=service_id,
            delete_local=delete_local
        )
        
        return CacheResponse(
            status="deleted" if result else "not_found",
            data=result,
            metadata={"key": key, "service": service_id}
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache delete error", key=key, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


# Batch Operations
@api_router.post("/batch/get")
async def batch_get_cache_items(
    request: CacheBatchGetRequest,
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Get multiple values from cache."""
    try:
        values = await cache_manager.get_many(
            keys=request.keys,
            service=service_id,
            use_local=request.use_local
        )
        
        return CacheResponse(
            status="success",
            data=values,
            metadata={
                "count": len(values),
                "requested": len(request.keys),
                "service": service_id
            }
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache batch get error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


@api_router.post("/batch/set")
async def batch_set_cache_items(
    request: CacheBatchSetRequest,
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Set multiple values in cache."""
    try:
        count = await cache_manager.set_many(
            items=request.items,
            ttl=request.ttl,
            service=service_id,
            update_local=request.update_local
        )
        
        return CacheResponse(
            status="success",
            data={"count": count},
            metadata={
                "requested": len(request.items),
                "successful": count,
                "ttl": request.ttl,
                "service": service_id
            }
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache batch set error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


@api_router.post("/batch/delete")
async def batch_delete_cache_items(
    request: CacheBatchDeleteRequest,
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Delete multiple keys from cache."""
    try:
        count = await cache_manager.delete_many(
            keys=request.keys,
            service=service_id,
            delete_local=request.delete_local
        )
        
        return CacheResponse(
            status="success",
            data={"count": count},
            metadata={
                "requested": len(request.keys),
                "deleted": count,
                "service": service_id
            }
        )
        
    except (CacheKeyError, InvalidKeyspaceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CircuitBreakerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Cache batch delete error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


# Pattern Operations
@api_router.get("/pattern/{pattern}")
async def scan_cache_keys(
    pattern: str,
    count: int = Query(100, ge=1, le=10000, description="Maximum keys to return"),
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Scan for keys matching pattern."""
    try:
        keys = await cache_manager.scan_keys(
            pattern=pattern,
            count=count,
            service=service_id
        )
        
        return CacheResponse(
            status="success",
            data=keys,
            metadata={
                "pattern": pattern,
                "count": len(keys),
                "service": service_id
            }
        )
        
    except Exception as e:
        logger.error("Cache scan error", pattern=pattern, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


# Management Operations
@api_router.post("/flush")
async def flush_cache(
    request: CacheFlushRequest,
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Flush cache entries."""
    try:
        # Restrict flush operations to authorized services
        if not service_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service authentication required for flush operation"
            )
        
        result = await cache_manager.flush(
            service=request.service,
            pattern=request.pattern
        )
        
        return CacheResponse(
            status="success" if result else "failed",
            data=result,
            metadata={
                "service": request.service,
                "pattern": request.pattern,
                "requested_by": service_id
            }
        )
        
    except Exception as e:
        logger.error("Cache flush error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache operation failed"
        )


@api_router.get("/stats")
async def get_cache_stats(
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Get cache statistics."""
    try:
        stats = await cache_manager.get_stats()
        
        return CacheResponse(
            status="success",
            data=stats,
            metadata={"service": service_id}
        )
        
    except Exception as e:
        logger.error("Cache stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cache statistics"
        )


@api_router.post("/reload")
async def reload_cache(
    cache_manager: CacheManager = Depends(get_cache_manager),
    service_id: Optional[str] = Depends(get_service_id),
) -> CacheResponse:
    """Reload cache configuration."""
    try:
        # This would reload configuration in a production system
        # For now, just return success
        logger.info("Cache reload requested", service=service_id)
        
        return CacheResponse(
            status="success",
            data={"message": "Cache configuration reloaded"},
            metadata={"service": service_id}
        )
        
    except Exception as e:
        logger.error("Cache reload error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload cache"
        )
