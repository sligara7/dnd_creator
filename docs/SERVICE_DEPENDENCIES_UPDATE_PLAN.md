# Service Dependencies Update Plan

## Overview
This document outlines the plan to update all service dependencies in the ICDs to ensure:
1. Removal of direct database dependencies
2. Addition of message hub client
3. Storage service client where needed

## Required Changes Per Service

### 1. Character Service
```diff
- Direct PostgreSQL client
- Redis client
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - redis_client
```

### 2. Campaign Service
```diff
- Direct PostgreSQL client
- Redis client
- Direct file storage
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - redis_client
    - s3_client
```

### 3. Image Service
```diff
- Direct file storage
- Redis client
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - s3_client
    - redis_client
```

### 4. LLM Service
```diff
- Redis client
- Direct file storage
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - redis_client
    - s3_client
```

### 5. API Gateway
```diff
- Direct HTTP clients
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
  removed:
    - http_clients
```

### 6. Message Hub
```diff
- Direct database dependencies
+ Storage Service client
```
Configuration updates:
```yaml
dependencies:
  required:
    - storage_client: "^1.0.0"
  removed:
    - pg_client
```

### 7. Storage Service
```yaml
# No changes needed - this service manages all persistence
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - postgresql_client: "^14.0.0"
    - s3_client: "^3.0.0"
```

### 8. Auth Service
```diff
- Direct PostgreSQL client
- Redis client
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - redis_client
```

### 9. Search Service
```diff
- Elasticsearch client
- Redis client
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - elasticsearch_client
    - redis_client
```

### 10. Metrics Service
```diff
- Direct PostgreSQL client
- Redis client
- Prometheus client (direct)
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - redis_client
    - prometheus_client
```

### 11. Catalog Service
```diff
- Direct PostgreSQL client
- Redis client
- Direct file storage
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - redis_client
    - s3_client
```

### 12. Audit Service
```diff
- Direct PostgreSQL client
- Elasticsearch client
+ Storage Service client
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - storage_client: "^1.0.0"
  removed:
    - pg_client
    - elasticsearch_client
```

### 13. Cache Service
```diff
- Direct Redis cluster management
+ Message Hub client
```
Configuration updates:
```yaml
dependencies:
  required:
    - message_hub_client: "^2.0.0"
    - redis_client: "^7.0.0"  # Keep for internal cache management only
  removed:
    - direct_redis_cluster
```

## Implementation Steps

### 1. Message Hub Client Integration
```python
# Required in all services
from dnd_message_hub import MessageHubClient

client = MessageHubClient(
    service_id="service_name",
    options={
        "retry": True,
        "max_retries": 3,
        "timeout": 30
    }
)

# Event publishing
await client.publish(
    "event.type",
    {
        "data": payload,
        "correlation_id": correlation_id
    }
)

# Event subscription
@client.subscribe("event.type.*")
async def handle_event(event):
    # Process event
    pass
```

### 2. Storage Service Client Integration
```python
# Required in most services
from dnd_storage import StorageClient

storage = StorageClient(
    service_id="service_name",
    message_hub=message_hub,  # Required Message Hub client
    options={
        "schema": "service_db",
        "retry": True
    }
)

# Data operations
await storage.write(
    "service_db",
    "table_name",
    {
        "id": uuid4(),
        "data": payload
    }
)

data = await storage.read(
    "service_db",
    "table_name",
    {"id": id}
)
```

## Common Configuration Updates

### 1. Service Base Configuration
```yaml
service:
  name: service_name
  version: 1.0.0
  
  # Required clients
  message_hub:
    required: true
    version: "^2.0.0"
    options:
      retry: true
      timeout: 30
  
  storage:
    required: true  # Most services
    version: "^1.0.0"
    options:
      schema: service_db
      retry: true
  
  metrics:
    required: true
    type: events  # Via Message Hub
```

### 2. Client Options
```yaml
# Message Hub client options
message_hub_options:
  retry:
    max_attempts: 3
    backoff: exponential
    initial_delay: 100
  
  circuit_breaker:
    threshold: 0.5
    window: 60
    min_requests: 20

# Storage client options
storage_options:
  cache:
    enabled: true
    ttl: 300
  
  consistency:
    level: strong
    timeout: 5000
```

## Migration Guidelines

1. Update all service ICDs to reflect new dependencies:
   - Remove direct database clients
   - Add Message Hub client requirement
   - Add Storage Service client where needed

2. Update service configuration files:
   - Add Message Hub client options
   - Add Storage Service client options
   - Remove old database connection configs

3. Update code patterns:
   - Replace direct database calls with Storage Service
   - Replace direct service calls with Message Hub events
   - Update health checks to use Message Hub

4. Update monitoring:
   - Add Message Hub metrics
   - Add Storage Service metrics
   - Remove direct database metrics

## Service Dependencies Matrix

| Service          | Message Hub | Storage Service | Direct DB | Notes |
|-----------------|-------------|-----------------|-----------|-------|
| API Gateway     | ✓           |                |           | Routes only |
| Message Hub     |             | ✓              |           | Persistence |
| Storage Service | ✓           |                | ✓         | DB Manager |
| Character       | ✓           | ✓              |           | Full switch |
| Campaign        | ✓           | ✓              |           | Full switch |
| Image           | ✓           | ✓              |           | Assets too |
| LLM             | ✓           | ✓              |           | Cache via MH |
| Auth            | ✓           | ✓              |           | Full switch |
| Search          | ✓           | ✓              |           | Full switch |
| Metrics         | ✓           | ✓              |           | Events only |
| Catalog         | ✓           | ✓              |           | Full switch |
| Audit           | ✓           | ✓              |           | Full switch |
| Cache           | ✓           |                |           | Redis stays |