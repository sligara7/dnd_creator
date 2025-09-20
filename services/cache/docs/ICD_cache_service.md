# Cache Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-30

## 1. Communication Architecture

### 1.1 Service Communication Pattern
- All service-to-service communication MUST be routed through the Message Hub service
- No direct HTTP calls between services are permitted
- All integrations must use asynchronous messaging patterns
- All events and requests must include proper correlation IDs

### 1.2 Base URL (API Gateway Access Only)
```http
http://cache-service:8000  # Only accessible via API Gateway
```

### 1.3 Message Hub Protocol
- Every request/event must include:
  * Correlation ID (for tracing)
  * Source service identifier
  * Request/event type and version
  * Timestamp
  * TTL (time-to-live)

### 1.4 Common Headers
## 1. Interface Overview

### 1.1 Purpose
This document defines the interfaces for the Cache Service, including APIs, events, and integration patterns for all services that interact with the distributed caching system.

### 1.2 Scope
- RESTful API endpoints
- Message Hub events
- Client libraries
- Service integrations
- Monitoring interfaces

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Cache Operations
```http
GET /api/v2/cache/{key}
PUT /api/v2/cache/{key}
DELETE /api/v2/cache/{key}
POST /api/v2/cache/batch
GET /api/v2/cache/pattern/{pattern}
```

#### 2.1.2 Cache Management
```http
POST /api/v2/cache/flush
GET /api/v2/cache/stats
POST /api/v2/cache/reload
GET /api/v2/cache/health
```

#### 2.1.3 Request/Response Format
```json
{
  "cache_request": {
    "key": "string",
    "value": "any",
    "ttl": "integer",
    "options": {
      "consistency": "string",
      "compression": "boolean",
      "encryption": "boolean"
    }
  },
  "cache_response": {
    "status": "string",
    "data": "any",
    "metadata": {
      "created_at": "timestamp",
      "expires_at": "timestamp",
      "version": "string"
    }
  }
}
```

### 2.2 Binary Protocol

#### 2.2.1 Connection
```protobuf
message CacheConnection {
  string service_id = 1;
  string auth_token = 2;
  Options options = 3;
}

message Options {
  bool compression = 1;
  bool encryption = 2;
  string consistency = 3;
}
```

#### 2.2.2 Operations
```protobuf
message CacheOperation {
  string operation = 1;
  bytes key = 2;
  bytes value = 3;
  uint32 ttl = 4;
  Options options = 5;
}

message CacheResponse {
  uint32 status = 1;
  bytes data = 2;
  Metadata metadata = 3;
}
```

## 3. Event Interfaces

### 3.1 Published Events

#### 3.1.1 Cache Events
```json
{
  "event": "cache.item.updated",
  "data": {
    "key": "string",
    "operation": "string",
    "timestamp": "datetime",
    "service_id": "string"
  }
}
```

#### 3.1.2 Health Events
```json
{
  "event": "cache.health.status",
  "data": {
    "status": "string",
    "metrics": {
      "hit_rate": "float",
      "memory_usage": "float",
      "ops_rate": "integer"
    }
  }
}
```

### 3.2 Subscribed Events

#### 3.2.1 Configuration Events
```json
{
  "event": "config.cache.update",
  "data": {
    "policy": "string",
    "parameters": {},
    "scope": "string"
  }
}
```

#### 3.2.2 Control Events
```json
{
  "event": "control.cache.action",
  "data": {
    "action": "string",
    "target": "string",
    "parameters": {}
  }
}
```

## 4. Service Integration

### 4.1 Character Service
```yaml
integration:
  service: character
  cache_types:
    - character_data:
        ttl: 3600
        consistency: "strong"
    - computation_results:
        ttl: 300
        consistency: "eventual"
```

### 4.2 Campaign Service
```yaml
integration:
  service: campaign
  cache_types:
    - campaign_state:
        ttl: 1800
        consistency: "strong"
    - participant_list:
        ttl: 600
        consistency: "eventual"
```

### 4.3 Image Service
```yaml
integration:
  service: image
  cache_types:
    - image_metadata:
        ttl: 7200
        consistency: "eventual"
    - transformation_results:
        ttl: 86400
        consistency: "eventual"
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_cache import CacheClient

client = CacheClient(
    service_id="character_service",
    options={
        "consistency": "strong",
        "compression": True,
        "encryption": True
    }
)

# Cache operations
client.get("character:1234")
client.set("character:1234", data, ttl=3600)
client.delete("character:1234")

# Batch operations
client.get_many(["char:1", "char:2"])
client.set_many({
    "char:1": data1,
    "char:2": data2
}, ttl=3600)
```

### 5.2 Go Client
```go
package main

import "dnd/cache"

func main() {
    client := cache.NewClient(&cache.Config{
        ServiceID: "campaign_service",
        Options: cache.Options{
            Consistency: "strong",
            Compression: true,
            Encryption: true,
        },
    })

    // Cache operations
    client.Get(ctx, "campaign:1234")
    client.Set(ctx, "campaign:1234", data, cache.TTL(3600))
    client.Delete(ctx, "campaign:1234")
}
```

## 6. Monitoring Interface

### 6.1 Metrics
```yaml
metrics:
  performance:
    - name: cache_hit_rate
      type: gauge
      labels: [service, operation]
    - name: cache_latency
      type: histogram
      labels: [service, operation]
    - name: cache_memory_usage
      type: gauge
      labels: [node, type]

  health:
    - name: cache_node_status
      type: gauge
      labels: [node, zone]
    - name: cache_replication_lag
      type: gauge
      labels: [node, target]
```

### 6.2 Health Checks
```http
GET /health/live
GET /health/ready
GET /health/metrics
```

## 7. Security Interface

### 7.1 Authentication
```yaml
auth:
  type: "jwt"
  claims:
    - service_id
    - roles
    - permissions
  scope: "cache:read cache:write"
```

### 7.2 Authorization
```yaml
permissions:
  read:
    - "cache:read"
    - "metrics:read"
  write:
    - "cache:write"
    - "cache:delete"
  admin:
    - "cache:flush"
    - "cache:reload"
```

## 8. Error Interface

### 8.1 Error Codes
```json
{
  "error_codes": {
    "CACHE_001": "Key not found",
    "CACHE_002": "Key expired",
    "CACHE_003": "Storage full",
    "CACHE_004": "Invalid key format",
    "CACHE_005": "Operation timeout",
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Insufficient permissions"
  }
}
```

### 8.2 Error Responses
```json
{
  "error": {
    "code": "CACHE_001",
    "message": "The requested key was not found",
    "details": {
      "key": "string",
      "operation": "string",
      "timestamp": "datetime"
    }
  }
}
```

## 9. Configuration Interface

### 9.1 Service Configuration
```yaml
config:
  service:
    id: "cache_service"
    version: "2.0.0"
    environment: "production"
  
  cluster:
    nodes: 3
    zones: ["us-east-1a", "us-east-1b"]
    replication: 2
  
  policies:
    eviction: "lru"
    ttl_default: 3600
    max_memory: "75%"
```

### 9.2 Client Configuration
```yaml
client_config:
  connection:
    timeout: 5
    retry: 3
    backoff: "exponential"
  
  pool:
    min_size: 5
    max_size: 50
    idle_timeout: 300
  
  circuit_breaker:
    threshold: 0.5
    window: 60
    min_requests: 20
```
