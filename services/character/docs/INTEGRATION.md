# Character Service Integration Patterns

Version: 1.0
Status: Active
Last Updated: 2025-08-31

## Overview

This document describes the integration patterns for the Character Service, focusing on service-to-service communication, event handling, and cross-service feature coordination.

## API Version

The service implements v2 of the API as specified in the ICD/SRD documents. All endpoints are prefixed with `/api/v2/`.
## Service Communication

### Message Hub Integration

All service-to-service communication flows through the Message Hub:

1. Event Publishing
```python
await message_hub.publish("character.created", {
    "character_id": "uuid",
    "timestamp": "iso8601",
    "details": {}
})
```

2. Event Subscription
```python
@message_hub.subscribe("campaign.theme_changed")
async def handle_theme_change(data: dict):
    campaign_id = data["campaign_id"]
    new_theme = data["new_theme"]
    # Handle theme change
```

### Event Patterns

#### Character Creation Flow
1. Client requests character creation
2. Service creates character
3. Service publishes `character.created`
4. Campaign service handles event
5. LLM service generates content
6. Service updates character with generated content
7. Service publishes `character.updated`

#### Evolution Flow
1. Client requests evolution
2. Service validates request
3. Service publishes `character.evolving`
4. LLM service generates changes
5. Service applies changes
6. Service publishes `character.evolved`
7. Campaign service updates state

#### Antitheticon System Flow
1. Client requests Antitheticon creation
2. Service analyzes party
3. Service requests LLM generation
4. Service creates Antitheticon
5. Service publishes `antitheticon.created`
6. Campaign service integrates opposition

## Cross-Service Features

### Campaign Integration

1. Theme Integration
```json
{
    "theme": "string",
    "elements": ["string"],
    "restrictions": ["string"],
    "style_guide": {}
}
```

2. Character Validation
```json
{
    "character_id": "uuid",
    "campaign_id": "uuid",
    "validation_type": "creation|evolution|custom",
    "validation_data": {}
}
```

### LLM Integration

1. Content Generation
```json
{
    "generation_type": "backstory|description|dialogue",
    "context": {},
    "constraints": [],
    "style": "string"
}
```

2. Theme Adaptation
```json
{
    "content": "string",
    "source_theme": "string",
    "target_theme": "string",
    "preserve_elements": ["string"]
}
```

## Performance Considerations

1. Caching Strategy
- Cache party analysis results
- Cache theme-specific generations
- Cache common inventory queries

2. Batch Operations
- Group minor updates
- Batch inventory changes
- Combine evolution steps

3. Async Processing
- Non-blocking LLM operations
- Background state updates
- Delayed consistency updates

## Error Handling

1. Transient Failures
```json
{
    "error": "TEMPORARY_FAILURE",
    "retry_after": "seconds",
    "context": {}
}
```

2. Validation Failures
```json
{
    "error": "VALIDATION_ERROR",
    "details": ["string"],
    "suggestions": ["string"]
}
```

3. Integration Failures
```json
{
    "error": "INTEGRATION_ERROR",
    "service": "string",
    "context": {},
    "fallback_applied": "boolean"
}
```

## Monitoring

1. Key Metrics
- Request latency
- Integration success rate
- Cache hit rate
- Event processing time
- Error rates by type

2. Health Checks
```http
GET /health
```
```json
{
    "status": "healthy|degraded|unhealthy",
    "integrations": {
        "message_hub": "status",
        "llm_service": "status",
        "campaign_service": "status"
    },
    "metrics": {}
}
```

## Security

1. Authentication
- JWT validation
- Service-to-service auth
- Role-based access

2. Authorization
- Feature-level permissions
- Campaign-specific roles
- DM approval flows

## Testing

1. Integration Tests
```bash
pytest tests/integration/
```

2. Performance Tests
```bash
pytest tests/performance/
```

3. Coverage Report
```bash
pytest --cov=src --cov-report=html
```
