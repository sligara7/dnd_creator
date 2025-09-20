# Database Migration Plan for Campaign and Image Services

## Overview
This plan outlines the steps to migrate the Campaign and Image service databases into the Storage Service as sub-services while maintaining their existing schema structures.

## 1. Directory Structure Updates

### Create New Module Structure
```bash
services/storage/
├── src/
│   ├── storage_service/
│   │   ├── databases/
│   │   │   ├── campaign_db/          # Campaign database module
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py         # Sqlalchemy models
│   │   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   │   └── migrations/
│   │   │   │       └── versions/
│   │   │   └── image_db/             # Image database module
│   │   │       ├── __init__.py
│   │   │       ├── models.py         # Sqlalchemy models
│   │   │       ├── schemas.py        # Pydantic schemas
│   │   │       └── migrations/
│   │   │           └── versions/
│   │   └── storage_service.py
└── alembic/
    ├── versions/
    │   ├── campaign_db/              # Campaign migrations
    │   └── image_db/                 # Image migrations
    └── env.py
```

## 2. Schema Migration

### 2.1 Campaign Database Schema

#### Move Campaign Tables
```sql
-- In storage_db schema
CREATE SCHEMA campaign_db;

-- Move existing tables to new schema
ALTER TABLE campaigns SET SCHEMA campaign_db;
ALTER TABLE chapters SET SCHEMA campaign_db;

-- Update sequences and dependencies
ALTER SEQUENCE campaigns_id_seq SET SCHEMA campaign_db;
ALTER SEQUENCE chapters_id_seq SET SCHEMA campaign_db;
```

#### Campaign Database Models
```python
# storage_service/databases/campaign_db/models.py

from uuid import UUID
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from ...db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = {"schema": "campaign_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50), nullable=False, server_default='traditional')
    state = Column(String(50), nullable=False, server_default='draft')
    theme_id = Column(PGUUID(as_uuid=True))
    theme_data = Column(JSON, nullable=False, server_default='{}')
    campaign_metadata = Column(JSON, nullable=False, server_default='{}')
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))

class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = {"schema": "campaign_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    campaign_id = Column(PGUUID(as_uuid=True), ForeignKey('campaign_db.campaigns.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    chapter_type = Column(String(50), nullable=False, server_default='story')
    state = Column(String(50), nullable=False, server_default='draft')
    sequence_number = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False, server_default='{}')
    chapter_metadata = Column(JSON, nullable=False, server_default='{}')
    prerequisites = Column(JSON, nullable=False, server_default='[]')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))
```

### 2.2 Image Database Schema

#### Create Image Tables
```sql
-- In storage_db schema
CREATE SCHEMA image_db;

CREATE TABLE image_db.images (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB NOT NULL,
    overlays JSONB DEFAULT '[]',
    references JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE image_db.overlays (
    id UUID PRIMARY KEY,
    image_id UUID NOT NULL REFERENCES image_db.images(id),
    type VARCHAR(50) NOT NULL,
    elements JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### Image Database Models
```python
# storage_service/databases/image_db/models.py

from uuid import UUID
from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from ...db.base import Base

class Image(Base):
    __tablename__ = "images"
    __table_args__ = {"schema": "image_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    type = Column(String(50), nullable=False)
    subtype = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False)
    overlays = Column(JSON, nullable=False, server_default='[]')
    references = Column(JSON, nullable=False, server_default='[]')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))

class Overlay(Base):
    __tablename__ = "overlays"
    __table_args__ = {"schema": "image_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    image_id = Column(PGUUID(as_uuid=True), ForeignKey('image_db.images.id'))
    type = Column(String(50), nullable=False)
    elements = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))
```

## 3. Data Migration

### 3.1 Campaign Data Migration
```python
# storage_service/databases/campaign_db/migration.py

async def migrate_campaign_data(source_db, target_db):
    """Migrate campaign data to storage service."""
    # Copy campaigns
    campaigns = await source_db.fetch_all(
        "SELECT * FROM campaigns"
    )
    for campaign in campaigns:
        await target_db.execute(
            "INSERT INTO campaign_db.campaigns SELECT * FROM campaign",
            campaign
        )

    # Copy chapters
    chapters = await source_db.fetch_all(
        "SELECT * FROM chapters"
    )
    for chapter in chapters:
        await target_db.execute(
            "INSERT INTO campaign_db.chapters SELECT * FROM chapter",
            chapter
        )

    # Verify migration
    source_count = await source_db.fetch_val(
        "SELECT COUNT(*) FROM campaigns"
    )
    target_count = await target_db.fetch_val(
        "SELECT COUNT(*) FROM campaign_db.campaigns"
    )
    assert source_count == target_count
```

### 3.2 Image Data Migration
```python
# storage_service/databases/image_db/migration.py

async def migrate_image_data(source_db, target_db):
    """Migrate image data to storage service."""
    # Copy images
    images = await source_db.fetch_all(
        "SELECT * FROM images"
    )
    for image in images:
        await target_db.execute(
            "INSERT INTO image_db.images SELECT * FROM image",
            image
        )

    # Copy overlays
    overlays = await source_db.fetch_all(
        "SELECT * FROM overlays"
    )
    for overlay in overlays:
        await target_db.execute(
            "INSERT INTO image_db.overlays SELECT * FROM overlay",
            overlay
        )

    # Verify migration
    source_count = await source_db.fetch_val(
        "SELECT COUNT(*) FROM images"
    )
    target_count = await target_db.fetch_val(
        "SELECT COUNT(*) FROM image_db.images"
    )
    assert source_count == target_count
```

## 4. Client Library Updates

### 4.1 Campaign Database Client
```python
# storage_service/databases/campaign_db/client.py

from typing import Dict, List, Optional
from uuid import UUID

from .models import Campaign, Chapter

class CampaignDBClient:
    def __init__(self, storage_client):
        self.storage = storage_client

    async def get_campaign(self, id: UUID) -> Optional[Dict]:
        return await self.storage.read(
            "campaign_db",
            "campaigns",
            {"id": id, "is_deleted": False}
        )

    async def create_campaign(self, campaign: Dict) -> Dict:
        return await self.storage.write(
            "campaign_db",
            "campaigns",
            campaign
        )

    async def get_chapters(self, campaign_id: UUID) -> List[Dict]:
        return await self.storage.read(
            "campaign_db",
            "chapters",
            {"campaign_id": campaign_id, "is_deleted": False},
            order_by=["sequence_number"]
        )
```

### 4.2 Image Database Client
```python
# storage_service/databases/image_db/client.py

from typing import Dict, List, Optional
from uuid import UUID

from .models import Image, Overlay

class ImageDBClient:
    def __init__(self, storage_client):
        self.storage = storage_client

    async def get_image(self, id: UUID) -> Optional[Dict]:
        return await self.storage.read(
            "image_db",
            "images",
            {"id": id, "is_deleted": False}
        )

    async def create_image(self, image: Dict) -> Dict:
        return await self.storage.write(
            "image_db",
            "images",
            image
        )

    async def get_overlays(self, image_id: UUID) -> List[Dict]:
        return await self.storage.read(
            "image_db",
            "overlays",
            {"image_id": image_id, "is_deleted": False}
        )
```

## 5. Migration Process

### 5.1 Pre-Migration Steps
1. Backup existing databases:
   ```bash
   pg_dump -Fc campaign_db > campaign_db_backup.dump
   pg_dump -Fc image_db > image_db_backup.dump
   ```

2. Create new schemas:
   ```sql
   CREATE SCHEMA campaign_db;
   CREATE SCHEMA image_db;
   ```

3. Update storage service configuration:
   ```yaml
   storage:
     databases:
       campaign_db:
         schema: campaign_db
         migrations: true
         backup: true
       image_db:
         schema: image_db
         migrations: true
         backup: true
   ```

### 5.2 Migration Steps
1. Deploy schema changes
   ```bash
   # Run in order
   alembic upgrade campaign_db@head
   alembic upgrade image_db@head
   ```

2. Run data migration:
   ```python
   async def migrate_data():
       # Campaign data
       await migrate_campaign_data(
           source_db=campaign_db,
           target_db=storage_db
       )

       # Image data
       await migrate_image_data(
           source_db=image_db,
           target_db=storage_db
       )
   ```

3. Verify migration:
   ```python
   async def verify_migration():
       # Verify campaigns
       campaign_count = await verify_campaign_migration()
       print(f"Campaign migration: {campaign_count} records verified")

       # Verify images
       image_count = await verify_image_migration()
       print(f"Image migration: {image_count} records verified")
   ```

### 5.3 Post-Migration Steps
1. Update service configurations:
   ```yaml
   # In Campaign Service
   database:
     type: storage_service
     schema: campaign_db
     client: storage_client

   # In Image Service
   database:
     type: storage_service
     schema: image_db
     client: storage_client
   ```

2. Update dependencies:
   ```diff
   # Remove direct database dependencies
   - asyncpg
   - sqlalchemy
   + storage_client
   ```

3. Update health checks:
   ```python
   async def check_health():
       storage_status = await storage_client.health()
       return {
           "status": "healthy" if storage_status["ok"] else "unhealthy",
           "storage": storage_status
       }
   ```

## 6. Rollback Plan

### 6.1 Database Rollback
1. Stop services accessing the migrated data
2. Restore from backups:
   ```bash
   pg_restore -d campaign_db campaign_db_backup.dump
   pg_restore -d image_db image_db_backup.dump
   ```
3. Update service configurations to use original databases
4. Restart services

### 6.2 Application Rollback
1. Deploy previous service versions
2. Update configuration to use original database connections
3. Verify service health
4. Resume normal operations