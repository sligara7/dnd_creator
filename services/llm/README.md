# D&D Character Creator LLM Service

AI-powered text and image generation service for the D&D Character Creator application.

## Quick Start

### Using Podman (Recommended)

1. **Build the container:**
   ```bash
   podman build -t dnd-llm-service .
   ```

2. **Run with environment variables:**
   ```bash
   podman run -d \
     --name dnd-llm-service \
     -p 8100:8000 \
     --network dnd_network \
     -e OPENAI_API_KEY="your-openai-api-key" \
     -e GETIMG_API_KEY="your-getimg-api-key" \
     -e MESSAGE_HUB_URL="http://message_hub:8200" \
     -e SECRET_KEY="your-64-char-secret-key" \
     -e REDIS_URL="redis://redis:6379/0" \
     dnd-llm-service
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8100/docs
   - Health Check: http://localhost:8100/health

### Local Development

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run the service:**
   ```bash
   poetry run uvicorn llm_service.main:app --reload
   ```

## Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `GETIMG_API_KEY`: Your GetImg.AI API key
- `SECRET_KEY`: A secure secret for JWT tokens (64+ characters)

## Optional Environment Variables

- `MESSAGE_HUB_URL`: URL of the Message Hub service (default: http://message_hub:8200)
- `REDIS_URL`: Redis connection string (default: redis://redis:6379/0)
- `LOG_LEVEL`: `INFO` (default), `DEBUG`, `WARNING`, `ERROR`
- `OPENAI_REQUEST_TIMEOUT`: OpenAI API timeout in seconds (default: 30)
- `GETIMG_REQUEST_TIMEOUT`: GetImg.AI API timeout in seconds (default: 60)

## Production Deployment

The container is optimized for rootless Podman deployment with:
- Non-root user execution
- Minimal attack surface
- Health checks
- Proper logging
- Rate limiting and caching
- Token usage tracking

## Architecture

### Core Components
- **FastAPI**: Modern async web framework
- **Redis**: Caching and rate limiting
- **Pydantic**: Data validation and serialization
- **OpenAI Client**: Text generation with GPT-4
- **GetImg.AI Client**: Image generation and manipulation

### Service Integration
- **Message Hub Client**: Communication with other services
- Character content generation for Character Service
- Campaign content generation for Campaign Service
- Portrait and map generation for Image Service

### Caching and Rate Limiting
- Redis-based caching system
- Configurable rate limits:
  * Text generation: 100 requests/minute
  * Image generation: 50 requests/minute
- Token usage tracking
- Request deduplication

## API Endpoints

### Text Generation
- `POST /api/v2/text/character`: Generate character content
- `POST /api/v2/text/campaign`: Generate campaign content
- `POST /api/v2/text/theme`: Apply theme to text content

### Image Generation
- `POST /api/v2/image/generate`: Text-to-image generation
- `POST /api/v2/image/transform`: Image-to-image transformation
- `POST /api/v2/image/enhance`: Image enhancement and style transfer

### Queue Management
- `GET /api/v2/queue/status`: View queue status
- `POST /api/v2/queue/prioritize`: Prioritize request
- `DELETE /api/v2/queue/{job_id}`: Cancel request

## Service Communication

### Outbound Events
- Generated text content completion
- Generated image completion
- Queue status updates
- Rate limit notifications

### Inbound Requests
- Character content generation
- Campaign content generation
- Portrait and map generation
- Theme application requests

## Error Handling

- Automatic retries with exponential backoff
- Model fallback strategy:
  * GPT-4 → GPT-3.5-turbo
- Detailed error reporting
- Rate limit handling
- Quota management

## Health and Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- Structured logging with JSON output
- Service registration with Message Hub
- API usage analytics
