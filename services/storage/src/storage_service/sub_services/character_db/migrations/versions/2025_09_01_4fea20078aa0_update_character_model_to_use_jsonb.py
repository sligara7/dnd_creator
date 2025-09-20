"""update character model to use JSONB

Revision ID: 4fea20078aa0
Revises: 2025_09_01_02
Create Date: 2025-09-01 20:26:30.954744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4fea20078aa0'
down_revision: Union[str, None] = '2025_09_01_02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new inventory items table
    op.create_table('inventory_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('root_id', sa.UUID(), nullable=True),
        sa.Column('theme', sa.String(), server_default='traditional', nullable=False),
        sa.Column('character_id', sa.UUID(), nullable=False),
        sa.Column('item_data', postgresql.JSONB(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('equipped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('container', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the new characters table with JSONB character_data
    op.create_table('characters',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('theme', sa.String(), server_default='traditional', nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('campaign_id', sa.UUID(), nullable=False),
        sa.Column('character_data', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the journal entries table
    op.create_table('journal_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('character_id', sa.UUID(), nullable=False),
        sa.Column('entry_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('session_number', sa.Integer(), nullable=True),
        sa.Column('session_date', sa.DateTime(), nullable=True),
        sa.Column('dm_name', sa.String(), nullable=True),
        sa.Column('session_summary', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'])
    )

    # Create experience entries table
    op.create_table('experience_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('journal_entry_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=True),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'])
    )

    # Create quests table
    op.create_table('quests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('journal_entry_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('importance', sa.String(), nullable=False, server_default='normal'),
        sa.Column('assigned_by', sa.String(), nullable=True),
        sa.Column('rewards', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('progress', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'])
    )

    # Create NPC relationships table
    op.create_table('npc_relationships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('journal_entry_id', sa.UUID(), nullable=False),
        sa.Column('npc_id', sa.UUID(), nullable=False),
        sa.Column('npc_name', sa.String(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('standing', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'])
    )

    # Create indexes
    op.create_index('ix_characters_name', 'characters', ['name'])
    op.create_index('ix_characters_parent_id', 'characters', ['parent_id'])
    op.create_index('ix_inventory_items_character_id', 'inventory_items', ['character_id'])
    op.create_index('ix_journal_entries_character_id', 'journal_entries', ['character_id'])
    op.create_index('ix_experience_entries_journal_entry_id', 'experience_entries', ['journal_entry_id'])
    op.create_index('ix_quests_journal_entry_id', 'quests', ['journal_entry_id'])
    op.create_index('ix_npc_relationships_journal_entry_id', 'npc_relationships', ['journal_entry_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_npc_relationships_journal_entry_id')
    op.drop_index('ix_quests_journal_entry_id')
    op.drop_index('ix_experience_entries_journal_entry_id')
    op.drop_index('ix_journal_entries_character_id')
    op.drop_index('ix_inventory_items_character_id')
    op.drop_index('ix_characters_parent_id')
    op.drop_index('ix_characters_name')

    # Drop tables in correct order
    op.drop_table('npc_relationships')
    op.drop_table('quests')
    op.drop_table('experience_entries')
    op.drop_table('journal_entries')
    op.drop_table('inventory_items')
    op.drop_table('characters')
    # ### end Alembic commands ###
