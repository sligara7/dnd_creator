"""Add journal system tables.

Revision ID: 2024_08_24_journals
Revises: 2024_08_23_add_unified_catalog
Create Date: 2024-08-24 21:09:14.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_08_24_journals'
down_revision = '2024_08_24_initial_schema'  # Depends on initial schema
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create journal_entries table
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
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
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.Index('idx_journal_character_id', 'character_id'),
        sa.Index('idx_journal_entry_type', 'entry_type'),
        sa.Index('idx_journal_timestamp', 'timestamp'),
        sa.Index('idx_journal_tags', 'tags', postgresql_using='gin')
    )
    
    # Create experience_entries table
    op.create_table(
        'experience_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('session_id', sa.String()),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='CASCADE'),
        sa.Index('idx_experience_journal_entry', 'journal_entry_id'),
        sa.Index('idx_experience_timestamp', 'timestamp')
    )
    
    # Create quests table
    op.create_table(
        'quests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('importance', sa.String(), nullable=False, server_default='normal'),
        sa.Column('assigned_by', sa.String()),
        sa.Column('rewards', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('progress', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='CASCADE'),
        sa.Index('idx_quest_journal_entry', 'journal_entry_id'),
        sa.Index('idx_quest_status', 'status'),
        sa.Index('idx_quest_importance', 'importance')
    )
    
    # Create npc_relationships table
    op.create_table(
        'npc_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('npc_id', sa.String(), nullable=False),
        sa.Column('npc_name', sa.String(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('standing', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('last_interaction', sa.DateTime()),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('journal_entry_id', 'npc_id', name='uq_relationship_npc'),
        sa.Index('idx_relationship_journal_entry', 'journal_entry_id'),
        sa.Index('idx_relationship_npc', 'npc_id'),
        sa.Index('idx_relationship_type', 'relationship_type'),
        sa.Index('idx_relationship_standing', 'standing')
    )
    
    # Add session metadata columns to journal_entries
    op.add_column('journal_entries', sa.Column('session_number', sa.Integer()))
    op.add_column('journal_entries', sa.Column('session_date', sa.DateTime()))
    op.add_column('journal_entries', sa.Column('dm_name', sa.String()))
    op.add_column('journal_entries', sa.Column('session_summary', sa.Text()))
    
    # Create indices for session-related queries
    op.create_index('idx_journal_session_number', 'journal_entries', ['session_number'])
    op.create_index('idx_journal_session_date', 'journal_entries', ['session_date'])
    
    # Create compound indices for common query patterns
    op.create_index(
        'idx_journal_char_session',
        'journal_entries',
        ['character_id', 'session_number'],
        unique=True,
        postgresql_where=sa.text("session_number IS NOT NULL")
    )
    op.create_index(
        'idx_journal_char_type_date',
        'journal_entries',
        ['character_id', 'entry_type', 'timestamp']
    )

def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('npc_relationships')
    op.drop_table('quests')
    op.drop_table('experience_entries')
    
    # Drop session-related indices
    op.drop_index('idx_journal_char_type_date')
    op.drop_index('idx_journal_char_session')
    op.drop_index('idx_journal_session_date')
    op.drop_index('idx_journal_session_number')
    
    # Drop session-related columns
    op.drop_column('journal_entries', 'session_summary')
    op.drop_column('journal_entries', 'dm_name')
    op.drop_column('journal_entries', 'session_date')
    op.drop_column('journal_entries', 'session_number')
    
    # Finally drop the main journal_entries table
    op.drop_table('journal_entries')
