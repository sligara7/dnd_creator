"""Add version control models

Revision ID: eb32a39a5c2d
Revises: abc2376a590e
Create Date: 2025-09-09 22:03:37.866722

Modified to use op and sa objects for table creation.
"""
from typing import Sequence
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'eb32a39a5c2d'
down_revision: str | None = 'abc2376a590e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create campaign_branches table
    op.create_table(
        'campaign_branches',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('state', sa.String(50), nullable=False),
        sa.Column('base_branch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaign_branches.id'), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        schema=None
    )

    # Create campaign_commits table
    op.create_table(
        'campaign_commits',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaign_branches.id'), nullable=False),
        sa.Column('parent_commit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaign_commits.id'), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        schema=None
    )

    # Create campaign_changes table
    op.create_table(
        'campaign_changes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('commit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaign_commits.id'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(255), nullable=False),
        sa.Column('old_value', postgresql.JSONB, nullable=True),
        sa.Column('new_value', postgresql.JSONB, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        schema=None
    )


def downgrade() -> None:
    # Tables must be dropped in correct dependency order
    op.drop_table('campaign_changes', schema=None)
    op.drop_table('campaign_commits', schema=None)
    op.drop_table('campaign_branches', schema=None)
