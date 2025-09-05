"""Add theme system tables.

Revision ID: 2025_09_05_add_theme_system
Revises: 2024_08_31_add_inventory_item_model
Create Date: 2025-09-05 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2025_09_05_add_theme_system"
down_revision: Union[str, None] = "2024_08_31_add_inventory_item_model"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create themes table
    op.create_table(
        "themes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("base_modifiers", sa.JSON, nullable=False, default=dict),
        sa.Column("ability_adjustments", sa.JSON, nullable=False, default=dict),
        sa.Column("level_requirement", sa.Integer, default=1),
        sa.Column("class_restrictions", sa.JSON, nullable=False, default=list),
        sa.Column("race_restrictions", sa.JSON, nullable=False, default=list),
        sa.Column("version", sa.Integer, default=1),
        sa.Column(
            "parent_theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create theme features table
    op.create_table(
        "theme_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("level_granted", sa.Integer, default=1),
        sa.Column("mechanics", sa.JSON, nullable=False, default=dict),
        sa.Column("is_optional", sa.Boolean, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create theme equipment table
    op.create_table(
        "theme_equipment",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id"),
            nullable=False,
        ),
        sa.Column("operation", sa.String, nullable=False),
        sa.Column("quantity", sa.Integer, default=1),
        sa.Column("requirements", sa.JSON, nullable=False, default=dict),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create theme progression rules table
    op.create_table(
        "theme_progression_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("trigger_type", sa.String, nullable=False),
        sa.Column("trigger_conditions", sa.JSON, nullable=False, default=dict),
        sa.Column("effects", sa.JSON, nullable=False, default=dict),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create theme states table
    op.create_table(
        "theme_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id"),
            nullable=False,
        ),
        sa.Column(
            "theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column(
            "applied_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "deactivated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("applied_features", sa.JSON, nullable=False, default=list),
        sa.Column("applied_modifiers", sa.JSON, nullable=False, default=dict),
        sa.Column("progress_state", sa.JSON, nullable=False, default=dict),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create theme transitions table
    op.create_table(
        "theme_transitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id"),
            nullable=False,
        ),
        sa.Column(
            "from_theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=True,
        ),
        sa.Column(
            "to_theme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("themes.id"),
            nullable=False,
        ),
        sa.Column("transition_type", sa.String, nullable=False),
        sa.Column("triggered_by", sa.String, nullable=False),
        sa.Column(
            "campaign_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaign_events.id"),
            nullable=True,
        ),
        sa.Column("changes", sa.JSON, nullable=False, default=dict),
        sa.Column("rolled_back", sa.Boolean, default=False),
        sa.Column("rollback_reason", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Add indexes
    op.create_index(
        "ix_themes_name",
        "themes",
        ["name"],
    )
    op.create_index(
        "ix_themes_category",
        "themes",
        ["category"],
    )
    op.create_index(
        "ix_theme_states_character_id",
        "theme_states",
        ["character_id"],
    )
    op.create_index(
        "ix_theme_states_theme_id",
        "theme_states",
        ["theme_id"],
    )
    op.create_index(
        "ix_theme_transitions_character_id",
        "theme_transitions",
        ["character_id"],
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("theme_transitions")
    op.drop_table("theme_states")
    op.drop_table("theme_progression_rules")
    op.drop_table("theme_equipment")
    op.drop_table("theme_features")
    op.drop_table("themes")
