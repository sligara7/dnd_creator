# LLM Service Documentation Update Plan

## ICD Updates Required

### 1. Remove Direct Integration Sections
1. Remove section "Integration Endpoints" that describes direct service communication
2. Replace with Message Hub event patterns

### 2. Update Service Communication
1. Remove Redis caching reference (should use Cache Service via Message Hub)
2. Remove direct API integration descriptions

### 3. Expand Message Hub Integration
1. Update section 6 with comprehensive event patterns:
   ```markdown
   ## 6. Message Hub Integration

   ### 6.1 Events Published
   ```json
   {
     "text_generation": {
       "request_id": "uuid",
       "type": "string",
       "status": "string",
       "content": "string",
       "metadata": {}
     },
     "image_generation": {
       "request_id": "uuid",
       "type": "string",
       "status": "string",
       "content": "string",
       "metadata": {}
     },
     "theme_application": {
       "request_id": "uuid",
       "type": "text|image",
       "status": "string",
       "metadata": {}
     }
   }
   ```

   ### 6.2 Events Consumed
   ```json
   {
     "character_content_request": {
       "request_id": "uuid",
       "type": "backstory|personality|combat|equipment",
       "parameters": {},
       "theme": {}
     },
     "campaign_content_request": {
       "request_id": "uuid",
       "type": "plot|location|quest|dialogue|event",
       "parameters": {},
       "theme": {}
     },
     "image_request": {
       "request_id": "uuid",
       "type": "portrait|map|item",
       "parameters": {},
       "theme": {}
     }
   }
   ```

   ### 6.3 Event Routing Patterns
   - All service requests MUST be routed through Message Hub
   - No direct HTTP endpoints for service integration
   - Each request type has a specific event topic
   - All events include correlation IDs for tracing
   ```

2. Update Health Check section:
   ```markdown
   - Remove direct service health checks
   - Add Message Hub health check
   - Add event processing metrics
   ```

3. Update Error Handling:
   ```markdown
   - Add Message Hub specific error codes
   - Update integration error handling patterns
   ```

## SRD Updates Required

### 1. Update Integration Requirements
1. Replace section 5 "Integration Requirements" with:
   ```markdown
   ## 5. Message Hub Integration Requirements

   ### 5.1 Service Communication
   - ALL service communication MUST flow through Message Hub
   - NO direct service-to-service communication permitted
   - Each request type has a dedicated event pattern
   - Implementation MUST use message correlation tracking

   ### 5.2 Event Patterns
   #### Content Generation Events
   - llm.text.character_request
   - llm.text.campaign_request
   - llm.text.narrative_request
   - llm.image.generate_request
   - llm.image.transform_request
   - llm.theme.apply_request

   #### Response Events
   - llm.text.content_generated
   - llm.image.content_generated
   - llm.theme.applied

   #### Status Events
   - llm.queue.status_update
   - llm.error.reported
   - llm.metrics.reported
   ```

### 2. Update Technical Requirements
1. Add Message Hub section to Technical Requirements:
   ```markdown
   ### 4.4 Message Hub Requirements

   #### Event Processing
   - Handle concurrent event streams
   - Implement event retry logic
   - Maintain event ordering where required
   - Track event correlation
   - Monitor event processing metrics

   #### Performance Requirements
   - Event processing latency: < 100ms
   - Event publishing latency: < 100ms
   - Event delivery success rate: > 99.9%
   - Event correlation accuracy: 100%
   ```

2. Update Caching and Rate Limiting:
   ```markdown
   ### 4.2 Caching and Rate Limiting
   
   #### Cache Integration (via Cache Service)
   - Request caching through Cache Service
   - Cache invalidation via Message Hub events
   - Cache synchronization across instances
   - Cache metrics reported via Message Hub

   #### Rate Limiting
   - Local rate limiting for external APIs
   - Distributed rate limiting via Cache Service
   - Rate limit events published to Message Hub
   - Rate limit metrics collection
   ```

### 3. Update Performance Requirements
1. Add Event Processing metrics:
   ```markdown
   ### 7.3 Event Processing Performance
   - Event consumption rate: > 1000/second
   - Event processing latency: < 100ms
   - Event correlation success: > 99.9%
   - Event delivery guarantee: exactly-once
   - Event order preservation: where required
   ```

## Implementation Changes Required

1. Update service initialization:
   ```python
   # REMOVE:
   redis_client = Redis()
   api_client = APIClient()
   
   # ADD:
   message_hub = MessageHubClient()
   cache_client = CacheServiceClient()  # accessed via Message Hub
   ```

2. Update integration patterns:
   ```python
   # REMOVE:
   async def generate_character_content(request):
       result = await text_generator.generate(request)
       await character_service.notify(result)
   
   # ADD:
   async def handle_character_content_request(event):
       result = await text_generator.generate(event.data)
       await message_hub.publish("llm.text.content_generated", result)
   ```

3. Update caching:
   ```python
   # REMOVE:
   await redis_client.set(key, value)
   
   # ADD:
   await message_hub.request("cache.set", {"key": key, "value": value})
   ```

4. Update dependencies:
   ```toml
   # REMOVE:
   redis = "^4.5.0"
   aiohttp = "^3.8.0"
   
   # ADD:
   aio-pika = "^9.0.0"  # Message Hub client
   ```