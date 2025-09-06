# LLM Service API Examples

This document provides example requests and responses for the LLM Service API endpoints.

## Text Generation

### Generate Character Content

```http
POST /api/v2/text/character
Content-Type: application/json
Authorization: Bearer <token>

{
  "type": "backstory",
  "character_context": {
    "character_class": "Paladin",
    "character_race": "Dragonborn",
    "character_level": 5,
    "alignment": "Lawful Good",
    "background": "Noble"
  },
  "theme": {
    "genre": "high fantasy",
    "tone": "heroic",
    "style": "epic"
  },
  "model": {
    "name": "gpt-4-turbo",
    "temperature": 0.8
  }
}
```

```json
{
  "content": "Born to the prestigious Silverclaw clan...",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "content_type": "character",
    "model_used": "gpt-4-turbo",
    "token_usage": {
      "prompt_tokens": 250,
      "completion_tokens": 500,
      "total_tokens": 750
    }
  }
}
```

## Campaign Content

### Generate Story Content

```http
POST /api/v2/campaign/story
Content-Type: application/json
Authorization: Bearer <token>

{
  "element_type": "plot",
  "context": {
    "campaign_theme": "Epic Fantasy",
    "party_level": 5,
    "party_size": 4,
    "campaign_type": "sandbox",
    "setting": "Forgotten Realms",
    "length": "long"
  },
  "parameters": {
    "focus": "political intrigue",
    "complexity": "high"
  }
}
```

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174001",
  "element_type": "plot",
  "content": "In the bustling city-state of Waterdeep...",
  "summary": "A tale of political intrigue and power...",
  "metadata": {
    "model_used": "gpt-4-turbo",
    "token_usage": {
      "prompt_tokens": 300,
      "completion_tokens": 800,
      "total_tokens": 1100
    }
  }
}
```

### Generate NPC

```http
POST /api/v2/campaign/npc
Content-Type: application/json
Authorization: Bearer <token>

{
  "role": "quest_giver",
  "context": {
    "campaign_theme": "Dark Fantasy",
    "party_level": 7,
    "party_size": 5,
    "campaign_type": "linear",
    "setting": "Ravenloft",
    "length": "medium"
  },
  "traits": {
    "personality": "mysterious",
    "motivation": "revenge"
  }
}
```

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174002",
  "name": "Lord Viktor Drakeheart",
  "role": "quest_giver",
  "description": "A tall, imposing figure...",
  "personality": "Mysterious and brooding...",
  "motivations": [
    "Seek revenge against those who destroyed his family",
    "Restore his ancestral home"
  ],
  "secrets": [
    "Actually a vampire",
    "Knows the true location of the artifact"
  ],
  "metadata": {
    "model_used": "gpt-4-turbo",
    "token_usage": {
      "prompt_tokens": 200,
      "completion_tokens": 400,
      "total_tokens": 600
    }
  }
}
```

## Theme Analysis

### Analyze Content Theme

```http
POST /api/v2/theme/analyze
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "A heroic tale of adventure and discovery in a mystical land.",
  "elements": ["tone", "mood", "setting"],
  "category_filter": ["fantasy"],
  "current_theme": {
    "genre": "fantasy",
    "tone": "light",
    "style": "adventurous"
  },
  "target_theme": {
    "genre": "dark fantasy",
    "tone": "grim",
    "style": "gothic"
  }
}
```

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174003",
  "primary_category": "fantasy",
  "secondary_categories": ["adventure"],
  "category_confidence": 0.95,
  "elements": [
    {
      "element": "tone",
      "score": 0.8,
      "description": "Light and optimistic tone...",
      "suggestions": [
        "Add darker elements",
        "Increase tension"
      ]
    }
  ],
  "compatibility": {
    "score": 0.6,
    "conflicts": [
      "Tone mismatch between light adventure and dark theme",
      "Style clash between adventurous and gothic elements"
    ],
    "transition_steps": [
      "Gradually introduce darker elements",
      "Shift descriptive language to gothic style"
    ]
  },
  "metadata": {
    "model_used": "gpt-4-turbo",
    "token_usage": {
      "prompt_tokens": 150,
      "completion_tokens": 350,
      "total_tokens": 500
    }
  }
}
```

## Content Validation

### Validate Content

```http
POST /api/v2/validation/content
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "A lighthearted story about friendship.",
  "content_type": "quest",
  "rules": [
    {
      "category": "theme",
      "name": "tone_consistency",
      "is_required": true
    },
    {
      "category": "quality",
      "name": "content_quality",
      "is_required": true
    }
  ],
  "theme": {
    "genre": "comedy",
    "tone": "light",
    "style": "whimsical"
  }
}
```

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174004",
  "overall_score": 0.85,
  "passed": true,
  "results": [
    {
      "rule_id": "123e4567-e89b-12d3-a456-426614174005",
      "passed": true,
      "score": 0.9,
      "issues": []
    },
    {
      "rule_id": "123e4567-e89b-12d3-a456-426614174006",
      "passed": true,
      "score": 0.8,
      "issues": [
        {
          "severity": "info",
          "message": "Consider adding more descriptive details",
          "suggestions": [
            "Include sensory descriptions",
            "Add character reactions"
          ]
        }
      ]
    }
  ],
  "summary": "Content passes all required validations with minor improvement suggestions",
  "metadata": {
    "model_used": "gpt-4-turbo",
    "token_usage": {
      "prompt_tokens": 100,
      "completion_tokens": 200,
      "total_tokens": 300
    }
  }
}
```

## Error Responses

### Rate Limit Exceeded

```json
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded for text generation",
  "details": {
    "limit": 100,
    "window": "60 seconds",
    "retry_after": "30 seconds"
  }
}
```

### Invalid Request

```json
{
  "code": "INVALID_REQUEST",
  "message": "Invalid request parameters",
  "details": {
    "field": "character_level",
    "error": "Value must be between 1 and 20"
  }
}
```

### Validation Error

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Content validation failed",
  "details": {
    "rule": "tone_consistency",
    "error": "Content tone does not match theme requirements"
  }
}
```
