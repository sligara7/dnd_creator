"""Inventory system models."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    Index,
    Table,
    Column,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from character_service.domain.base import Base


class ItemRarity(str, Enum):
    """Item rarity levels."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemType(str, Enum):
    """Types of items."""

    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SCROLL = "scroll"
    RING = "ring"
    ROD = "rod"
    STAFF = "staff"
    WAND = "wand"
    WONDROUS = "wondrous"
    AMMUNITION = "ammunition"
    CONTAINER = "container"
    CURRENCY = "currency"
    OTHER = "other"


class ItemLocation(str, Enum):
    """Where an item is located."""

    EQUIPPED = "equipped"
    CARRIED = "carried"
    STORED = "stored"
    CONTAINER = "container"
    MOUNT = "mount"
    BANK = "bank"
    VAULT = "vault"


class AttunementState(str, Enum):
    """States for magic item attunement."""

    NONE = "none"
    ATTUNED = "attuned"
    ATTUNING = "attuning"
    BROKEN = "broken"


class EffectType(str, Enum):
    """Types of magic item effects."""

    PASSIVE = "passive"
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CHARGED = "charged"
    CURSE = "curse"


class EffectDurationType(str, Enum):
    """Types of effect durations."""

    INSTANT = "instant"
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    UNTIL_DAWN = "until_dawn"
    UNTIL_DUSK = "until_dusk"
    UNTIL_LONG_REST = "until_long_rest"
    UNTIL_SHORT_REST = "until_short_rest"
    CHARGES = "charges"


# Many-to-many association tables
item_effects = Table(
    "item_effects",
    Base.metadata,
    Column(
        "item_id",
        PGUUID(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "effect_id",
        PGUUID(as_uuid=True),
        ForeignKey("item_effects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class InventoryItem(Base):
    """Base model for inventory items."""

    __tablename__ = "inventory_items"
    __table_args__ = (
        Index("ix_inventory_items_character_id", "character_id"),
        Index("ix_inventory_items_container_id", "container_id"),
        Index("ix_inventory_items_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        primary_key=True,
    )

    character_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    container_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("inventory_items.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    item_type: Mapped[ItemType] = mapped_column(
        String(50),
        nullable=False,
    )

    location: Mapped[ItemLocation] = mapped_column(
        String(50),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    metadata: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    container_items = relationship(
        "InventoryItem",
        backref="container",
        remote_side=[id],
        cascade="all, delete-orphan",
    )


class Container(InventoryItem):
    """Model for containers (bags, chests, etc.)."""

    __tablename__ = "containers"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("inventory_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    capacity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="weight",
    )

    is_magical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    restrictions: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )


class MagicItem(InventoryItem):
    """Model for magic items."""

    __tablename__ = "magic_items"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("inventory_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    rarity: Mapped[ItemRarity] = mapped_column(
        String(50),
        nullable=False,
    )

    requires_attunement: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    attunement_requirements: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    attunement_state: Mapped[AttunementState] = mapped_column(
        String(50),
        nullable=False,
        default=AttunementState.NONE,
    )

    attunement_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    charges: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    max_charges: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    recharge_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    last_recharged: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Relationships
    effects = relationship(
        "ItemEffect",
        secondary=item_effects,
        back_populates="items",
    )


class ItemEffect(Base):
    """Model for magic item effects."""

    __tablename__ = "item_effects"

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    effect_type: Mapped[EffectType] = mapped_column(
        String(50),
        nullable=False,
    )

    duration_type: Mapped[EffectDurationType] = mapped_column(
        String(50),
        nullable=False,
    )

    duration_value: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    activation_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    activation_cost: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    saving_throw: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    items = relationship(
        "MagicItem",
        secondary=item_effects,
        back_populates="effects",
    )
