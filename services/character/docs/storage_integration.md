# Storage Service Integration

The Character Service uses the centralized Storage Service for all data persistence needs. This document describes the integration architecture and implementation details.

## Overview

The Storage Service integration provides:
1. Character data persistence
2. Inventory management
3. Journal system
4. Campaign integration
5. Character evolution tracking

## Architecture

### Components

1. **Storage Port** (`clients/storage_port.py`)
   - Interface definition for storage operations
   - Consistent data models across services
   - Type definitions and validation

2. **Storage Client** (`clients/storage_client.py`)
   - Implementation of Storage Port
   - Communication with Storage Service
   - Error handling and retries
   - Caching integration

3. **Repository Layer** (`repositories/`)
   - Character storage repository
   - Inventory management
   - Journal and campaign data
   - Evolution tracking

### Data Flow

```ascii
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   API Layer  │      │Service Layer │      │  Repository  │
│  (FastAPI)   │─────▶│  (Business)  │─────▶│   Layer     │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │   Storage    │
                                            │    Port      │
                                            └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │  Message Hub  │
                                            │  Integration  │
                                            └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │   Storage    │
                                            │   Service    │
                                            └──────────────┘
```

## Implementation Details

### Storage Port Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

class StoragePort(ABC):
    """Interface for storage operations."""

    @abstractmethod
    async def get_character(self, character_id: UUID) -> Optional[Dict]:
        """Get a character by ID."""
        pass

    @abstractmethod
    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List characters with optional filters."""
        pass

    # ... additional methods ...
```

### Key Features

1. **Data Models**
   - All models use UUIDs as primary keys
   - Consistent soft delete pattern
   - Created/Updated timestamps
   - JSONB for flexible data storage
   - Version control for evolution

2. **Character Data**
   - Core character information
   - Character sheet data
   - Evolution history
   - Relationships and connections

3. **Inventory Management**
   - Item tracking and metadata
   - Equipment state
   - Container management
   - Item evolution

4. **Journal System**
   - Session logs
   - Experience tracking
   - Quest management
   - Campaign events

5. **Campaign Integration**
   - Character-campaign relationships
   - Theme management
   - Event impacts
   - NPC relationships

## Configuration

### Environment Variables

Required environment variables:

```bash
# Storage service configuration
STORAGE_SERVICE_URL=http://storage-service:8000
STORAGE_SERVICE_TOKEN=your-token-here

# Message Hub configuration
MESSAGE_HUB_URL=http://message-hub:8200
MESSAGE_HUB_TOKEN=your-token-here

# Redis caching configuration
REDIS_URL=redis://redis:6379
REDIS_CACHE_TTL=3600
```

### Optional Features

1. **Caching**
   ```python
   # In storage_client.py
   class StorageClient(StoragePort):
       def __init__(self, cache: Optional[CacheClient] = None):
           self.cache = cache
   ```

2. **Circuit Breaking**
   ```python
   # In storage_client.py
   @circuit_breaker(
       failure_threshold=5,
       recovery_timeout=60,
       retry_count=3
   )
   async def get_character(self, character_id: UUID):
       # Implementation
   ```

3. **Batch Operations**
   ```python
   # In storage_client.py
   async def bulk_create_characters(
       self,
       characters: List[Dict]
   ) -> List[Dict]:
       # Implementation
   ```

## Testing

### Unit Tests

The repository layer is tested using a mock storage service:

```python
class MockStorageService(StoragePort):
    """Mock storage service for testing."""
    
    def __init__(self):
        self.characters: Dict[UUID, Dict] = {}
        self.inventory_items: Dict[UUID, Dict] = {}
        # ... other storage ...

    async def get_character(self, character_id: UUID):
        return self.characters.get(character_id)

    # ... other methods ...
```

### Integration Tests

Integration tests use the test instance of the Storage Service:

```python
@pytest.fixture
async def storage_client():
    client = StorageClient(
        url=os.getenv("TEST_STORAGE_SERVICE_URL"),
        token=os.getenv("TEST_STORAGE_TOKEN")
    )
    yield client
```

### End-to-End Tests

End-to-end tests verify the complete data flow:

```python
async def test_character_lifecycle(client: AsyncClient):
    # Create character
    response = await client.post("/api/v2/characters", json={...})
    char_id = response.json()["id"]

    # Verify in storage
    stored = await storage_client.get_character(UUID(char_id))
    assert stored is not None
    # ... additional assertions ...
```

## Monitoring

The integration exposes metrics for monitoring:

1. **Operation Metrics**
   - Request counts
   - Error rates
   - Operation latencies

2. **Cache Metrics**
   - Hit/miss rates
   - Cache size
   - Eviction rates

3. **Circuit Breaker Metrics**
   - Open/closed state
   - Failure counts
   - Recovery attempts

## Error Handling

1. **Retries**
   ```python
   @retry(
       retry_on_exceptions=(ConnectionError, TimeoutError),
       max_retries=3,
       backoff_factor=1
   )
   async def storage_operation():
       # Implementation
   ```

2. **Fallbacks**
   ```python
   async def get_character(self, character_id: UUID):
       try:
           return await self._get_from_storage(character_id)
       except StorageServiceError:
           return await self._get_from_cache(character_id)
   ```

3. **Error Reporting**
   ```python
   async def handle_storage_error(
       self,
       operation: str,
       error: Exception,
       context: Dict
   ):
       await self.error_reporter.report(
           service="storage",
           operation=operation,
           error=error,
           context=context
       )
   ```

## Deployment

The Storage Service integration requires:

1. **Service Discovery**
   ```yaml
   # In k8s/deployment.yaml
   spec:
     containers:
       - name: character-service
         env:
           - name: STORAGE_SERVICE_URL
             valueFrom:
               configMapKeyRef:
                 name: service-urls
                 key: storage-service-url
   ```

2. **Secret Management**
   ```yaml
   # In k8s/deployment.yaml
   spec:
     containers:
       - name: character-service
         env:
           - name: STORAGE_SERVICE_TOKEN
             valueFrom:
               secretKeyRef:
                 name: service-tokens
                 key: storage-service-token
   ```

3. **Health Checks**
   ```yaml
   # In k8s/deployment.yaml
   spec:
     containers:
       - name: character-service
         livenessProbe:
           httpGet:
             path: /health
             port: 8000
   ```