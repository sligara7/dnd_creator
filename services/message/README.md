# Message Hub Service

Central communication backbone for the D&D Character Creator system, providing reliable inter-service messaging with advanced features.

## Status: FEATURE COMPLETE ✅

## Overview

The Message Hub is the mandatory central communication layer for all inter-service communication. It ensures complete service isolation, reliable message delivery, and system-wide event propagation. No direct service-to-service communication is permitted - all messages flow through the Message Hub.

## Core Features

### 🔄 Event Management System
- **Event Persistence**: Durable storage with write-ahead logging (WAL)
- **Event Replay**: Replay events from any point in time
- **Retry Mechanism**: Exponential backoff with jitter
- **Dead Letter Queue**: Automatic handling of permanently failed messages
- **Event Correlation**: Track related events across services
- **Snapshot Support**: State reconstruction from snapshots

### 📬 Message Prioritization
- **Multi-Level Priorities**: CRITICAL, HIGH, NORMAL, LOW, DEFERRED
- **Deadline-Aware Scheduling**: Messages with deadlines get priority boost
- **Service Quotas**: Rate limiting per service to prevent overload
- **Intelligent Queue Management**: Automatic throttling and overflow handling
- **Age-Based Priority**: Older messages gradually increase in priority

### 🔍 Service Discovery
- **Dynamic Registration**: Services register and deregister dynamically
- **Health Monitoring**: Continuous health checks with configurable thresholds
- **Load Balancing Strategies**:
  - Round-robin
  - Least connections
  - Weighted distribution
  - Random selection
  - Health-aware (default)
- **Dependency Tracking**: Ensure required services are available
- **Automatic Failover**: Route around unhealthy instances

### 🛡️ Reliability Features
- **Circuit Breakers**: Prevent cascading failures
- **Optimistic Concurrency Control**: Ensure event ordering
- **Transaction Support**: Distributed transaction coordination
- **Message Validation**: Schema enforcement and validation
- **Duplicate Detection**: Prevent duplicate message processing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     External Services                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Message Hub Core                       │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Message   │  │    Event     │  │   Service    │      │
│  │   Router    │  │   Manager    │  │  Registry    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Retry     │  │   Priority   │  │   Circuit    │      │
│  │  Manager    │  │    Queue     │  │   Breaker    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Storage Layer                            │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL  │  │    Redis     │  │  Event Store │      │
│  │  (Events)   │  │   (Queues)   │  │   (WAL)     │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Message Operations
- `POST /v1/messages/send` - Send a message to a service
- `GET /v1/messages/{id}` - Get message status

### Event Operations
- `POST /v1/events` - Publish an event
- `GET /v1/events` - Get events (with filtering)
- `POST /v1/events/replay` - Replay events from a point

### Service Registry
- `POST /v1/services/register` - Register a service
- `GET /v1/services` - List all services
- `GET /v1/services/{service}/health` - Get service health

### Transaction Management
- `POST /v1/transactions/begin` - Begin a distributed transaction
- `POST /v1/transactions/{id}/commit` - Commit a transaction
- `POST /v1/transactions/{id}/rollback` - Rollback a transaction

### Monitoring
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /v1/queue/status` - Queue status and statistics

## Configuration

Key configuration parameters in `config/config.yaml`:

```yaml
# Message Queue Settings
redis_url: "redis://localhost:6379"
message_timeout: 30
max_queue_size: 10000

# Retry Settings
max_retry_attempts: 5
base_retry_delay: 1
max_retry_delay: 300

# Service Discovery
service_check_interval: 30
service_timeout: 10
unhealthy_threshold: 3
healthy_threshold: 2

# Event Store
database_url: "postgresql://msg_hub_user:password@localhost:5432/msg_hub"
event_retention_days: 30
wal_flush_interval: 1
compaction_interval: 3600

# Circuit Breaker
circuit_breaker_failure_threshold: 5
circuit_breaker_reset_timeout: 60
```

## Performance Specifications

- **Message Latency**: < 10ms average
- **Throughput**: 10,000+ messages/second
- **Event Persistence**: Write-ahead logging ensures zero message loss
- **Queue Capacity**: 10,000 messages per priority level
- **Health Check Interval**: Every 30 seconds
- **Retry Backoff**: Exponential from 1s to 5 minutes
- **Circuit Breaker**: Opens after 5 consecutive failures

## Testing

Comprehensive test coverage with 2,079 lines of tests:

### Unit Tests
- `test_retry_manager.py` - 456 lines testing retry logic
- `test_priority_queue.py` - 517 lines testing queue management
- `test_enhanced_service_registry.py` - 619 lines testing service discovery

### Integration Tests
- `test_integration.py` - 487 lines testing component interactions

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_retry_manager.py -v

# Run integration tests only
poetry run pytest tests/test_integration.py -v
```

## Development

### Prerequisites
- Python 3.11+
- Poetry for dependency management
- Redis for message queuing
- PostgreSQL for event storage
- Docker for containerization

### Setup
```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn src.app:app --reload --port 8200

# Run with Docker
docker-compose up -d
```

### Project Structure
```
services/message/
├── src/
│   ├── app.py                      # Main FastAPI application
│   ├── models.py                    # Pydantic models
│   ├── config.py                    # Configuration management
│   ├── retry_manager.py            # Retry logic with exponential backoff
│   ├── priority_queue.py           # Priority queue management
│   ├── enhanced_service_registry.py # Service discovery and load balancing
│   ├── event_persistence.py        # Event store with WAL
│   ├── message_router.py           # Message routing logic
│   ├── circuit_breaker.py          # Circuit breaker implementation
│   └── event_store/                # Event sourcing components
│       ├── models.py
│       ├── service.py
│       └── api.py
├── tests/                           # Comprehensive test suite
├── config/                          # Configuration files
├── docker-compose.yml              # Docker orchestration
└── pyproject.toml                  # Poetry dependencies
```

## Monitoring

### Metrics Exposed
- Message queue sizes by priority
- Message processing rates
- Retry attempt counts
- Dead letter queue size
- Service health status
- Circuit breaker states
- Event store statistics

### Health Checks
- Redis connectivity
- PostgreSQL connectivity
- Registered service health
- Queue capacity status

## Security

- Service-to-service authentication via API keys
- Message validation and sanitization
- Rate limiting per service
- Audit logging for all operations
- Encrypted storage for sensitive data

## Future Enhancements

1. **Message Compression**: Reduce network overhead for large payloads
2. **Event Streaming**: WebSocket support for real-time event streaming
3. **Message Batching**: Batch multiple messages for efficiency
4. **Advanced Analytics**: Event pattern detection and analysis
5. **Multi-Region Support**: Geographic distribution for global deployments

## Documentation

- [System Requirements Document (SRD)](./SRD_message_hub.md)
- [Interface Control Document (ICD)](./ICD_message_hub.md)
- [Completion Tasks](./COMPLETION_TASKS.md)

## Support

For issues or questions, refer to the main project documentation or contact the development team.

---

*Last Updated: 2025-09-07*
*Status: Feature Complete*
*Version: 1.0.0*
