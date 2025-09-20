"""Service initialization and startup functions."""

import logging
from typing import Dict

import httpx
from prometheus_client import Counter, Gauge, Histogram

from catalog_service.config import settings
from catalog_service.core.message_hub import message_hub
from catalog_service.models.storage import StorageOperation, StorageRequest
from catalog_service.models.migration import DatabaseSchema, CollectionSchema
from catalog_service.models import ContentType

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Metrics
COMPONENT_HEALTH = Gauge(
    "catalog_service_component_health",
    "Health status of service components",
    ["component"]
)

REQUEST_COUNT = Counter(
    "catalog_service_request_total",
    "Total number of requests processed",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "catalog_service_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

CONTENT_COUNT = Gauge(
    "catalog_service_content_count",
    "Total number of content items",
    ["type"]
)

async def init_services() -> None:
    """Initialize service dependencies."""
    logger.info("Initializing catalog service...")
    
    # Initialize message hub client
    await message_hub.connect()
    
    # Initialize catalog schema
    await init_catalog_schema()
    
    logger.info("Service initialization complete")

async def init_catalog_schema() -> None:
    """Initialize catalog database schema through Message Hub."""
    logger.info("Initializing catalog database schema...")
    
    # Define schema for each content type
    schema = DatabaseSchema(
        collections=[
            CollectionSchema(
                name=str(ContentType.ITEM),
                indexes=["name", "source", "properties.category", "theme_data.themes"]
            ),
            CollectionSchema(
                name=str(ContentType.SPELL),
                indexes=["name", "source", "properties.level", "properties.school", "theme_data.themes"]
            ),
            CollectionSchema(
                name=str(ContentType.MONSTER),
                indexes=["name", "source", "properties.challenge_rating", "properties.type", "theme_data.themes"]
            )
        ]
    )
    
    try:
        # Request schema initialization
        exchange = await message_hub.channel.declare_exchange(
            "storage_ops",
            aio_pika.ExchangeType.TOPIC
        )
        
        request = StorageRequest(
            operation=StorageOperation.CREATE,
            database="catalog_db",
            collection="_schema",  # Special collection for schema
            data=schema.model_dump()
        )
        
        await exchange.publish(
            Message(
                body=request.json().encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key="storage.schema.initialize"
        )
        
        logger.info("Catalog database schema initialization requested")
        
    except Exception as e:
        logger.error(f"Failed to initialize catalog schema: {e}")
        raise

async def cleanup_services() -> None:
    """Clean up service resources."""
    logger.info("Cleaning up service resources...")
    
    # Cleanup message hub client
    await message_hub.disconnect()
    
    logger.info("Service cleanup complete")

async def check_component_health() -> Dict[str, str]:
    """Check health of service components."""
components = {
        "service": "healthy",
        "storage": "unknown",
        "message_hub": "unknown",
    }
    
    # Check Message Hub
    if message_hub.connection and message_hub.connection.is_closed:
        components["message_hub"] = "unhealthy"
    elif message_hub.connection:
        components["message_hub"] = "healthy"
    
    # Check storage service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.STORAGE_SERVICE_URL}/health")
            components["storage"] = "healthy" if response.is_success else "unhealthy"
    except Exception as e:
        logger.error(f"Storage service health check failed: {e}")
        components["storage"] = "unhealthy"
    
    COMPONENT_HEALTH.labels("service").set(1 if components["service"] == "healthy" else 0)
    COMPONENT_HEALTH.labels("storage").set(1 if components["storage"] == "healthy" else 0)
    COMPONENT_HEALTH.labels("message_hub").set(1 if components["message_hub"] == "healthy" else 0)
    
    return components

async def get_health_metrics() -> Dict[str, int]:
    """Get service metrics for health check."""
    return {
        "content_count": CONTENT_COUNT._value.sum(),
        "request_count": REQUEST_COUNT._value.sum(),
    }

def get_prometheus_metrics() -> str:
    """Return prometheus metrics in text format."""
    from prometheus_client import generate_latest
    return generate_latest().decode("utf-8")