# Image Service Documentation Update Plan

## ICD Updates Required

### 1. Remove Direct Service Integration Section
1. Remove section 7 "Integration Endpoints" as it specifies direct service communication
2. Move relevant functionality to Message Hub section

### 2. Update Storage References
1. In Health Check section (line 347):
   ```diff
   - "storage": "healthy"
   + "storage_service": "healthy"
   ```

2. Update Common Error Codes:
   ```diff
   - "STORAGE_ERROR": "Image storage/retrieval failed"
   + "STORAGE_SERVICE_ERROR": "Storage service access failed"
   ```

### 3. Add Storage Service Integration
1. Add new section:
   ```markdown
   ## 11. Storage Service Integration

   ### 11.1 Data Storage Pattern
   All persistent data operations MUST use the storage service's image_storage_db schema:

   - Image metadata and references
   - Theme associations
   - Overlay data
   - Cache indexes
   - Image binary data (via blob storage)

   ### 11.2 Binary Storage
   Large binary data (images) MUST be stored using the storage service's blob storage:
   - Tactical maps
   - Campaign maps
   - Character portraits
   - Item illustrations
   ```

### 4. Update Message Hub Integration
1. Add storage service events:
   ```markdown
   ### 8.3 Storage Service Events
   - image.storage.store
   - image.storage.retrieve
   - image.storage.delete
   - image.storage.list
   ```

2. Update event schema to include storage correlation:
   ```json
   {
     "image_generated": {
       "storage_correlation_id": "uuid",
       "image_id": "uuid",
       "type": "string",
       "source_id": "uuid",
       "timestamp": "string"
     }
   }
   ```

## SRD Updates Required

### 1. Remove Direct Storage Requirements
1. Remove section 3.2.1 "Image Database" and replace with:
   ```markdown
   ### 3.2.1 Storage Service Integration
   
   #### Image Data Storage
   - All image metadata stored in image_storage_db schema
   - Binary image data stored in storage service blob storage
   - Storage service provides version control and backup
   - Cache indexes managed through storage service
   ```

2. Update Performance Requirements section 3.3:
   - Remove direct storage references
   - Add storage service timing requirements
   - Update scalability metrics

### 2. Update Integration Requirements

1. Add new section:
   ```markdown
   ### 3.1.4 Storage Service Integration
   - Uses storage service for all persistent data
   - Implements retry logic for storage operations
   - Maintains data consistency
   - Handles storage service failures gracefully

   #### Storage Service Performance
   - Metadata operations: < 100ms
   - Binary storage operations: < 1s
   - Bulk operations: < 5s
   - Cache operations: < 50ms
   ```

2. Update section 3.1.3 Message Hub Integration:
   ```markdown
   #### Additional Message Hub Requirements
   - All storage operations routed through Message Hub
   - Storage service health monitoring
   - Storage operation metrics collection
   ```

### 3. Update Dependencies Section

1. Revise section 10.1:
   ```markdown
   ### 10.1 Required Services
   - GetImg.AI API
   - Message Hub (for all service communication)
   - Storage Service (for all persistent data)
   - Cache Service (via storage service)

   ### 10.2 Storage Requirements
   - image_storage_db schema in storage service
   - Blob storage for binary data
   - Version control capabilities
   - Data consistency guarantees
   ```

### 4. Update Data Models Section

1. Update Image Model (section 7.1):
   ```markdown
   ### 7.1 Image Model
   All data stored in storage service's image_storage_db schema:

   ```json
   {
     "id": "uuid",
     "storage_id": "uuid",  // Storage service reference
     "type": "map|character|item",
     "subtype": "tactical|campaign|portrait|weapon",
     "content": {
       "storage_path": "string",  // Storage service blob path
       "format": "string",
       "size": {
         "width": "integer",
         "height": "integer"
       }
     },
     "metadata": {
       "theme": "string",
       "source_id": "uuid",
       "service": "string",
       "generation_params": {}
     },
     "overlays": [],
     "references": []
   }
   ```

## Implementation Changes Required

1. Remove all direct storage operations:
   ```python
   # REMOVE:
   database.save_image()
   
   # ADD:
   storage_client.Images.store()
   ```

2. Update service initialization:
   ```python
   # REMOVE:
   db = Database()
   blob_store = BlobStorage()
   
   # ADD:
   storage_client = StorageServiceClient()
   message_hub = MessageHubClient()
   ```

3. Update dependencies:
   ```toml
   # REMOVE:
   sqlalchemy = "^2.0.0"
   asyncpg = "^0.28.0"
   minio = "^7.0.0"
   
   # ADD:
   storage-service-client = "^1.0.0"
   aio-pika = "^9.0.0"
   ```

4. Update metrics collection:
   ```python
   # REMOVE:
   metrics.track_database_operation()
   
   # ADD:
   metrics.track_storage_operation()
   ```