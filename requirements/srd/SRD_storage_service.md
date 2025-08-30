# System Requirements Document: Storage Service (SRD-STORE-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The Storage Service provides centralized, scalable object storage specifically for binary assets in the D&D Character Creator system. It complements (but does not replace) the core services' databases by managing shared binary assets like images, maps, documents, and other files that benefit from centralized storage, versioning, and transformation capabilities.

### 1.1.1 Service Database Separation
This service is explicitly NOT a replacement for core service databases:
- Character Service retains its PostgreSQL database for character data
- Campaign Service keeps its PostgreSQL database for campaign structures
- Image Service maintains its PostgreSQL database for image metadata
- Catalog Service uses its PostgreSQL database for game content

Instead, this service focuses on binary asset management, providing features like:
- Centralized binary storage (images, maps, PDFs)
- Asset versioning and lifecycle management
- Content delivery optimization
- Asset transformation pipelines
- Cross-service asset sharing
- Backup coordination

### 1.2 Service Boundaries

Responsibilities:
- Binary asset storage and retrieval
- Asset versioning and history
- Asset transformation pipelines
- Content delivery optimization
- Cross-service asset sharing
- Backup coordination

NOT Responsibilities:
- Core service data storage (remains in service databases)
- Business logic implementation
- Game content management
- User data storage
- Service state management

### 1.3 Core Mission
- **Asset Management**: Centralized storage for all binary assets
- **Data Protection**: Secure storage with backup and recovery
- **Version Control**: Asset versioning and history tracking
- **Lifecycle Management**: Automated data lifecycle policies
- **Performance Optimization**: Fast and efficient asset delivery

### 1.3 Scope
- Binary asset storage
- Image storage and processing
- Version management
- Access control
- Backup management
- Asset lifecycle
- Content delivery
- Service integration

## 2. Functional Requirements

### 2.1 Asset Management

#### 2.1.1 Asset Operations
- Upload/download
- Copy/move
- Delete/restore
- List/search
- Version control
- Metadata management

#### 2.1.2 Asset Types
- Character portraits
- Campaign maps
- Item images
- Audio files
- Document assets
- Binary blobs
- Backup archives

#### 2.1.3 Version Control
- Version tracking
- Change history
- Rollback support
- Branching
- Tagging
- Conflict resolution

### 2.2 Image Processing

#### 2.2.1 Image Operations
- Resize/crop
- Format conversion
- Optimization
- Thumbnail generation
- Watermarking
- Metadata extraction

#### 2.2.2 Image Delivery
- CDN integration
- Caching
- Streaming
- Progressive loading
- Responsive images
- Format negotiation

### 2.3 Data Protection

#### 2.3.1 Backup System
- Scheduled backups
- Incremental backups
- Point-in-time recovery
- Cross-region replication
- Backup verification
- Restore testing

#### 2.3.2 Security
- Encryption at rest
- Encryption in transit
- Access control
- Audit logging
- Secure deletion
- Compliance controls

### 2.4 Lifecycle Management

#### 2.4.1 Policy Management
- Retention policies
- Archival rules
- Deletion policies
- Version pruning
- Storage tiering
- Cost optimization

#### 2.4.2 Monitoring
- Storage metrics
- Usage tracking
- Performance monitoring
- Error detection
- Capacity planning
- Cost analysis

## 3. Technical Requirements

### 3.1 Performance Requirements
- Upload speed: 50MB/s+
- Download speed: 100MB/s+
- API latency: < 100ms
- High availability: 99.99%
- Concurrent operations: 1000+

### 3.2 Scalability Requirements
- Support 100TB+ storage
- Handle 1M+ assets
- Scale to multiple regions
- Support 1000+ requests/s
- Auto-scaling capability

### 3.3 Reliability Requirements
- Data durability: 99.999999999%
- Automatic failover
- Data replication
- Consistency checks
- Error recovery

### 3.4 Security Requirements
- AES-256 encryption
- Access control
- Audit logging
- WORM support
- Compliance features

## 4. API Endpoints

### 4.1 Asset Operations
```http
POST /api/v2/assets/upload
GET /api/v2/assets/{id}
PUT /api/v2/assets/{id}
DELETE /api/v2/assets/{id}
```

### 4.2 Version Management
```http
GET /api/v2/assets/{id}/versions
POST /api/v2/assets/{id}/versions
PUT /api/v2/assets/{id}/restore
```

### 4.3 Image Processing
```http
POST /api/v2/images/process
POST /api/v2/images/optimize
GET /api/v2/images/{id}/thumbnail
```

### 4.4 Lifecycle Management
```http
POST /api/v2/lifecycle/policy
GET /api/v2/lifecycle/status
POST /api/v2/lifecycle/execute
```

## 5. Data Models

### 5.1 Asset Model
```json
{
  "asset": {
    "id": "uuid",
    "type": "string",
    "name": "string",
    "size": "integer",
    "content_type": "string",
    "checksum": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "metadata": {
      "service": "string",
      "owner": "string",
      "tags": ["string"]
    },
    "versions": ["string"],
    "lifecycle": {
      "policy": "string",
      "retention": "integer",
      "expiration": "timestamp"
    }
  }
}
```

### 5.2 Version Model
```json
{
  "version": {
    "id": "string",
    "asset_id": "uuid",
    "size": "integer",
    "checksum": "string",
    "created_at": "timestamp",
    "created_by": "string",
    "metadata": {
      "change_type": "string",
      "description": "string"
    }
  }
}
```

### 5.3 Policy Model
```json
{
  "policy": {
    "id": "string",
    "name": "string",
    "rules": [
      {
        "type": "retention|archival|deletion",
        "condition": "string",
        "action": "string",
        "parameters": {}
      }
    ],
    "targets": {
      "asset_types": ["string"],
      "paths": ["string"],
      "tags": ["string"]
    }
  }
}
```

## 6. Storage Architecture

### 6.1 Storage Tiers
```yaml
tiers:
  hot:
    type: "s3"
    class: "standard"
    replicas: 3
    lifecycle:
      enabled: true
      rules:
        - age: 30
          action: "move_to_warm"
  
  warm:
    type: "s3"
    class: "infrequent_access"
    lifecycle:
      enabled: true
      rules:
        - age: 90
          action: "move_to_cold"
  
  cold:
    type: "glacier"
    retrieval: "standard"
    lifecycle:
      enabled: true
      rules:
        - age: 365
          action: "delete"
```

### 6.2 Backup Configuration
```yaml
backup:
  schedule: "daily"
  retention: "90d"
  type: "incremental"
  encryption: true
  verification: true
  locations:
    - region: "primary"
      copies: 2
    - region: "dr"
      copies: 1
```

## 7. Integration Patterns

### 7.1 Message Hub Events
Published Events:
- storage.asset_created
- storage.asset_updated
- storage.asset_deleted
- storage.version_created
- storage.lifecycle_executed

Subscribed Events:
- service.asset_requested
- service.backup_requested
- service.policy_updated
- monitoring.alert_triggered

### 7.2 Service Integration
```yaml
services:
  image_service:
    asset_types:
      - portraits
      - maps
      - items
    operations:
      - upload
      - process
      - optimize
  
  campaign_service:
    asset_types:
      - maps
      - documents
      - audio
    operations:
      - upload
      - version
      - share
  
  backup_service:
    operations:
      - backup
      - restore
      - verify
      - report
```

## 8. Monitoring

### 8.1 Metrics
- Storage utilization
- Operation latency
- Throughput
- Error rates
- Backup status
- Version counts
- Cost analysis

### 8.2 Alerts
- Storage capacity
- Backup failures
- Operation errors
- Policy violations
- Performance issues
- Security events
- Cost thresholds

## 9. Compliance

### 9.1 Data Protection
- Encryption standards
- Access controls
- Audit trails
- Retention policies
- Data sovereignty
- Privacy controls

### 9.2 Recovery Capabilities
- RTO objectives
- RPO objectives
- Recovery testing
- Backup validation
- Disaster recovery
- Business continuity
