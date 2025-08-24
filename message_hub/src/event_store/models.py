"""
Event Store Models

Database models for storing and retrieving events.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class EventType(str, Enum):
    """Types of events that can be stored."""
    # Character events
    CHARACTER_CREATED = "character.created"
    CHARACTER_UPDATED = "character.updated"
    CHARACTER_DELETED = "character.deleted"
    
    # Character attribute events
    ABILITY_SCORES_UPDATED = "ability_scores.updated"
    SKILLS_UPDATED = "skills.updated"
    BACKGROUND_UPDATED = "background.updated"
    RACE_UPDATED = "race.updated"
    CLASS_UPDATED = "class.updated"
    
    # Inventory and equipment events
    INVENTORY_UPDATED = "inventory.updated"
    SPELLS_UPDATED = "spells.updated"
    FEATURES_UPDATED = "features.updated"
    
    # Progression events
    CHARACTER_LEVEL_UP = "character.level_up"
    CHARACTER_EXPERIENCE_GAINED = "character.experience_gained"
    
    # Transaction events
    TRANSACTION_STARTED = "transaction.started"
    TRANSACTION_COMMITTED = "transaction.committed"
    TRANSACTION_ROLLED_BACK = "transaction.rolled_back"

class Event(Base):
    """
    Represents a system event.
    
    Events are immutable records of things that happened in the system.
    They can be used for:
    - Audit trails
    - Event sourcing
    - System recovery
    - Debugging
    """
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(SQLAEnum(EventType), nullable=False)
    event_id = Column(String(36), nullable=False, unique=True)  # UUID
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Event source information
    source_service = Column(String(50), nullable=False)
    source_component = Column(String(50), nullable=True)
    
    # Event data
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Correlation for distributed tracing
    correlation_id = Column(String(36), nullable=True)
    causation_id = Column(String(36), nullable=True)
    
    # Event sequence tracking
    sequence_number = Column(Integer, nullable=False)
    stream_id = Column(String(36), nullable=True)  # For event streams
    
    def __repr__(self):
        return (f"<Event(id={self.id}, "
                f"type={self.event_type}, "
                f"event_id={self.event_id}, "
                f"source={self.source_service})>")

class EventStream(Base):
    """
    Represents a stream of related events.
    
    Streams can represent:
    - All events for a particular service
    - All events in a transaction
    - All events related to a particular entity
    """
    
    __tablename__ = "event_streams"
    
    id = Column(Integer, primary_key=True)
    stream_id = Column(String(36), nullable=False, unique=True)  # UUID
    stream_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_event_at = Column(DateTime, nullable=True)
    
    # Stream metadata
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return (f"<EventStream(id={self.id}, "
                f"stream_id={self.stream_id}, "
                f"type={self.stream_type})>")

class EventSubscription(Base):
    """
    Represents a subscription to events.
    
    Subscriptions track:
    - Which events a service is interested in
    - Last processed event
    - Retry/error state
    """
    
    __tablename__ = "event_subscriptions"
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(String(36), nullable=False, unique=True)  # UUID
    subscriber_service = Column(String(50), nullable=False)
    
    # Subscription filters
    event_types = Column(JSON, nullable=True)  # List of event types to receive
    source_services = Column(JSON, nullable=True)  # List of services to monitor
    
    # Processing state
    last_processed_sequence = Column(Integer, nullable=False, default=0)
    last_processed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_count = Column(Integer, nullable=False, default=0)
    last_error = Column(String(500), nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    
    # Subscription metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return (f"<EventSubscription(id={self.id}, "
                f"subscriber={self.subscriber_service}, "
                f"last_seq={self.last_processed_sequence})>")
