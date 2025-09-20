"""Script to migrate auth data to storage service."""
import asyncio
import logging
import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from auth.clients.storage import StorageClient
from auth.core.config import get_settings
from auth.core.exceptions import StorageError
from auth.models.api import (
    ApiKeyCreate,
    AuditLogCreate,
    RoleCreate,
    SessionCreate,
    UserCreate
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def export_table(
    engine,
    table_name: str,
    order_by: str = "created_at"
) -> List[Dict[str, Any]]:
    """Export data from a table.

    Args:
        engine: SQLAlchemy engine
        table_name: Table to export
        order_by: Column to order by

    Returns:
        List of table records
    """
    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT * FROM {table_name} ORDER BY {order_by}")
        )
        return [dict(row._mapping) for row in result]


async def migrate_users(
    engine,
    storage_client: StorageClient,
    batch_size: int = 100
) -> None:
    """Migrate users to storage service.

    Args:
        engine: SQLAlchemy engine
        storage_client: Storage service client
        batch_size: Number of records to migrate in each batch
    """
    users = await export_table(engine, "users")
    logger.info(f"Migrating {len(users)} users")

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        for user_data in batch:
            try:
                user = UserCreate(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password_hash"]  # Already hashed
                )
                await storage_client.create_user(user)
            except StorageError as e:
                logger.error(f"Failed to migrate user {user_data['id']}: {e}")

        logger.info(f"Migrated {i + len(batch)} users")


async def migrate_roles(
    engine,
    storage_client: StorageClient,
    batch_size: int = 100
) -> None:
    """Migrate roles to storage service.

    Args:
        engine: SQLAlchemy engine
        storage_client: Storage service client
        batch_size: Number of records to migrate in each batch
    """
    roles = await export_table(engine, "roles")
    logger.info(f"Migrating {len(roles)} roles")

    for i in range(0, len(roles), batch_size):
        batch = roles[i:i + batch_size]
        for role_data in batch:
            try:
                role = RoleCreate(
                    name=role_data["name"],
                    description=role_data.get("description"),
                    is_system_role=role_data.get("is_system_role", False)
                )
                await storage_client.create_role(role)
            except StorageError as e:
                logger.error(f"Failed to migrate role {role_data['id']}: {e}")

        logger.info(f"Migrated {i + len(batch)} roles")


async def migrate_sessions(
    engine,
    storage_client: StorageClient,
    batch_size: int = 100
) -> None:
    """Migrate sessions to storage service.

    Args:
        engine: SQLAlchemy engine
        storage_client: Storage service client
        batch_size: Number of records to migrate in each batch
    """
    sessions = await export_table(
        engine,
        "sessions",
        order_by="created_at"
    )
    logger.info(f"Migrating {len(sessions)} sessions")

    for i in range(0, len(sessions), batch_size):
        batch = sessions[i:i + batch_size]
        for session_data in batch:
            try:
                session = SessionCreate(
                    user_id=session_data["user_id"],
                    access_token=session_data["access_token"],
                    refresh_token=session_data["refresh_token"],
                    token_type=session_data.get("token_type", "Bearer"),
                    expires_at=session_data["expires_at"],
                    client_info=session_data.get("client_info", {})
                )
                await storage_client.create_session(session)
            except StorageError as e:
                logger.error(f"Failed to migrate session {session_data['id']}: {e}")

        logger.info(f"Migrated {i + len(batch)} sessions")


async def migrate_api_keys(
    engine,
    storage_client: StorageClient,
    batch_size: int = 100
) -> None:
    """Migrate API keys to storage service.

    Args:
        engine: SQLAlchemy engine
        storage_client: Storage service client
        batch_size: Number of records to migrate in each batch
    """
    api_keys = await export_table(engine, "api_keys")
    logger.info(f"Migrating {len(api_keys)} API keys")

    for i in range(0, len(api_keys), batch_size):
        batch = api_keys[i:i + batch_size]
        for key_data in batch:
            try:
                api_key = ApiKeyCreate(
                    user_id=key_data["user_id"],
                    key_hash=key_data["key_hash"],
                    name=key_data["name"],
                    description=key_data.get("description"),
                    expires_at=key_data.get("expires_at")
                )
                await storage_client.create_api_key(api_key)
            except StorageError as e:
                logger.error(f"Failed to migrate API key {key_data['id']}: {e}")

        logger.info(f"Migrated {i + len(batch)} API keys")


async def migrate_audit_logs(
    engine,
    storage_client: StorageClient,
    batch_size: int = 100
) -> None:
    """Migrate audit logs to storage service.

    Args:
        engine: SQLAlchemy engine
        storage_client: Storage service client
        batch_size: Number of records to migrate in each batch
    """
    audit_logs = await export_table(
        engine,
        "audit_logs",
        order_by="created_at"
    )
    logger.info(f"Migrating {len(audit_logs)} audit logs")

    for i in range(0, len(audit_logs), batch_size):
        batch = audit_logs[i:i + batch_size]
        for log_data in batch:
            try:
                audit_log = AuditLogCreate(
                    user_id=log_data.get("user_id"),
                    action=log_data["action"],
                    resource_type=log_data["resource_type"],
                    resource_id=log_data.get("resource_id"),
                    old_data=log_data.get("old_data"),
                    new_data=log_data.get("new_data"),
                    client_info=log_data.get("client_info", {}),
                    ip_address=log_data.get("ip_address"),
                    success=log_data["success"],
                    failure_reason=log_data.get("failure_reason")
                )
                await storage_client.create_audit_log(audit_log)
            except StorageError as e:
                logger.error(f"Failed to migrate audit log {log_data['id']}: {e}")

        logger.info(f"Migrated {i + len(batch)} audit logs")


async def migrate_data() -> None:
    """Migrate all data to storage service."""
    # Get configuration
    settings = get_settings()

    # Read database URL from environment or config
    database_url = settings.database_url
    if not database_url:
        logger.error("DATABASE_URL environment variable is required")
        return

    # Create SQLAlchemy engine
    engine = create_async_engine(database_url)

    # Create storage client
    storage_client = StorageClient()

    try:
        # Migrate data in logical order
        await migrate_users(engine, storage_client)
        await migrate_roles(engine, storage_client)
        await migrate_sessions(engine, storage_client)
        await migrate_api_keys(engine, storage_client)
        await migrate_audit_logs(engine, storage_client)

        logger.info("Migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

    finally:
        # Clean up resources
        await storage_client.cleanup()
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(migrate_data())
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise