"""Initial migration

Revision ID: dd7f296ff218
Revises: 
Create Date: 2025-09-09 20:17:34.892114

"""
from typing import Sequence
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'dd7f296ff218'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    print("Running migration upgrade")
    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('campaign_type', sa.String(50), nullable=False, server_default='traditional'),
        sa.Column('state', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('theme_data', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('campaign_metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('chapter_type', sa.String(50), nullable=False, server_default='story'),
        sa.Column('state', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('chapter_metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('prerequisites', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_chapters_campaign_id'),
    )

    # Create updated_at triggers
    op.execute("""
        CREATE TRIGGER update_campaigns_modtime 
            BEFORE UPDATE ON campaigns 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_chapters_modtime 
            BEFORE UPDATE ON chapters 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    """)

    # Create indexes
    op.create_index('ix_campaigns_name', 'campaigns', ['name'])
    op.create_index('ix_chapters_campaign_id', 'chapters', ['campaign_id'])
    op.create_index('ix_chapters_sequence_number', 'chapters', ['sequence_number'])


def downgrade() -> None:
    op.drop_index('ix_chapters_sequence_number')
    op.drop_index('ix_chapters_campaign_id')
    op.drop_index('ix_campaigns_name')
    op.drop_table('chapters')
    op.drop_table('campaigns')
    op.execute('DROP FUNCTION update_updated_at_column();')
