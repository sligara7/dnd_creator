# Catalog Service Documentation Update Plan

## Core Changes Required
- Remove direct API endpoints and replace with Message Hub events
- Move all data persistence to storage service
- Update client libraries for Message Hub integration
- Ensure theme-aware content adaption via Message Hub
- Update validation and search integration patterns

## ICD Updates Required

### 1. Remove Direct API Endpoints
1. Replace REST endpoints with event patterns:
   ```markdown
   ## 2. Service Events

   ### 2.1 Content Management Events
   ```json
   {
     "type": "catalog.content.manage",
     "data": {
       "operation": "get|create|update|delete",
       "content_type": "item|spell|monster",
       "content_id": "uuid?",
       "content": {
         "name": "string",
         "description": "string",
         "properties": {},
         "theme_data": {}
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.2 Search Events
   ```json
   {
     "type": "catalog.search.execute",
     "data": {
       "query": "string",
       "filters": {
         "types": ["string"],
         "themes": ["string"],
         "properties": {}
       },
       "pagination": {
         "page": "integer",
         "size": "integer"
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.3 Validation Events
   ```json
   {
     "type": "catalog.content.validate",
     "data": {
       "content": {
         "id": "uuid",
         "type": "string",
         "properties": {}
       },
       "context": {
         "campaign_id": "uuid?",
         "character_level": "integer?"
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.4 Theme Events
   ```json
   {
     "type": "catalog.theme.apply",
     "data": {
       "content_id": "uuid",
       "theme": "string",
       "options": {
         "strength": "float",
         "preserve": ["string"]
       },
       "correlation_id": "uuid"
     }
   }
   ```
   ```

### 2. Update Storage Integration
1. Add storage service schema:
   ```markdown
   ## 3. Storage Integration

   ### 3.1 Content Storage
   ```json
   {
     "operation": "write",
     "database": "catalog_db",
     "table": "content",
     "data": {
       "id": "uuid",
       "type": "string",
       "name": "string",
       "source": "string",
       "description": "string",
       "properties": "jsonb",
       "theme_data": "jsonb",
       "metadata": {
         "version": "string",
         "created_at": "timestamp",
         "updated_at": "timestamp"
       }
     }
   }
   ```

   ### 3.2 Validation Storage
   ```json
   {
     "operation": "write",
     "database": "catalog_db",
     "table": "validation_history",
     "data": {
       "content_id": "uuid",
       "timestamp": "datetime",
       "result": {
         "valid": "boolean",
         "balance_score": "float",
         "issues": ["object"]
       }
     }
   }
   ```

   ### 3.3 Theme Storage
   ```json
   {
     "operation": "write",
     "database": "catalog_db",
     "table": "theme_adaptations",
     "data": {
       "content_id": "uuid",
       "theme": "string",
       "adaptation": "jsonb",
       "created_at": "timestamp"
     }
   }
   ```
   ```

### 3. Update Client Libraries
1. Update Python client:
   ```python
   from dnd_catalog import CatalogClient

   client = CatalogClient(
       service_id="character_service",
       message_hub=message_hub,  # Message Hub client required
       options={
           "timeout": 30,
           "retries": 3
       }
   )

   # Content operations via Message Hub
   item = await client.get_content("item", "sword_123")
   await client.create_content("item", {
       "name": "Flaming Sword",
       "properties": {"damage": "1d6"}
   })

   # Search via Message Hub
   results = await client.search(
       query="sword",
       filters={"type": "weapon"}
   )
   ```

2. Update Go client:
   ```go
   package main

   import "dnd/catalog"

   func main() {
       client := catalog.NewClient(&catalog.Config{
           ServiceID: "campaign_service",
           MessageHub: messageHub,  # Message Hub client required
           Options: catalog.Options{
               Timeout: 30,
               Retries: 3,
           },
       })

       // Content operations via Message Hub
       spell, err := client.GetContent(ctx, "spell", "fireball")
       err = client.CreateContent(ctx, "spell", catalog.Content{
           Name: "Ice Storm",
           Properties: map[string]interface{}{
               "level": 4,
               "school": "evocation",
           },
       })
   }
   ```

## SRD Updates Required

### 1. Update Core Principles
1. Strengthen messaging requirements:
   ```markdown
   ### 1.2 Core Principles
   - ALL service communication via Message Hub
   - ALL persistence via storage service
   - NO direct service-to-service communication
   - Asynchronous event-driven operations
   - Event correlation and tracing
   ```

### 2. Update Technical Requirements
1. Add event processing requirements:
   ```markdown
   ### 3.1 Integration Requirements

   #### Message Hub Integration
   - Event processing latency: < 10ms
   - Event ordering preserved
   - At-least-once delivery
   - Event correlation required
   - Circuit breaking enabled

   #### Storage Integration
   - Content persistence in storage service
   - Analytics in storage service
   - Theme data in storage service
   - Validation history in storage service
   - Proper data versioning
   ```

### 3. Update Data Models
1. Add message hub event models:
   ```markdown
   ### 4.4 Event Models
   ```json
   // Content event model
   {
     "type": "catalog.content.*",
     "data": {
       "operation": "string",
       "content": "object",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }

   // Search event model
   {
     "type": "catalog.search.*",
     "data": {
       "query": "object",
       "results": "object?",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```
   ```

## Implementation Changes Required

### 1. Update Content Management
```python
# Remove direct endpoints
@app.post("/api/v2/catalog/{type}")  # REMOVE
async def create_content(type: str, content: dict):
    pass

# Add event handlers
async def handle_content_event(event):
    content_type = event.data["content_type"]
    operation = event.data["operation"]
    content = event.data["content"]
    
    if operation == "create":
        # Store via storage service
        response = await storage.write(
            "catalog_db",
            "content",
            {
                "id": uuid4(),
                "type": content_type,
                **content,
                "metadata": {
                    "created_at": datetime.utcnow()
                }
            }
        )
        
        # Publish event
        await message_hub.publish(
            "catalog.content.created",
            {
                "content_id": response.id,
                "type": content_type,
                "correlation_id": event.correlation_id
            }
        )
```

### 2. Update Search Integration
```python
# Remove direct search endpoint
@app.get("/api/v2/catalog/search")  # REMOVE
async def search(query: str):
    pass

# Add event handler
async def handle_search_event(event):
    query = event.data["query"]
    filters = event.data["filters"]
    
    # Get content via storage service
    items = await storage.read(
        "catalog_db",
        "content",
        {"type": {"in": filters["types"]}}
    )
    
    # Filter and rank results
    results = rank_search_results(items, query)
    
    # Publish results
    await message_hub.publish(
        "catalog.search.completed",
        {
            "results": results,
            "correlation_id": event.correlation_id
        }
    )
```

### 3. Update Theme Processing
```python
# Remove direct theme endpoint
@app.post("/api/v2/catalog/theme/apply")  # REMOVE
async def apply_theme(request: dict):
    pass

# Add event handler
async def handle_theme_event(event):
    content_id = event.data["content_id"]
    theme = event.data["theme"]
    
    # Get content via storage service
    content = await storage.read(
        "catalog_db",
        "content",
        {"id": content_id}
    )
    
    # Apply theme adaptation
    adapted = await adapt_content(content, theme)
    
    # Store adaptation
    await storage.write(
        "catalog_db",
        "theme_adaptations",
        {
            "content_id": content_id,
            "theme": theme,
            "adaptation": adapted,
            "created_at": datetime.utcnow()
        }
    )
    
    # Publish event
    await message_hub.publish(
        "catalog.theme.applied",
        {
            "content_id": content_id,
            "theme": theme,
            "correlation_id": event.correlation_id
        }
    )
```