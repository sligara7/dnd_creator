"""Add campaign events and progression tracking

Revision ID: 2025_09_06_events
Revises: 2025_09_05_add_theme_system
Create Date: 2025-09-06 03:37:00.000000

"""
from datetime import datetime
from typing import Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2025_09_06_events'
down_revision: Optional[str] = '2025_09_05_add_theme_system'
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    # Create campaign_events table
    op.create_table(
        'campaign_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String, nullable=False),
        sa.Column('event_data', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('impact_type', sa.String, nullable=False),
        sa.Column('impact_magnitude', sa.Integer, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('applied', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('applied_at', sa.DateTime, nullable=True),
        sa.Column('data', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ),
    )
    op.create_index(op.f('ix_campaign_events_character_id'), 'campaign_events', ['character_id'])

    # Create event_impacts table
    op.create_table(
        'event_impacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('impact_type', sa.String, nullable=False),
        sa.Column('impact_data', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('applied', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('applied_at', sa.DateTime, nullable=True),
        sa.Column('reversion_data', postgresql.JSONB, nullable=True),
        sa.Column('is_reverted', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('reverted_at', sa.DateTime, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('data', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['event_id'], ['campaign_events.id'], ),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    )
    op.create_index(op.f('ix_event_impacts_event_id'), 'event_impacts', ['event_id'])
    op.create_index(op.f('ix_event_impacts_character_id'), 'event_impacts', ['character_id'])

    # Create character_progress table
    op.create_table(
        'character_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('experience_points', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('milestones', postgresql.JSONB, nullable=False, server_default=sa.text('[]')),
        sa.Column('achievements', postgresql.JSONB, nullable=False, server_default=sa.text('[]')),
        sa.Column('current_level', sa.Integer, nullable=False, server_default=sa.text('1')),
        sa.Column('previous_level', sa.Integer, nullable=False, server_default=sa.text('1')),
        sa.Column('level_updated_at', sa.DateTime, nullable=True),
        sa.Column('data', postgresql.JSONB, nullable=False, server_default=sa.text('{}')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    )
    op.create_index(op.f('ix_character_progress_character_id'), 'character_progress', ['character_id'])

    # Create updated_at trigger function if it doesn't exist
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # Create update triggers for each table
    op.execute("""
    CREATE TRIGGER update_campaign_events_updated_at
        BEFORE UPDATE ON campaign_events
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_event_impacts_updated_at
        BEFORE UPDATE ON event_impacts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_character_progress_updated_at
        BEFORE UPDATE ON character_progress
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS update_campaign_events_updated_at ON campaign_events")
    op.execute("DROP TRIGGER IF EXISTS update_event_impacts_updated_at ON event_impacts")
    op.execute("DROP TRIGGER IF EXISTS update_character_progress_updated_at ON character_progress")

    # Drop tables in reverse order
    op.drop_table('character_progress')
    op.drop_table('event_impacts')
    op.drop_table('campaign_events')
