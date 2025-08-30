# Interface Control Document: API Gateway Service (ICD-GW-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Gateway Architecture

### 1.1 Traefik Overview
The API Gateway is implemented using Traefik v2, providing:
- Edge routing and load balancing
- TLS termination and HTTPS enforcement
- Authentication and authorization
- Rate limiting and circuit breaking
- Service discovery and health monitoring
- Metrics collection and tracing

### 1.2 Service Endpoints
```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
```

### 1.3 Middleware Chain
```yaml
http:
  middlewares:
    # Security middleware
    secure-headers:
      headers:
        frameDeny: true
        sslRedirect: true
        browserXssFilter: true
        contentTypeNosniff: true
        referrerPolicy: "strict-origin-when-cross-origin"
        stsSeconds: 31536000
    
    # Authentication
    auth:
      forwardAuth:
        address: "http://auth-service:8300/validate"
        trustForwardHeader: true
    
    # Rate limiting
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
    
    # Circuit breaker
    circuit-breaker:
      circuitBreaker:
        expression: "NetworkErrorRatio() > 0.10"
```

## 2. External Interface

### 1.1 Base URL
```
https://api.dndcreator.com/v1
```

### 1.2 Authentication
All requests must include one of:
```
Authorization: Bearer <token>
X-API-Key: <api_key>
```

### 1.3 Common Headers
```
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
```

### 1.4 Rate Limit Headers
```
X-RateLimit-Limit: <requests_per_window>
X-RateLimit-Remaining: <requests_remaining>
X-RateLimit-Reset: <window_reset_time>
```

## 2. Character Service Routes

### 2.1 Create Character
```http
POST /character
```

#### Request Body
```json
{
  "name": "string",
  "race": "string",
  "class": "string",
  "level": "integer",
  "attributes": {
    "strength": "integer",
    "dexterity": "integer",
    "constitution": "integer",
    "intelligence": "integer",
    "wisdom": "integer",
    "charisma": "integer"
  }
}
```

### 2.2 Get Character
```http
GET /character/{id}
```

### 2.3 Update Character
```http
PUT /character/{id}
```

### 2.4 Delete Character
```http
DELETE /character/{id}
```

## 3. Campaign Service Routes

### 3.1 Create Campaign
```http
POST /campaign
```

#### Request Body
```json
{
  "name": "string",
  "description": "string",
  "dm_id": "string",
  "player_ids": ["string"],
  "settings": {}
}
```

### 3.2 Get Campaign
```http
GET /campaign/{id}
```

### 3.3 Update Campaign
```http
PUT /campaign/{id}
```

### 3.4 Delete Campaign
```http
DELETE /campaign/{id}
```

## 4. Image Service Routes

### 4.1 Generate Character Image
```http
POST /image/character
```

#### Request Body
```json
{
  "character_id": "string",
  "style": "string",
  "pose": "string",
  "background": "string"
}
```

### 4.2 Get Image
```http
GET /image/{id}
```

### 4.3 Update Image
```http
PUT /image/{id}
```

### 4.4 Delete Image
```http
DELETE /image/{id}
```

## 5. Message Hub Integration

### 5.1 Message Format
```json
{
  "id": "uuid",
  "source": "api-gateway",
  "destination": "service_name",
  "type": "request|response",
  "payload": {},
  "correlation_id": "uuid",
  "timestamp": "2025-08-30T14:49:14Z"
}
```

### 5.2 Event Format
```json
{
  "id": "uuid",
  "source": "api-gateway",
  "type": "event",
  "event_type": "request|error|audit",
  "payload": {},
  "timestamp": "2025-08-30T14:49:14Z"
}
```

## 6. Health API

### 6.1 Gateway Health
```http
GET /health
```

#### Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-08-30T14:49:14Z",
  "services": {
    "character-service": "healthy",
    "campaign-service": "healthy",
    "image-service": "healthy",
    "message-hub": "healthy"
  }
}
```

### 6.2 Service Health
```http
GET /health/{service}
```

#### Response
```json
{
  "service": "string",
  "status": "healthy|degraded|unhealthy",
  "last_check": "2025-08-30T14:49:14Z",
  "details": {
    "uptime": "integer",
    "response_time": "integer",
    "error_rate": "float"
  }
}
```

## 7. Circuit Breaker Interface

### 7.1 Circuit State
```json
{
  "service": "string",
  "state": "CLOSED|OPEN|HALF_OPEN",
  "last_failure": "2025-08-30T14:49:14Z",
  "failure_count": "integer",
  "reset_timeout": "integer"
}
```

### 7.2 Circuit Configuration
```json
{
  "failure_threshold": 5,
  "reset_timeout": "1m",
  "half_open_requests": 3
}
```

## 8. Metrics API

### 8.1 Prometheus Metrics
```http
GET /metrics
```

#### Response Format
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="get",path="/character",service="character-service"} 1000

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1",path="/character"} 900
```

## 9. Error Handling

### 9.1 Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "request_id": "string",
      "timestamp": "2025-08-30T14:49:14Z",
      "service": "string"
    }
  }
}
```

### 9.2 Common Error Codes
- `AUTH_REQUIRED`: Authentication required
- `INVALID_AUTH`: Invalid authentication
- `RATE_LIMITED`: Rate limit exceeded
- `SERVICE_UNAVAILABLE`: Backend service unavailable
- `BAD_GATEWAY`: Error from backend service
- `TIMEOUT`: Request timeout
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid request data
- `INTERNAL_ERROR`: Internal server error

## 10. Traefik Configuration

### 10.1 Static Configuration
```yaml
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: internal
  file:
    directory: "/etc/traefik/dynamic"
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@dndcreator.com"
      storage: "/etc/traefik/acme/acme.json"
      httpChallenge:
        entryPoint: web
```

### 10.2 Dynamic Configuration
```yaml
http:
  routers:
    character-service:
      rule: "PathPrefix(`/api/v2/characters`)"
      service: "character-service"
      middlewares:
        - auth
        - rate-limit
        - secure-headers
      tls: {}
    
    campaign-service:
      rule: "PathPrefix(`/api/v2/campaigns`)"
      service: "campaign-service"
      middlewares:
        - auth
        - rate-limit
        - secure-headers
      tls: {}

  services:
    character-service:
      loadBalancer:
        servers:
          - url: "http://character-service:8000"
        healthCheck:
          path: "/health"
          interval: "10s"
    
    campaign-service:
      loadBalancer:
        servers:
          - url: "http://campaign-service:8001"
        healthCheck:
          path: "/health"
          interval: "10s"
```

## 11. Service Discovery

### 10.1 Service Registration
```http
POST /discovery/register
```

#### Request Body
```json
{
  "service": "string",
  "status": "healthy",
  "endpoints": [
    {
      "path": "string",
      "methods": ["GET", "POST"],
      "rate_limit": 1000
    }
  ],
  "version": "1.0.0"
}
```

### 10.2 Service Discovery
```http
GET /discovery/services
```

#### Response
```json
{
  "services": [
    {
      "name": "string",
      "status": "healthy|degraded|unhealthy",
      "endpoints": [],
      "version": "1.0.0",
      "last_seen": "2025-08-30T14:49:14Z"
    }
  ]
}
```
