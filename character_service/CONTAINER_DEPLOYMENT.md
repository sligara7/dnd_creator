# D&D Character Creator - Container Deployment Guide

## Environment Variables Required

The D&D Character Creator backend requires several environment variables to be provided from the host system. **No API keys or secrets are stored in the container image or files.**

### Required Environment Variables

1. **OPENAI_API_KEY** - Your OpenAI API key for character generation
2. **SECRET_KEY** - A secure secret key for JWT token generation (generate a random 64-character string)

### Optional Environment Variables

- **ANTHROPIC_API_KEY** - If using Anthropic instead of OpenAI
- **DATABASE_URL** - For PostgreSQL (defaults to SQLite)
- **LLM_MODEL** - Override the default model
- **LOG_LEVEL** - Set logging level (default: INFO)

## Running with Podman

### Basic Usage
```bash
podman run -d \
  --name dnd-character-creator \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-actual-openai-api-key" \
  -e SECRET_KEY="your-64-character-random-secret-key" \
  dnd-character-creator:latest
```

### With Volume for Data Persistence
```bash
podman run -d \
  --name dnd-character-creator \
  -p 8000:8000 \
  -v dnd-data:/app/data \
  -e OPENAI_API_KEY="your-actual-openai-api-key" \
  -e SECRET_KEY="your-64-character-random-secret-key" \
  dnd-character-creator:latest
```

### Using Environment File
Create a file `secrets.env` on the host:
```env
OPENAI_API_KEY=your-actual-openai-api-key
SECRET_KEY=your-64-character-random-secret-key
```

Then run:
```bash
podman run -d \
  --name dnd-character-creator \
  -p 8000:8000 \
  --env-file secrets.env \
  dnd-character-creator:latest
```

### Production Deployment
For production, use podman-compose with environment variables stored securely:

```yaml
# podman-compose.yml
version: '3.8'
services:
  dnd-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ENV=production
    volumes:
      - dnd-data:/app/data
    restart: unless-stopped

volumes:
  dnd-data:
```

## Security Notes

- **Never commit API keys to version control**
- **Never include API keys in container images**
- The container image contains no secrets or API keys
- All sensitive data must be provided via host environment variables
- Use secure methods to manage environment variables in production (e.g., HashiCorp Vault, Kubernetes secrets, etc.)

## Generating a Secure Secret Key

```bash
# Generate a random 64-character secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Health Check

The container includes a health check endpoint:
```bash
curl http://localhost:8000/health
```

## Logs

View container logs:
```bash
podman logs dnd-character-creator
```
