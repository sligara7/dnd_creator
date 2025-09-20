# Campaign Service Database Migration Plan

Version: 1.0
Status: Draft
Last Updated: 2025-09-20

## Overview

This document outlines the plan for migrating binary assets from the Campaign Service's internal database to use the Storage Service, while maintaining our core campaign data in the service's PostgreSQL database.

## 1. Requirements Analysis

### Binary Assets to Migrate
1. Campaign maps
2. Session note documents
3. Generated content assets

### Core Data to Retain
1. Campaign records
2. Theme data
3. Story/plot structures
4. Version control data
5. Service metadata

### Storage Service Integration
- Maps: image/jpeg, image/png up to 25MB
- Session notes: text/markdown, application/pdf up to 10MB
- 365-day retention policy
- Version control support
- ACL management

## 2. Migration Strategy

### Phase 1: Storage Service Integration
1. Add storage service client configuration
2. Implement storage service integration layer
3. Update API endpoints to use storage service
4. Add health checks for storage service

### Phase 2: Schema Updates
1. Add asset reference fields to campaign models
2. Add storage metadata tracking
3. Create migration scripts
4. Update ORM models

### Phase 3: Data Migration
1. Identify all binary assets
2. Upload assets to storage service
3. Update references
4. Validate migration
5. Clean up old binary storage

### Phase 4: API Updates
1. Update asset endpoints to use storage service
2. Add storage service health checks
3. Update documentation
4. Add metrics for storage operations

## 3. Implementation Plan

### Step 1: Storage Service Integration
```python
# StorageClient configuration
from dnd_storage import StorageClient

storage_client = StorageClient(
    service="campaign_service",
    options={
        "versioning": True,
        "compression": True,
        "encryption": True,
    }
)
```

### Step 2: Database Schema Updates
```sql
-- Add storage references to maps
ALTER TABLE campaign_maps
ADD COLUMN storage_asset_id UUID,
ADD COLUMN storage_version_id UUID;

-- Add storage metadata
ALTER TABLE campaign_maps
ADD COLUMN storage_metadata JSONB;
```

### Step 3: Migration Script
```python
async def migrate_maps():
    # Query all maps with binary data
    maps = await db.execute(
        select(CampaignMap).where(CampaignMap.data.is_not(None))
    )
    
    for map in maps:
        # Upload to storage service
        response = await storage_client.upload_asset(
            file_path=map.data_path,
            metadata={
                "campaign_id": str(map.campaign_id),
                "type": "map",
            },
            tags=["map", "campaign"],
        )
        
        # Update references
        map.storage_asset_id = response.asset_id
        map.storage_version_id = response.version
        map.storage_metadata = response.metadata
        map.data = None  # Clear binary data
        
    await db.commit()
```

### Step 4: API Updates
```python
@router.get("/api/v2/campaigns/{id}/maps/{map_id}")
async def get_campaign_map(id: UUID, map_id: UUID):
    map = await get_map(map_id)
    if map.storage_asset_id:
        # Fetch from storage service
        return await storage_client.get_asset(map.storage_asset_id)
    else:
        # Legacy path
        return map.data
```

## 4. Rollback Plan

### Triggers
- Migration failure exceeds 1% error rate
- Performance degradation over 100ms
- Data integrity issues
- Storage service unavailability

### Rollback Steps
1. Disable new storage service endpoints
2. Revert schema changes
3. Restore database backup
4. Enable legacy endpoints
5. Update documentation

### Validation Steps
1. Verify data integrity
2. Check performance metrics
3. Test all endpoints
4. Validate rollback success

## 5. Testing Strategy

### Unit Tests
1. Storage service client tests
2. Schema validation tests
3. Migration utility tests
4. API endpoint tests

### Integration Tests
1. End-to-end map operations
2. Storage service interaction
3. Performance impact tests
4. Rollback procedure tests

### Performance Tests
1. Asset upload/download speed
2. API latency comparison
3. Concurrent operation limits
4. Storage service scaling

## 6. Success Criteria

### Migration Success
- All binary assets migrated
- References updated correctly
- No data loss or corruption
- Original functionality preserved

### Performance Targets
- Asset retrieval < 100ms
- Upload speed > 10MB/s
- API latency unchanged
- No timeout increases

### Validation Requirements
- All tests passing
- No critical errors
- Performance within targets
- Data integrity verified

## 7. Timeline

### Week 1
- Storage integration
- Schema updates
- Initial testing

### Week 2
- Data migration
- API updates
- Integration testing

### Week 3
- Performance testing
- Documentation updates
- Production migration

### Week 4
- Monitoring
- Cleanup
- Final validation

## 8. Monitoring and Metrics

### Migration Metrics
- Assets migrated
- Migration errors
- Data validation results
- Performance impact

### Operational Metrics
- Asset operation latency
- Storage service health
- Error rates
- Resource usage

### Alerts
- Migration failures
- Performance degradation
- Storage unavailability
- Data integrity issues

## 9. Communication Plan

### Stakeholders
- Development team
- Operations team
- QA team
- Project management

### Updates
- Daily migration progress
- Issue reports
- Success/failure metrics
- Rollback decisions

### Documentation
- Technical specifications
- API changes
- Migration procedures
- Rollback procedures