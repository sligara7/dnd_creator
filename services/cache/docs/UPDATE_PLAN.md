# Cache Service Documentation Update Plan

## ICD Updates Required

### 1. Remove Direct Service Integration Section
1. Replace section 4 with message hub based integration:
   ```markdown
   ## 4. Message Hub Integration

   ### 4.1 Cache Events
   The Cache Service communicates with other services ONLY through Message Hub events:

   #### Cache Operation Events
   ```json
   {
     "event": "cache.operation.request",
     "data": {
       "operation": "get|set|delete",
       "service": "character",
       "key": "string",
       "value": "any?",
       "ttl": "integer?",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```

   #### Cache Response Events
   ```json
   {
     "event": "cache.operation.response",
     "data": {
       "operation": "get|set|delete",
       "status": "success|error",
       "key": "string",
       "value": "any?",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```

   #### Cache Management Events
   ```json
   {
     "event": "cache.management.request",
     "data": {
       "operation": "flush|reload|stats",
       "service": "string",
       "scope": "string?",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```
   ```

### 2. Update Client Libraries
1. Modify Python client for message hub:
   ```markdown
   ### 5.1 Python Client
   ```python
   from dnd_cache import CacheClient

   client = CacheClient(
       service_id="character_service",
       message_hub="required",  # Message Hub client required
       options={
           "consistency": "strong",
           "compression": True,
           "encryption": True
       }
   )

   # All operations routed through Message Hub
   response = await client.get("character:1234")  # Sends cache.operation.request
   await client.set("character:1234", data, ttl=3600)
   await client.delete("character:1234")

   # Batch operations
   responses = await client.get_many(["char:1", "char:2"])
   await client.set_many({
       "char:1": data1,
       "char:2": data2
   }, ttl=3600)
   ```
   ```

2. Modify Go client for message hub:
   ```markdown
   ### 5.2 Go Client
   ```go
   package main

   import "dnd/cache"

   func main() {
       client := cache.NewClient(&cache.Config{
           ServiceID: "campaign_service",
           MessageHub: messageHub,  // Message Hub client required
           Options: cache.Options{
               Consistency: "strong",
               Compression: true,
               Encryption: true,
           },
       })

       // All operations routed through Message Hub
       response, err := client.Get(ctx, "campaign:1234")
       err = client.Set(ctx, "campaign:1234", data, cache.TTL(3600))
       err = client.Delete(ctx, "campaign:1234")
   }
   ```
   ```

### 3. Update Configuration Interface
1. Update client configuration:
   ```markdown
   ### 9.2 Client Configuration
   ```yaml
   client_config:
     message_hub:  # Explicit Message Hub configuration
       required: true
       event_patterns:
         - cache.operation.*
         - cache.management.*
       retry:
         max_attempts: 3
         backoff: "exponential"
     
     connection:
       timeout: 5
       retry: 3
       backoff: "exponential"
     
     circuit_breaker:
       threshold: 0.5
       window: 60
       min_requests: 20
   ```
   ```

## SRD Updates Required

### 1. Update Integration Model
1. Replace direct service integration section:
   ```markdown
   ## Integration Model

   ### 1. Message Hub Integration
   All service interactions MUST flow through Message Hub:
   - Cache operations via events
   - Responses via correlated events
   - Management operations via events
   - Health/metrics via events

   #### Character Service Events
   - cache.char.get
   - cache.char.set
   - cache.char.invalidate

   #### Campaign Service Events
   - cache.campaign.get
   - cache.campaign.set
   - cache.campaign.invalidate

   #### Image Service Events
   - cache.image.get
   - cache.image.set
   - cache.image.invalidate
   ```

### 2. Update Technical Requirements
1. Strengthen message hub requirements:
   ```markdown
   ### 5. Message Hub Requirements
   - Event latency: <5ms
   - Event delivery guarantee: exactly-once
   - Event ordering: preserved per key
   - Event correlation: required
   - Event retry: automatic
   - Event circuit breaking: required
   ```

### 3. Update Development Guidelines
1. Add message hub guidelines:
   ```markdown
   ### 4. Message Hub Guidelines
   - All cache operations MUST use Message Hub
   - Events MUST include correlation IDs
   - Events MUST specify source service
   - Events MUST include timestamps
   - Events SHOULD be idempotent
   ```

### 4. Update Client Integration
1. Update example usage:
   ```markdown
   ### 3. Example Usage
   ```python
   # Message Hub based cache-aside pattern
   async def get_user_data(user_id):
       # Try cache first via Message Hub
       cache_key = f"user:{user_id}"
       cache_response = await message_hub.request(
           "cache.operation.request",
           {
               "operation": "get",
               "service": "user_service",
               "key": cache_key
           }
       )
       if cache_response.data:
           return cache_response.data
       
       # Cache miss - get from storage service
       storage_response = await message_hub.request(
           "storage.query",
           {
               "database": "user_db",
               "table": "users",
               "where": {"id": user_id}
           }
       )
       
       # Update cache via Message Hub
       await message_hub.request(
           "cache.operation.request",
           {
               "operation": "set",
               "service": "user_service",
               "key": cache_key,
               "value": storage_response.data,
               "ttl": 3600
           }
       )
       return storage_response.data
   ```
   ```

## Implementation Changes Required

1. Update service initialization:
   ```python
   # REMOVE:
   redis_client = Redis()
   
   # ADD:
   message_hub = MessageHubClient()
   ```

2. Update cache operations:
   ```python
   # REMOVE:
   async def get_value(key):
       return await redis_client.get(key)
   
   # ADD:
   async def get_value(key, service):
       response = await message_hub.request(
           "cache.operation.request",
           {
               "operation": "get",
               "service": service,
               "key": key
           }
       )
       return response.data
   ```

3. Update health checks:
   ```python
   # REMOVE:
   async def check_health():
       status = await redis_client.ping()
       return {
           "status": "healthy" if status else "unhealthy",
           "redis": status
       }
   
   # ADD:
   async def check_health():
       message_hub_status = await message_hub.health()
       return {
           "status": message_hub_status["status"],
           "message_hub": message_hub_status
       }
   ```