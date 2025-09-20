"""Initial campaign database schema.

Revision ID: 001
Create Date: 2025-09-20 17:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schema if it doesn't exist
    op.execute('CREATE SCHEMA IF NOT EXISTS campaign_db')
    
    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION campaign_db.update_updated_at_column()
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
        sa.Column('description', sa.Text),
        sa.Column('campaign_type', sa.String(50), nullable=False, server_default='traditional'),
        sa.Column('state', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('theme_id', postgresql.UUID(as_uuid=True)),
        sa.Column('theme_data', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('campaign_metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='campaign_db'
    )

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('chapter_type', sa.String(50), nullable=False, server_default='story'),
        sa.Column('state', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('chapter_metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('prerequisites', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign_db.campaigns.id'], name='fk_chapters_campaign_id'),
        schema='campaign_db'
    )

    # Create indexes
    op.create_index(
        'ix_campaigns_name',
        'campaigns',
        ['name'],
        schema='campaign_db'
    )
    op.create_index(
        'ix_chapters_campaign_id',
        'chapters',
        ['campaign_id'],
        schema='campaign_db'
    )
    op.create_index(
        'ix_chapters_sequence_number',
        'chapters',
        ['sequence_number'],
        schema='campaign_db'
    )

    # Create updated_at triggers
    op.execute("""
        CREATE TRIGGER update_campaigns_modtime 
            BEFORE UPDATE ON campaign_db.campaigns 
            FOR EACH ROW 
            EXECUTE FUNCTION campaign_db.update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_chapters_modtime 
            BEFORE UPDATE ON campaign_db.chapters 
            FOR EACH ROW 
            EXECUTE FUNCTION campaign_db.update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("""
        DROP TRIGGER IF EXISTS update_campaigns_modtime ON campaign_db.campaigns;
        DROP TRIGGER IF EXISTS update_chapters_modtime ON campaign_db.chapters;
    """)

    # Drop indexes
    op.drop_index('ix_chapters_sequence_number', schema='campaign_db')
    op.drop_index('ix_chapters_campaign_id', schema='campaign_db')
    op.drop_index('ix_campaigns_name', schema='campaign_db')

    # Drop tables
    op.drop_table('chapters', schema='campaign_db')
    op.drop_table('campaigns', schema='campaign_db')

    # Drop functions
    op.execute('DROP FUNCTION IF EXISTS campaign_db.update_updated_at_column() CASCADE;')

    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS campaign_db CASCADE;')