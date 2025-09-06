# API Gateway Service

The API Gateway serves as the unified entry point for all client requests in the D&D Character Creator system. It provides authentication, routing, rate limiting, and monitoring capabilities.

## Features

- Single entry point for all client requests
- Secure authentication and authorization
- Traffic management and rate limiting
- Service discovery and routing
- Comprehensive monitoring and logging
- Health checking and circuit breaking

## Architecture

The API Gateway is built using:

- **Traefik v2**: Edge router and load balancer
- **FastAPI**: Service implementation and API
- **Message Hub Integration**: Inter-service communication
- **Prometheus**: Metrics and monitoring
- **Structured Logging**: Request and error tracking

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Poetry for dependency management

### Installation

1. Set up the Python environment:
   ```bash
   # Install dependencies
   poetry install

   # Activate virtual environment
   poetry shell
   ```

2. Configure environment variables:
   ```bash
   # Create .env file
   cp .env.example .env

   # Edit configuration
   nano .env
   ```

3. Start the service:
   ```bash
   # Start with Docker Compose
   docker-compose up -d

   # Or run locally
   poetry run uvicorn src.api_gateway.main:app --reload
   ```

### Configuration

The service is configured through:

1. **Traefik Configuration**:
   - `config/traefik.yml`: Static configuration
   - `config/dynamic.yml`: Dynamic routing rules

2. **Environment Variables**:
   - `AUTH_SERVICE_URL`: Auth service endpoint
   - `MESSAGE_HUB_URL`: Message Hub endpoint

## API Documentation

### Core Endpoints

1. **Service Discovery**
   ```http
   POST /discovery/register    # Register a service
   GET /discovery/services     # List registered services
   GET /discovery/health       # System health status
   ```

2. **Monitoring**
   ```http
   GET /monitoring/metrics    # Prometheus metrics
   GET /monitoring/health     # Gateway health status
   ```

3. **Authentication**
   ```http
   # Include in requests:
   Authorization: Bearer <token>
   X-API-Key: <api_key>
   ```

### Routing Rules

Services are routed based on path prefixes:

- `/api/v2/characters/*` → Character Service
- `/api/v2/campaigns/*` → Campaign Service
- `/api/v2/images/*` → Image Service

## Security

The API Gateway implements multiple security layers:

1. **Authentication**:
   - JWT token validation
   - API key authentication
   - Role-based access control

2. **Traffic Management**:
   - Rate limiting per client
   - Circuit breaking
   - Request throttling

3. **TLS/Security**:
   - HTTPS enforcement
   - Security headers
   - CORS configuration

## Monitoring

### Metrics

Prometheus metrics are available at `/monitoring/metrics`, including:

- Request counts and latencies
- Error rates and types
- Service health status
- Circuit breaker states
- Authentication failures

### Logging

Structured logging includes:

- Request/response details
- Error tracking
- Performance metrics
- Security events
- Health status changes

## Health Checking

Health checks are performed at multiple levels:

1. **Gateway Health**:
   - Internal component status
   - Dependencies health
   - Resource utilization

2. **Service Health**:
   - Regular health probes
   - Response time tracking
   - Error rate monitoring
   - Circuit breaker status

## Development

### Code Organization

```
services/api_gateway/
├── src/
│   └── api_gateway/
│       ├── middleware/     # Auth, rate limiting
│       ├── monitoring/     # Metrics, logging
│       ├── routers/        # API routes
│       └── services/       # Business logic
├── config/                 # Traefik config
├── tests/                 # Test suites
└── docker-compose.yml     # Deployment config
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_auth.py
```

### Local Development

```bash
# Start Traefik
docker-compose up traefik -d

# Run the service
poetry run uvicorn src.api_gateway.main:app --reload
```

## Contributing

1. Create a feature branch
2. Implement changes
3. Add tests
4. Submit pull request

## License

[License Information]
