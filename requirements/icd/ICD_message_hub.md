# Interface Control Document: Message Hub Service (ICD-MH-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Service Interface

### 1.1 Base URL
```
http://message-hub:8200
```

### 1.2 Authentication Headers
```
X-Service-Name: <service_name>
X-Service-Key: <service_auth_key>
X-Request-ID: <uuid>
Content-Type: application/json
```

## 2. Message API

### 2.1 Send Message
```http
POST /message
```

#### Request Body
```json
{
  "id": "uuid",
  "type": "service_message",
  "source": "service_name",
  "destination": "service_name",
  "correlation_id": "uuid",
  "payload": {},
  "timestamp": "2025-08-30T14:49:14Z",
  "ttl": 300,
  "priority": 1
}
```

#### Response
```json
{
  "id": "uuid",
  "status": "accepted|delivered|failed",
  "timestamp": "2025-08-30T14:49:14Z"
}
```

### 2.2 Get Message Status
```http
GET /message/{id}
```

#### Response
```json
{
  "id": "uuid",
  "status": "pending|delivered|failed",
  "delivery_attempts": 1,
  "last_attempt": "2025-08-30T14:49:14Z"
}
```

## 3. Event API

### 3.1 Publish Event
```http
POST /event
```

#### Request Body
```json
{
  "id": "uuid",
  "type": "event",
  "source": "service_name",
  "event_type": "state_change|error|lifecycle|business|audit",
  "payload": {},
  "timestamp": "2025-08-30T14:49:14Z"
}
```

### 3.2 Subscribe to Events
```http
POST /subscribe
```

#### Request Body
```json
{
  "service": "service_name",
  "event_types": ["state_change", "error"],
  "callback_url": "http://service:port/callback"
}
```

## 4. Service Registry API

### 4.1 Register Service
```http
POST /registry
```

#### Request Body
```json
{
  "service": "service_name",
  "version": "1.0.0",
  "endpoints": [
    {
      "path": "/api/v1/resource",
      "methods": ["GET", "POST"]
    }
  ],
  "health_check": {
    "endpoint": "/health",
    "interval": 30
  }
}
```

### 4.2 Get Service Info
```http
GET /registry/{service}
```

#### Response
```json
{
  "service": "service_name",
  "status": "healthy|degraded|unhealthy",
  "last_seen": "2025-08-30T14:49:14Z",
  "version": "1.0.0"
}
```

## 5. Circuit Breaker API

### 5.1 Get Circuit States
```http
GET /circuit
```

#### Response
```json
{
  "circuits": [
    {
      "service": "service_name",
      "state": "CLOSED|OPEN|HALF_OPEN",
      "failure_count": 0,
      "last_failure": "2025-08-30T14:49:14Z",
      "reset_timeout": 60
    }
  ]
}
```

### 5.2 Update Circuit State
```http
PUT /circuit/{service}
```

#### Request Body
```json
{
  "state": "CLOSED|OPEN|HALF_OPEN",
  "reason": "string",
  "reset_timeout": 60
}
```

## 6. Health API

### 6.1 Health Check
```http
GET /health
```

#### Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "1.0.0",
  "uptime": 3600,
  "message_stats": {
    "processed": 1000,
    "failed": 10,
    "pending": 5
  },
  "services": {
    "character-service": "healthy",
    "campaign-service": "healthy"
  }
}
```

### 6.2 Detailed Health
```http
GET /health/details
```

#### Response
```json
{
  "status": "healthy",
  "components": {
    "message_queue": {
      "status": "healthy",
      "queue_depth": 10,
      "consumers": 5
    },
    "event_store": {
      "status": "healthy",
      "events_processed": 1000
    },
    "service_registry": {
      "status": "healthy",
      "registered_services": 5
    }
  }
}
```

## 7. Metrics API

### 7.1 Prometheus Metrics
```http
GET /metrics
```

#### Response Format
```
# HELP message_hub_messages_total Total messages processed
# TYPE message_hub_messages_total counter
message_hub_messages_total{type="service_message"} 1000

# HELP message_hub_events_total Total events processed
# TYPE message_hub_events_total counter
message_hub_events_total{type="state_change"} 500
```

## 8. Error Handling

### 8.1 Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "request_id": "string",
      "timestamp": "2025-08-30T14:49:14Z"
    }
  }
}
```

### 8.2 Common Error Codes
- `INVALID_MESSAGE`: Message format invalid
- `SERVICE_UNAVAILABLE`: Destination service unavailable
- `DELIVERY_FAILED`: Message delivery failed
- `INVALID_SUBSCRIPTION`: Invalid event subscription
- `AUTH_FAILED`: Service authentication failed
- `CIRCUIT_OPEN`: Circuit breaker open
- `RATE_LIMITED`: Rate limit exceeded

## 9. WebSocket Interface

### 9.1 Event Stream
```
ws://message-hub:8200/events
```

#### Subscribe Message
```json
{
  "type": "subscribe",
  "service": "service_name",
  "event_types": ["state_change", "error"]
}
```

#### Event Message
```json
{
  "type": "event",
  "event": {
    "id": "uuid",
    "type": "state_change",
    "data": {}
  }
}
```
