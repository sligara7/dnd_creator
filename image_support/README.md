# D&D Character Creator Image Service

Image generation and management service for the D&D Character Creator application.

## Quick Start

### Using Podman (Recommended)

1. **Build the container:**
   ```bash
   podman build -t dnd-image-service .
   ```

2. **Run with environment variables:**
   ```bash
   podman run -d \
     --name dnd-image-service \
     -p 8002:8000 \
     --network dnd_network \
     --gpus all \
     -e MESSAGE_HUB_URL="http://message_hub:8200" \
     -e SECRET_KEY="your-64-char-secret-key" \
     dnd-image-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8002/docs
   - Health Check: http://localhost:8002/health

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
- GPU support for image generation

## Architecture

### Core Components
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Database ORM with async support
- **Pydantic**: Data validation and serialization

### Service Integration
- **Message Hub Client**: Communication with other services
- Image generation prompts through LLM Service
- Image generation through Stable Diffusion

### Database
- Independent PostgreSQL database for image metadata
- Binary storage for generated images
- Async/await database operations

## Image Generation Features

### Character Portraits
- Character portrait generation
- Token generation for VTTs
- Style consistency control
- Image history and versioning

### Campaign Maps
- Battle map generation
- World map generation
- Location-specific map styles
- Map overlay support

## Service Communication

### Outbound Messages
- Image generation prompts to LLM Service
- Generated image notifications

### Inbound Messages
- Portrait requests from Character Service
- Map requests from Campaign Service

## Resource Management

- GPU utilization monitoring
- Image generation queue
- Resource allocation strategies
- Cache management for common requests

## Health and Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- GPU status monitoring
- Service registration with Message Hub
