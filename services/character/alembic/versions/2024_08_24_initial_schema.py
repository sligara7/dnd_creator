"""Initial schema

Revision ID: 2024_08_24_initial_schema
Create Date: 2024-08-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_08_24_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('race', sa.String(), nullable=False),
        sa.Column('class_', sa.String(), nullable=False),
        sa.Column('background', sa.String(), nullable=False),
        sa.Column('alignment', sa.String(), nullable=False),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create journal_entries table
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('character_id', sa.String(), nullable=False),
        sa.Column('entry_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('session_number', sa.Integer()),
        sa.Column('session_date', sa.DateTime()),
        sa.Column('dm_name', sa.String()),
        sa.Column('session_summary', sa.Text()),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('journal_entries')
    op.drop_table('characters')
