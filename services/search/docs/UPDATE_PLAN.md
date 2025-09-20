# Search Service Documentation Update Plan

## ICD Updates Required

### 1. Update API Interfaces Section
1. Replace REST API endpoints with Message Hub events:
   ```markdown
   ## 2. Service Events

   ### 2.1 Search Events
   ```json
   {
     "type": "search.execute",
     "data": {
       "index": "string",
       "query": {
         "term": "string",
         "fields": ["array"],
         "type": "match|phrase|fuzzy",
         "operator": "and|or"
       },
       "filters": [{
         "field": "string",
         "value": "any",
         "operator": "eq|ne|gt|lt|in"
       }],
       "pagination": {
         "size": "integer",
         "offset": "integer"
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.2 Index Events
   ```json
   {
     "type": "search.index.manage",
     "data": {
       "operation": "create|update|delete|refresh",
       "index": "string",
       "settings": {
         "shards": "integer",
         "replicas": "integer"
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.3 Document Events
   ```json
   {
     "type": "search.document.manage",
     "data": {
       "operation": "index|update|delete",
       "index": "string",
       "document": {
         "id": "string",
         "content": "object"
       },
       "correlation_id": "uuid"
     }
   }
   ```

### 2. Update Client Libraries Section
1. Update Python client for message hub:
   ```python
   from dnd_search import SearchClient

   client = SearchClient(
       service_id="character_service",
       message_hub="required",  # Message Hub client required
       options={
           "index": "characters",
           "timeout": 5,
           "retry_count": 3
       }
   )

   # Async Message Hub based operations
   results = await client.search(
       query="ranger",
       filters={"level": {"gte": 5}},
       sort=["name:asc"]
   )

   # Document operations
   await client.index_document({
       "id": "char123",
       "content": {
           "name": "Aragorn",
           "class": "ranger"
       }
   })
   ```

2. Update Go client:
   ```go
   package main

   import "dnd/search"

   func main() {
       client := search.NewClient(&search.Config{
           ServiceID: "campaign_service",
           MessageHub: messageHub,  // Message Hub client required
           Options: search.Options{
               Index: "campaigns",
               Timeout: 5,
               RetryCount: 3,
           },
       })

       // Message Hub based operations
       results, err := client.Search(ctx, &search.Query{
           Term: "forgotten realms",
           Filters: map[string]interface{}{
               "status": "active",
           },
       })
   }
   ```

### 3. Update Service Integration Section
1. Remove direct integration patterns:
   ```diff
   - Direct HTTP endpoints
   - Service-specific clients
   - Direct database connections
   + Message Hub event patterns
   + Storage service integration
   + Event-based communication
   ```

## SRD Updates Required

### 1. Update Core Principles
1. Strengthen message hub requirements:
   ```markdown
   ### 1.2 Core Principles
   - NO direct service-to-service communication
   - All communication MUST flow through Message Hub
   - All persistence through storage service
   - Event-driven architecture
   - Asynchronous operations
   ```

### 2. Update Technical Requirements
1. Add event processing requirements:
   ```markdown
   ### 3.5 Event Processing
   - Message Hub latency: < 10ms
   - Event ordering preserved
   - At-least-once delivery
   - Failed event handling
   - Event correlation
   - Circuit breaking
   ```

2. Update storage requirements:
   ```markdown
   ### 3.6 Storage Requirements
   - All persistence via storage service
   - Index data in storage service
   - Analytics in storage service
   - Backup coordination
   - No direct database access
   ```

### 3. Update Integration Patterns
1. Revise integration section:
   ```markdown
   ## 7. Integration Patterns

   ### 7.1 Message Hub Events

   #### Published Events
   - search.execute.completed
   - search.index.updated
   - search.document.changed
   - search.error.occurred
   - search.metrics.collected

   #### Subscribed Events
   - content.updated
   - content.indexed.requested
   - search.execute.requested
   - system.config.changed

   ### 7.2 Storage Integration
   ```yaml
   storage:
     schema: search_db
     tables:
       - index_metadata:
           ttl: none
           backup: true
       - search_analytics:
           ttl: 90d
           backup: false
       - index_stats:
           ttl: 30d
           backup: false
   ```

### 4. Update Data Models
1. Add event models:
   ```markdown
   ### 5.4 Event Models
   ```json
   // Search request event
   {
     "type": "search.execute.requested",
     "data": {
       "query": {},
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }

   // Search response event
   {
     "type": "search.execute.completed",
     "data": {
       "results": {},
       "metrics": {},
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```
   ```

## Implementation Changes Required

### 1. Update Service Configuration
```yaml
service:
  name: search_service
  message_hub:
    required: true
    events:
      - search.execute.*
      - search.index.*
      - search.document.*
  storage:
    schema: search_db
    tables:
      - index_metadata
      - search_analytics
  metrics:
    enabled: true
    interval: 60
```

### 2. Update Integration Logic
```python
# Remove REST endpoints
@app.post("/api/v2/search")  # REMOVE
async def search(request):
    pass

# Add event handlers
async def handle_search_event(event):
    query = event.data["query"]
    results = await search_engine.execute(query)
    
    # Store analytics via storage service
    await storage.write(
        "search_db",
        "search_analytics",
        {
            "query_id": uuid4(),
            "query": query,
            "results": results.metadata
        }
    )
    
    # Publish results
    await message_hub.publish(
        "search.execute.completed",
        {
            "results": results.data,
            "correlation_id": event.correlation_id
        }
    )
```

### 3. Update Data Access
```python
# Remove direct database access
async def get_index_metadata(index):  # REMOVE
    return await db.fetch_one(
        "SELECT * FROM indices WHERE name = $1",
        index
    )

# Add storage service access
async def get_index_metadata(index):
    response = await message_hub.request(
        "storage.read",
        {
            "database": "search_db",
            "table": "index_metadata",
            "where": {"name": index}
        }
    )
    return response.data
```