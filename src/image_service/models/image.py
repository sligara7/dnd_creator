"""
Image models for the Image Service.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, DateTime, String, Integer, LargeBinary, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from shared.db import Base

class Image(Base):
    """Image model representing a generated or stored image."""
    __tablename__ = "images"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, nullable=True)
    campaign_id = Column(PGUUID, nullable=True)
    style = Column(String, nullable=False)
    description = Column(String)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    tags = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
