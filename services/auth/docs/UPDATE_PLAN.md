# Auth Service Documentation Update Plan

## ICD Updates Required

### 1. Update Overview Section
1. Add storage service integration description:
   ```markdown
   ### 1.5 Data Persistence
   - All persistent data is stored in auth_db schema via storage service
   - No direct database connections permitted
   - Data access via storage service events through Message Hub
   - Schema managed through storage service
   ```

### 2. Add Storage Service Event Patterns
1. Add new section:
   ```markdown
   ## 10. Storage Service Integration

   ### 10.1 Data Operations
   All data operations MUST be performed through storage service events:

   #### User Operations
   ```json
   {
     "operation": "query",
     "database": "auth_db",
     "table": "users",
     "type": "select",
     "fields": ["id", "username", "status"],
     "where": {
       "username": "value",
       "status": "active"
     }
   }
   ```

   #### Session Operations
   ```json
   {
     "operation": "write",
     "database": "auth_db",
     "table": "sessions",
     "type": "insert",
     "data": {
       "user_id": "uuid",
       "token": "string",
       "expires_at": "timestamp"
     }
   }
   ```

   #### Role Operations
   ```json
   {
     "operation": "transaction",
     "database": "auth_db",
     "operations": [
       {
         "type": "insert",
         "table": "roles",
         "data": {}
       },
       {
         "type": "insert",
         "table": "user_roles",
         "data": {}
       }
     ]
   }
   ```
   ```

### 3. Update Client Libraries
1. Remove direct database references:
   ```diff
   # Python Client
   - db = Database()
   + storage_client = StorageServiceClient()

   # Update operation example
   - async def get_user(self, user_id):
   -     return await db.users.get(user_id)
   + async def get_user(self, user_id):
   +     result = await message_hub.request(
   +         "storage.query",
   +         {
   +             "database": "auth_db",
   +             "table": "users",
   +             "where": {"id": user_id}
   +         }
   +     )
   +     return result.data
   ```

### 4. Update Event System
1. Add storage events to Published Events:
   ```markdown
   #### 3.1.3 Storage Events
   ```json
   {
     "event": "auth.storage.operation",
     "data": {
       "operation": "query|write|transaction",
       "database": "auth_db",
       "correlation_id": "uuid",
       "timestamp": "datetime"
     }
   }
   ```
   ```

2. Add storage events to Subscribed Events:
   ```markdown
   #### 3.2.3 Storage Events
   ```json
   {
     "event": "storage.operation.complete",
     "data": {
       "operation_id": "uuid",
       "status": "success|error",
       "result": {},
       "correlation_id": "uuid"
     }
   }
   ```
   ```

## SRD Updates Required

### 1. Update Technical Requirements
1. Remove direct database references:
   ```diff
   ### 7.1 Infrastructure
   - Database clustering
   - Redis for sessions
   + Storage service integration for persistence
   + Cache service integration for sessions
   ```

2. Add storage service requirements:
   ```markdown
   ### 3.5 Storage Requirements
   - Storage service response time: < 50ms
   - Transaction consistency guarantee
   - Schema versioning support
   - Data isolation per service
   - Backup and recovery support
   ```

### 2. Update Data Models
1. Add storage context:
   ```markdown
   ## 5. Data Models

   All data models are stored in the auth_db schema managed by the storage service:
   - Users table: User authentication data
   - Sessions table: Active session tracking
   - Roles table: Role definitions and hierarchies
   - Permissions table: Permission assignments
   - API Keys table: Service API key management
   ```

### 3. Update Integration Requirements
1. Add storage service integration:
   ```markdown
   ### 3.3 Integration Requirements

   #### 3.3.3 Storage Service Integration
   - Event-driven data access
   - Schema version management
   - Transaction coordination
   - Data consistency handling
   - Backup coordination
   ```

### 4. Update Session Management
1. Update session handling:
   ```markdown
   ### 2.3 Session Management

   #### 2.3.1 Session Handling
   - Session data stored in auth_db via storage service
   - Session lookups through storage service events
   - Cache service integration for performance
   - Message hub coordination for updates
   ```

## Implementation Changes Required

1. Update service initialization:
   ```python
   # REMOVE:
   database = Database()
   redis_client = Redis()

   # ADD:
   message_hub = MessageHubClient()
   storage_client = StorageServiceClient()
   cache_client = CacheServiceClient()
   ```

2. Update data access patterns:
   ```python
   # REMOVE:
   async def get_user(user_id):
       return await db.users.get(user_id)

   # ADD:
   async def get_user(user_id):
       result = await message_hub.request(
           "storage.query",
           {
               "database": "auth_db",
               "table": "users",
               "where": {"id": user_id}
           }
       )
       return result.data
   ```

3. Update session management:
   ```python
   # REMOVE:
   async def create_session(user_id, token):
       await db.sessions.create({
           "user_id": user_id,
           "token": token
       })
       await redis_client.set(f"session:{token}", user_id)

   # ADD:
   async def create_session(user_id, token):
       # Store in storage service
       await message_hub.request(
           "storage.write",
           {
               "database": "auth_db",
               "table": "sessions",
               "data": {
                   "user_id": user_id,
                   "token": token
               }
           }
       )
       # Cache for performance
       await message_hub.request(
           "cache.set",
           {
               "key": f"session:{token}",
               "value": user_id
           }
       )
   ```

4. Update token validation:
   ```python
   # REMOVE:
   async def validate_token(token):
       user_id = await redis_client.get(f"session:{token}")
       if not user_id:
           user_id = await db.sessions.get_user_id(token)
           if user_id:
               await redis_client.set(f"session:{token}", user_id)
       return user_id

   # ADD:
   async def validate_token(token):
       # Try cache first
       result = await message_hub.request(
           "cache.get",
           {"key": f"session:{token}"}
       )
       if result.exists:
           return result.value

       # Query storage
       result = await message_hub.request(
           "storage.query",
           {
               "database": "auth_db",
               "table": "sessions",
               "where": {"token": token}
           }
       )
       if result.data:
           # Cache for subsequent requests
           await message_hub.request(
               "cache.set",
               {
                   "key": f"session:{token}",
                   "value": result.data["user_id"]
               }
           )
           return result.data["user_id"]
       return None
   ```