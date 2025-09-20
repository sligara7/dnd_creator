# Audit Service - Interface Control Document (ICD)

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
http://audit-service:8000  # Only accessible via API Gateway
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
This document defines the interfaces for the Audit Service, including event collection APIs, query interfaces, reporting APIs, and integration patterns for audit logging and compliance monitoring.

### 1.2 Scope
- Event collection endpoints
- Query interfaces
- Report generation APIs
- Service integrations
- Monitoring interfaces

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Event Operations
```http
POST /api/v2/events
POST /api/v2/events/batch
GET /api/v2/events/search
GET /api/v2/events/{id}
GET /api/v2/events/aggregate
```

#### 2.1.2 Report Operations
```http
GET /api/v2/reports
POST /api/v2/reports
GET /api/v2/reports/{id}
GET /api/v2/reports/{id}/download
POST /api/v2/reports/schedule
```

#### 2.1.3 Analysis Operations
```http
POST /api/v2/analysis/patterns
POST /api/v2/analysis/anomalies
GET /api/v2/analysis/trends
GET /api/v2/analysis/summary
```

### 2.2 Event Format

#### 2.2.1 Event Structure
```json
{
  "event": {
    "id": "uuid",
    "timestamp": "datetime",
    "service": "string",
    "type": "string",
    "action": "string",
    "actor": {
      "id": "string",
      "type": "user|service|system",
      "name": "string"
    },
    "target": {
      "id": "string",
      "type": "string",
      "name": "string"
    },
    "context": {
      "request_id": "string",
      "session_id": "string",
      "ip_address": "string",
      "user_agent": "string"
    },
    "data": {
      "changes": ["array"],
      "metadata": {}
    },
    "severity": "string",
    "outcome": "success|failure|error"
  }
}
```

#### 2.2.2 Batch Event Format
```json
{
  "events": [
    {
      "event": {}
    }
  ],
  "metadata": {
    "batch_id": "string",
    "source": "string",
    "timestamp": "datetime"
  }
}
```

## 3. Event Categories

### 3.1 Security Events
```yaml
events:
  security:
    authentication:
      - user.login
      - user.logout
      - user.password_change
      - user.mfa_setup
      - user.token_refresh

    authorization:
      - permission.check
      - permission.grant
      - permission.revoke
      - role.assign
      - role.remove
```

### 3.2 User Events
```yaml
events:
  user:
    profile:
      - profile.create
      - profile.update
      - profile.delete
      - profile.view

    data:
      - data.access
      - data.modify
      - data.export
      - data.share
```

### 3.3 System Events
```yaml
events:
  system:
    configuration:
      - config.change
      - config.deploy
      - config.rollback
      - config.validate

    resource:
      - resource.create
      - resource.update
      - resource.delete
      - resource.access
```

## 4. Service Integration

### 4.1 Character Service
```yaml
integration:
  service: character
  events:
    - character_created:
        severity: info
        retention: 180d
    - character_modified:
        severity: info
        retention: 180d
    - character_deleted:
        severity: warning
        retention: 365d
    - character_shared:
        severity: info
        retention: 180d
```

### 4.2 Campaign Service
```yaml
integration:
  service: campaign
  events:
    - campaign_created:
        severity: info
        retention: 180d
    - campaign_modified:
        severity: info
        retention: 180d
    - campaign_deleted:
        severity: warning
        retention: 365d
    - player_joined:
        severity: info
        retention: 180d
```

### 4.3 Auth Service
```yaml
integration:
  service: auth
  events:
    - user_authenticated:
        severity: info
        retention: 365d
    - auth_failed:
        severity: warning
        retention: 365d
    - permission_changed:
        severity: warning
        retention: 365d
    - role_changed:
        severity: warning
        retention: 365d
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_audit import AuditClient

client = AuditClient(
    service="character_service",
    options={
        "batch_size": 100,
        "flush_interval": 5,
        "retry_count": 3
    }
)

# Single event
client.log_event(
    event_type="character.created",
    actor_id="user123",
    target_id="char456",
    data={
        "changes": ["name", "class"],
        "metadata": {"source": "api"}
    }
)

# Batch events
client.log_events([
    {
        "event_type": "character.modified",
        "actor_id": "user123",
        "target_id": "char456",
        "data": {}
    }
])
```

### 5.2 Go Client
```go
package main

import "dnd/audit"

func main() {
    client := audit.NewClient(&audit.Config{
        Service: "campaign_service",
        Options: audit.Options{
            BatchSize: 100,
            FlushInterval: 5,
            RetryCount: 3,
        },
    })

    // Single event
    client.LogEvent(ctx, &audit.Event{
        Type: "campaign.created",
        ActorID: "user123",
        TargetID: "camp456",
        Data: map[string]interface{}{
            "changes": []string{"name", "description"},
        },
    })
}
```

## 6. Query Interface

### 6.1 Search Query
```json
{
  "query": {
    "time_range": {
      "start": "timestamp",
      "end": "timestamp"
    },
    "filters": [
      {
        "field": "string",
        "operator": "eq|ne|gt|lt|in",
        "value": "any"
      }
    ],
    "aggregations": [
      {
        "field": "string",
        "type": "count|sum|avg|min|max"
      }
    ],
    "sort": [
      {
        "field": "string",
        "order": "asc|desc"
      }
    ],
    "page": {
      "size": "integer",
      "number": "integer"
    }
  }
}
```

### 6.2 Analysis Query
```json
{
  "analysis": {
    "type": "pattern|anomaly|trend",
    "parameters": {
      "field": "string",
      "window": "duration",
      "threshold": "float"
    },
    "filters": [],
    "options": {
      "sensitivity": "float",
      "min_support": "float"
    }
  }
}
```

## 7. Report Interface

### 7.1 Report Definition
```yaml
report:
  name: "Security Events Summary"
  schedule: "0 0 * * *"
  format: "pdf|csv|json"
  content:
    - section:
        name: "Authentication Events"
        query: {}
        chart: "line|bar|table"
    - section:
        name: "Authorization Events"
        query: {}
        chart: "pie|table"
```

### 7.2 Report Template
```yaml
template:
  header:
    title: "string"
    timestamp: "datetime"
    generated_by: "string"
  
  sections: []
  
  footer:
    page: "integer"
    total_pages: "integer"
```

## 8. Security Interface

### 8.1 Authentication
```yaml
auth:
  type: "bearer"
  roles:
    - audit_reader
    - audit_writer
    - report_generator
  scope: "audit:read audit:write"
```

### 8.2 Authorization
```yaml
permissions:
  read:
    - "events:read"
    - "reports:read"
    - "analysis:read"
  write:
    - "events:write"
    - "reports:write"
    - "analysis:write"
  admin:
    - "events:admin"
    - "reports:admin"
    - "analysis:admin"
```

## 9. Configuration Interface

### 9.1 Service Configuration
```yaml
config:
  ingest:
    batch_size: 1000
    flush_interval: 5
    retry_count: 3
    buffer_size: 10000

  storage:
    retention:
      hot: 30d
      warm: 90d
      cold: 365d
    shards: 5
    replicas: 2

  processing:
    enrichment: true
    correlation: true
    pattern_detection: true
```

### 9.2 Index Configuration
```yaml
indices:
  template:
    name: "audit-events"
    patterns: ["audit-*"]
    settings:
      number_of_shards: 5
      number_of_replicas: 1
    mappings:
      properties:
        timestamp:
          type: "date"
        service:
          type: "keyword"
        type:
          type: "keyword"
```
