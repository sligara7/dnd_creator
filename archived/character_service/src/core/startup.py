"""
Character Service Startup Handlers

This module manages all startup tasks for the character service, including
database initialization, catalog migrations, and system checks.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.core.logging_config import get_logger, MigrationEvent
from src.models.database_models import UnifiedItem, SystemState, CharacterDB
from src.services.unified_catalog_migration import run_migration
from src.core.config import settings

logger = get_logger(__name__)

async def run_startup_tasks(db: CharacterDB, session: Session) -> None:
    """Run all startup tasks for the character service."""
    try:
        # Check if migration is needed
        if await should_run_migration(session):
            # Run the catalog migration
            migration_results = await run_migration(db, session)
            
            # Log migration results
            event = MigrationEvent(
                migration_type="catalog",
                items_migrated=sum(migration_results.values()),
                success=True,
                source_type="official",
                errors=[]
            )
            logger.info(
                "catalog_migration_complete",
                event=event.to_dict(),
                results=migration_results
            )
            
            # Update system state
            await update_migration_state(session)
        else:
            logger.info("catalog_migration_skipped", reason="recently_run")
            
    except Exception as e:
        logger.error(
            "startup_tasks_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise

async def should_run_migration(session: Session) -> bool:
    """Check if we should run the catalog migration."""
    try:
        # Check when the last migration was run
        last_state = session.query(SystemState).filter(
            SystemState.component == "catalog_migration"
        ).first()
        
        if not last_state:
            return True
        
        # Get current official content count
        official_count = session.query(func.count(UnifiedItem.id)).filter(
            and_(
                UnifiedItem.source_type == "official",
                UnifiedItem.is_active == True
            )
        ).scalar()
        
        # Run if:
        # 1. No official content exists
        # 2. Last migration was more than 1 week ago
        # 3. Force migration flag is set
        force_migration = bool(settings.FORCE_CATALOG_MIGRATION)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        if official_count == 0:
            logger.info("migration_required", reason="no_official_content")
            return True
        elif force_migration:
            logger.info("migration_required", reason="force_flag_set")
            return True
        elif last_state.updated_at < week_ago:
            logger.info("migration_required", reason="age", last_run=last_state.updated_at)
            return True
            
        return False
        
    except Exception as e:
        logger.error(
            "migration_check_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # On error, assume we should run
        return True

async def update_migration_state(session: Session) -> None:
    """Update the migration state after a successful run."""
    try:
        state = session.query(SystemState).filter(
            SystemState.component == "catalog_migration"
        ).first()
        
        if not state:
            state = SystemState(
                component="catalog_migration",
                status="success",
                details={
                    "last_successful_run": datetime.utcnow().isoformat()
                }
            )
            session.add(state)
        else:
            state.status = "success"
            state.details = {
                "last_successful_run": datetime.utcnow().isoformat()
            }
            state.updated_at = datetime.utcnow()
        
        session.commit()
        
    except Exception as e:
        logger.error(
            "migration_state_update_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # Don't raise - this is not critical
        pass
