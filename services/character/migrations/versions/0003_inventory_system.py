"""Inventory system migration.

Revision ID: 0003
Revises: 0002
Create Date: 2025-09-06 01:57:30.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create inventory system tables."""
    # Create inventory_items table
    op.create_table(
        "inventory_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "container_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("location", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("weight", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("value", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Create indices for inventory_items
    op.create_index(
        "ix_inventory_items_character_id",
        "inventory_items",
        ["character_id"],
    )
    op.create_index(
        "ix_inventory_items_container_id",
        "inventory_items",
        ["container_id"],
    )
    op.create_index(
        "ix_inventory_items_created_at",
        "inventory_items",
        ["created_at"],
    )

    # Create containers table
    op.create_table(
        "containers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("capacity", sa.Float, nullable=False, server_default="0.0"),
        sa.Column(
            "capacity_type",
            sa.String(50),
            nullable=False,
            server_default="'weight'",
        ),
        sa.Column(
            "is_magical",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "restrictions",
            postgresql.ARRAY(sa.String),
            nullable=True,
        ),
    )

    # Create magic_items table
    op.create_table(
        "magic_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("rarity", sa.String(50), nullable=False),
        sa.Column(
            "requires_attunement",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "attunement_requirements",
            postgresql.ARRAY(sa.String),
            nullable=True,
        ),
        sa.Column(
            "attunement_state",
            sa.String(50),
            nullable=False,
            server_default="'none'",
        ),
        sa.Column("attunement_date", sa.DateTime, nullable=True),
        sa.Column("charges", sa.Integer, nullable=True),
        sa.Column("max_charges", sa.Integer, nullable=True),
        sa.Column("recharge_type", sa.String(50), nullable=True),
        sa.Column("last_recharged", sa.DateTime, nullable=True),
    )

    # Create item_effects table
    op.create_table(
        "item_effects",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=False),
        sa.Column("effect_type", sa.String(50), nullable=False),
        sa.Column("duration_type", sa.String(50), nullable=False),
        sa.Column("duration_value", sa.Integer, nullable=True),
        sa.Column("activation_type", sa.String(50), nullable=True),
        sa.Column("activation_cost", postgresql.JSONB, nullable=True),
        sa.Column("saving_throw", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Create item_effects association table
    op.create_table(
        "item_effects_association",
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "effect_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("item_effects.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Create indices
    op.create_index(
        "ix_magic_items_attunement_state",
        "magic_items",
        ["attunement_state"],
    )
    op.create_index(
        "ix_item_effects_effect_type",
        "item_effects",
        ["effect_type"],
    )


def downgrade() -> None:
    """Remove inventory system tables."""
    # Drop tables in reverse order
    op.drop_table("item_effects_association")
    op.drop_table("item_effects")
    op.drop_table("magic_items")
    op.drop_table("containers")

    # Drop indices
    op.drop_index("ix_inventory_items_created_at")
    op.drop_index("ix_inventory_items_container_id")
    op.drop_index("ix_inventory_items_character_id")
    op.drop_index("ix_magic_items_attunement_state")
    op.drop_index("ix_item_effects_effect_type")

    # Drop base table
    op.drop_table("inventory_items")
