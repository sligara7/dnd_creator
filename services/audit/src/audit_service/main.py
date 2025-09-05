from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from audit_service.core.config import settings
from audit_service.api.routes import api_router
from audit_service.core.exceptions import AuditServiceError
from audit_service.core.monitoring import setup_monitoring
from audit_service.services.event_processor import EventProcessor
from audit_service.services.archival_service import ArchivalService
from audit_service.services.analysis_service import AnalysisService

app = FastAPI(
    title="Audit Service",
    description="Security and Compliance Audit Service for D&D Character Creator",
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
event_processor = EventProcessor()
archival_service = ArchivalService()
analysis_service = AnalysisService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await event_processor.setup()
    await archival_service.setup()
    await analysis_service.setup()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await event_processor.cleanup()
    await archival_service.cleanup()
    await analysis_service.cleanup()

@app.exception_handler(AuditServiceError)
async def audit_service_exception_handler(request: Request, exc: AuditServiceError):
    """Handle Audit Service specific errors"""
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
    processor_health = await event_processor.health_check()
    archival_health = await archival_service.health_check()
    analysis_health = await analysis_service.health_check()
    
    # Determine overall health
    all_healthy = all([processor_health, archival_health, analysis_health])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "event_processor": "healthy" if processor_health else "degraded",
            "archival_service": "healthy" if archival_health else "degraded",
            "analysis_service": "healthy" if analysis_health else "degraded",
        },
        "metrics": {
            "events_processed": event_processor.get_processed_count(),
            "events_pending": event_processor.get_pending_count(),
            "archive_size": archival_service.get_archive_size(),
            "active_analyses": analysis_service.get_active_analyses(),
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
        "audit_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_config=None,  # Use structlog configuration
    )

def dev() -> None:
    """Entry point for running in development"""
    import uvicorn
    uvicorn.run(
        "audit_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None,  # Use structlog configuration
    )

if __name__ == "__main__":
    dev()
