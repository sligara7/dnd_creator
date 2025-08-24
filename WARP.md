# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Development Commands

### Build and Run Services

```bash
# Full stack development setup
./deployment/scripts/setup-full.sh

# Backend-only development setup
./deployment/scripts/setup-backend-dev.sh

# Run individual backend service
podman run -d \
  --name dnd-char-creator \
  -p 8000:8000 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e SECRET_KEY="${SECRET_KEY}" \
  dnd-char-creator
```

### Testing

```bash
# Run all backend tests
podman exec dnd_character_api_dev python -m pytest -v

# Run specific test file
podman exec dnd_character_api_dev python -m pytest path/to/test_file.py -v

# Run tests with coverage
podman exec dnd_character_api_dev python -m pytest --cov=. -v
```

### Development Tools

```bash
# Access backend container shell
podman exec -it dnd_character_api_dev /bin/bash

# Check service health
curl http://localhost:8000/health

# View service logs
podman-compose logs -f

# Check service status
podman-compose ps
```

## Architecture Overview

The application follows a microservices architecture with the following services:

# Service Architecture

## Core Services

1. **Character Service** (`character_service/`)
   - Character creation and management API
   - Core D&D mechanics and validation
   - FastAPI + SQLAlchemy + Pydantic
   - Internal PostgreSQL database
   - Port: 8000

2. **Campaign Service** (`campaign_service/`)
   - Campaign and party management
   - Character progression tracking
   - Git-like version control for campaigns
   - Internal PostgreSQL database
   - Port: 8001

3. **Image Service** (`image_service/`)
   - Character portrait generation
   - Map and token creation
   - GPU-accelerated image generation
   - Internal PostgreSQL database
   - Port: 8002

## Infrastructure Services

1. **API Gateway** (`gateway/`)
   - Single entry point for all client requests
   - Route requests to appropriate services
   - Handle authentication and authorization
   - Basic request validation
   - Port: 3000

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
- `/api_gateway/` - API Gateway service
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
