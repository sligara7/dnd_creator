# D&D Character Creator Character Service

Core character creation and management service for the D&D Character Creator application.

## Quick Start

### Using Podman (Recommended)

1. **Build the container:**
   ```bash
   podman build -t dnd-character-service .
   ```

2. **Run with environment variables:**
   ```bash
   podman run -d \
     --name dnd-character-service \
     -p 8000:8000 \
     --network dnd_network \
     -e MESSAGE_HUB_URL="http://message_hub:8200" \
     -e SECRET_KEY="your-64-char-secret-key" \
     dnd-character-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Required Environment Variables

- `SECRET_KEY`: A secure secret for JWT tokens (64+ characters)

## Optional Environment Variables

- `MESSAGE_HUB_URL`: URL of the Message Hub service (default: http://message_hub:8200)
- `DATABASE_URL`: PostgreSQL connection string (uses SQLite by default)
- `LOG_LEVEL`: `INFO` (default), `DEBUG`, `WARNING`, `ERROR`

## Production Deployment

The container is optimized for rootless Podman deployment with:
- Non-root user execution
- Minimal attack surface
- Health checks
- Proper logging
- Volume support for data persistence

## Architecture

### Core Components
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Database ORM with async support
- **Pydantic**: Data validation and serialization

### Service Integration
- **Message Hub Client**: Communication with other services
- Character generation requests routed through Message Hub to LLM Service
- Character portraits requested through Image Service

### Database
- Independent PostgreSQL database for character data
- Migration support through Alembic
- Async/await database operations

## Service Communication

### Outbound Messages
- Character generation requests to LLM Service
- Portrait generation requests to Image Service
- Campaign integration with Campaign Service

### Inbound Messages
- Character data requests from Campaign Service
- Status updates from Image Service

## Health and Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- Structured logging with JSON output
- Service registration with Message Hub
