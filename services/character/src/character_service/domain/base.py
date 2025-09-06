"""Base module for domain models."""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields."""

    __abstract__ = True

    id: UUID = Column(PGUUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
