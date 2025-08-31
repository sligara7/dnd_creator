"""Initial database schema.

Revision ID: 2024_08_24_initial_schema
Revises: None
Create Date: 2024-08-24 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_08_24_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('race', sa.String(), nullable=False),
        sa.Column('class_', sa.String(), nullable=False),
        sa.Column('background', sa.String(), nullable=False),
        sa.Column('alignment', sa.String(), nullable=False),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Index('idx_character_name', 'name'),
        sa.Index('idx_character_level', 'level'),
        sa.Index('idx_character_race', 'race'),
        sa.Index('idx_character_class', 'class_'),
        sa.Index('idx_character_background', 'background'),
        sa.Index('idx_character_alignment', 'alignment'),
        sa.Index('idx_character_experience', 'experience'),
        sa.Index('idx_character_is_active', 'is_active')
    )

def downgrade() -> None:
    op.drop_table('characters')
