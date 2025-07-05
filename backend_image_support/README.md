# D&D Character Creator Backend

Production-ready backend API service for the D&D Character Creator application.

## Quick Start

### Using Podman (Recommended)

1. **Build the container:**
   ```bash
   podman build -t dnd-char-creator .
   ```

2. **Run with environment variables:**
   ```bash
   podman run -d \
     --name dnd-char-creator \
     -p 8000:8000 \
     -e OPENAI_API_KEY="your-openai-api-key" \
     -e SECRET_KEY="your-64-char-secret-key" \
     dnd-char-creator
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for character generation
- `SECRET_KEY`: A secure secret for JWT tokens (64+ characters)

## Optional Environment Variables

- `LLM_PROVIDER`: `openai` (default) or `anthropic`
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

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Database ORM with async support
- **Pydantic**: Data validation and serialization
- **OpenAI**: LLM integration for character generation

## Health and Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics` (if enabled)
- Structured logging with JSON output
