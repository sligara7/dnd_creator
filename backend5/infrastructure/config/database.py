"""
Database Configuration and Management

Provides database configuration, connection management, session handling,
and database lifecycle operations for the D&D Character Creator application.
"""

from typing import Generator, Optional, Dict, Any
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
import logging
import asyncio
from datetime import datetime

from .settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseConfig:
    """
    Database configuration and connection management.
    
    Handles database engine creation, session management, connection pooling,
    and database lifecycle operations.
    """
    
    def __init__(self, database_url: Optional[str] = None, **engine_kwargs):
        self.database_url = database_url or settings.database_url
        self.echo = settings.database_echo
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._engine_kwargs = engine_kwargs
        self._connection_count = 0
        
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._session_factory
    
    def _create_engine(self) -> Engine:
        """Create database engine with appropriate configuration."""
        engine_config = {
            'echo': self.echo,
            'future': True,  # Use SQLAlchemy 2.0 style
            **self._engine_kwargs
        }
        
        # Configure based on database type
        if self.database_url.startswith('sqlite'):
            engine_config.update({
                'poolclass': StaticPool,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 20
                }
            })
        elif self.database_url.startswith('postgresql'):
            engine_config.update({
                'pool_size': settings.db_pool_size if hasattr(settings, 'db_pool_size') else 5,
                'max_overflow': settings.db_max_overflow if hasattr(settings, 'db_max_overflow') else 10,
                'pool_timeout': 30,
                'pool_recycle': 3600
            })
        elif self.database_url.startswith('mysql'):
            engine_config.update({
                'pool_size': settings.db_pool_size if hasattr(settings, 'db_pool_size') else 5,
                'max_overflow': settings.db_max_overflow if hasattr(settings, 'db_max_overflow') else 10,
                'pool_timeout': 30,
                'pool_recycle': 3600
            })
        
        engine = create_engine(self.database_url, **engine_config)
        
        # Add event listeners
        self._setup_event_listeners(engine)
        
        return engine
    
    def _setup_event_listeners(self, engine: Engine):
        """Setup database event listeners for monitoring and logging."""
        
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Handle new database connections."""
            self._connection_count += 1
            logger.debug(f"New database connection established. Total: {self._connection_count}")
            
            # SQLite-specific configuration
            if self.database_url.startswith('sqlite'):
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle connection checkout from pool."""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Handle connection checkin to pool."""
            logger.debug("Connection checked in to pool")
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup.
        
        Yields:
            Session: SQLAlchemy session
        """
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """
        Get database session as context manager.
        
        Usage:
            with db_config.get_session_context() as session:
                # Use session
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_session(self) -> Session:
        """
        Create a new database session.
        
        Note: Caller is responsible for closing the session.
        
        Returns:
            Session: New SQLAlchemy session
        """
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            bool: True if connection successful
        """
        try:
            with self.get_session_context() as session:
                session.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection information.
        
        Returns:
            Dict containing connection details
        """
        engine = self.engine
        pool = engine.pool
        
        return {
            'url': str(engine.url).replace(str(engine.url.password), '***') if engine.url.password else str(engine.url),
            'driver': engine.dialect.name,
            'pool_size': pool.size() if hasattr(pool, 'size') else 'N/A',
            'checked_in': pool.checkedin() if hasattr(pool, 'checkedin') else 'N/A',
            'checked_out': pool.checkedout() if hasattr(pool, 'checkedout') else 'N/A',
            'total_connections': self._connection_count
        }
    
    def close(self):
        """Close database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed")


class DatabaseManager:
    """
    High-level database management operations.
    
    Provides database initialization, migration, backup, and maintenance operations.
    """
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.metadata_table = None  # Will be set when importing models
    
    def initialize_database(self, drop_existing: bool = False):
        """
        Initialize database schema.
        
        Args:
            drop_existing: Whether to drop existing tables first
        """
        try:
            from core.entities.base import Base  # Import base model
            
            if drop_existing:
                logger.warning("Dropping all existing database tables")
                Base.metadata.drop_all(bind=self.db_config.engine)
            
            logger.info("Creating database tables")
            Base.metadata.create_all(bind=self.db_config.engine)
            
            # Insert initial data if needed
            self._insert_initial_data()
            
            logger.info("Database initialization complete")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _insert_initial_data(self):
        """Insert initial/seed data into database."""
        try:
            with self.db_config.get_session_context() as session:
                # Add any initial data here
                # Example: default user roles, system configurations, etc.
                pass
        except Exception as e:
            logger.error(f"Failed to insert initial data: {e}")
            raise
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            bool: True if backup successful
        """
        try:
            if self.db_config.database_url.startswith('sqlite'):
                return self._backup_sqlite(backup_path)
            else:
                logger.warning("Backup not implemented for this database type")
                return False
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def _backup_sqlite(self, backup_path: str) -> bool:
        """Backup SQLite database."""
        import sqlite3
        import shutil
        
        try:
            # Extract database path from URL
            db_path = self.db_config.database_url.replace('sqlite:///', '')
            
            # Simple file copy for SQLite
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict containing database statistics
        """
        try:
            with self.db_config.get_session_context() as session:
                stats = {
                    'connection_info': self.db_config.get_connection_info(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add table-specific stats if possible
                try:
                    from core.entities.base import Base
                    stats['tables'] = {}
                    
                    for table in Base.metadata.tables.values():
                        try:
                            count = session.execute(f"SELECT COUNT(*) FROM {table.name}").scalar()
                            stats['tables'][table.name] = {'row_count': count}
                        except Exception:
                            stats['tables'][table.name] = {'row_count': 'N/A'}
                            
                except ImportError:
                    stats['tables'] = 'Models not available'
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {'error': str(e)}


# Global database instances
_db_config: Optional[DatabaseConfig] = None
_db_manager: Optional[DatabaseManager] = None


def get_database_config() -> DatabaseConfig:
    """
    Get global database configuration instance.
    
    Returns:
        DatabaseConfig: Global database configuration
    """
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config


def get_database_manager() -> DatabaseManager:
    """
    Get global database manager instance.
    
    Returns:
        DatabaseManager: Global database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(get_database_config())
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """
    Convenience function to get database session.
    
    This is the primary function used throughout the application.
    
    Yields:
        Session: SQLAlchemy session
    """
    db_config = get_database_config()
    yield from db_config.get_session()


# Dependency injection function for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    yield from get_db_session()


# Health check function
def check_database_health() -> Dict[str, Any]:
    """
    Check database health status.
    
    Returns:
        Dict containing health check results
    """
    db_config = get_database_config()
    
    health_status = {
        'status': 'unknown',
        'timestamp': datetime.now().isoformat(),
        'details': {}
    }
    
    try:
        # Test connection
        connection_ok = db_config.test_connection()
        health_status['details']['connection'] = 'ok' if connection_ok else 'failed'
        
        # Get connection info
        health_status['details']['connection_info'] = db_config.get_connection_info()
        
        # Overall status
        health_status['status'] = 'healthy' if connection_ok else 'unhealthy'
        
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['details']['error'] = str(e)
    
    return health_status


# Cleanup function
def cleanup_database_connections():
    """Clean up database connections on application shutdown."""
    global _db_config
    if _db_config:
        _db_config.close()
        _db_config = None
        logger.info("Database connections cleaned up")