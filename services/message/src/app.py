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
service_registry = EnhancedServiceRegistry()
event_persistence = EventPersistence()
retry_manager = RetryManager()
priority_queue_manager = PriorityQueueManager()
message_router = MessageRouter(settings, service_registry)
transaction_manager = TransactionManager(message_router)
metrics = MessageHubMetrics(app, circuit_breaker_manager=None)

# Include event store API router
app.include_router(event_router, prefix="/api")

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

# Retry Manager endpoints
@app.post("/v1/retry")
async def schedule_retry(message: ServiceMessage):
    """Schedule a message for retry with exponential backoff."""
    try:
        await retry_manager.schedule_retry(
            message=message.dict(),
            service_name=message.destination,
            max_retries=5
        )
        return {"status": "scheduled", "message": "Message scheduled for retry"}
    except Exception as e:
        logger.error("retry_scheduling_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/retry/status/{message_id}")
async def get_retry_status(message_id: str):
    """Get retry status for a message."""
    try:
        status = await retry_manager.get_retry_status(message_id)
        return status
    except Exception as e:
        logger.error("retry_status_failed", message_id=message_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Priority Queue endpoints
@app.post("/v1/queue/enqueue")
async def enqueue_message(message: ServiceMessage, priority: int = 1):
    """Enqueue a message with priority."""
    try:
        await priority_queue_manager.enqueue(
            message.dict(),
            priority=priority
        )
        return {"status": "enqueued", "priority": priority}
    except Exception as e:
        logger.error("enqueue_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/queue/status")
async def get_queue_status():
    """Get priority queue status."""
    try:
        stats = await priority_queue_manager.get_queue_stats()
        return stats
    except Exception as e:
        logger.error("queue_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Service Registry endpoints
@app.post("/v1/services/{service_name}/instances")
async def register_service_instance(service_name: str, instance_url: str):
    """Register a new instance of a service."""
    try:
        await service_registry.register_instance(
            service_name=service_name,
            instance_id=f"{service_name}-{instance_url.split(':')[-1]}",
            url=instance_url
        )
        return {"status": "registered", "service": service_name, "url": instance_url}
    except Exception as e:
        logger.error("instance_registration_failed", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/services/{service_name}/next")
async def get_next_instance(service_name: str):
    """Get next available instance using load balancing."""
    try:
        instance = await service_registry.get_next_instance(service_name)
        if not instance:
            raise HTTPException(status_code=503, detail=f"No healthy instances for {service_name}")
        return instance
    except Exception as e:
        logger.error("instance_selection_failed", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/services/{service_name}/dependencies")
async def add_service_dependency(service_name: str, depends_on: str):
    """Add a service dependency."""
    try:
        await service_registry.add_dependency(service_name, depends_on)
        return {"status": "dependency_added", "service": service_name, "depends_on": depends_on}
    except Exception as e:
        logger.error("dependency_add_failed", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Event Persistence endpoints
@app.post("/v1/events/persist")
async def persist_event(event_data: dict):
    """Persist an event for durability."""
    try:
        event_id = await event_persistence.save_event(event_data)
        return {"event_id": event_id, "status": "persisted"}
    except Exception as e:
        logger.error("event_persistence_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/events/replay")
async def replay_events(from_sequence: int = 0, to_sequence: int = None):
    """Replay events from the event store."""
    try:
        events = await event_persistence.replay_events(
            from_sequence=from_sequence,
            to_sequence=to_sequence
        )
        return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error("event_replay_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
