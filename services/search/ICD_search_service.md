# Search Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-30

## 1. Communication Architecture

### 1.1 Service Communication Pattern
- All service-to-service communication MUST be routed through the Message Hub service
- No direct HTTP calls between services are permitted
- All integrations must use asynchronous messaging patterns
- All events and requests must include proper correlation IDs

### 1.2 Base URL (API Gateway Access Only)
```http
http://search-service:8000  # Only accessible via API Gateway
```

### 1.3 Message Hub Protocol
- Every request/event must include:
  * Correlation ID (for tracing)
  * Source service identifier
  * Request/event type and version
  * Timestamp
  * TTL (time-to-live)

### 1.4 Common Headers
## 1. Interface Overview

### 1.1 Purpose
This document defines the interfaces for the Search Service, including search APIs, index management interfaces, and integration patterns for search functionality across the platform.

### 1.2 Scope
- Search endpoints
- Index management APIs
- Query interfaces
- Service integrations
- Monitoring interfaces

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Search Operations
```http
POST /api/v2/search
POST /api/v2/search/multi
GET /api/v2/search/suggest
GET /api/v2/search/autocomplete
POST /api/v2/search/scroll
```

#### 2.1.2 Index Operations
```http
POST /api/v2/indices
DELETE /api/v2/indices/{name}
PUT /api/v2/indices/{name}/mappings
POST /api/v2/indices/{name}/refresh
POST /api/v2/indices/{name}/analyze
```

#### 2.1.3 Document Operations
```http
POST /api/v2/documents
PUT /api/v2/documents/{id}
DELETE /api/v2/documents/{id}
POST /api/v2/documents/bulk
GET /api/v2/documents/{id}
```

### 2.2 Query Format

#### 2.2.1 Search Query
```json
{
  "search_request": {
    "query": {
      "term": "string",
      "fields": ["array"],
      "type": "match|phrase|fuzzy",
      "operator": "and|or"
    },
    "filters": [
      {
        "field": "string",
        "value": "any",
        "operator": "eq|ne|gt|lt|in"
      }
    ],
    "sort": [
      {
        "field": "string",
        "order": "asc|desc"
      }
    ],
    "page": {
      "size": "integer",
      "number": "integer"
    },
    "highlight": {
      "fields": ["array"],
      "pre_tags": ["string"],
      "post_tags": ["string"]
    }
  }
}
```

#### 2.2.2 Document Format
```json
{
  "document": {
    "id": "string",
    "type": "string",
    "content": {
      "title": "string",
      "description": "string",
      "tags": ["array"],
      "metadata": {}
    },
    "permissions": {
      "read": ["array"],
      "write": ["array"]
    },
    "timestamp": "datetime",
    "version": "integer"
  }
}
```

## 3. Search Types

### 3.1 Character Search
```yaml
search_type:
  character:
    fields:
      - name
      - class
      - race
      - level
      - abilities
      - inventory
    filters:
      - level
      - class
      - race
    sorts:
      - name
      - level
      - created_at
```

### 3.2 Campaign Search
```yaml
search_type:
  campaign:
    fields:
      - name
      - description
      - setting
      - players
      - npcs
    filters:
      - status
      - level_range
      - player_count
    sorts:
      - name
      - start_date
      - activity
```

### 3.3 Content Search
```yaml
search_type:
  content:
    fields:
      - name
      - description
      - category
      - rules
      - effects
    filters:
      - type
      - category
      - source
    sorts:
      - name
      - relevance
      - popularity
```

## 4. Service Integration

### 4.1 Character Service
```yaml
integration:
  service: character
  indices:
    - name: characters
      settings:
        shards: 3
        replicas: 1
      mappings:
        properties:
          name:
            type: text
            analyzer: standard
          class:
            type: keyword
          level:
            type: integer
```

### 4.2 Campaign Service
```yaml
integration:
  service: campaign
  indices:
    - name: campaigns
      settings:
        shards: 3
        replicas: 1
      mappings:
        properties:
          name:
            type: text
            analyzer: standard
          status:
            type: keyword
          player_count:
            type: integer
```

### 4.3 Content Service
```yaml
integration:
  service: content
  indices:
    - name: game_content
      settings:
        shards: 5
        replicas: 1
      mappings:
        properties:
          name:
            type: text
            analyzer: standard
          type:
            type: keyword
          source:
            type: keyword
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_search import SearchClient

client = SearchClient(
    service="character_service",
    options={
        "index": "characters",
        "timeout": 5,
        "retry_count": 3
    }
)

# Search
results = client.search(
    query="ranger",
    filters={
        "level": {"gte": 5},
        "class": "ranger"
    },
    sort=["name:asc"],
    page={"size": 10, "number": 1}
)

# Index
client.index_document({
    "id": "char123",
    "type": "character",
    "content": {
        "name": "Aragorn",
        "class": "ranger",
        "level": 5
    }
})
```

### 5.2 Go Client
```go
package main

import "dnd/search"

func main() {
    client := search.NewClient(&search.Config{
        Service: "campaign_service",
        Options: search.Options{
            Index: "campaigns",
            Timeout: 5,
            RetryCount: 3,
        },
    })

    // Search
    results, err := client.Search(ctx, &search.Query{
        Term: "forgotten realms",
        Filters: map[string]interface{}{
            "status": "active",
        },
        Sort: []string{"name:asc"},
        Page: &search.Page{
            Size: 10,
            Number: 1,
        },
    })
}
```

## 6. Analysis Interface

### 6.1 Analyzers
```yaml
analyzers:
  standard:
    tokenizer: standard
    filters:
      - lowercase
      - stop
      - snowball
  
  name:
    tokenizer: standard
    filters:
      - lowercase
      - asciifolding
  
  keyword:
    tokenizer: keyword
    filters:
      - lowercase
```

### 6.2 Analysis Chain
```yaml
analysis:
  char_names:
    analyzer: name
    field_mapping:
      - name
      - title
  
  content:
    analyzer: standard
    field_mapping:
      - description
      - rules
      - effects
```

## 7. Security Interface

### 7.1 Authentication
```yaml
auth:
  type: "bearer"
  roles:
    - search_reader
    - search_writer
    - index_admin
  scope: "search:read search:write"
```

### 7.2 Authorization
```yaml
permissions:
  read:
    - "search:read"
    - "suggest:read"
    - "complete:read"
  write:
    - "index:write"
    - "document:write"
    - "analyze:write"
  admin:
    - "index:admin"
    - "settings:admin"
    - "mappings:admin"
```

## 8. Monitoring Interface

### 8.1 Metrics
```yaml
metrics:
  search:
    - name: search_requests_total
      type: counter
      labels: [index, type]
    - name: search_latency_seconds
      type: histogram
      labels: [index, type]
  
  index:
    - name: index_size_bytes
      type: gauge
      labels: [index]
    - name: index_documents_total
      type: gauge
      labels: [index]
```

### 8.2 Health Checks
```http
GET /health/live
GET /health/ready
GET /health/metrics
```

## 9. Configuration Interface

### 9.1 Service Configuration
```yaml
config:
  search:
    max_results: 1000
    timeout: 5
    scroll_size: 1000
    highlight_size: 100
  
  index:
    refresh_interval: 1s
    number_of_shards: 5
    number_of_replicas: 1
    max_result_window: 10000
```

### 9.2 Analysis Configuration
```yaml
settings:
  analysis:
    analyzer:
      default:
        type: custom
        tokenizer: standard
        filter:
          - lowercase
          - stop
          - snowball
    
    filter:
      snowball:
        type: snowball
        language: english
```
