# D&D Character Creator Campaign Service

Campaign and party management service for the D&D Character Creator application.

## Quick Start

### Using Podman (Recommended)

1. **Build the container:**
   ```bash
   podman build -t dnd-campaign-service .
   ```

2. **Run with environment variables:**
   ```bash
   podman run -d \
     --name dnd-campaign-service \
     -p 8001:8000 \
     --network dnd_network \
     -e MESSAGE_HUB_URL="http://message_hub:8200" \
     -e SECRET_KEY="your-64-char-secret-key" \
     dnd-campaign-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

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
- Campaign content generation through LLM Service
- Campaign maps and tokens through Image Service
- Character data from Character Service

### Database
- Independent PostgreSQL database for campaign data
- Git-like version control for campaign changes
- Async/await database operations

## Service Communication

### Outbound Messages
- Campaign content generation requests to LLM Service
- Map and token requests to Image Service
- Character data requests to Character Service

### Inbound Messages
- Character updates from Character Service
- Map and token generation status from Image Service

## Git-like Campaign Version Control

- Campaign state snapshots
- Branch support for alternate storylines
- Merge capability for storyline integration
- Revert support for undoing changes

## Health and Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- Structured logging with JSON output
- Service registration with Message Hub
