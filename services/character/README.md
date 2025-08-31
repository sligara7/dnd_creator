# D&D Character Service

Character creation and management service for the D&D Character Creator project.

## Overview

The Character Service is a FastAPI-based microservice that handles character creation, management, and evolution for D&D 5e 2024. It includes support for both traditional D&D character creation and the Antitheticon identity deception system.

### Key Features

- Complete character sheet support (PCs, NPCs, monsters)
- Journal system with CRUD, sessions, XP, milestones
- Unified catalog for items, spells, and equipment
- Version control for character evolution (branches, merges, approvals)
- Support for traditional D&D and Antitheticon campaigns
- Integration with LLM service for content generation
- Rich narrative development and backstory generation
- Dynamic campaign integration
- Character evolution tracking

## Project Structure

```
character-service/
├── alembic/                  # Database migrations
├── config/                   # Configuration files
├── docs/                     # Documentation files
├── k8s/                     # Kubernetes configurations
├── src/                     # Source code
│   └── character_service/
│       ├── api/             # API endpoints
│       │   └── v1/
│       │       └── endpoints/  # API endpoint implementations
│       ├── core/            # Core application code
│       ├── models/          # Database models
│       ├── repositories/    # Data access layer
│       ├── schemas/         # Pydantic schemas
│       └── utils/           # Utility functions
└── tests/                   # Test files
    ├── api/                 # API tests
    ├── repositories/        # Repository tests
    └── utils/               # Utility tests
```

## Getting Started

### Prerequisites

- Python 3.10
- PostgreSQL 14
- Redis 7
- Poetry
- podman or docker

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/OpenSourceLoot/dnd_tools.git
   cd services/character/character-service
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Copy environment example and update:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Service

#### Development

```bash
poetry run uvicorn character_service.main:app --reload
```

#### Production

```bash
podman-compose up -d
```

## API Documentation

After starting the service, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Main APIs

- `/api/v1/characters`: Character management
- `/api/v1/journals`: Journal system
- `/api/v1/inventory`: Inventory management
- `/api/v1/evolution`: Character evolution
- `/api/v1/antitheticon`: Antitheticon system

## Configuration

Service configuration is managed through:
1. Environment variables (`.env`)
2. Configuration files (`config.yaml`)
3. Kubernetes ConfigMaps and Secrets

See `.env.example` and `config/config.yaml` for available options.

## Testing

Run tests with:
```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/api/test_characters.py

# With coverage
poetry run pytest --cov=src tests/
```

## Development Commands

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run flake8 src/ tests/

# Type checking
poetry run mypy src/ tests/
```

## Architecture

The service follows Clean Architecture principles:

1. **API Layer** (`api/`)
   - FastAPI endpoints
   - Request/Response handling
   - Input validation

2. **Service Layer** (`core/`)
   - Business logic
   - Service orchestration
   - Domain rules

3. **Repository Layer** (`repositories/`)
   - Data access abstraction
   - Database operations
   - Caching logic

4. **Model Layer** (`models/`)
   - Database models
   - Domain models
   - Type definitions

## Deployment

### Local Containers

```bash
# Build and run all services
podman-compose up -d

# Build and run specific service
podman-compose up -d character_service
```

### Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n dnd-services
```

## Monitoring

The service exposes metrics at `/metrics` for Prometheus, including:
- Request counts and latencies
- Database operation metrics
- Cache hit/miss rates
- Character creation/update rates
- Integration metrics (LLM, Campaign, etc.)

Grafana dashboards are available in `monitoring/dashboards/`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
