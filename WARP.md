# Web Application Requirements & Planning (WARP)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## Core Mission
Create a next-generation D&D 5e 2024 character creation and campaign management system that:
- Enables ANY character concept through AI-powered content generation
- Supports deep storytelling and character evolution
- Provides theme-aware campaign integration
- Maintains D&D 5e 2024 rules compliance
- Offers seamless service communication

## Common Development Commands

### Build and Run Services

```bash
# Full stack development setup
./deployment/scripts/setup-full.sh

# Services development setup
./deployment/scripts/setup-services.sh

# Run individual service
podman run -d \
  --name dnd-character-service \
  -p 8000:8000 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e SECRET_KEY="${SECRET_KEY}" \
  dnd-character-service
```

### Environment Setup

```bash
# Local development environment setup (runs inside pixi shell)
pixi shell

# Build container with pixi environment
FROM ghcr.io/prefix-dev/pixi:latest
COPY . /app
WORKDIR /app
RUN pixi install
```

### Testing

```bash
# Run all tests (in pixi shell)
pixi run test

# Run specific test file
pixi run pytest path/to/test_file.py -v

# Run tests with coverage
pixi run coverage

# Run inside container
podman exec dnd_character_service pixi run test
```

### Development Tools

```bash
# Start local development server
pixi run start

# Format code
pixi run format

# Lint code
pixi run lint

# Type checking
pixi run typecheck

# Access service container shell
podman exec -it dnd_character_service /bin/bash

# Check service health
curl http://localhost:8000/health

# View service logs
podman-compose logs -f

# Check service status
podman-compose ps
```

## Architecture Overview

The application follows a secure microservices architecture supporting two main campaign types: traditional D&D and Antitheticon (identity deception). The architecture enforces several key principles:

1. API Gateway (Traefik) serves as the single public entry point
2. All inter-service communication flows through the Message Hub
3. No direct service-to-service communication is allowed
4. Authentication and authorization are handled at the gateway level
5. Services are internal only - no direct external access

Key documentation is split between:

1. This file (WARP.md) - Development and deployment guidance
2. Service Requirements Documents (SRDs) - Detailed service requirements
3. Interface Control Documents (ICDs) - Service interface specifications

The system consists of the following services:

### Service Architecture

The system comprises several layers of services:

#### Edge Layer
1. **API Gateway Service** (Traefik)
   - Edge routing and load balancing
   - TLS termination and HTTPS enforcement
   - Request routing to Message Hub
   - Rate limiting and circuit breaking

2. **Auth Service**
   - Authentication and authorization
   - Token management
   - Session handling
   - RBAC enforcement
   - Security event logging

#### Communication Layer
3. **Message Hub**
   - Inter-service communication backbone
   - Event management and routing
   - Service discovery
   - Health monitoring
   - State synchronization

#### Core Services
4. **Character Service**
   - Character creation and management
   - Custom content generation
   - Character evolution
   - Journal system
   - Inventory management

5. **Campaign Service**
   - Campaign creation and management
   - Theme system
   - Chapter organization
   - NPC management
   - World building

6. **Image Service**
   - Portrait generation
   - Map creation
   - Item visualization
   - Tactical overlays
   - Image processing

7. **LLM Service**
   - Text generation
   - Story narration
   - Content refinement
   - Theme adaptation
   - Context management

8. **Catalog Service**
   - Content management
   - Game content discovery
   - Content validation
   - Theme adaptation
   - Asset organization

#### Infrastructure Layer
9. **Cache Service**
   - Distributed caching
   - Performance optimization
   - Data consistency
   - Resource efficiency
   - Load reduction

10. **Storage Service**
    - Binary asset storage
    - Version control
    - Backup management
    - Asset lifecycle
    - Content delivery

11. **Search Service**
    - Full-text search
    - Semantic search
    - Content indexing
    - Search analytics
    - Result ranking

2. **Message Hub**
   - Centralized communication backbone
   - Event management and routing
   - Service discovery and health monitoring
   - No direct service-to-service communication

3. **Character Service**
   - Character creation and management
   - Custom content generation
   - Character evolution and versioning
   - Journal system

4. **Campaign Service**
   - Campaign creation and management
   - Theme system and story generation
   - Chapter organization
   - NPC management

5. **Image Service**
   - Portrait generation
   - Map creation
   - Item visualization
   - Tactical overlay system

6. **LLM Service**
   - Text content generation
   - Story and narrative generation
   - Content refinement
   - Theme integration

7. **Catalog Service**
   - Unified content management
   - Game content discovery and search
   - Content validation and balance
   - Theme-aware content adaptation

## Core Services

1. **Character Service** (`character_service/`)
   - Character creation and management API
   - Core D&D mechanics and validation
   - Support for both campaign types:
     * Traditional: Mechanically balanced D&D characters
     * Antitheticon: Identity deception networks and plots
   - Rich narrative development and evolution
   - Campaign integration hooks
   - FastAPI + SQLAlchemy + Pydantic
   - Internal PostgreSQL database
   - Port: 8000

2. **Campaign Service** (`campaign_service/`)
   - Campaign and party management
   - Character progression tracking
   - Event processing and story hooks
   - World effects integration
   - Relationship tracking
   - Git-like version control for campaigns
   - Theme management and balance
   - Multi-layer plot tracking (Antitheticon)
   - Internal PostgreSQL database
   - Port: 8001

3. **Image Service** (`image_service/`)
   - Character portrait generation
   - Map generation (tactical and campaign)
   - Item/equipment visualization
   - Character and NPC visualization
   - Location and environment visualization
   - Magical effect visualization
   - Theme-aware content generation
   - GetImg.AI API integration
   - Content version tracking
   - Image asset management
   - Port: 8002

## Infrastructure Services

### API Gateway (Traefik)

Traefik v2 serves as the API gateway, providing:

1. Edge Routing
   - Path-based routing to services
   - HTTPS enforcement
   - Request/response transformation
   - Service mesh integration

2. Security Features
   - TLS termination and management
   - Let's Encrypt integration
   - JWT validation
   - API key validation
   - Rate limiting
   - Circuit breaking
   - CORS enforcement
   - Security headers

3. Service Management
   - Docker provider integration
   - Dynamic configuration
   - Health checking
   - Load balancing
   - Circuit breaking
   - Service discovery
   - Automatic failover

4. Monitoring
   - Prometheus metrics
   - Request/response logging
   - Health status tracking
   - Performance metrics
   - Error tracking
   - Dashboard UI

Configuration Example:
```yaml
# Static Configuration (traefik.yml)
api:
  dashboard: true  # Enable dashboard in dev only
  insecure: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:  # Force HTTPS
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

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

metrics:
  prometheus:
    buckets: [0.1, 0.3, 1.2, 5.0]
    addEntryPointsLabels: true
    addServicesLabels: true

log:
  level: INFO
  format: json

accessLog:
  format: json
  fields:
    headers:
      defaultMode: keep
      names:
        User-Agent: keep
        Authorization: redact
        X-API-Key: redact

# Dynamic Configuration (dynamic.yml)
http:
  middlewares:
    # Security headers
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
    
    # CORS
    cors:
      cors:
        allowedOrigins:
          - "https://dndcreator.com"
          - "https://*.dndcreator.com"
        allowedMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allowedHeaders: ["Authorization", "Content-Type", "X-Request-ID"]
        exposedHeaders: ["X-Rate-Limit-*"]
        maxAge: 86400
```

Service Configuration (in docker-compose.yml):
```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - --api.insecure=false
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.myresolver.acme.httpchallenge=true
      - --certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./certs:/etc/certs:ro
      - ./dynamic:/etc/traefik/dynamic:ro
    networks:
      - internal
      - external
    healthcheck:
      test: ["CMD", "traefik", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

  character-service:
    image: dnd-character-service:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.character.rule=PathPrefix(`/api/v2/characters`)"
      - "traefik.http.routers.character.middlewares=auth,rate-limit,secure-headers"
      - "traefik.http.services.character.loadbalancer.server.port=8000"
      - "traefik.http.services.character.loadbalancer.healthcheck.path=/health"
    networks:
      - internal
    environment:
      - MESSAGE_HUB_URL=http://message-hub:8200
```

Production Security Requirements:

Traefik v2 serves as the API gateway and authentication layer. It provides:

1. Authentication & Authorization
   - JWT validation and processing
   - API key validation
   - Role-based access control
   - Session management

2. Traffic Management
   - Rate limiting
   - Circuit breaking
   - Load balancing
   - Request routing

3. Security Features
   - TLS termination
   - HTTPS enforcement
   - Security headers
   - Request validation

4. Service Discovery
   - Dynamic service registration
   - Health checking
   - Automatic failover
   - Load balancing

Service Configuration:
```yaml
services:
  api_gateway:
    image: traefik:v2.10
    command:
      - --api.insecure=false
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.myresolver.acme.tlschallenge=true
    ports:
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./certs:/etc/certs:ro
    networks:
      - internal
      - external
```

Production Security Requirements:
- HTTPS only (no HTTP traffic)
- Valid SSL certificates
- Strict security headers
- Rate limiting enabled
- Request size limits
- Timeouts configured
- Private network isolation
- Regular security audits

1. **API Gateway (Traefik)** (`traefik/`)
   - Edge router and reverse proxy for all client requests
   - Routes by path prefix to backend services (e.g., /api/character, /api/campaign)
   - Handles TLS termination, middleware (CORS, rate limits, security headers)
   - Can perform basic auth/API key checks at the edge
   - Ports: 80 (HTTP), 443 (HTTPS), 8080 (dashboard in dev)

2. **Message Hub** (`message_hub/`)
   - Central communication coordinator
   - All service-to-service communication
   - Circuit breakers and retries
   - Event sourcing and transactions
   - Service health monitoring
   - Port: 8200

3. **LLM Service** (`llm_service/`)
   - Centralized LLM operations with multiple model support:
     * GPT-4 (primary model)
     * GPT-3.5-turbo (fallback model)
     * Claude 3 (alternative model)
   - Text generation capabilities:
     * Character backstories and traits
     * Campaign narratives and plots
     * NPC dialogues and interactions
     * Equipment and spell descriptions
   - Image generation via GetImg.AI:
     * Text-to-image for new content
     * Image-to-image for modifications
     * Face enhancement and upscaling
     * Theme-aware style transfer
   - Advanced caching and rate limiting:
     * Redis-based caching with configurable TTL
     * Service-specific rate limits:
       - Text: 100 requests/minute
       - Image: 10 requests/minute
     * Token usage tracking and quotas
   - Comprehensive monitoring:
     * Request tracking by type and service
     * Latency histograms
     * Token usage metrics
     * Cache performance metrics
     * Resource utilization tracking
   - Theme management:
     * Consistent text and visual styles
     * Genre-appropriate content
     * Cross-service coordination
   - Integration management:
     * API authentication and key management
     * Queue prioritization and circuit breakers
     * Error handling and recovery strategies
   - Port: 8100

## Service Features

### Character Creation & Evolution
- Complete character sheet support (PCs, NPCs, monsters)
- Journal system with CRUD, sessions, XP, milestones
- Unified catalog for items, spells, and equipment
- Version control for character evolution (branches, merges, approvals)
- Performance monitoring and metrics endpoints
- Support for traditional D&D and Antitheticon campaigns
- Mechanically balanced character generation
- Rich narrative development and backstory
- Dynamic campaign integration
- Character evolution tracking

### Antitheticon System
- Identity deception networks
- Multi-layer plot management
- Evolution and transformation tracking
- Theme and balance management
- Identity relationship mapping

### Campaign Integration
- Event processing and tracking
- Story hook generation and management
- World effect simulation
- Character relationship tracking
- Plot development assistance

### Service Integration
- Campaign service coordination
- World state management
- Theme service balancing
- Story hook distribution
- Cross-service event handling
- State consistency management

## Service Communication Flow

```ascii
┌──────────────────────────────────────────────────────────┐
│                      External Clients                     │
└────────────────────────┬─────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│                     API Gateway Layer                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│ │ API Gateway │  │    Auth     │  │  Metrics    │      │
│ │  (Traefik)  │  │   Service   │  │  Service    │      │
│ └─────┬───────┘  └─────┬───────┘  └─────┬───────┘      │
└───────┼─────────────────┼─────────────────┼─────────────┘
        │                 │                 │
┌───────┼─────────────────┼─────────────────┼─────────────┐
│       │  Communication  │      Layer      │             │
│ ┌─────┴─────┬─────┴─────┬─────┴─────┐                  │
│ │ Message   │  Cache    │  Storage  │                  │
│ │   Hub     │ Service   │  Service  │                  │
│ └─────┬─────┴─────┬─────┴─────┬─────┘                  │
└───────┼─────────────────┼─────────────────┼─────────────┘
        │                 │                 │
┌───────┼─────────────────┼─────────────────┼─────────────┐
│     Core Services Layer │                               │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│ │Character│ │Campaign │ │  Image  │ │   LLM   │       │
│ │ Service │ │ Service │ │ Service │ │ Service │       │
│ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
└──────┼──────────┼───────────┼───────────┼──────────────┘
       │          │           │           │
┌──────┼──────────┼───────────┼───────────┼──────────────┐
│  Support Services Layer    │           │               │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│ │Catalog  │ │ Search  │ │ Audit   │ │ Metrics │      │
│ │Service  │ │ Service │ │ Service │ │ Service │      │
│ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │
└──────┼──────────┼───────────┼───────────┼─────────────┘
       │          │           │           │
┌──────┼──────────┼───────────┼───────────┼─────────────┐
│     Data Layer            │           │               │
│ ┌─────┐ ┌─────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐  │
│ │Pgsql│ │Redis│ │ S3 │ │ ES │ │Embd│ │Time│ │Prom│  │
│ └─────┘ └─────┘ └────┘ └────┘ └────┘ └────┘ └────┘  │
└─────────────────────────────────────────────────────────┘

Legend:
Pgsql = PostgreSQL     Redis = Redis Cache    S3 = Object Storage
ES = Elasticsearch     Embd = Embedding DB    Time = TimescaleDB
Prom = Prometheus
```

The system uses Clean Architecture principles with clear separation of concerns:

```ascii
┌─────────────────┐
│   API Gateway   │  ← Single entry point for clients
└───────┬─────────┘
        │
┌───────┼─────────┐
│ Message Hub &   │  ← All inter-service communication
│ Orchestrator    │
└─┬─────┬─────┬───┘
  │     │     │
  │     │     │    ┌─────────────┐
  │     │     │    │ LLM Service │
  │     │     │    └─────────────┘
  ▼     ▼     ▼         ▲
┌────────┐ ┌────────┐   │   ┌────────┐
│Character│ │Campaign│   │   │ Image  │
│Service  │ │Service │───┘   │Service │
└────────┘ └────────┘       └────────┘
    │          │                │
    ▼          ▼                ▼
┌────────┐ ┌────────┐      ┌────────┐
│Character│ │Campaign│      │ Image  │
│   DB    │ │   DB   │      │   DB   │
└────────┘ └────────┘      └────────┘
```

Each service follows Clean Architecture internally:

```
Service Internal Layers
┌────────────────────────────┐
│    Presentation Layer      │
│  - FastAPI Routes/Controllers
│  - Request/Response Models │
├────────────────────────────┤
│    Application Layer       │
│  - Use Cases              │
│  - Service Orchestration  │
├────────────────────────────┤
│     Domain Layer          │
│  - Business Logic         │
│  - Domain Models          │
├────────────────────────────┤
│   Infrastructure Layer    │
│  - Database Access        │
│  - External Services      │
└────────────────────────────┘
```

## Key Development Patterns

1. **Router-Based API Organization**
   - Each major feature set has its own router module
   - Routes are organized by resource and functionality
   - Core business logic lives in service classes

2. **Service Layer Pattern**
   - Business logic encapsulated in service classes
   - Services are independent of the web framework
   - Dependency injection for external services

3. **Repository Pattern**
   - Data access abstracted through repositories
   - Support for multiple database backends
   - Async/await patterns for database operations

4. **Factory Pattern for Content Generation**
   - Modular content generation system
   - Pluggable LLM provider support
   - Extensible validation framework

## Important Files and Directories

### Core Services
- `/character_service/src/` - Character creation and management
- `/campaign_service/src/` - Campaign and party management
- `/image_service/src/` - Image generation and management

### Infrastructure Services
- `/traefik/` - Traefik configuration (static and dynamic)
- `/docker-compose.yml` - Orchestrates Traefik and services
- `/message_hub/` - Service communication hub
- `/llm_service/` - Centralized LLM operations

### Support Directories
- `/deployment/` - Deployment configurations and scripts
- `/shared/` - Shared code and utilities
- `/tests/` - Test suites for all components

## Development Guidelines

1. **API Design**
   - Follow REST principles for endpoint design
   - Use Pydantic models for request/response validation
   - Include OpenAPI documentation for all endpoints

2. **Testing**
   - Maintain high test coverage for core functionality
   - Use pytest fixtures for test setup
   - Mock external services in unit tests

3. **Error Handling**
   - Use custom exception classes
   - Return appropriate HTTP status codes
   - Provide detailed error messages

4. **Code Organization**
   - Follow Clean Architecture principles
   - Keep modules focused and single-purpose
   - Use dependency injection for better testability
