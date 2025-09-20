# D&D Character Creator Image Service

Streamlined image storage and retrieval service for the D&D Character Creator application. This service integrates with the Storage Service via Message Hub for image persistence and management.

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
     -e MESSAGE_HUB_URL="amqp://message_hub:5672" \
     -e STORAGE_SERVICE_URL="http://storage:8000" \
     dnd-image-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8002/docs
   - Health Check: http://localhost:8002/health

## Required Environment Variables

- `MESSAGE_HUB_URL`: Message Hub AMQP URL
- `STORAGE_SERVICE_URL`: Storage Service URL

## Optional Environment Variables

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
- **Pydantic**: Data validation and serialization
- **aio-pika**: Async AMQP client for Message Hub

### Service Integration
- **Message Hub Client**: Service communication
  - Event-based messaging
  - Request/response correlation
  - Automatic reconnection
  - Error handling

- **Storage Service Client**: Asset management via Message Hub
  - Image persistence
  - Metadata management
  - Theme-aware storage
  - Content delivery

## Core Features

### Image Storage
- Secure image upload
- Theme-aware organization
- Metadata management
- Content type validation

### Image Retrieval
- Direct image access
- Filtered image listing
- Theme-based searching
- Metadata querying

## Service Communication

### Message Hub Events
- `storage.request`: Operations on images
- `storage.response`: Operation responses

## Theme Support
Theme information is preserved and stored with images for consistent organization and retrieval.

## Health and Monitoring

- Health endpoint: `/health`
  - Service status
  - Message Hub status
  - Storage service status
- Prometheus metrics:
  - Storage operations
  - Message Hub events
  - Error rates
  - API latency
- Structured JSON logging

## Performance Targets

- Storage operations: < 100ms
- Image upload: < 2s for 5MB
- List operations: < 50ms
- API response time: < 100ms
