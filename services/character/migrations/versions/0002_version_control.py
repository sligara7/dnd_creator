"""Version control migration.

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-05 21:52:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create version control tables."""
    # Create character_versions table
    op.create_table(
        "character_versions",
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
            "parent_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("character_versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("state", postgresql.JSONB, nullable=False),
        sa.Column("changes", postgresql.JSONB, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(255), nullable=False),
    )

    # Create character_changes table
    op.create_table(
        "character_changes",
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
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("character_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("attribute_path", sa.String(255), nullable=False),
        sa.Column("old_value", postgresql.JSONB, nullable=True),
        sa.Column("new_value", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(255), nullable=False),
    )

    # Create version_metadata table
    op.create_table(
        "version_metadata",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("character_versions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("level", sa.Integer, nullable=False),
        sa.Column("class_name", sa.String(50), nullable=False),
        sa.Column(
            "active_theme_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("ability_scores", postgresql.JSONB, nullable=False),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "branch_point",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("character_versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "is_milestone",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
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

    # Create indices
    op.create_index(
        "ix_character_versions_character_id",
        "character_versions",
        ["character_id"],
    )
    op.create_index(
        "ix_character_versions_parent_version_id",
        "character_versions",
        ["parent_version_id"],
    )
    op.create_index(
        "ix_character_versions_created_at",
        "character_versions",
        ["created_at"],
    )

    op.create_index(
        "ix_character_changes_character_id",
        "character_changes",
        ["character_id"],
    )
    op.create_index(
        "ix_character_changes_version_id",
        "character_changes",
        ["version_id"],
    )
    op.create_index(
        "ix_character_changes_created_at",
        "character_changes",
        ["created_at"],
    )

    op.create_index(
        "ix_version_metadata_character_id",
        "version_metadata",
        ["character_id"],
    )
    op.create_index(
        "ix_version_metadata_version_id",
        "version_metadata",
        ["version_id"],
    )


def downgrade() -> None:
    """Remove version control tables."""
    # Drop indices first
    op.drop_index("ix_version_metadata_version_id")
    op.drop_index("ix_version_metadata_character_id")

    op.drop_index("ix_character_changes_created_at")
    op.drop_index("ix_character_changes_version_id")
    op.drop_index("ix_character_changes_character_id")

    op.drop_index("ix_character_versions_created_at")
    op.drop_index("ix_character_versions_parent_version_id")
    op.drop_index("ix_character_versions_character_id")

    # Drop tables in reverse order
    op.drop_table("version_metadata")
    op.drop_table("character_changes")
    op.drop_table("character_versions")
