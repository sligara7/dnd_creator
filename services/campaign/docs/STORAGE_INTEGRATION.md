# Storage Service Integration Plan

Version: 1.0
Status: Draft
Last Updated: 2025-09-20

## Overview

This document outlines the plan to integrate the Campaign Service with the Storage Service, replacing direct database access in compliance with updated ARCHITECTURE.json requirements.

## 1. Current Architecture

### Direct Database Access (To Be Removed)
- SQLAlchemy ORM and Core
- Direct PostgreSQL connections
- Local database schemas
- Transaction management
- Migration scripts

### Current Dependencies
```toml
[tool.poetry.dependencies]
sqlalchemy = "^2.0.20"
alembic = "^1.11.3"
asyncpg = "^0.28.0"
```

## 2. Target Architecture

### Storage Service Integration
- Storage service client
- Campaign_db sub-database
- Message-based operations
- Event-driven updates
- No direct database access

### Required Dependencies
```toml
[tool.poetry.dependencies]
aio-pika = "^9.3.0"  # Message Hub integration
httpx = "^0.25.0"    # Storage service HTTP client
```

## 3. Migration Strategy

### Phase 1: Storage Client Implementation
1. Create storage service client:
   ```python
   from campaign_service.storage import StorageClient
   
   class StorageClient:
       def __init__(self, message_hub):
           self.message_hub = message_hub
           self.db_name = "campaign_db"
   
       async def execute_query(self, query: dict) -> dict:
           return await self.message_hub.request(
               "storage.query",
               {
                   "db": self.db_name,
                   "query": query
               }
           )
   ```

2. Update repository pattern:
   ```python
   class CampaignRepository:
       def __init__(self, storage_client: StorageClient):
           self.storage = storage_client
   
       async def get_campaign(self, id: UUID) -> Campaign:
           result = await self.storage.execute_query({
               "type": "select",
               "table": "campaigns",
               "where": {"id": str(id)}
           })
           return Campaign.model_validate(result[0])
   ```

### Phase 2: Data Migration
1. Schema creation in storage service:
   ```sql
   -- To be executed by storage service
   CREATE TABLE campaign_db.campaigns (
       id UUID PRIMARY KEY,
       name TEXT NOT NULL,
       description TEXT,
       theme_data JSONB,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
       updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```

2. Data migration script:
   ```python
   async def migrate_data():
       # Get all campaigns
       campaigns = await old_db.execute(
           select(Campaign)
       )
       
       # Migrate each campaign
       for campaign in campaigns:
           await storage.execute_query({
               "type": "insert",
               "table": "campaigns",
               "data": campaign.model_dump()
           })
   ```

### Phase 3: Repository Updates
1. Update all repository methods:
   ```python
   class CampaignRepository:
       async def create(self, campaign: Campaign) -> Campaign:
           result = await self.storage.execute_query({
               "type": "insert",
               "table": "campaigns",
               "data": campaign.model_dump()
           })
           return Campaign.model_validate(result)
   
       async def update(self, campaign: Campaign) -> Campaign:
           result = await self.storage.execute_query({
               "type": "update",
               "table": "campaigns",
               "where": {"id": str(campaign.id)},
               "data": campaign.model_dump()
           })
           return Campaign.model_validate(result)
   ```

2. Add event handlers:
   ```python
   @message_hub.subscribe("storage.campaign_db.updated")
   async def handle_campaign_update(event: dict):
       campaign_id = UUID(event["campaign_id"])
       # Refresh local cache/state
   ```

### Phase 4: Service Layer Updates
1. Update service methods:
   ```python
   class CampaignService:
       def __init__(self, repository: CampaignRepository):
           self.repository = repository
   
       async def create_campaign(self, data: dict) -> Campaign:
           campaign = Campaign.model_validate(data)
           return await self.repository.create(campaign)
   ```

2. Add event publishing:
   ```python
   async def update_campaign_theme(self, id: UUID, theme: dict):
       campaign = await self.repository.update(
           id, {"theme_data": theme}
       )
       await self.message_hub.publish(
           "campaign.theme.updated",
           {
               "campaign_id": str(id),
               "theme": theme
           }
       )
       return campaign
   ```

## 4. Testing Strategy

### Unit Tests
1. Mock storage client:
   ```python
   class MockStorageClient:
       async def execute_query(self, query: dict) -> dict:
           # Return mock data based on query
   ```

2. Test repository methods:
   ```python
   async def test_campaign_creation():
       storage = MockStorageClient()
       repo = CampaignRepository(storage)
       campaign = await repo.create({
           "name": "Test Campaign"
       })
       assert campaign.id is not None
   ```

### Integration Tests
1. Storage service integration:
   ```python
   async def test_storage_integration():
       # Test complete flow through storage service
       campaign = await service.create_campaign({
           "name": "Integration Test"
       })
       assert campaign.id is not None
       
       # Verify in storage
       result = await storage.execute_query({
           "type": "select",
           "table": "campaigns",
           "where": {"id": str(campaign.id)}
       })
       assert len(result) == 1
   ```

2. Event handling:
   ```python
   async def test_event_handling():
       # Publish event
       await message_hub.publish(
           "storage.campaign_db.updated",
           {"campaign_id": str(campaign_id)}
       )
       
       # Verify handler processed event
       await asyncio.sleep(0.1)
       assert cache.was_invalidated(campaign_id)
   ```

## 5. Rollback Plan

### Triggers
- Migration failure rate > 1%
- Data inconsistency detected
- Performance degradation > 100ms
- Storage service unavailability

### Rollback Steps
1. Disable new storage integration
2. Re-enable direct database access
3. Restore from backup if needed
4. Validate application state
5. Update documentation

## 6. Validation Steps

### Data Integrity
1. Compare record counts
2. Validate data consistency
3. Check relationships
4. Verify soft deletes
5. Test versioning

### Performance
1. Measure latency impact
2. Test concurrent access
3. Verify transaction isolation
4. Check memory usage

### Integration
1. Verify event flow
2. Test error handling
3. Check retry mechanisms
4. Validate state sync

## 7. Success Criteria

### Functional Requirements
- All operations working via storage service
- No direct database access
- Complete event integration
- Data integrity maintained

### Performance Requirements
- Latency increase < 50ms
- Successful concurrent operations
- No timeout increases
- Memory usage stable

### Validation Requirements
- All tests passing
- No data inconsistencies
- Events properly handled
- Proper error handling

## 8. Timeline

### Week 1: Implementation
- Storage client development
- Repository updates
- Initial testing

### Week 2: Migration
- Schema creation
- Data migration
- Validation testing

### Week 3: Integration
- Event handler implementation
- Performance testing
- Documentation updates

### Week 4: Deployment
- Production migration
- Monitoring
- Final validation