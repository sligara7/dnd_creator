# LLM Service

This service provides AI-powered text and image generation for the D&D Character Creator system, utilizing OpenAI for narrative content and GetImg.AI for visual content.

## Core Features
- Text generation via OpenAI (GPT-4, GPT-3.5-turbo, Claude 3)
- Image generation via GetImg.AI
- Theme management and content consistency
- Cross-service integration via Message Hub
- Advanced caching and rate limiting
- Comprehensive monitoring and metrics

## Requirements
- Python 3.11+
- Poetry
- Redis
- PostgreSQL

## Local Development
1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the service:
   ```bash
   poetry run uvicorn llm_service.main:app --reload
   ```

## API Documentation
Once running, visit:
- OpenAPI docs: http://localhost:8100/docs
- ReDoc: http://localhost:8100/redoc
