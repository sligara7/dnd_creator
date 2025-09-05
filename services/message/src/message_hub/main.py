from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from message_hub.core.config import settings
from message_hub.api.routes import api_router
from message_hub.core.exceptions import MessageHubError
from message_hub.core.monitoring import setup_monitoring
from message_hub.service.circuit_breaker_manager import CircuitBreakerManager
from message_hub.service.message_router import MessageRouter
from message_hub.service.service_registry import ServiceRegistry

app = FastAPI(
    title="Message Hub",
    description="Central communication hub for D&D Character Creator services",
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
message_router = MessageRouter()
circuit_breaker = CircuitBreakerManager()
service_registry = ServiceRegistry()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await message_router.setup()
    await circuit_breaker.setup()
    await service_registry.setup()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await message_router.cleanup()
    await circuit_breaker.cleanup()
    await service_registry.cleanup()

@app.exception_handler(MessageHubError)
async def message_hub_exception_handler(request: Request, exc: MessageHubError):
    """Handle Message Hub specific errors"""
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
    # Check health of all dependent services
    router_health = await message_router.health_check()
    breaker_health = await circuit_breaker.health_check()
    registry_health = await service_registry.health_check()
    
    # Determine overall health
    services_healthy = all([router_health, breaker_health, registry_health])
    
    return {
        "status": "healthy" if services_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "message_router": "healthy" if router_health else "degraded",
            "circuit_breaker": "healthy" if breaker_health else "degraded",
            "service_registry": "healthy" if registry_health else "degraded",
        },
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Return prometheus metrics
    return await setup_monitoring.get_metrics()
