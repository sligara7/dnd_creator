# D&D Character Creator Image Service

AI-powered image generation and manipulation service for the D&D Character Creator application.

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
     -e GETIMG_API_KEY="your-getimg-api-key" \
     -e MESSAGE_HUB_URL="http://message_hub:8200" \
     -e REDIS_HOST="redis" \
     -e POSTGRES_SERVER="db" \
     -e POSTGRES_USER="dnd" \
     -e POSTGRES_PASSWORD="your-db-password" \
     -e POSTGRES_DB="dnd_image" \
     dnd-image-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8002/docs
   - Health Check: http://localhost:8002/health

## Required Environment Variables

- `GETIMG_API_KEY`: API key for GetImg.AI
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## Optional Environment Variables

- `MESSAGE_HUB_URL`: Message Hub service URL (default: http://message_hub:8200)
- `GETIMG_API_URL`: GetImg.AI API URL (default: https://api.getimg.ai/v1)
- `POSTGRES_SERVER`: PostgreSQL server (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `REDIS_HOST`: Redis server (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (optional)
- `LOG_LEVEL`: `INFO` (default), `DEBUG`, `WARNING`, `ERROR`

## Production Deployment

The container is optimized for rootless Podman deployment with:
- Non-root user execution
- Minimal attack surface
- Health checks
- Proper logging
- Volume support for asset persistence

## Architecture

### Core Components
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Database ORM with async support
- **Pydantic**: Data validation and serialization
- **aio-pika**: Async AMQP client for Message Hub
- **Redis**: Caching and queue management

### Service Integration
- **GetImg.AI Client**: AI image generation
- **Message Hub Client**: Service communication
- **Storage Service**: Asset management
- **Redis Cache**: Performance optimization

### Database
- Independent PostgreSQL database for image metadata
- Version control for image assets
- Queue management for generation tasks
- Theme and style configuration storage

## Image Generation Features

### Map Generation
- Tactical battle maps with grid support
- Campaign maps with points of interest
- Terrain and feature generation
- Theme-aware visual styles

### Character Visualization
- Character portraits from descriptions
- Equipment visualization
- Theme-appropriate styling
- Pose and background variations

### Item Illustration
- Weapon and armor visualization
- Magical item effects
- Material and quality representation
- Theme-consistent styling

### Overlay System
- Tactical position markers
- Range and effect areas
- Territory control visualization
- Travel route mapping

## Service Communication

### Outbound Events
- `image_generated`: New image creation
- `overlay_updated`: Overlay modifications
- `theme_applied`: Theme application

### Inbound Events
- `character_updated`: Character appearance changes
- `campaign_theme_changed`: Theme updates
- `map_state_changed`: Map overlay updates

## Theme System

### Visual Themes
- Fantasy (traditional)
- Western
- Cyberpunk
- Steampunk
- Horror
- Space Fantasy

### Style Elements
- Architecture design
- Clothing styles
- Technology level
- Environmental features
- Color schemes
- Lighting effects

## Health and Monitoring

- Health endpoint: `/health`
  - Service status
  - Dependency checks
  - Queue metrics
- Structured JSON logging
- Generation pipeline metrics
- Cache performance tracking

## Performance Targets

- Map generation: < 30 seconds
- Character portraits: < 15 seconds
- Item illustrations: < 10 seconds
- Overlay application: < 1 second
- Cache hit rate: > 90%
