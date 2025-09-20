"""Initial schema migration for character database."""

from typing import Sequence
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '000001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def create_type_alignment() -> None:
    """Create alignment enum type."""
    alignment_type = postgresql.ENUM(
        'LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE',
        name='alignment'
    )
    alignment_type.create(op.get_bind())


def create_type_resource_recharge() -> None:
    """Create resource recharge enum type."""
    recharge_type = postgresql.ENUM(
        'short_rest', 'long_rest', 'dawn',
        name='resource_recharge'
    )
    recharge_type.create(op.get_bind())


def upgrade() -> None:
    """Upgrade database schema."""
    # Create enum types
    create_type_alignment()
    create_type_resource_recharge()

    # Create themes table first (no dependencies)
    op.create_table(
        'themes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.String()),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('themes.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}')
    )

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('player_name', sa.String()),
        sa.Column('class_name', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('background', sa.String(), nullable=False),
        sa.Column('race', sa.String(), nullable=False),
        sa.Column('alignment', sa.Enum('LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE', name='alignment'), nullable=False),
        sa.Column('experience_points', sa.Integer(), server_default='0'),
        
        # Character Details
        sa.Column('age', sa.Integer()),
        sa.Column('height', sa.String()),
        sa.Column('weight', sa.String()),
        sa.Column('eye_color', sa.String()),
        sa.Column('skin_color', sa.String()),
        sa.Column('hair_color', sa.String()),
        
        # Ability Scores
        sa.Column('strength', sa.Integer(), nullable=False),
        sa.Column('dexterity', sa.Integer(), nullable=False),
        sa.Column('constitution', sa.Integer(), nullable=False),
        sa.Column('intelligence', sa.Integer(), nullable=False),
        sa.Column('wisdom', sa.Integer(), nullable=False),
        sa.Column('charisma', sa.Integer(), nullable=False),
        
        # Health & Resources
        sa.Column('max_hit_points', sa.Integer(), nullable=False),
        sa.Column('current_hit_points', sa.Integer(), nullable=False),
        sa.Column('temporary_hit_points', sa.Integer(), server_default='0'),
        sa.Column('hit_dice_total', sa.String(), nullable=False),
        sa.Column('hit_dice_current', sa.Integer(), nullable=False),
        sa.Column('death_save_successes', sa.Integer(), server_default='0'),
        sa.Column('death_save_failures', sa.Integer(), server_default='0'),
        sa.Column('exhaustion_level', sa.Integer(), server_default='0'),
        sa.Column('inspiration', sa.Boolean(), server_default='false'),
        
        # Proficiencies
        sa.Column('languages', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('weapon_proficiencies', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('armor_proficiencies', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('tool_proficiencies', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('saving_throw_proficiencies', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('skill_proficiencies', postgresql.ARRAY(sa.String()), server_default='{}'),
        
        # Character Personality
        sa.Column('personality_traits', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('ideals', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('bonds', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('flaws', postgresql.ARRAY(sa.String()), server_default='{}'),
        
        # Rich Text
        sa.Column('backstory', sa.String(), server_default=''),
        sa.Column('notes', sa.String(), server_default=''),
        
        # Foreign Keys
        sa.Column('theme_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('themes.id')),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True)),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}')
    )

    # Create character_versions table
    op.create_table(
        'character_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('theme_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('themes.id')),
        sa.Column('parent_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('character_versions.id')),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changes', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('reason', sa.String())
    )

    # Create inventories table
    op.create_table(
        'inventories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False, unique=True),
        sa.Column('copper', sa.Integer(), server_default='0'),
        sa.Column('silver', sa.Integer(), server_default='0'),
        sa.Column('electrum', sa.Integer(), server_default='0'),
        sa.Column('gold', sa.Integer(), server_default='0'),
        sa.Column('platinum', sa.Integer(), server_default='0'),
        sa.Column('armor_slot', postgresql.UUID(as_uuid=True)),
        sa.Column('shield_slot', postgresql.UUID(as_uuid=True)),
        sa.Column('weapon_slots', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('attuned_items', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}')
    )

    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inventories.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('quantity', sa.Integer(), server_default='1'),
        sa.Column('weight', sa.Float(), server_default='0'),
        sa.Column('value_cp', sa.Integer(), server_default='0'),
        sa.Column('properties', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_equipped', sa.Boolean(), server_default='false'),
        sa.Column('requires_attunement', sa.Boolean(), server_default='false'),
        sa.Column('is_attuned', sa.Boolean(), server_default='false')
    )

    # Create spellcasting table
    op.create_table(
        'spellcasting',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False, unique=True),
        sa.Column('spellcasting_ability', sa.String(), nullable=False),
        sa.Column('spell_class', sa.String(), nullable=False),
        sa.Column('slots_total', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('slots_expended', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('spells_known', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('spells_prepared', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('concentrating', sa.Boolean(), server_default='false'),
        sa.Column('concentration_spell_id', postgresql.UUID(as_uuid=True))
    )

    # Create character_conditions table
    op.create_table(
        'character_conditions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('condition_name', sa.String(), nullable=False),
        sa.Column('source', sa.String()),
        sa.Column('duration', sa.Integer()),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime()),
        sa.Column('notes', sa.String())
    )

    # Create class_resources table
    op.create_table(
        'class_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('maximum', sa.Integer(), nullable=False),
        sa.Column('current', sa.Integer(), nullable=False),
        sa.Column('recharge', sa.Enum('short_rest', 'long_rest', 'dawn', name='resource_recharge'), nullable=False)
    )

    # Create journal_entries table
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('xp_gained', sa.Integer(), server_default='0'),
        sa.Column('milestones', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('dm_notes', sa.String()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # Create indexes
    op.create_index('ix_characters_name', 'characters', ['name'])
    op.create_index('ix_characters_owner_id', 'characters', ['owner_id'])
    op.create_index('ix_characters_campaign_id', 'characters', ['campaign_id'])
    op.create_index('ix_character_versions_character_id', 'character_versions', ['character_id'])
    op.create_index('ix_inventory_items_inventory_id', 'inventory_items', ['inventory_id'])
    op.create_index('ix_journal_entries_character_id', 'journal_entries', ['character_id'])
    op.create_index('ix_journal_entries_session_date', 'journal_entries', ['session_date'])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop tables in reverse order of creation
    op.drop_table('journal_entries')
    op.drop_table('class_resources')
    op.drop_table('character_conditions')
    op.drop_table('spellcasting')
    op.drop_table('inventory_items')
    op.drop_table('inventories')
    op.drop_table('character_versions')
    op.drop_table('characters')
    op.drop_table('themes')

    # Drop enum types
    op.execute('DROP TYPE alignment')
    op.execute('DROP TYPE resource_recharge')