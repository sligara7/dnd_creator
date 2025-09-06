"""Add story management models.

Revision ID: 2025_09_06_1435
Revises: previous_revision_id  # Update this with actual previous revision ID
Create Date: 2025-09-06 14:35:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2025_09_06_1435"
down_revision: Union[str, None] = "previous_revision_id"  # Update this
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create story_arcs table
    op.create_table(
        "story_arcs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "arc_type",
            sa.String(50),
            nullable=False,
            server_default="campaign",
        ),
        sa.Column(
            "content",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("sequence_number", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Create plots table
    op.create_table(
        "plots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "plot_type",
            sa.String(50),
            nullable=False,
            server_default="side",
        ),
        sa.Column(
            "state",
            sa.String(50),
            nullable=False,
            server_default="planned",
        ),
        sa.Column(
            "content",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "parent_plot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plots.id"),
            nullable=True,
        ),
        sa.Column(
            "arc_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("story_arcs.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Create plot_chapters table
    op.create_table(
        "plot_chapters",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "plot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plots.id"),
            nullable=False,
        ),
        sa.Column(
            "chapter_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chapters.id"),
            nullable=False,
        ),
        sa.Column(
            "plot_content",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("plot_order", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Create npc_relationships table
    op.create_table(
        "npc_relationships",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column(
            "npc_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "relation_type",
            sa.String(50),
            nullable=False,
            server_default="neutral",
        ),
        sa.Column(
            "plot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("plots.id"),
            nullable=True,
        ),
        sa.Column(
            "arc_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("story_arcs.id"),
            nullable=True,
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Create indexes
    op.create_index(
        "ix_story_arcs_campaign_id",
        "story_arcs",
        ["campaign_id"],
    )
    op.create_index(
        "ix_plots_campaign_id",
        "plots",
        ["campaign_id"],
    )
    op.create_index(
        "ix_plots_arc_id",
        "plots",
        ["arc_id"],
    )
    op.create_index(
        "ix_plot_chapters_plot_id",
        "plot_chapters",
        ["plot_id"],
    )
    op.create_index(
        "ix_plot_chapters_chapter_id",
        "plot_chapters",
        ["chapter_id"],
    )
    op.create_index(
        "ix_npc_relationships_campaign_id",
        "npc_relationships",
        ["campaign_id"],
    )
    op.create_index(
        "ix_npc_relationships_npc_id",
        "npc_relationships",
        ["npc_id"],
    )
    op.create_index(
        "ix_npc_relationships_plot_id",
        "npc_relationships",
        ["plot_id"],
    )
    op.create_index(
        "ix_npc_relationships_arc_id",
        "npc_relationships",
        ["arc_id"],
    )

    # Add triggers for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    for table in ["story_arcs", "plots", "plot_chapters", "npc_relationships"]:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ["story_arcs", "plots", "plot_chapters", "npc_relationships"]:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")

    # Drop tables
    op.drop_table("npc_relationships")
    op.drop_table("plot_chapters")
    op.drop_table("plots")
    op.drop_table("story_arcs")

    # Drop update_updated_at function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at()")
