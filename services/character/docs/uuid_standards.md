# UUID and Soft-Delete Standards

This document outlines our standards for UUID usage and soft-delete functionality across the Character Service.

## Database Standards (SQLAlchemy Models)

### UUID Fields
- **Primary Keys**
  ```python
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  ```

- **Foreign Keys**
  ```python
  other_id = Column(UUID(as_uuid=True), ForeignKey("other_table.id"), nullable=False)
  ```

### Soft Delete Fields
Every entity must include:
- `is_deleted`: Boolean NOT NULL DEFAULT false
- `deleted_at`: DateTime NULL
- `created_at`: DateTime NOT NULL
- `updated_at`: DateTime NOT NULL (maintained by trigger)

### Timestamps
- All entities have `created_at` and `updated_at` timestamps
- `updated_at` is maintained automatically by database trigger
- Standard trigger implementation:
  ```sql
  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.updated_at = CURRENT_TIMESTAMP;
      RETURN NEW;
  END;
  $$ language 'plpgsql';
  ```

## API Standards (Pydantic Schemas)

### ID Fields
- All ID fields must use `uuid.UUID` type
- Example:
  ```python
  class CharacterBase(BaseModel):
      user_id: uuid.UUID
      campaign_id: uuid.UUID
  ```

## Repository Standards

### Query Parameters
- All ID parameters must be of type `UUID`
- Example:
  ```python
  async def get_character(self, character_id: UUID) -> Optional[Character]:
  ```

### Soft Delete Handling
- Queries exclude soft-deleted records by default
- Standard where clause: `is_deleted == False`
- Implementation:
  ```python
  base_query = select(Character).where(Character.is_deleted == False)
  ```

## Migration Standards (Alembic)

### Initial Schema
- All ID columns created as PostgreSQL UUID type
- Example:
  ```python
  sa.Column('id', postgresql.UUID(as_uuid=True), 
            primary_key=True, server_default=sa.text('uuid_generate_v4()'))
  ```

### Type Preservation
- Upgrade/downgrade operations must preserve UUID types
- No implicit type conversions

### Required Extensions
- UUID extension must be created:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  ```

## Current Implementation Status

### Completed Fixes
1. Models (`src/character_service/models/models.py`)
   - All PK/FK fields use UUID type
   - Soft-delete fields added to all tables
   - Cascade deletes removed in favor of soft-delete

2. Schemas (`src/character_service/schemas/schemas.py`)
   - All ID fields use `uuid.UUID` type
   - Consistent typing across create/update/base schemas

3. Repositories
   - UUID parameters for all operations
   - Soft-delete filtering implemented
   - Consistent UUID handling in queries

### Pending Issues

#### Database Schema
Current issues with varchar vs UUID mismatches:
- `characters.id`: currently varchar, needs UUID
- Foreign key constraints using string columns
- Missing soft-delete columns on some tables

#### Migration Chain
Current head differs from intended chain:
1. initial_schema
2. inventory_items
3. character_model_update
4. journals
5. uuid_columns

## Migration Plan

### Option A: Clean Reset (Selected)
1. Drop and recreate test database
2. Apply corrected migration chain
3. Verify schema compliance
4. Run test suite

### Schema Verification Checklist
After migration, verify UUID types for:
- [ ] characters (id, user_id, campaign_id)
- [ ] inventory_items (id, character_id)
- [ ] journal_entries (id, character_id)
- [ ] experience_entries (id, journal_entry_id, session_id)
- [ ] quests (id, journal_entry_id)
- [ ] npc_relationships (id, journal_entry_id, npc_id)

### Next Steps
1. Update migration dependencies
2. Reset test database
3. Apply migrations
4. Run tests
5. Fix any remaining async test issues
