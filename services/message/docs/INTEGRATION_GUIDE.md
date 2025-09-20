# Message Hub Integration Guide

Version: 1.0
Last Updated: 2025-09-20

## Overview

This guide provides detailed instructions for integrating services with the Message Hub. The Message Hub acts as the central communication backbone for the D&D Character Creator system, enforcing service isolation and reliable message delivery.

### Key Principles

1. **Service Isolation**: Services must never communicate directly with each other. All communication MUST go through Message Hub.
2. **Event-Driven**: Use asynchronous event-based patterns for inter-service communication.
3. **Reliable Delivery**: Messages and events include correlation IDs and retries for reliability.
4. **Circuit Breaking**: Handle failures gracefully using the circuit breaker pattern.
5. **Monitoring**: Track and monitor all message and event flows.

## Getting Started

### 1. Installation

Add the Message Hub client library to your service's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
message-hub-client = "^1.0.0"
```

Install dependencies:
```bash
poetry install
```

### 2. Basic Integration

Initialize the Message Hub client:

```python
from message_hub.client import MessageHubClient, CircuitBreakerConfig

# Initialize client
client = MessageHubClient(
    service_name="your-service-name",
    rabbitmq_url="amqp://localhost:5672",
    auth_key="your-service-key",
    circuit_breaker_config=CircuitBreakerConfig(
        failure_threshold=5,
        reset_timeout=60,
        half_open_timeout=30
    )
)

# Connect to Message Hub
await client.connect()
```

### 3. Sending Messages

Send a message to another service:

```python
try:
    message_id = await client.send_message(
        destination="target-service",
        payload={
            "action": "process_data",
            "data": {"key": "value"}
        },
        correlation_id=request_id,  # Optional
        ttl=300,  # 5 minutes
        priority=0  # 0-9, higher is more important
    )
    logger.info("Message sent: %s", message_id)
    
except MessageHubCircuitBreakerError:
    logger.error("Circuit breaker is open")
except MessageHubDeliveryError as e:
    logger.error("Failed to deliver message: %s", e)
```

### 4. Publishing Events

Publish an event:

```python
try:
    event_id = await client.publish_event(
        event_type="your.event.type",
        payload={
            "event_data": "some data",
            "timestamp": "2025-09-20T10:00:00Z"
        },
        correlation_id=request_id  # Optional
    )
    logger.info("Event published: %s", event_id)
    
except MessageHubDeliveryError as e:
    logger.error("Failed to publish event: %s", e)
```

### 5. Subscribing to Events

Subscribe to events:

```python
async def handle_event(event_data: str):
    """Handle received events."""
    try:
        event = json.loads(event_data)
        # Process the event
        logger.info("Processed event: %s", event)
        
    except Exception as e:
        logger.exception("Error processing event: %s", e)

# Subscribe to event types
await client.subscribe(
    event_types=["event.type.one", "event.type.two"],
    callback=handle_event,
    durable=True  # Survive service restarts
)
```

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```python
try:
    await client.send_message(...)
except MessageHubConnectionError:
    # Handle connection issues
    logger.error("Connection to Message Hub failed")
    # Attempt reconnection
    await client.connect()
except MessageHubCircuitBreakerError:
    # Circuit is open, back off
    logger.error("Circuit breaker is open")
    # Implement fallback behavior
except MessageHubDeliveryError as e:
    # Message delivery failed
    logger.error("Delivery failed: %s", e)
    # Consider retry with backoff
except Exception as e:
    # Unexpected error
    logger.exception("Unexpected error: %s", e)
```

### 2. Correlation and Tracing

Always include correlation IDs for request tracing:

```python
# Generate or propagate correlation ID
correlation_id = uuid.uuid4()

# Include in messages/events
await client.send_message(
    destination="service",
    payload=data,
    correlation_id=correlation_id
)

# Log with correlation ID
logger.info("Operation completed", extra={
    "correlation_id": str(correlation_id)
})
```

### 3. Message Schema Best Practices

Define clear message schemas:

```python
# Good message payload example
{
    "action": "process_data",
    "version": "1.0",
    "timestamp": "2025-09-20T10:00:00Z",
    "data": {
        "id": "uuid-here",
        "attributes": {
            "name": "value",
            "type": "type"
        }
    },
    "metadata": {
        "source": "service-name",
        "correlation_id": "uuid-here"
    }
}
```

### 4. Event Naming Conventions

Follow consistent event naming patterns:

- Use dot notation: `service.resource.action`
- Examples:
  - `character.created`
  - `campaign.theme.changed`
  - `image.portrait.generated`

### 5. Health Monitoring

Regularly check client health:

```python
# Get health status
status = client.get_health_status()

if not status["connected"]:
    logger.warning("Message Hub connection lost")
    await client.connect()

# Log metrics
logger.info("Message Hub status", extra={
    "subscriptions": status["subscriptions"],
    "circuit_breaker": status["circuit_breaker_state"]
})
```

## Common Integration Patterns

### 1. Request-Response Pattern

```python
# Service A: Send request
correlation_id = uuid.uuid4()
await client.send_message(
    destination="service-b",
    payload={"action": "get_data", "id": "123"},
    correlation_id=correlation_id
)

# Service B: Handle request and respond
async def handle_message(message):
    correlation_id = message["correlation_id"]
    await client.send_message(
        destination="service-a",
        payload={"data": "response data"},
        correlation_id=correlation_id
    )
```

### 2. Event Broadcasting

```python
# Broadcast an event to multiple subscribers
await client.publish_event(
    event_type="system.status.changed",
    payload={
        "status": "maintenance",
        "start_time": "2025-09-20T10:00:00Z",
        "duration": 3600
    }
)
```

### 3. State Synchronization

```python
# Service maintaining state
async def handle_state_change():
    await client.publish_event(
        event_type="resource.state.changed",
        payload={
            "resource_id": "id",
            "state": "new_state",
            "version": 2,
            "timestamp": "2025-09-20T10:00:00Z"
        }
    )

# Service tracking state
async def handle_state_event(event):
    state = json.loads(event)
    await update_local_state(
        resource_id=state["resource_id"],
        new_state=state["state"],
        version=state["version"]
    )
```

## Debugging Tips

### 1. Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("message_hub")
```

### 2. Message Tracing

Use correlation IDs to trace message flows:

```python
# Log message path
logger.info("Message flow", extra={
    "correlation_id": str(correlation_id),
    "source": "service-a",
    "destination": "service-b",
    "message_id": str(message_id),
    "timestamp": datetime.utcnow().isoformat()
})
```

### 3. Monitoring Message Flow

Use Prometheus metrics:

```python
from message_hub.client import MESSAGE_COUNTER, MESSAGE_LATENCY

# Track custom metrics
MESSAGE_COUNTER.labels(
    service="your-service",
    type="custom_event",
    status="success"
).inc()

# Track operation latency
with MESSAGE_LATENCY.labels(
    service="your-service",
    type="operation"
).time():
    # Perform operation
    await do_something()
```

### 4. Common Issues

1. **Connection Issues**
   - Check RabbitMQ connection string
   - Verify service credentials
   - Check network connectivity

2. **Message Delivery Failures**
   - Verify destination service is running
   - Check queue existence and permissions
   - Verify message TTL settings

3. **Event Subscription Issues**
   - Verify exchange and queue bindings
   - Check event type patterns
   - Verify consumer is running

4. **Circuit Breaker Triggers**
   - Check failure thresholds
   - Monitor service health
   - Verify retry settings

## Testing

### 1. Unit Testing

Use the provided test framework:

```python
from message_hub.testing import MessageHubTestFramework

async def test_service_integration():
    framework = MessageHubTestFramework("amqp://localhost:5672")
    await framework.start()
    
    # Create mock services
    service_a = await framework.create_mock_service("service-a")
    service_b = await framework.create_mock_service("service-b")
    
    # Test message delivery
    message_id = await service_a.send_message(
        destination="service-b",
        payload={"test": "data"}
    )
    
    # Verify delivery
    success = await framework.verify_message_delivery(
        source="service-a",
        destination="service-b",
        message_id=message_id
    )
    assert success
```

### 2. Integration Testing

Test service interactions:

```python
async def test_service_coordination():
    # Set up test framework
    framework = MessageHubTestFramework("amqp://localhost:5672")
    
    # Create and configure services
    service_a = await framework.create_mock_service("service-a")
    service_b = await framework.create_mock_service("service-b")
    await service_b.subscribe_to_events(["test.event"])
    
    # Test event flow
    event_id = await service_a.publish_event(
        "test.event",
        {"data": "test"}
    )
    
    # Verify delivery
    success, received_by = await framework.verify_event_delivery(
        source="service-a",
        event_type="test.event",
        event_id=event_id,
        subscribers=["service-b"]
    )
    assert success
```

## Security Considerations

1. **Authentication**
   - Always use service-specific auth keys
   - Rotate keys periodically
   - Never share keys between services

2. **Message Validation**
   - Validate message schemas
   - Verify source services
   - Check message integrity

3. **Access Control**
   - Use appropriate exchange/queue permissions
   - Implement service-level authorization
   - Monitor access patterns

## Performance Tuning

1. **Connection Pooling**
   - Reuse connections
   - Configure appropriate pool sizes
   - Monitor connection usage

2. **Message Batching**
   - Batch related operations
   - Use bulk APIs when available
   - Monitor batch sizes

3. **Circuit Breaker Configuration**
   - Tune failure thresholds
   - Adjust timeout values
   - Monitor breaker states

4. **Resource Management**
   - Monitor queue depths
   - Configure appropriate TTLs
   - Implement dead letter handling

## Support and Resources

For additional support:

1. Check Message Hub logs
2. Monitor Prometheus metrics
3. Review circuit breaker status
4. Check service health endpoints
5. Monitor RabbitMQ status

## Message Hub Events Reference

### Character Service Events

Published:
- `character.created`: Character creation complete
- `character.updated`: Character details updated
- `character.deleted`: Character removed
- `character.validated`: Character validation complete
- `character.leveled_up`: Character level increased
- `character.refined`: Character refinements applied
- `character.journal_updated`: Journal entries modified
- `character.inventory_changed`: Inventory items modified
- `character.spells_changed`: Spell list modified

Subscribed:
- `campaign.theme_changed`: Campaign theme updated
- `campaign.validated`: Campaign validation complete
- `llm.content_generated`: LLM content received
- `llm.refinement_suggested`: LLM refinements available

### Campaign Service Events

Published:
- `campaign.created`: Campaign creation complete
- `campaign.evolved`: Campaign evolution applied
- `campaign.chapter_created`: New chapter added
- `campaign.validate_character`: Character validation requested
- `campaign.character_approved`: Character approved for campaign
- `campaign.theme_changed`: Campaign theme updated

Subscribed:
- `character.created`: New character available
- `character.updated`: Character modifications
- `character.validated`: Character validation complete
- `llm.content_generated`: LLM content received

### Image Service Events

Published:
- `image.portrait_generated`: Portrait creation complete
- `image.map_generated`: Map generation complete
- `image.item_generated`: Item visualization complete
- `image.theme_applied`: Theme application complete

Subscribed:
- `character.updated`: Character appearance changed
- `campaign.theme_changed`: Visual theme updated
- `llm.generate_prompt`: Generation prompt received

### LLM Service Events

Published:
- `llm.content_generated`: Content generation complete
- `llm.refinement_suggested`: Refinement suggestions available
- `llm.generate_prompt`: Generation prompt created

Subscribed:
- `character.created`: Character creation trigger
- `campaign.theme_changed`: Theme update trigger
- `character.refined`: Refinement request received