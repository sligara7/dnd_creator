# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

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

### Testing

```bash
# Run all tests
podman exec dnd_character_service python -m pytest -v

# Run specific test file
podman exec dnd_character_service python -m pytest path/to/test_file.py -v

# Run tests with coverage
podman exec dnd_character_service python -m pytest --cov=. -v
```

### Development Tools

```bash
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

The application follows a microservices architecture supporting two main campaign types: traditional D&D and Antitheticon (identity deception). Key documentation is split between:

1. This file (WARP.md) - Development and deployment guidance
2. SERVICE.md - High-level service architecture and functionality
3. api-spec.yaml - OpenAPI specification detailing endpoints and schemas

The system consists of the following services:

# Service Architecture

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
   - Map and token creation
   - GPU-accelerated image generation
   - Internal PostgreSQL database
   - Port: 8002

## Infrastructure Services

### API Gateway and Routing (Traefik)

Traefik v2 is used as the API gateway. It discovers services via Docker labels and routes by path prefix.

- Static config: `traefik/traefik.yml`
- Dynamic middlewares: `traefik/dynamic/middlewares.yml`
- Compose service: `docker-compose.yml` (service: traefik)

Local development quick start:

```bash
# Start Traefik and all services
docker-compose up -d

# Traefik dashboard (dev mode only)
http://localhost:8080

# Service endpoints (via Traefik)
http://localhost/api/character
http://localhost/api/campaign
http://localhost/api/world
http://localhost/api/theme
http://localhost/api/hub
```

Service label pattern (example for Character Service):

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.character.rule=PathPrefix(`/api/character`)"
  - "traefik.http.middlewares.character-strip.stripprefix.prefixes=/api/character"
  - "traefik.http.routers.character.middlewares=character-strip,cors,rate-limit,secure-headers"
  - "traefik.http.services.character.loadbalancer.server.port=8000"
```

Production hardening checklist:
- Enable HTTPS with Let’s Encrypt in `traefik/traefik.yml`
- Redirect HTTP → HTTPS
- Disable or protect the dashboard (port 8080)
- Enable middlewares: CORS, rate limiting, security headers
- Set request size/timeouts as appropriate
- Keep services on a private Docker network; only Traefik is publicly exposed

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
   - Centralized LLM operations
   - Text generation (OpenAI)
   - Image generation (Stable Diffusion)
   - API key and rate limit management
   - Response caching and optimization
   - Port: 8100

## Service Features

### Character Creation & Evolution
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
