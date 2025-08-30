# Interface Control Document: LLM Service (ICD-LLM-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Service Interface

### 1.1 Base URL
```
http://llm-service:8100
```

### 1.2 Common Headers
```
X-Request-ID: <uuid>
Content-Type: application/json
Authorization: Bearer <token>
```

## 2. Text Generation API

### 2.1 Generate Character Content
```http
POST /api/v2/text/character
```

#### Request Body
```json
{
  "type": "backstory|personality|combat|equipment",
  "parameters": {
    "character_class": "string",
    "character_race": "string",
    "character_level": "integer",
    "alignment": "string",
    "background": "string"
  },
  "theme": {
    "genre": "string",
    "tone": "string",
    "style": "string"
  },
  "model": {
    "name": "gpt-4-turbo",
    "temperature": "float",
    "max_tokens": "integer"
  }
}
```

### 2.2 Generate Campaign Content
```http
POST /api/v2/text/campaign
```

#### Request Body
```json
{
  "type": "plot|location|quest|dialogue|event",
  "parameters": {
    "campaign_theme": "string",
    "party_level": "integer",
    "party_size": "integer",
    "duration": "string"
  },
  "theme": {
    "genre": "string",
    "tone": "string",
    "style": "string"
  },
  "model": {
    "name": "gpt-4-turbo",
    "temperature": "float",
    "max_tokens": "integer"
  }
}
```

## 3. Image Generation API

### 3.1 Text to Image Generation
```http
POST /api/v2/image/generate
```

#### Request Body
```json
{
  "prompt": "string",
  "negative_prompt": "string",
  "model": {
    "name": "stable-diffusion-v1-5",
    "cfg_scale": "float",
    "steps": "integer"
  },
  "size": {
    "width": "integer",
    "height": "integer"
  },
  "parameters": {
    "style_preset": "string",
    "seed": "integer"
  }
}
```

### 3.2 Image to Image Generation
```http
POST /api/v2/image/transform
```

#### Request Body
```json
{
  "source_image": "string",
  "prompt": "string",
  "negative_prompt": "string",
  "model": {
    "name": "stable-diffusion-v1-5",
    "cfg_scale": "float",
    "steps": "integer"
  },
  "parameters": {
    "style_preset": "string",
    "strength": "float",
    "seed": "integer"
  }
}
```

### 3.3 Image Enhancement
```http
POST /api/v2/image/enhance
```

#### Request Body
```json
{
  "image": "string",
  "enhancements": ["upscale", "face_fix"],
  "parameters": {
    "upscale_factor": "integer",
    "face_restore_model": "string",
    "quality": "string"
  }
}
```

## 4. Theme Management API

### 4.1 Text Theme Application
```http
POST /api/v2/theme/text
```

#### Request Body
```json
{
  "content": "string",
  "theme": {
    "genre": "string",
    "tone": "string",
    "style": "string"
  },
  "parameters": {
    "strength": "float",
    "preserve_key_elements": "boolean"
  }
}
```

### 4.2 Visual Theme Application
```http
POST /api/v2/theme/visual
```

#### Request Body
```json
{
  "image": "string",
  "theme": {
    "style": "string",
    "color_scheme": "string",
    "lighting": "string"
  },
  "parameters": {
    "strength": "float",
    "preserve_composition": "boolean"
  }
}
```

## 5. Queue Management API

### 5.1 Queue Operations
```http
GET /api/v2/queue/status
POST /api/v2/queue/prioritize
DELETE /api/v2/queue/{job_id}
```

#### Queue Status Response
```json
{
  "text_generation": {
    "active": "integer",
    "waiting": "integer",
    "completed": "integer"
  },
  "image_generation": {
    "active": "integer",
    "waiting": "integer",
    "completed": "integer"
  }
}
```

## 6. Message Hub Integration

### 6.1 Events Published
```json
{
  "text_generated": {
    "request_id": "uuid",
    "type": "string",
    "status": "string",
    "metadata": {}
  },
  "image_generated": {
    "request_id": "uuid",
    "type": "string",
    "status": "string",
    "metadata": {}
  }
}
```

### 7.4 Events Published
```json
{
  "character_created": {
    "character_id": "uuid",
    "details": {}
  },
  "campaign_updated": {
    "campaign_id": "uuid",
    "changes": {}
  }
}
```

## 7. Health and Monitoring

### 7.1 Health Check
```http
GET /health
```

#### Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "components": {
    "openai": "healthy",
    "getimg_ai": "healthy",
    "message_hub": "healthy",
    "queue": "healthy"
  },
  "metrics": {
    "text_generation_rate": "float",
    "image_generation_rate": "float",
    "error_rate": "float",
    "queue_length": "integer"
  }
}
```

### 7.2 Detailed Metrics
```http
GET /metrics/detailed
```

#### Response
```json
{
  "generation_metrics": {
    "text": {
      "total_requests": "integer",
      "successful_requests": "integer",
      "failed_requests": "integer",
      "average_latency": "float",
      "p95_latency": "float",
      "p99_latency": "float",
      "token_usage": {
        "prompt_tokens": "integer",
        "completion_tokens": "integer",
        "total_tokens": "integer"
      }
    },
    "image": {
      "total_requests": "integer",
      "successful_requests": "integer",
      "failed_requests": "integer",
      "average_latency": "float",
      "p95_latency": "float",
      "p99_latency": "float",
      "resource_usage": {
        "total_images": "integer",
        "total_modifications": "integer",
        "average_steps": "float"
      }
    }
  },
  "cache_metrics": {
    "hit_rate": "float",
    "miss_rate": "float",
    "eviction_rate": "float",
    "memory_usage": "float"
  },
  "rate_limiting": {
    "text": {
      "current_rate": "float",
      "limit_remaining": "integer",
      "reset_at": "string"
    },
    "image": {
      "current_rate": "float",
      "limit_remaining": "integer",
      "reset_at": "string"
    }
  }
}
```

### 7.3 Prometheus Metrics
```http
GET /metrics
```

#### Response
```json
{
  "request_count": {
    "text": "integer",
    "image": "integer"
  },
  "latencies": {
    "text_p95": "float",
    "image_p95": "float"
  },
  "error_rates": {
    "text": "float",
    "image": "float"
  },
  "quotas": {
    "openai": {
      "remaining": "integer",
      "reset_at": "string"
    },
    "getimg_ai": {
      "remaining": "integer",
      "reset_at": "string"
    }
  }
}
```

## 8. Error Handling

### 8.1 Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "request_id": "string",
      "service": "string",
      "timestamp": "string"
    }
  }
}
```

### 8.2 Common Error Codes
- `TEXT_GENERATION_FAILED`: OpenAI API error
- `IMAGE_GENERATION_FAILED`: GetImg.AI API error
- `INVALID_PROMPT`: Prompt validation failed
- `QUOTA_EXCEEDED`: API quota exceeded
- `THEME_ERROR`: Theme application error
- `QUEUE_FULL`: Processing queue full
- `INVALID_PARAMETERS`: Invalid request parameters
- `SERVICE_UNAVAILABLE`: External service unavailable
