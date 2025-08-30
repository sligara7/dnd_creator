# Storage Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-30

## 1. Interface Overview

### 1.1 Purpose
This document defines the interfaces for the Storage Service, including APIs, events, and integration patterns for managing binary assets and content across the D&D Character Creator platform.

### 1.2 Scope
- Asset management endpoints
- Version control interfaces
- Backup management APIs
- Service integrations
- Monitoring interfaces

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Asset Operations
```http
POST /api/v2/assets/upload
POST /api/v2/assets/batch-upload
GET /api/v2/assets/{id}
PUT /api/v2/assets/{id}
DELETE /api/v2/assets/{id}
HEAD /api/v2/assets/{id}
GET /api/v2/assets/{id}/metadata
```

#### 2.1.2 Version Operations
```http
GET /api/v2/assets/{id}/versions
POST /api/v2/assets/{id}/versions
GET /api/v2/assets/{id}/versions/{version_id}
PUT /api/v2/assets/{id}/versions/{version_id}
DELETE /api/v2/assets/{id}/versions/{version_id}
```

#### 2.1.3 Backup Operations
```http
POST /api/v2/backups
GET /api/v2/backups/{id}
GET /api/v2/backups/{id}/status
POST /api/v2/backups/{id}/restore
GET /api/v2/backups/policy
```

### 2.2 Request/Response Format

#### 2.2.1 Upload Request
```json
{
  "upload_request": {
    "asset": {
      "content_type": "string",
      "filename": "string",
      "metadata": {},
      "tags": ["array"],
      "acl": {
        "read": ["array"],
        "write": ["array"]
      }
    },
    "options": {
      "versioning": "boolean",
      "compression": "boolean",
      "encryption": "boolean",
      "retention": "string"
    }
  }
}
```

#### 2.2.2 Asset Response
```json
{
  "asset_response": {
    "id": "uuid",
    "url": "string",
    "version": "string",
    "metadata": {
      "content_type": "string",
      "size": "integer",
      "created_at": "timestamp",
      "checksum": "string",
      "tags": ["array"]
    },
    "storage": {
      "bucket": "string",
      "path": "string",
      "class": "string"
    }
  }
}
```

## 3. Event Interfaces

### 3.1 Published Events

#### 3.1.1 Asset Events
```json
{
  "event": "storage.asset.created",
  "data": {
    "asset_id": "string",
    "version": "string",
    "metadata": {},
    "timestamp": "datetime"
  }
}
```

#### 3.1.2 Version Events
```json
{
  "event": "storage.version.created",
  "data": {
    "asset_id": "string",
    "version_id": "string",
    "changes": ["array"],
    "timestamp": "datetime"
  }
}
```

### 3.2 Subscribed Events

#### 3.2.1 Lifecycle Events
```json
{
  "event": "storage.lifecycle.transition",
  "data": {
    "asset_id": "string",
    "action": "string",
    "target_class": "string",
    "timestamp": "datetime"
  }
}
```

#### 3.2.2 Retention Events
```json
{
  "event": "storage.retention.update",
  "data": {
    "asset_id": "string",
    "policy": "string",
    "duration": "string",
    "timestamp": "datetime"
  }
}
```

## 4. Service Integration

### 4.1 Character Service
```yaml
integration:
  service: character
  asset_types:
    - portraits:
        formats: ["image/jpeg", "image/png"]
        max_size: 10MB
        retention: 365d
    - character_sheets:
        formats: ["application/pdf"]
        max_size: 5MB
        retention: 365d
```

### 4.2 Campaign Service
```yaml
integration:
  service: campaign
  asset_types:
    - maps:
        formats: ["image/jpeg", "image/png"]
        max_size: 25MB
        retention: 365d
    - session_notes:
        formats: ["text/markdown", "application/pdf"]
        max_size: 10MB
        retention: 365d
```

### 4.3 Image Service
```yaml
integration:
  service: image
  asset_types:
    - generated_images:
        formats: ["image/png", "image/jpeg"]
        max_size: 15MB
        retention: 30d
    - templates:
        formats: ["image/png"]
        max_size: 5MB
        retention: 365d
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_storage import StorageClient

client = StorageClient(
    service="character_service",
    options={
        "versioning": True,
        "compression": True,
        "encryption": True
    }
)

# Upload asset
response = client.upload_asset(
    file_path="portrait.png",
    metadata={
        "character_id": "char123",
        "type": "portrait"
    },
    tags=["portrait", "character"]
)

# Get asset
asset = client.get_asset(asset_id)

# Update asset
client.update_asset(
    asset_id,
    new_file_path="updated_portrait.png",
    metadata={"version": "2"}
)
```

### 5.2 Go Client
```go
package main

import "dnd/storage"

func main() {
    client := storage.NewClient(&storage.Config{
        Service: "campaign_service",
        Options: storage.Options{
            Versioning: true,
            Compression: true,
            Encryption: true,
        },
    })

    // Upload asset
    response, err := client.UploadAsset(ctx, &storage.UploadRequest{
        FilePath: "map.jpg",
        Metadata: map[string]interface{}{
            "campaign_id": "camp123",
            "type": "map",
        },
        Tags: []string{"map", "campaign"},
    })
}
```

## 6. Backup Interface

### 6.1 Backup Configuration
```yaml
backup:
  schedule:
    full:
      frequency: "daily"
      retention: "30d"
      time: "00:00"
    incremental:
      frequency: "hourly"
      retention: "7d"

  targets:
    - type: "s3"
      bucket: "backup-bucket"
      prefix: "daily/"
    - type: "local"
      path: "/backup/storage"
```

### 6.2 Restore Configuration
```yaml
restore:
  options:
    - type: "point-in-time"
      parameters:
        timestamp: "datetime"
        consistency: "strong"
    - type: "selective"
      parameters:
        asset_ids: ["array"]
        versions: ["array"]
```

## 7. Lifecycle Interface

### 7.1 Policy Configuration
```yaml
lifecycle:
  rules:
    - name: "archive_old_assets"
      condition:
        age: "90d"
        accessed: "never"
      action: "move_to_archive"
    
    - name: "delete_temp_assets"
      condition:
        tag: "temporary"
        age: "7d"
      action: "delete"
```

### 7.2 Storage Classes
```yaml
storage_classes:
  hot:
    type: "standard"
    availability: "immediate"
    cost: "high"
  
  warm:
    type: "infrequent_access"
    availability: "within_hours"
    cost: "medium"
  
  cold:
    type: "archive"
    availability: "within_days"
    cost: "low"
```

## 8. Security Interface

### 8.1 Authentication
```yaml
auth:
  type: "bearer"
  roles:
    - storage_reader
    - storage_writer
    - storage_admin
  scope: "storage:read storage:write"
```

### 8.2 Authorization
```yaml
permissions:
  read:
    - "assets:read"
    - "versions:read"
    - "metadata:read"
  write:
    - "assets:write"
    - "versions:write"
    - "metadata:write"
  admin:
    - "backups:admin"
    - "lifecycle:admin"
    - "policy:admin"
```

## 9. Monitoring Interface

### 9.1 Metrics
```yaml
metrics:
  storage:
    - name: storage_usage_bytes
      type: gauge
      labels: [service, class]
    - name: storage_operations_total
      type: counter
      labels: [operation, status]
  
  backup:
    - name: backup_status
      type: gauge
      labels: [type, target]
    - name: backup_duration_seconds
      type: histogram
      labels: [type, target]
```

### 9.2 Health Checks
```http
GET /health/live
GET /health/ready
GET /health/metrics
```

## 10. Configuration Interface

### 10.1 Service Configuration
```yaml
config:
  storage:
    base_path: "/data/storage"
    max_file_size: "100MB"
    supported_types: ["image/*", "application/pdf"]
    temp_dir: "/tmp/storage"
  
  versioning:
    enabled: true
    max_versions: 10
    retention: "90d"
  
  compression:
    enabled: true
    algorithm: "gzip"
    min_size: "1KB"
```

### 10.2 Integration Configuration
```yaml
integrations:
  character_service:
    asset_types:
      - name: portrait
        formats: ["image/jpeg", "image/png"]
        max_size: "10MB"
      - name: sheet
        formats: ["application/pdf"]
        max_size: "5MB"
  
  campaign_service:
    asset_types:
      - name: map
        formats: ["image/jpeg", "image/png"]
        max_size: "25MB"
      - name: document
        formats: ["application/pdf", "text/markdown"]
        max_size: "10MB"
```
