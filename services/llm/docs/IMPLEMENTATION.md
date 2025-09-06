# LLM Service Implementation Guide

## Overview

The LLM (Language Learning Model) Service is a core component of the D&D Character Creator system, providing AI-powered text and image generation capabilities. It integrates with OpenAI for narrative content and GetImg.AI for visual content generation.

## Architecture

### Service Organization

```
services/llm/
├── src/
│   └── llm_service/
│       ├── api/             # FastAPI endpoints
│       ├── core/            # Core infrastructure
│       ├── models/          # Database models
│       ├── schemas/         # Pydantic models
│       └── services/        # Business logic
├── tests/
│   ├── core/               # Unit tests
│   ├── integration/        # Integration tests
│   └── performance/        # Performance tests
└── docs/                   # Documentation
```

### Core Components

1. **API Layer (`api/`)**
   - REST endpoints using FastAPI
   - Request/response handling
   - Input validation
   - Error handling

2. **Core Infrastructure (`core/`)**
   - Configuration management
   - Database setup
   - Caching (Redis)
   - Rate limiting
   - Exception handling
   - Metrics collection

3. **Service Layer (`services/`)**
   - Content generation logic
   - Theme management
   - Validation system
   - External service integration (OpenAI, GetImg.AI)

4. **Data Layer (`models/`)**
   - SQLAlchemy models
   - Database operations
   - Data validation

## Features

### Text Generation
- Character content (backstories, personalities, etc.)
- Campaign content (plots, locations, NPCs)
- Theme-aware generation
- Content validation

### Image Generation
- Character portraits
- Location visualizations
- Item illustrations
- Style transfer
- Image enhancement

### Theme Management
- Theme application
- Style consistency
- Cross-content alignment
- Theme validation

### Content Validation
- Quality checks
- Theme consistency
- D&D rule compliance
- Error detection

## Integration

### Message Hub Integration
All inter-service communication happens through the Message Hub:

1. **Events Published**
   - `text_generated`
   - `image_generated`
   - `theme_applied`
   - `content_validated`

2. **Events Consumed**
   - `character_created`
   - `campaign_updated`
   - `theme_changed`

### Dependencies
- Message Hub service for events
- Redis for caching and rate limiting
- PostgreSQL for persistence
- OpenAI API for text generation
- GetImg.AI API for image generation

## Extension Points

### Adding New Content Types
1. Define new content type in `models/content.py`
2. Create prompt template in `services/prompts/`
3. Implement generation logic in `services/`
4. Add API endpoint in `api/`
5. Update OpenAPI schema
6. Add tests

### Adding New Theme Types
1. Define theme in `models/theme.py`
2. Add theme handling in `services/theme.py`
3. Update validation rules
4. Add tests

### Custom Validation Rules
1. Add rule in `services/validation.py`
2. Define validation logic
3. Update validation pipeline
4. Add tests

## Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- OpenAI API key
- GetImg.AI API key

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install
```

### Configuration
Create `.env` file with required settings:
```env
# Service config
SERVICE_NAME=llm_service
VERSION=0.1.0
DEBUG=false
LOG_LEVEL=INFO

# API config
HOST=0.0.0.0
PORT=8100
WORKERS=4

# Database config
POSTGRES_HOST=llm_db
POSTGRES_PORT=5432
POSTGRES_DB=llm_db
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=llm_pass

# Redis config
REDIS_HOST=llm_cache
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# OpenAI config
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-nano
OPENAI_MAX_TOKENS=8000

# GetImg config
GETIMG_API_KEY=your_key_here
```

### Running the Service

#### Development
```bash
# Run with auto-reload
poetry run uvicorn llm_service.main:app --reload

# Run tests
poetry run pytest

# Run specific test file
poetry run pytest path/to/test_file.py -v

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

#### Production
```bash
# Using Docker
docker build -t llm_service .
docker run -d \
  --name llm_service \
  -p 8100:8100 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e GETIMG_API_KEY="${GETIMG_API_KEY}" \
  llm_service

# Using Docker Compose
docker-compose up -d
```

### Performance Tuning

#### Memory Usage
- Adjust `OPENAI_MAX_TOKENS` based on usage
- Configure Redis cache size
- Set appropriate database connection pool size

#### Response Times
Target response times:
- Text generation: < 5 seconds
- Image generation: < 30 seconds
- Content validation: < 2 seconds
- Theme application: < 15 seconds

#### Rate Limits
Default limits:
- Text generation: 100 requests/minute
- Image generation: 10 requests/minute
- Cache TTL: 1 hour

## Monitoring

### Health Checks
Endpoint: `/health`
```json
{
  "status": "healthy",
  "components": {
    "openai": "healthy",
    "getimg_ai": "healthy",
    "message_hub": "healthy",
    "database": "healthy",
    "cache": "healthy"
  }
}
```

### Metrics
Endpoint: `/metrics/detailed`
- Request counts
- Response times
- Error rates
- Cache hit rates
- Resource usage
- Rate limit status

### Logging
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

Log levels:
- DEBUG: Detailed debugging
- INFO: General information
- WARNING: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical conditions

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Verify request format
   - Check rate limits
   - Review token usage

2. **Image Generation Failures**
   - Verify GetImg.AI API status
   - Check image specifications
   - Validate input formats
   - Monitor resource usage

3. **Rate Limiting**
   - Check current limits
   - Monitor usage patterns
   - Adjust limits if needed
   - Implement retries

4. **Cache Issues**
   - Verify Redis connection
   - Check memory usage
   - Monitor eviction rate
   - Adjust TTL settings

5. **Database Issues**
   - Check connection pool
   - Monitor query performance
   - Review error logs
   - Verify indexes

### Debug Tools
```bash
# Check service status
curl http://localhost:8100/health

# View logs
tail -f logs/app.log

# Monitor metrics
curl http://localhost:8100/metrics/detailed

# Test rate limits
./scripts/test_rate_limits.py

# Generate test load
./scripts/run_performance_tests.py
```

## Security

### API Security
- API key authentication
- Rate limiting
- Request validation
- Content filtering
- Error masking

### Data Security
- Input sanitization
- Output validation
- PII protection
- Data encryption
- Access logging

### Environment Security
- Secure settings
- Secret management
- Network isolation
- Resource limits
- Error handling

## Future Enhancements

1. **Content Generation**
   - More content types
   - Enhanced prompts
   - Better validation
   - Style refinement

2. **Performance**
   - Response caching
   - Batch processing
   - Async improvements
   - Resource optimization

3. **Integration**
   - More event types
   - Better coordination
   - Enhanced validation
   - Richer metadata

4. **Monitoring**
   - Enhanced metrics
   - Better logging
   - More analytics
   - Improved debugging
