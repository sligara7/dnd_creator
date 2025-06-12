"""
Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_settings

settings = get_settings()

class DatabaseConfig:
    def __init__(self):
        self.engine = create_engine(
            settings.database_url,
            echo=settings.database_echo
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """Get database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()