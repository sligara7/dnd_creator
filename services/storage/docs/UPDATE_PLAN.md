# Storage Service Documentation Update Plan

## ICD Updates Required

### 1. Update Overview Section
1. Replace section 1.1 with centralized database description:
   ```markdown
   ### 1.1 Purpose
   The Storage Service is the centralized data persistence layer for the entire D&D Character Creator system, providing:
   1. Isolated sub-databases for each service
   2. Binary asset storage and management
   3. Version control and backup
   4. Schema management
   5. Data consistency guarantees

   All persistent data storage MUST go through this service - no other service is permitted to directly manage databases or permanent storage.
   ```

2. Add sub-database specification:
   ```markdown
   ### 1.2 Service Databases
   Each service has a dedicated database schema:

   - character_db: Character Service data
   - campaign_db: Campaign Service data
   - auth_db: Auth Service data
   - metrics_db: Metrics Service data
   - catalog_db: Catalog Service data
   - image_storage_db: Image Service data
   - search_db: Search Service data

   ### 1.3 Database Access Pattern
   - All database access MUST be routed through Message Hub
   - No direct database connections from other services
   - Each service has isolated schema access
   - Cross-service data access via Message Hub events
   ```

### 2. Add Database API Section
1. Add new section:
   ```markdown
   ## 11. Database Operations API

   ### 11.1 Query Operations
   ```json
   {
     "operation": "query",
     "database": "character_db",
     "query": {
       "type": "select",
       "table": "characters",
       "fields": ["id", "name"],
       "where": {
         "field": "level",
         "operator": ">",
         "value": 5
       }
     }
   }
   ```

   ### 11.2 Write Operations
   ```json
   {
     "operation": "write",
     "database": "campaign_db",
     "transaction": {
       "operations": [
         {
           "type": "insert",
           "table": "campaigns",
           "data": {}
         },
         {
           "type": "update",
           "table": "chapters",
           "data": {},
           "where": {}
         }
       ]
     }
   }
   ```

   ### 11.3 Schema Operations
   ```json
   {
     "operation": "schema",
     "database": "auth_db",
     "action": "migrate",
     "version": "1.2.0",
     "migrations": [
       {
         "up": "CREATE TABLE users...",
         "down": "DROP TABLE users..."
       }
     ]
   }
   ```
   ```

### 3. Update Event System
1. Add database event patterns:
   ```markdown
   ### 3.3 Database Events

   #### Database Operation Events
   - storage.db.query_complete
   - storage.db.write_complete
   - storage.db.transaction_complete
   - storage.db.error
   - storage.db.deadlock
   - storage.db.migration_complete

   #### Schema Events
   - storage.schema.update_requested
   - storage.schema.update_complete
   - storage.schema.version_change
   ```

### 4. Update Service Integration
1. Replace section 4 with new database-centric integration:
   ```markdown
   ## 4. Service Database Integration

   ### 4.1 Character Service Database
   ```yaml
   database:
     name: character_db
     schemas:
       - characters
       - inventories
       - journals
       - progression
     access:
       service: character
       permissions: [read, write, schema]
   ```

   ### 4.2 Campaign Service Database
   ```yaml
   database:
     name: campaign_db
     schemas:
       - campaigns
       - chapters
       - npcs
       - plots
     access:
       service: campaign
       permissions: [read, write, schema]
   ```
   ```

## SRD Updates Required

### 1. Update System Overview
1. Replace section 1.1.1 with:
   ```markdown
   ### 1.1.1 Centralized Database Service
   This service is the ONLY service permitted to directly manage databases:
   - All other services must access data through this service
   - Each service has an isolated database schema
   - No direct database connections are permitted
   - All database operations route through Message Hub
   ```

### 2. Add Database Management Section
1. Add new section:
   ```markdown
   ## 10. Database Management

   ### 10.1 Schema Management
   - Schema version control
   - Migration coordination
   - Dependency tracking
   - Schema validation
   - Breaking change detection

   ### 10.2 Data Consistency
   - Transaction management
   - Isolation levels
   - Deadlock detection
   - Referential integrity
   - Constraint enforcement

   ### 10.3 Database Operations
   - Query optimization
   - Connection pooling
   - Statement caching
   - Index management
   - Statistics collection
   ```

### 3. Update Technical Requirements
1. Add database-specific requirements:
   ```markdown
   ### 3.5 Database Requirements
   - Query latency: < 50ms (95th percentile)
   - Write latency: < 100ms (95th percentile)
   - Transaction throughput: 1000+ TPS
   - Connection pool: 100+ connections/service
   - Schema changes: Zero-downtime
   ```

### 4. Update Integration Patterns
1. Add database event patterns:
   ```markdown
   ### 7.3 Database Event Patterns

   Request Flow:
   1. Service sends database operation request
   2. Storage service validates request
   3. Storage service executes operation
   4. Storage service publishes result
   5. Requesting service processes result

   Common Events:
   - service.db.query_request
   - storage.db.query_complete
   - service.db.write_request
   - storage.db.write_complete
   - service.db.transaction_begin
   - storage.db.transaction_complete
   ```

## Implementation Changes Required

1. Add database routing configuration:
   ```python
   # Database routing configuration
   DATABASE_CONFIG = {
       "character_db": {
           "service": "character",
           "schema": "public",
           "pool_size": 50,
           "max_overflow": 10
       },
       "campaign_db": {
           "service": "campaign",
           "schema": "public",
           "pool_size": 50,
           "max_overflow": 10
       }
   }

   async def route_database_request(message: DatabaseRequest):
       database = DATABASE_CONFIG.get(message.database)
       if not database:
           raise InvalidDatabaseError()
       
       if message.service != database["service"]:
           raise UnauthorizedAccessError()
       
       await process_database_request(message)
   ```

2. Add schema management:
   ```python
   # Schema version management
   SCHEMA_VERSIONS = {
       "character_db": "1.0.0",
       "campaign_db": "1.0.0",
       "auth_db": "1.0.0"
   }

   async def handle_schema_migration(message: SchemaMigration):
       if not await validate_schema_change(message):
           raise InvalidSchemaError()
       
       await apply_schema_migration(message)
       await publish_schema_event("schema.update_complete", message)
   ```

3. Add transaction coordination:
   ```python
   # Transaction management
   async def handle_transaction(message: TransactionRequest):
       async with database.transaction():
           try:
               for operation in message.operations:
                   await execute_operation(operation)
               await commit_transaction()
               await publish_event("transaction.complete", message)
           except Exception as e:
               await rollback_transaction()
               await publish_event("transaction.failed", message, error=e)
   ```