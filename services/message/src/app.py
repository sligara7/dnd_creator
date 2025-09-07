"""
Message Hub - Main Application

Central message hub for service-to-service communication in the D&D Character Creator.
"""

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .models import ServiceMessage, ServiceResponse, ServiceRegistration
from .enhanced_service_registry import EnhancedServiceRegistry
from .message_router import MessageRouter
from .monitoring import MessageHubMetrics
from .transaction_manager import TransactionManager
from .retry_manager import RetryManager
from .priority_queue import PriorityQueueManager
from .event_store.api import router as event_router
from .event_persistence import EventPersistence
from .database import get_session

# Initialize logging
logger = structlog.get_logger()

# Load configuration
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="D&D Character Creator Message Hub",
    description="Central communication hub for service coordination",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
service_registry = ServiceRegistry(settings)
message_router = MessageRouter(settings, service_registry)
transaction_manager = TransactionManager(message_router)
metrics = MessageHubMetrics(app, circuit_breaker_manager=None)

@app.post("/v1/messages/send")
async def send_message(message: ServiceMessage) -> ServiceResponse:
    """Send a message from one service to another."""
    try:
        logger.info("message_received",
                   source=message.source,
                   destination=message.destination,
                   message_type=message.message_type)
        
        # Route the message
        response = await message_router.route_message(message)
        
        metrics.record_message_success(
            message.source,
            message.destination,
            message.message_type
        )
        
        return response
        
    except Exception as e:
        metrics.record_message_failure(
            message.source,
            message.destination,
            message.message_type
        )
        logger.error("message_routing_failed",
                    source=message.source,
                    destination=message.destination,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/services/register")
async def register_service(registration: ServiceRegistration):
    """Register a new service with the message hub."""
    try:
        await service_registry.register_service(
            name=registration.name,
            url=registration.url,
            health_check=registration.health_check
        )
        return {"status": "registered"}
    except Exception as e:
        logger.error("service_registration_failed",
                    service=registration.name,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/services")
async def list_services():
    """List all registered services and their status."""
    return await service_registry.get_all_services()

@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    try:
        # Check all registered services
        status = await service_registry.check_all_services()
        if not status["all_healthy"]:
            raise HTTPException(
                status_code=503,
                detail=f"Unhealthy services: {status['unhealthy_services']}"
            )
        return {"status": "healthy", "details": status}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/metrics")
async def metrics_endpoint():
    """Metrics endpoint."""
    return metrics.get_metrics()

# Transaction endpoints (for internal testing/usage)
@app.post("/v1/transactions/begin")
async def begin_transaction():
    tx = await transaction_manager.begin_transaction()
    return {"transaction_id": tx.id, "state": tx.state.value}

@app.post("/v1/transactions/{transaction_id}/commit")
async def commit_transaction(transaction_id: str):
    success = await transaction_manager.commit_transaction(transaction_id)
    return {"transaction_id": transaction_id, "committed": success}

@app.post("/v1/transactions/{transaction_id}/rollback")
async def rollback_transaction(transaction_id: str):
    await transaction_manager.rollback_transaction(transaction_id)
    return {"transaction_id": transaction_id, "rolled_back": True}

@app.get("/v1/transactions")
async def list_transactions():
    return transaction_manager.get_metrics()
