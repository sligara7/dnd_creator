# Interface Control Document: Catalog Service (ICD-CAT-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Communication Architecture

### 1.1 Service Communication Pattern
- All service-to-service communication MUST be routed through the Message Hub service
- No direct HTTP calls between services are permitted
- All integrations must use asynchronous messaging patterns
- All events and requests must include proper correlation IDs

### 1.2 Base URL (API Gateway Access Only)
```http
http://catalog-service:8000  # Only accessible via API Gateway
```

### 1.3 Message Hub Protocol
- Every request/event must include:
  * Correlation ID (for tracing)
  * Source service identifier
  * Request/event type and version
  * Timestamp
  * TTL (time-to-live)

### 1.4 Common Headers
### 1.1 Base URL
```
http://catalog-service:8003
```

### 1.2 Common Headers
```
X-Request-ID: <uuid>
X-Correlation-ID: <uuid>
Content-Type: application/json
Authorization: Bearer <token>
```

## 2. Content Management API

### 2.1 Get Content Item
```http
GET /api/v2/catalog/{type}/{id}
```

#### Response
```json
{
  "id": "uuid",
  "type": "item|spell|monster",
  "name": "string",
  "source": "official|custom",
  "description": "string",
  "properties": {},
  "metadata": {
    "version": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "created_by": "string"
  },
  "theme_data": {
    "themes": ["string"],
    "adaptations": {}
  },
  "validation": {
    "balance_score": "float",
    "consistency_check": "boolean",
    "last_validated": "timestamp"
  }
}
```

### 2.2 Create Content Item
```http
POST /api/v2/catalog/{type}
```

#### Request Body
```json
{
  "name": "string",
  "source": "official|custom",
  "description": "string",
  "properties": {},
  "theme_data": {
    "themes": ["string"]
  }
}
```

### 2.3 Update Content Item
```http
PUT /api/v2/catalog/{type}/{id}
```

#### Request Body
```json
{
  "name": "string",
  "description": "string",
  "properties": {},
  "theme_data": {
    "themes": ["string"]
  }
}
```

### 2.4 Delete Content Item
```http
DELETE /api/v2/catalog/{type}/{id}
```

## 3. Search API

### 3.1 Basic Search
```http
GET /api/v2/catalog/search?q={query}&type={type}&theme={theme}
```

#### Response
```json
{
  "total": "integer",
  "page": "integer",
  "items": [{
    "id": "uuid",
    "type": "string",
    "name": "string",
    "description": "string",
    "highlight": {
      "name": ["string"],
      "description": ["string"]
    }
  }]
}
```

### 3.2 Advanced Search
```http
POST /api/v2/catalog/search/advanced
```

#### Request Body
```json
{
  "query": "string",
  "filters": {
    "types": ["string"],
    "themes": ["string"],
    "properties": {},
    "balance_range": {
      "min": "float",
      "max": "float"
    }
  },
  "sort": {
    "field": "string",
    "order": "asc|desc"
  },
  "page": "integer",
  "size": "integer"
}
```

### 3.3 Recommendations
```http
GET /api/v2/catalog/recommend?character_id={id}&campaign_id={id}
```

#### Response
```json
{
  "recommendations": [
    {
      "id": "uuid",
      "type": "string",
      "name": "string",
      "description": "string",
      "score": "float",
      "reason": "string"
    }
  ]
}
```

## 4. Validation API

### 4.1 Validate Content
```http
POST /api/v2/catalog/validate
```

#### Request Body
```json
{
  "content": {
    "type": "string",
    "properties": {},
    "theme_data": {}
  },
  "context": {
    "campaign_id": "uuid",
    "character_level": "integer"
  }
}
```

#### Response
```json
{
  "valid": "boolean",
  "balance_score": "float",
  "issues": [
    {
      "type": "string",
      "severity": "error|warning",
      "message": "string",
      "suggestions": ["string"]
    }
  ]
}
```

### 4.2 Validation History
```http
GET /api/v2/catalog/validate/history?content_id={id}
```

#### Response
```json
{
  "history": [
    {
      "timestamp": "string",
      "valid": "boolean",
      "balance_score": "float",
      "issues": []
    }
  ]
}
```

## 5. Theme API

### 5.1 Apply Theme
```http
POST /api/v2/catalog/theme/apply
```

#### Request Body
```json
{
  "content_id": "uuid",
  "theme": "string",
  "options": {
    "strength": "float",
    "preserve": ["string"]
  }
}
```

### 5.2 List Themes
```http
GET /api/v2/catalog/theme/list
```

#### Response
```json
{
  "themes": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "compatible_types": ["string"],
      "modifiers": {}
    }
  ]
}
```

## 6. Message Hub Integration

### 6.1 Published Events
```json
{
  "catalog.item.created": {
    "content_id": "uuid",
    "type": "string",
    "name": "string",
    "timestamp": "string"
  },
  "catalog.item.updated": {
    "content_id": "uuid",
    "changes": ["string"],
    "timestamp": "string"
  },
  "catalog.item.deleted": {
    "content_id": "uuid",
    "type": "string",
    "timestamp": "string"
  },
  "catalog.item.validated": {
    "content_id": "uuid",
    "valid": "boolean",
    "balance_score": "float",
    "timestamp": "string"
  },
  "catalog.theme.applied": {
    "content_id": "uuid",
    "theme": "string",
    "timestamp": "string"
  }
}
```

### 6.2 Subscribed Events
```json
{
  "character.created": {
    "character_id": "uuid",
    "type": "string",
    "level": "integer"
  },
  "campaign.theme_changed": {
    "campaign_id": "uuid",
    "theme": "string"
  },
  "llm.content_generated": {
    "content_id": "uuid",
    "type": "string",
    "content": {}
  }
}
```

## 7. Health and Metrics

### 7.1 Health Check
```http
GET /health
```

#### Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "string",
  "components": {
    "search": "healthy|degraded|unhealthy",
    "database": "healthy|degraded|unhealthy",
    "cache": "healthy|degraded|unhealthy"
  },
  "metrics": {
    "total_items": "integer",
    "search_latency": "float",
    "cache_hit_rate": "float"
  }
}
```

### 7.2 Metrics
```http
GET /metrics
```

#### Response Format
```
# HELP catalog_items_total Total number of catalog items
# TYPE catalog_items_total counter
catalog_items_total{type="item"} 1000
catalog_items_total{type="spell"} 500

# HELP catalog_search_latency Search latency in seconds
# TYPE catalog_search_latency histogram
catalog_search_latency_bucket{le="0.1"} 900
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
      "timestamp": "string",
      "validation_errors": []
    }
  }
}
```

### 8.2 Common Error Codes
- `INVALID_CONTENT`: Content validation failed
- `NOT_FOUND`: Content item not found
- `THEME_ERROR`: Theme application failed
- `SEARCH_ERROR`: Search operation failed
- `VALIDATION_ERROR`: Content validation error
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Operation not allowed
