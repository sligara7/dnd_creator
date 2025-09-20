"""Create consolidated character schema.

This migration creates the complete character database schema and all required tables
within the character schema in the storage service, replacing the direct database access
that was previously in the Character Service.

Revision ID: 2025_09_20_02
Revises: 2025_09_20_01
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_02'
down_revision: Union[str, None] = '2025_09_20_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create character schema and all required tables."""
    # First create all enums
    op.execute("""
        CREATE TYPE character.alignment_type AS ENUM (
            'LG', 'NG', 'CG',
            'LN', 'N', 'CN',
            'LE', 'NE', 'CE'
        )
    """)

    op.execute("""
        CREATE TYPE character.resource_recharge_type AS ENUM (
            'short_rest',
            'long_rest',
            'dawn'
        )
    """)

    op.execute("""
        CREATE TYPE character.item_location_type AS ENUM (
            'equipped',
            'carried',
            'stored',
            'container',
            'mount',
            'bank',
            'vault'
        )
    """)

    op.execute("""
        CREATE TYPE character.effect_type AS ENUM (
            'passive',
            'active',
            'triggered',
            'charged',
            'curse'
        )
    """)

    op.execute("""
        CREATE TYPE character.effect_duration_type AS ENUM (
            'instant',
            'permanent',
            'temporary',
            'until_dawn',
            'until_dusk',
            'until_long_rest',
            'until_short_rest',
            'charges'
        )
    """)

    op.execute("""
        CREATE TYPE character.event_type AS ENUM (
            'level_up',
            'milestone',
            'quest_complete',
            'achievement',
            'story_development',
            'campaign_event',
            'death',
            'resurrection',
            'theme_transition',
            'party_role',
            'training',
            'custom'
        )
    """)

    # Create theme tables
    op.create_table('themes',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('base_modifiers', JSONB, nullable=False, server_default='{}'),
        sa.Column('ability_adjustments', JSONB, nullable=False, server_default='{}'),
        sa.Column('level_requirement', sa.Integer(), default=1),
        sa.Column('class_restrictions', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('race_restrictions', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('parent_theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('theme_features',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('level_granted', sa.Integer(), default=1),
        sa.Column('mechanics', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_optional', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('theme_equipment',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id'), nullable=False),
        sa.Column('item_id', UUID(as_uuid=True), nullable=False),  # References catalog service item
        sa.Column('operation', sa.String(), nullable=False),  # add/remove/replace
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('requirements', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('theme_progression_rules',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('trigger_type', sa.String(), nullable=False),
        sa.Column('trigger_conditions', JSONB, nullable=False, server_default='{}'),
        sa.Column('effects', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    # Create core character tables
    op.create_table('characters',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('parent_id', UUID(as_uuid=True)),  # For theme chain
        sa.Column('theme', sa.String(), nullable=False, server_default='traditional'),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', UUID(as_uuid=True), nullable=False),
        sa.Column('character_data', JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    # Create theme state table (links themes to characters)
    op.create_table('theme_states',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('applied_at', sa.DateTime(), nullable=False),
        sa.Column('deactivated_at', sa.DateTime()),
        sa.Column('applied_features', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('applied_modifiers', JSONB, nullable=False, server_default='{}'),
        sa.Column('progress_state', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    # Create inventory tables
    op.create_table('inventory_items',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('root_id', UUID(as_uuid=True)),  # Original item this was adapted from
        sa.Column('theme', sa.String(), nullable=False, server_default='traditional'),
        sa.Column('character_id', UUID(as_uuid=True), sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('item_data', JSONB, nullable=False),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('equipped', sa.Boolean(), default=False),
        sa.Column('container', sa.String()),
        sa.Column('notes', sa.Text()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('containers',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('character.inventory_items.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('capacity', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('capacity_type', sa.String(), nullable=False, server_default='weight'),
        sa.Column('is_magical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('restrictions', ARRAY(sa.String)),
        schema='character'
    )

    # Create journal system tables
    op.create_table('journal_entries',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('entry_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('data', JSONB, nullable=False, server_default='{}'),
        sa.Column('tags', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('session_number', sa.Integer()),
        sa.Column('session_date', sa.DateTime()),
        sa.Column('dm_name', sa.String()),
        sa.Column('session_summary', sa.Text()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('experience_entries',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('journal_entry_id', UUID(as_uuid=True), sa.ForeignKey('character.journal_entries.id'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('session_id', UUID(as_uuid=True)),
        sa.Column('data', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='character'
    )

    op.create_table('quests',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('journal_entry_id', UUID(as_uuid=True), sa.ForeignKey('character.journal_entries.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('importance', sa.String(), nullable=False, server_default='normal'),
        sa.Column('assigned_by', sa.String()),
        sa.Column('rewards', JSONB, nullable=False, server_default='{}'),
        sa.Column('progress', ARRAY(JSONB), nullable=False, server_default='{}'),
        sa.Column('data', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='character'
    )

    op.create_table('npc_relationships',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('journal_entry_id', UUID(as_uuid=True), sa.ForeignKey('character.journal_entries.id'), nullable=False),
        sa.Column('npc_id', UUID(as_uuid=True), nullable=False),
        sa.Column('npc_name', sa.String(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('standing', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('last_interaction', sa.DateTime()),
        sa.Column('data', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='character'
    )

    # Create version control tables
    op.create_table('version_graphs',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('version_nodes',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('graph_id', UUID(as_uuid=True), sa.ForeignKey('character.version_graphs.id'), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),  # ID of the actual entity
        sa.Column('type', sa.String(), nullable=False),  # VersionNodeType
        sa.Column('theme', sa.String(), nullable=False),
        sa.Column('node_metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    op.create_table('version_edges',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('graph_id', UUID(as_uuid=True), sa.ForeignKey('character.version_graphs.id'), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True), sa.ForeignKey('character.version_nodes.id'), nullable=False),
        sa.Column('target_id', UUID(as_uuid=True), sa.ForeignKey('character.version_nodes.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),  # EdgeType
        sa.Column('edge_metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    # Create indices
    op.create_index('ix_character_themes_name', 'themes', ['name'], unique=True, schema='character')
    op.create_index('ix_character_characters_user_id', 'characters', ['user_id'], schema='character')
    op.create_index('ix_character_characters_campaign_id', 'characters', ['campaign_id'], schema='character')
    op.create_index('ix_character_inventory_items_character_id', 'inventory_items', ['character_id'], schema='character')
    op.create_index('ix_character_journal_entries_character_id', 'journal_entries', ['character_id'], schema='character')
    op.create_index('ix_character_journal_entries_session_date', 'journal_entries', ['session_date'], schema='character')
    op.create_index('ix_character_version_nodes_graph_id', 'version_nodes', ['graph_id'], schema='character')
    op.create_index('ix_character_version_nodes_entity_id', 'version_nodes', ['entity_id'], schema='character')
    op.create_index('ix_character_version_edges_graph_id', 'version_edges', ['graph_id'], schema='character')
    op.create_index('ix_character_version_edges_source_id', 'version_edges', ['source_id'], schema='character')
    op.create_index('ix_character_version_edges_target_id', 'version_edges', ['target_id'], schema='character')

def downgrade() -> None:
    """Remove character schema and all tables."""
    # Drop indices
    op.drop_index('ix_character_version_edges_target_id', table_name='version_edges', schema='character')
    op.drop_index('ix_character_version_edges_source_id', table_name='version_edges', schema='character')
    op.drop_index('ix_character_version_edges_graph_id', table_name='version_edges', schema='character')
    op.drop_index('ix_character_version_nodes_entity_id', table_name='version_nodes', schema='character')
    op.drop_index('ix_character_version_nodes_graph_id', table_name='version_nodes', schema='character')
    op.drop_index('ix_character_journal_entries_session_date', table_name='journal_entries', schema='character')
    op.drop_index('ix_character_journal_entries_character_id', table_name='journal_entries', schema='character')
    op.drop_index('ix_character_inventory_items_character_id', table_name='inventory_items', schema='character')
    op.drop_index('ix_character_characters_campaign_id', table_name='characters', schema='character')
    op.drop_index('ix_character_characters_user_id', table_name='characters', schema='character')
    op.drop_index('ix_character_themes_name', table_name='themes', schema='character')

    # Drop tables in correct order
    op.drop_table('version_edges', schema='character')
    op.drop_table('version_nodes', schema='character')
    op.drop_table('version_graphs', schema='character')
    op.drop_table('npc_relationships', schema='character')
    op.drop_table('quests', schema='character')
    op.drop_table('experience_entries', schema='character')
    op.drop_table('journal_entries', schema='character')
    op.drop_table('containers', schema='character')
    op.drop_table('inventory_items', schema='character')
    op.drop_table('theme_states', schema='character')
    op.drop_table('characters', schema='character')
    op.drop_table('theme_progression_rules', schema='character')
    op.drop_table('theme_equipment', schema='character')
    op.drop_table('theme_features', schema='character')
    op.drop_table('themes', schema='character')

    # Drop enums
    op.execute('DROP TYPE character.event_type')
    op.execute('DROP TYPE character.effect_duration_type')
    op.execute('DROP TYPE character.effect_type')
    op.execute('DROP TYPE character.item_location_type')
    op.execute('DROP TYPE character.resource_recharge_type')
    op.execute('DROP TYPE character.alignment_type')