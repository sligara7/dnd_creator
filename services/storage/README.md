# Storage Service

## Overview

The Storage Service provides centralized binary asset storage and management for the D&D Character Creator system. It handles all binary assets including images, documents, maps, and other files, providing versioning, lifecycle management, and backup capabilities.

## Status

**Current Status:** IN PROGRESS  
**Initial Implementation:** 2025-09-07

### Completed Features
- ✅ Core infrastructure and configuration
- ✅ Database models (Asset, Version, Policy, Backup)
- ✅ S3/MinIO integration client
- ✅ FastAPI application structure
- ✅ Health check endpoints
- ✅ Alembic migration setup

### In Progress
- Asset management service implementation
- API endpoint completion
- Message Hub integration

## Architecture

### Technology Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL with asyncpg
- **Object Storage:** MinIO (development) / S3 (production)
- **Caching:** Redis (configured, not yet implemented)
- **ORM:** SQLAlchemy with async support
- **Migration:** Alembic

### Key Design Patterns
- **Async/Await:** Throughout for optimal performance
- **Repository Pattern:** For data access abstraction
- **Service Layer:** For business logic encapsulation
- **Soft Delete:** For data recovery capabilities
- **UUID Primary Keys:** For distributed system compatibility
- **Event-Driven:** Via Message Hub integration

## API Endpoints

### Health Checks
- `GET /health` - Combined health status
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

### Asset Management (In Development)
- `POST /api/v2/assets/upload` - Upload asset
- `GET /api/v2/assets/{id}` - Get asset
- `PUT /api/v2/assets/{id}` - Update asset
- `DELETE /api/v2/assets/{id}` - Delete asset
- `GET /api/v2/assets` - List assets

### Version Management (In Development)
- `GET /api/v2/assets/{id}/versions` - List versions
- `POST /api/v2/assets/{id}/versions` - Create version
- `GET /api/v2/assets/{id}/versions/{version_id}` - Get specific version

### Lifecycle Policies (In Development)
- `GET /api/v2/policies` - List policies
- `POST /api/v2/policies` - Create policy
- `PUT /api/v2/policies/{id}` - Update policy
- `DELETE /api/v2/policies/{id}` - Delete policy

### Backup Management (In Development)
- `POST /api/v2/backups` - Create backup
- `GET /api/v2/backups/{id}` - Get backup status
- `POST /api/v2/backups/{id}/restore` - Restore from backup

## Configuration

### Environment Variables

```bash
# Service Configuration
STORAGE_SERVICE_NAME=storage-service
STORAGE_PORT=8005
STORAGE_ENVIRONMENT=development

# Database
STORAGE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/storage_db

# S3/MinIO
STORAGE_S3_ENDPOINT_URL=http://localhost:9000
STORAGE_S3_ACCESS_KEY_ID=minioadmin
STORAGE_S3_SECRET_ACCESS_KEY=minioadmin
STORAGE_S3_BUCKET_NAME=dnd-storage
STORAGE_S3_REGION=us-east-1

# Redis
STORAGE_REDIS_URL=redis://localhost:6379/0

# Message Hub
STORAGE_MESSAGE_HUB_URL=http://message-hub:8200

# Storage Settings
STORAGE_MAX_UPLOAD_SIZE=104857600  # 100MB
STORAGE_MAX_VERSIONS=10
STORAGE_VERSION_RETENTION_DAYS=90

# Backup Settings
STORAGE_BACKUP_ENABLED=true
STORAGE_BACKUP_RETENTION_DAYS=30
```

## Database Schema

### Core Tables
- **assets** - Main asset storage metadata
- **asset_versions** - Version history for assets
- **asset_metadata** - Extended metadata key-value pairs
- **lifecycle_policies** - Lifecycle management rules
- **policy_rules** - Individual rules within policies
- **backup_jobs** - Backup job tracking

### Key Features
- UUID primary keys for all entities
- Soft delete support with is_deleted flag
- Automatic timestamp tracking (created_at, updated_at)
- Comprehensive indexes for performance
- Foreign key relationships with CASCADE delete

## Development

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- MinIO or S3-compatible storage
- Redis (optional but recommended)
- Poetry for dependency management

### Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up database:
```bash
# Create database
createdb storage_db

# Run migrations
poetry run alembic upgrade head
```

3. Start MinIO (for local development):
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

4. Run the service:
```bash
poetry run uvicorn storage.main:app --reload --port 8005
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=storage --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_assets.py
```

## Integration

### Message Hub Events

#### Published Events
- `storage.asset.created` - When a new asset is uploaded
- `storage.asset.updated` - When an asset is modified
- `storage.asset.deleted` - When an asset is deleted
- `storage.version.created` - When a new version is created
- `storage.backup.completed` - When a backup job completes

#### Subscribed Events
- `service.asset.requested` - Request for asset upload
- `service.backup.requested` - Request for backup operation
- `service.policy.updated` - Policy update notifications

### Service Dependencies
- **Message Hub** - For event-driven communication
- **Auth Service** - For access control (when implemented)
- **Cache Service** - For performance optimization

## Performance Targets

Per SRD requirements:
- Upload speed: 50MB/s+
- Download speed: 100MB/s+
- API latency: < 100ms
- High availability: 99.99%
- Concurrent operations: 1000+

## Monitoring

### Metrics (Prometheus)
- Storage utilization
- Operation latency
- Upload/download throughput
- Error rates
- Cache hit rates (when implemented)

### Health Checks
- Database connectivity
- S3/MinIO accessibility
- Redis connection (when implemented)

## Security

### Current Implementation
- CORS configuration
- Environment-based configuration
- Checksum validation for uploads
- Soft delete for data recovery

### Planned Enhancements
- Encryption at rest
- Access control lists
- Audit logging
- Rate limiting
- Security scanning

## Documentation

- [Service Requirements Document (SRD)](./SRD_storage_service.md)
- [Interface Control Document (ICD)](./ICD_storage_service.md)
- [Completion Tasks](./COMPLETION_TASKS.md)
- [Project WARP](../../WARP.md)

## Next Steps

1. Complete asset repository and service layers
2. Implement full CRUD API endpoints
3. Add Message Hub integration
4. Create comprehensive test suite
5. Add Redis caching layer
6. Implement lifecycle policies
7. Add backup scheduling

## License

Part of the D&D Character Creator system - Internal use only.
