# Message Hub Documentation Update Plan

## ICD Updates Required

### 1. Add Storage Service Integration
1. Add new section for storage service event patterns:
   ```markdown
   ### 3.4 Storage Service Integration

   #### Storage Service Events
   Published by Storage Service:
   - `storage.operation_completed`: Storage operation completed
   - `storage.operation_failed`: Storage operation failed
   - `storage.schema_updated`: Database schema updated
   - `storage.backup_completed`: Backup operation completed

   Consumed by Storage Service:
   - `storage.operation_request`: Request for storage operation
   - `storage.schema_request`: Request for schema operation
   - `storage.backup_request`: Request for backup operation
   ```

2. Add storage service circuit breaker handling:
   ```markdown
   ### 5.3 Storage Service Circuit Breaking
   The Message Hub manages circuit breaking for storage service operations:
   - Monitor storage service health
   - Track operation success/failure
   - Manage circuit state transitions
   - Coordinate retry attempts
   - Handle failover scenarios
   ```

### 2. Update Event System
1. Add standard event routing patterns for storage operations:
   ```markdown
   ### 3.5 Standard Event Routing

   #### Storage Operation Pattern
   1. Service sends operation request
   2. Message Hub routes to storage service
   3. Storage service processes request
   4. Storage service publishes result
   5. Message Hub routes result to requesting service

   #### Example Flow:
   ```json
   {
     "request": {
       "type": "storage_operation",
       "operation": "query",
       "source_service": "character",
       "database": "character_db",
       "correlation_id": "uuid",
       "payload": {
         "query": "...",
         "parameters": {}
       }
     },
     "response": {
       "type": "storage_result",
       "operation": "query",
       "source": "storage",
       "correlation_id": "uuid",
       "status": "success",
       "payload": {
         "results": []
       }
     }
   }
   ```
   ```

### 3. Add Service Schema Management
1. Add new section for database schema management:
   ```markdown
   ### 3.6 Schema Management Events

   The Message Hub coordinates database schema updates:
   - Schema version tracking
   - Migration coordination
   - Schema deployment
   - Service notification

   Events:
   - `schema.update_requested`
   - `schema.update_started`
   - `schema.update_completed`
   - `schema.update_failed`
   ```

## SRD Updates Required

### 1. Add Storage Service Requirements
1. Add new section:
   ```markdown
   ### 2.6 Storage Service Coordination
   - FR6.1: Route storage operation requests
   - FR6.2: Track storage operation status
   - FR6.3: Manage storage service health
   - FR6.4: Coordinate schema updates
   - FR6.5: Handle storage service failures

   #### Storage Operation Requirements
   - Guaranteed delivery of storage requests
   - Operation correlation tracking
   - Transaction coordination
   - Error handling and recovery
   - Status propagation
   ```

### 2. Update Performance Requirements
1. Add storage operation timing requirements:
   ```markdown
   ### 3.1 Performance Requirements
   - NFR1.5: Storage operation routing < 5ms
   - NFR1.6: Storage transaction coordination < 50ms
   - NFR1.7: Schema update coordination < 1s
   ```

### 3. Add Data Consistency Requirements
1. Add new section:
   ```markdown
   ### 3.5 Data Consistency
   - NFR5.1: Transaction consistency across services
   - NFR5.2: Schema version consistency
   - NFR5.3: Storage operation ordering
   - NFR5.4: Event-storage synchronization
   - NFR5.5: State recovery procedures
   ```

### 4. Update System Architecture
1. Add storage coordination component:
   ```markdown
   ### 4.1 Components

   6. **Storage Coordinator**
      - Storage operation routing
      - Transaction management
      - Schema coordination
      - Failover handling
      - State synchronization
   ```

### 5. Add Storage Event Patterns
1. Add new section:
   ```markdown
   ### 5.4 Storage Event Patterns
   - SEP1.1: Operation request/response
   - SEP1.2: Transaction coordination
   - SEP1.3: Schema management
   - SEP1.4: Backup coordination
   - SEP1.5: State synchronization
   ```

## Implementation Changes Required

1. Add storage service event routing:
   ```python
   # Add storage routing configuration
   STORAGE_ROUTES = {
       "character": "character_db",
       "campaign": "campaign_db",
       "auth": "auth_db",
       "metrics": "metrics_db",
       "catalog": "catalog_db"
   }

   async def route_storage_request(message: StorageRequest):
       service = message.source_service
       database = STORAGE_ROUTES.get(service)
       if not database:
           raise InvalidRouteError()
       
       message.set_database(database)
       await storage_queue.put(message)
   ```

2. Add schema management:
   ```python
   # Add schema version tracking
   SCHEMA_VERSIONS = {
       "character_db": "1.0.0",
       "campaign_db": "1.0.0",
       "auth_db": "1.0.0",
       "metrics_db": "1.0.0",
       "catalog_db": "1.0.0"
   }

   async def handle_schema_update(message: SchemaUpdate):
       current_version = SCHEMA_VERSIONS[message.database]
       if message.version <= current_version:
           raise InvalidVersionError()
           
       await coordinate_schema_update(message)
   ```

3. Update health monitoring:
   ```python
   # Add storage health tracking
   async def check_storage_health():
       status = await storage_service.check_health()
       for db, health in status.databases.items():
           circuit = circuit_breakers.get(f"storage.{db}")
           if health.status == "unhealthy":
               await circuit.open()
           else:
               await circuit.close()
   ```

4. Add transaction coordination:
   ```python
   # Add transaction management
   async def coordinate_transaction(message: TransactionRequest):
       transaction = await begin_transaction()
       try:
           for operation in message.operations:
               await execute_operation(operation, transaction)
           await commit_transaction(transaction)
       except Exception as e:
           await rollback_transaction(transaction)
           raise TransactionError(str(e))
   ```