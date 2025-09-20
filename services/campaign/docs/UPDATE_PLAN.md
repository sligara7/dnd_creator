# Campaign Service Documentation Update Plan

## ICD Updates Required

### 1. Remove Database References
1. In Health Check section (line 491):
   ```diff
   - "database": "healthy"
   + "storage_service": "healthy"
   ```

2. Remove any database-specific error codes

### 2. Update Service Integration Section

1. Add new section "Storage Service Integration":
   ```markdown
   ## 11. Storage Service Integration

   ### 11.1 Data Storage Pattern
   All persistent data operations MUST use the storage service's campaign_db schema:

   - Campaign data
   - Version control data
   - Chapter content
   - Plot branches
   - Session records
   ```

2. Remove section 8 "Integration Endpoints" that specifies direct service integrations

3. Expand Message Hub Integration section to include:
   ```markdown
   ### 7.5 Data Access Events
   - All data operations must be requested via storage service events
   - Events must include correlation IDs for tracing
   - Events must specify campaign_db schema
   - Events must handle storage service failures
   ```

### 3. Update Error Handling
1. Add new error codes:
   ```markdown
   - `STORAGE_SERVICE_ERROR`: Error accessing storage service
   - `STORAGE_CONSISTENCY_ERROR`: Data consistency issue
   ```

2. Remove any database-specific error codes

## SRD Updates Required

### 1. Remove Direct Database References

1. Remove from Performance Standards (section 3.1):
   - Any direct database metrics
   - Database query timing requirements

2. Add Storage Service performance requirements:
   ```markdown
   - Storage service operations: < 500ms
   - Bulk operations: < 2s
   - Data consistency requirements: eventual consistency
   ```

3. Update Data Models section (section 6):
   ```markdown
   All data models are stored in the campaign_db schema managed by the storage service.
   No direct database access is permitted.
   ```

### 2. Add Storage Service Requirements

1. Add new section:
   ```markdown
   ### 3.4 Storage Service Requirements

   #### Data Storage Requirements
   - All campaign data MUST be stored in campaign_db schema
   - Service MUST implement storage service retry logic
   - Service MUST handle storage service failures gracefully
   - Service MUST maintain data consistency across operations

   #### Schema Requirements
   - Campaign data schema
   - Version control schema
   - Session tracking schema
   - Plot branch schema
   ```

### 3. Update Service Integration Section

1. Revise section 3.2 to specify all service communication via Message Hub:
   ```markdown
   ### 3.2 Service Integration Requirements

   #### Message Hub (Required Gateway)
   - ALL service-to-service communication MUST route through Message Hub
   - NO direct service-to-service calls permitted
   - ALL data operations MUST use storage service via Message Hub
   ```

2. Add specific Message Hub routing patterns:
   ```markdown
   #### Message Routing Patterns
   - Data Operations: campaign.storage.operation
   - Character Updates: campaign.character.update
   - Content Generation: campaign.content.generate
   - Map Generation: campaign.map.generate
   ```

### 4. Update Technical Requirements

1. Add storage service retry and circuit breaker requirements:
   ```markdown
   ### 3.5 Resilience Requirements

   #### Storage Service Interaction
   - Implement exponential backoff retry
   - Maximum 3 retry attempts
   - Circuit breaker pattern for failures
   - Fallback behavior for outages
   ```

2. Add storage service monitoring:
   ```markdown
   ### 8.3 Storage Monitoring
   - Storage operation latency
   - Storage operation success rate
   - Data consistency metrics
   - Schema version tracking
   ```

## Implementation Changes Required

1. Remove all direct database access:
   ```python
   # REMOVE:
   database.Query()
   
   # ADD:
   storage_client.Campaign.Query()
   ```

2. Update service initialization:
   ```python
   # REMOVE:
   db = Database()
   
   # ADD:
   storage_client = StorageServiceClient()
   message_hub = MessageHubClient()
   ```

3. Update dependencies:
   ```toml
   # REMOVE:
   sqlalchemy = "^2.0.0"
   asyncpg = "^0.28.0"
   
   # ADD:
   storage-service-client = "^1.0.0"
   aio-pika = "^9.0.0"
   ```