from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from cache_service.core.config import settings
from cache_service.api.routes import api_router
from cache_service.core.exceptions import CacheServiceError
from cache_service.core.monitoring import setup_monitoring
from cache_service.services.cache_manager import CacheManager
from cache_service.services.local_cache import LocalCache
from cache_service.services.circuit_breaker import CircuitBreaker

app = FastAPI(
    title="Cache Service",
    description="Distributed Cache Service for D&D Character Creator",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dependencies
local_cache = LocalCache(
    maxsize=settings.LOCAL_CACHE_SIZE,
    ttl=settings.LOCAL_CACHE_TTL,
)
circuit_breaker = CircuitBreaker(
    threshold=settings.CIRCUIT_BREAKER_THRESHOLD,
    timeout=settings.CIRCUIT_BREAKER_TIMEOUT,
    half_open_requests=settings.CIRCUIT_BREAKER_HALF_OPEN_REQUESTS,
)
cache_manager = CacheManager(
    local_cache=local_cache,
    circuit_breaker=circuit_breaker,
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await cache_manager.setup()
    await circuit_breaker.setup()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await cache_manager.cleanup()
    await circuit_breaker.cleanup()

@app.exception_handler(CacheServiceError)
async def cache_service_exception_handler(request: Request, exc: CacheServiceError):
    """Handle Cache Service specific errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": {
                    "request_id": request.headers.get("X-Request-ID"),
                    "timestamp": exc.timestamp.isoformat(),
                },
            }
        },
    )

# Include API routes
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Service health check endpoint"""
    # Check health of all dependencies
    local_health = local_cache.is_healthy()
    primary_health = await cache_manager.check_primary_health()
    replica_health = await cache_manager.check_replica_health()
    breaker_health = circuit_breaker.is_healthy()
    
    # Get cache stats
    cache_stats = await cache_manager.get_stats()
    
    # Determine overall health
    all_healthy = all([
        local_health,
        primary_health,
        replica_health,
        breaker_health,
    ])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "local_cache": "healthy" if local_health else "degraded",
            "primary_cache": "healthy" if primary_health else "degraded",
            "replica_cache": "healthy" if replica_health else "degraded",
            "circuit_breaker": "healthy" if breaker_health else "degraded",
        },
        "stats": {
            "hit_rate": cache_stats["hit_rate"],
            "miss_rate": cache_stats["miss_rate"],
            "memory_used": cache_stats["memory_used"],
            "memory_limit": cache_stats["memory_limit"],
            "total_keys": cache_stats["total_keys"],
            "local_cache_size": len(local_cache),
            "replication_lag": cache_stats["replication_lag"],
        },
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Return prometheus metrics
    return await setup_monitoring.get_metrics()

def start() -> None:
    """Entry point for running in production"""
    import uvicorn
    uvicorn.run(
        "cache_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_config=None,  # Use structlog configuration
    )

def dev() -> None:
    """Entry point for running in development"""
    import uvicorn
    uvicorn.run(
        "cache_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None,  # Use structlog configuration
    )

if __name__ == "__main__":
    dev()
