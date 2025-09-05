from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from catalog_service.core.config import settings
from catalog_service.api.routes import api_router
from catalog_service.core.exceptions import CatalogError
from catalog_service.core import startup

app = FastAPI(
    title="Catalog Service",
    description="D&D Content Catalog and Management Service",
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

# Include API routes
app.include_router(api_router, prefix="/api/v2")

@app.on_event("startup")
async def startup_event():
    await startup.init_services()

@app.on_event("shutdown")
async def shutdown_event():
    await startup.cleanup_services()

@app.exception_handler(CatalogError)
async def catalog_exception_handler(request: Request, exc: CatalogError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": {
                    "request_id": request.headers.get("X-Request-ID"),
                    "timestamp": exc.timestamp.isoformat(),
                    "validation_errors": exc.validation_errors,
                }
            }
        },
    )

@app.get("/health")
async def health_check():
    """Service health check endpoint"""
    components = await startup.check_component_health()
    return {
        "status": "healthy" if all(v == "healthy" for v in components.values()) else "degraded",
        "version": settings.VERSION,
        "components": components,
        "metrics": await startup.get_health_metrics(),
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return startup.get_prometheus_metrics()
