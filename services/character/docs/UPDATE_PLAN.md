# Character Service Documentation Update Plan

## ICD Updates Required

### Remove Database-Related Content
1. Dependencies section:
   - Remove SQLAlchemy, asyncpg from dependencies
   - Add storage-service-client requirement
   - Retain aio-pika for Message Hub

2. Health Check section (line 713):
   - Remove direct database health check
   - Replace with storage service health check
   - Update health response format

3. Update base configuration:
   - Remove database connection configs
   - Add storage service client config
   - Update Message Hub config

### Add Storage Service Integration
1. Add new section "Storage Service Integration":
   ```markdown
   ## 13. Storage Service Integration

   ### 13.1 Data Access Pattern
   All persistent data operations MUST use the storage service's character_db schema:

   - Character data
   - Journal entries
   - Version control data
   - Custom content
   - Inventory and equipment
   ```

2. Update error handling section to include storage service errors
3. Add storage service retry and circuit breaker patterns
4. Document storage service health check requirements

### Message Hub Integration Updates
1. Remove direct service communication references
2. Expand section 11 (Message Hub Integration):
   - Add detailed event schemas
   - Add routing patterns
   - Add correlation tracking
   - Add message priorities
   - Add dead letter handling

## SRD Updates Required

### Remove Database Requirements
1. Remove from Technical Requirements (section 3.1):
   - Database persistence
   - Direct database metrics
   - Database query performance standards

2. Remove Data Requirements (section 3.3) items:
   - Direct database references
   - Database-specific validation

### Add Storage Service Requirements
1. Add new section:
   ```markdown
   ### 3.5 Storage Service Requirements

   #### Data Storage
   - All persistent data MUST be stored in character_db schema via storage service
   - Service MUST implement storage service retry logic
   - Service MUST handle storage service failures gracefully

   #### Performance Requirements
   - Storage service operations: < 500ms
   - Bulk operations: < 2s
   - Failed operation retry policy:
     * Max 3 retries
     * Exponential backoff
     * Circuit breaker pattern
   ```

2. Update Integration Requirements (section 3.4):
   - Add storage service integration details
   - Specify data consistency requirements
   - Add data migration guidelines

### Update Service Integration Section
1. Expand Message Hub section:
   - Add message delivery guarantees
   - Add event ordering requirements
   - Add failure handling

2. Remove direct integrations:
   - Remove direct Campaign service integration
   - Remove direct LLM service integration
   - Route all through Message Hub

## Implementation Changes Required

1. Remove all direct database access:
   ```go
   // REMOVE:
   database.Query()
   
   // ADD:
   storageService.Character.Query()
   ```

2. Update service initialization:
   ```python
   # REMOVE:
   db = Database()
   
   # ADD:
   storage_client = StorageServiceClient()
   message_hub = MessageHubClient()
   ```

3. Update health checks:
   ```python
   # REMOVE:
   status["database"] = check_database()
   
   # ADD:
   status["storage"] = storage_client.health()
   status["message_hub"] = message_hub.health()
   ```