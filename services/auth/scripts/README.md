# Auth Service Data Migration

This directory contains scripts for migrating auth service data to the new storage service infrastructure.

## Migration Process

### Prerequisites

1. Both source database (PostgreSQL) and storage service must be running and accessible
2. Environment variables must be properly configured:
   ```bash
   # Source database connection
   export AUTH_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/auth_db"

   # Storage service connection
   export AUTH_STORAGE_SERVICE_URL="http://storage-service:8000"
   ```

### Running the Migration

1. Ensure the auth service virtualenv is activated:
   ```bash
   poetry shell
   ```

2. Run the migration script:
   ```bash
   python scripts/migrate_to_storage.py
   ```

The script will:
1. Connect to both source database and storage service
2. Migrate data in logical order:
   - Users
   - Roles
   - Sessions
   - API keys
   - Audit logs
3. Report progress for each entity type
4. Log any errors encountered
5. Clean up resources at the end

### Error Handling

- The script processes entities in batches and logs errors individually
- If an entity fails to migrate, the script continues with the next one
- Check the log output for any errors that need manual attention

### Rollback

To roll back the migration:
1. No action needed for the source database (it's read-only during migration)
2. For the storage service, use the rollback migration in:
   `/services/storage/migrations/auth_db/0001_initial_rollback.sql`

### Verification

After migration:
1. Compare record counts between source and destination
2. Sample check a few records of each type
3. Verify relationships are maintained
4. Test key service functionality with migrated data

## Support

For any issues with the migration:
1. Check the logs for specific error messages
2. Verify environment variables are correct
3. Ensure both databases are accessible
4. Contact the system admin if problems persist