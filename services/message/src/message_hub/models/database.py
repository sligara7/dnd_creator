from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


class ServiceRegistry(Base):
    """Service registration information"""
    __tablename__ = "service_registry"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")
    last_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    __table_args__ = (
        UniqueConstraint("name", "url", name="uq_service_name_url"),
    )


class CircuitBreaker(Base):
    """Circuit breaker state"""
    __tablename__ = "circuit_breakers"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    service: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="closed")
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_failure: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_success: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reset_timeout: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    half_open_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Transaction(Base):
    """Distributed transaction record"""
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Relationships
    events: Mapped[List["Event"]] = relationship("Event", back_populates="transaction")


class Event(Base):
    """Event store record"""
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    transaction_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID, ForeignKey("transactions.id"), nullable=True
    )
    
    # Relationships
    transaction: Mapped[Optional[Transaction]] = relationship(
        Transaction, back_populates="events"
    )
