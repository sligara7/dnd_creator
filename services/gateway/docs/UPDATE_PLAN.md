# API Gateway Documentation Update Plan

## ICD Updates Required

### 1. Remove Direct Service Communication
1. Update Middleware Chain (section 1.3):
   ```diff
   # REMOVE:
   auth:
     forwardAuth:
       address: "http://auth-service:8300/validate"
       trustForwardHeader: true
   
   # ADD:
   auth:
     forwardAuth:
       messageHub: true
       event: "auth.validate_request"
       correlationHeader: "X-Request-ID"
   ```

2. Remove direct service URLs in Dynamic Configuration:
   ```diff
   # REMOVE:
   services:
     character-service:
       loadBalancer:
         servers:
           - url: "http://character-service:8000"
   
   # ADD:
   services:
     character-service:
       messageHub: true
       eventPrefix: "character"
       healthEvent: "character.health"
   ```

### 2. Enhance Message Hub Integration
1. Update Message Hub Integration section:
   ```markdown
   ## 5. Message Hub Integration

   ### 5.1 Service Communication
   All service communication MUST be routed through Message Hub:
   - No direct HTTP calls to services
   - All requests translated to Message Hub events
   - All responses handled via Message Hub
   - Health checks via Message Hub events
   ```

2. Add Message Hub Event Patterns:
   ```markdown
   ### 5.3 Event Patterns
   - Gateway → Auth: auth.validate_request
   - Gateway → Service: service.request
   - Service → Gateway: service.response
   - Gateway → Health: health.check
   - Health → Gateway: health.status
   ```

3. Update Service Discovery section:
   ```markdown
   ## 11. Service Discovery
   Service discovery MUST be handled through Message Hub:
   - Service registration via events
   - Service health status via events
   - No direct service polling
   ```

### 3. Update Circuit Breaker
1. Modify circuit breaker to work through Message Hub:
   ```markdown
   ## 7. Circuit Breaker Interface

   ### 7.1 Message Hub Circuit Breaking
   - Circuit state maintained via Message Hub events
   - State changes published as events
   - Health checks routed through Message Hub
   - No direct service health polling
   ```

## SRD Updates Required

### 1. Update Core Principles
1. Strengthen Message Hub requirements:
   ```markdown
   ### 1.2 Core Principles
   - ALL service communication MUST route through Message Hub
   - ZERO direct service-to-service communication allowed
   - Gateway acts as HTTP-to-MessageHub bridge
   - Message Hub handles all service discovery
   ```

### 2. Update Functional Requirements
1. Revise Message Hub Integration section:
   ```markdown
   ### 2.2 Message Hub Integration (Required)
   - FR2.1: Convert all HTTP requests to Message Hub events
   - FR2.2: NO direct service communication
   - FR2.3: Handle request-response via Message Hub correlation
   - FR2.4: Manage service health via Message Hub events
   - FR2.5: Handle service discovery via Message Hub
   ```

### 3. Update System Architecture
1. Revise Components section:
   ```markdown
   ### 4.1 Components

   1. Message Hub Bridge
      - HTTP to Message Hub translation
      - Response correlation
      - Event routing
      - State management

   2. Service Router
      - Event-based routing
      - Message Hub event mapping
      - Request transformation
      - Response handling
   ```

2. Remove direct service communication:
   ```markdown
   ### 4.2 External Interfaces
   - Remove direct service URLs
   - Add Message Hub event patterns
   - Update health check flows
   ```

### 4. Update Message Routing
1. Add explicit Message Hub routing patterns:
   ```markdown
   ### 5.1 Message Routing
   - MR1.1: Convert ALL HTTP requests to Message Hub events
   - MR1.2: Route via Message Hub topics/queues
   - MR1.3: Handle responses via correlated events
   - MR1.4: Manage timeouts via Message Hub
   - MR1.5: Support event-driven patterns
   ```

## Implementation Changes Required

1. Update service configuration:
   ```yaml
   # REMOVE:
   services:
     character-service:
       url: http://character-service:8000
       health: /health
   
   # ADD:
   services:
     character-service:
       message_hub:
         topic: character
         health_check: character.health
         timeout: 30s
   ```

2. Update middleware:
   ```yaml
   # REMOVE:
   auth:
     forwardAuth:
       url: http://auth-service:8300/validate
   
   # ADD:
   auth:
     messageHub:
       event: auth.validate
       timeout: 5s
   ```

3. Update health checks:
   ```yaml
   # REMOVE:
   healthcheck:
     url: /health
     interval: 30s
   
   # ADD:
   healthcheck:
     messageHub:
       event: service.health
       interval: 30s
       timeout: 5s
   ```