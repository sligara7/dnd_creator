"""Create session database schema.

This migration creates the session database schema and all required tables
within the session schema in the storage service. The schema is designed
to handle real-time game session management and state tracking.

Revision ID: 2025_09_20_07
Revises: 2025_09_20_06
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_07'
down_revision: Union[str, None] = '2025_09_20_06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create session schema and all required tables."""
    # Create session schema
    op.execute('CREATE SCHEMA IF NOT EXISTS session')
    
    # Create enums
    op.execute("""
        CREATE TYPE session.session_state AS ENUM (
            'setup',      -- Initial session setup
            'running',    -- Session in progress
            'paused',     -- Temporarily paused
            'combat',     -- In combat mode
            'roleplay',   -- In roleplay mode
            'exploration',-- In exploration mode
            'complete'    -- Session completed
        )
    """)

    op.execute("""
        CREATE TYPE session.combat_state AS ENUM (
            'not_in_combat',
            'initiative',
            'combat_active',
            'combat_paused',
            'combat_complete'
        )
    """)

    op.execute("""
        CREATE TYPE session.connection_state AS ENUM (
            'connected',
            'connecting',
            'disconnected',
            'reconnecting',
            'error'
        )
    """)

    op.execute("""
        CREATE TYPE session.action_type AS ENUM (
            'movement',
            'action',
            'bonus_action',
            'reaction',
            'ability',
            'spell',
            'item_use',
            'roleplay',
            'custom'
        )
    """)

    # Create game_sessions table
    op.create_table('game_sessions',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('dm_id', UUID(as_uuid=True), nullable=False),  # Game Master
        sa.Column('state', sa.Enum('setup', 'running', 'paused', 'combat', 'roleplay',
                            'exploration', 'complete', name='session_state', schema='session'),
                 nullable=False, server_default='setup'),
        sa.Column('session_number', sa.Integer(), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True)),
        sa.Column('ended_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='session'
    )

    # Create session_participants table
    op.create_table('session_participants',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', UUID(as_uuid=True)),  # Null for DMs/observers
        sa.Column('role', sa.String(50), nullable=False),  # player, dm, observer
        sa.Column('connection_state',
                 sa.Enum('connected', 'connecting', 'disconnected', 'reconnecting', 'error',
                       name='connection_state', schema='session'),
                 nullable=False, server_default='disconnected'),
        sa.Column('last_action', sa.DateTime(timezone=True)),
        sa.Column('joined_at', sa.DateTime(timezone=True)),
        sa.Column('left_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='session'
    )

    # Create combat_encounters table
    op.create_table('combat_encounters',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('state', sa.Enum('not_in_combat', 'initiative', 'combat_active', 'combat_paused',
                            'combat_complete', name='combat_state', schema='session'),
                 nullable=False, server_default='not_in_combat'),
        sa.Column('round_number', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_turn', sa.Integer()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('ended_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='session'
    )

    # Create combat_participants table
    op.create_table('combat_participants',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('encounter_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.combat_encounters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('character_id', UUID(as_uuid=True)),  # Can be null for NPCs/monsters
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('initiative', sa.Integer(), nullable=False),
        sa.Column('initiative_modifier', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_hp', sa.Integer()),
        sa.Column('max_hp', sa.Integer()),
        sa.Column('temporary_hp', sa.Integer(), server_default='0'),
        sa.Column('conditions', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('is_ally', sa.Boolean(), nullable=False),
        sa.Column('turn_order', sa.Integer()),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='session'
    )

    # Create session_actions table
    op.create_table('session_actions',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.session_participants.id'), nullable=False),
        sa.Column('encounter_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.combat_encounters.id')),  # Null if not in combat
        sa.Column('action_type', sa.Enum('movement', 'action', 'bonus_action', 'reaction',
                                'ability', 'spell', 'item_use', 'roleplay', 'custom',
                                name='action_type', schema='session'),
                 nullable=False),
        sa.Column('action_data', JSONB, nullable=False),
        sa.Column('targets', ARRAY(UUID(as_uuid=True)), nullable=False, server_default='{}'),
        sa.Column('round_number', sa.Integer()),  # Null if not in combat
        sa.Column('turn_number', sa.Integer()),   # Null if not in combat
        sa.Column('resolution', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='session'
    )

    # Create session_events table for other significant events
    op.create_table('session_events',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True)),  # Optional reference to event source
        sa.Column('source_type', sa.String(50)),     # Type of the source
        sa.Column('event_data', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='session'
    )

    # Create session_state_history table
    op.create_table('session_state_history',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True),
                 sa.ForeignKey('session.game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('state', sa.Enum('setup', 'running', 'paused', 'combat', 'roleplay',
                            'exploration', 'complete', name='session_state', schema='session'),
                 nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('changed_by', UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.Text()),
        schema='session'
    )

    # Create indices
    op.create_index('ix_session_game_sessions_campaign_id', 'game_sessions',
                  ['campaign_id'], schema='session')
    op.create_index('ix_session_game_sessions_dm_id', 'game_sessions',
                  ['dm_id'], schema='session')
    op.create_index('ix_session_participants_session_id', 'session_participants',
                  ['session_id'], schema='session')
    op.create_index('ix_session_participants_user_id', 'session_participants',
                  ['user_id'], schema='session')
    op.create_index('ix_session_combat_encounters_session_id', 'combat_encounters',
                  ['session_id'], schema='session')
    op.create_index('ix_session_combat_participants_encounter_id', 'combat_participants',
                  ['encounter_id'], schema='session')
    op.create_index('ix_session_actions_session_id', 'session_actions',
                  ['session_id'], schema='session')
    op.create_index('ix_session_actions_participant_id', 'session_actions',
                  ['participant_id'], schema='session')
    op.create_index('ix_session_events_session_id', 'session_events',
                  ['session_id'], schema='session')
    op.create_index('ix_session_state_history_session_id', 'session_state_history',
                  ['session_id'], schema='session')

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION session.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers
    for table in ['game_sessions', 'session_participants', 'combat_encounters',
                'combat_participants']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_modtime
                BEFORE UPDATE ON session.{table}
                FOR EACH ROW
                EXECUTE FUNCTION session.update_updated_at_column();
        """)

def downgrade() -> None:
    """Remove session schema and all tables."""
    # Drop triggers
    for table in ['game_sessions', 'session_participants', 'combat_encounters',
                'combat_participants']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_modtime ON session.{table}')
    op.execute('DROP FUNCTION IF EXISTS session.update_updated_at_column()')

    # Drop indices
    op.drop_index('ix_session_state_history_session_id', table_name='session_state_history',
                schema='session')
    op.drop_index('ix_session_events_session_id', table_name='session_events',
                schema='session')
    op.drop_index('ix_session_actions_participant_id', table_name='session_actions',
                schema='session')
    op.drop_index('ix_session_actions_session_id', table_name='session_actions',
                schema='session')
    op.drop_index('ix_session_combat_participants_encounter_id',
                table_name='combat_participants', schema='session')
    op.drop_index('ix_session_combat_encounters_session_id',
                table_name='combat_encounters', schema='session')
    op.drop_index('ix_session_participants_user_id', table_name='session_participants',
                schema='session')
    op.drop_index('ix_session_participants_session_id', table_name='session_participants',
                schema='session')
    op.drop_index('ix_session_game_sessions_dm_id', table_name='game_sessions',
                schema='session')
    op.drop_index('ix_session_game_sessions_campaign_id', table_name='game_sessions',
                schema='session')

    # Drop tables
    op.drop_table('session_state_history', schema='session')
    op.drop_table('session_events', schema='session')
    op.drop_table('session_actions', schema='session')
    op.drop_table('combat_participants', schema='session')
    op.drop_table('combat_encounters', schema='session')
    op.drop_table('session_participants', schema='session')
    op.drop_table('game_sessions', schema='session')

    # Drop enums
    op.execute('DROP TYPE session.action_type')
    op.execute('DROP TYPE session.connection_state')
    op.execute('DROP TYPE session.combat_state')
    op.execute('DROP TYPE session.session_state')

    # Drop schema
    op.execute('DROP SCHEMA session')