"""Create character database schema.

Revision ID: 2025_09_20_01
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create character schema
    op.execute('CREATE SCHEMA IF NOT EXISTS character')

    # Create Alignment enum type
    op.execute("""
        CREATE TYPE character.alignment_type AS ENUM (
            'LG', 'NG', 'CG',
            'LN', 'N', 'CN',
            'LE', 'NE', 'CE'
        )
    """)

    # Create ResourceRecharge enum type
    op.execute("""
        CREATE TYPE character.resource_recharge_type AS ENUM (
            'short_rest',
            'long_rest',
            'dawn'
        )
    """)

    # Create themes table first (referenced by characters)
    op.create_table('themes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.String()),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', JSON, default=dict),
        schema='character'
    )

    # Create characters table
    op.create_table('characters',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('player_name', sa.String()),
        sa.Column('class_name', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('background', sa.String(), nullable=False),
        sa.Column('race', sa.String(), nullable=False),
        sa.Column('alignment', sa.Enum('LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE',
                                     name='alignment_type', schema='character')),
        sa.Column('experience_points', sa.Integer(), default=0),
        
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
        sa.Column('temporary_hit_points', sa.Integer(), default=0),
        sa.Column('hit_dice_total', sa.String(), nullable=False),
        sa.Column('hit_dice_current', sa.Integer(), nullable=False),
        sa.Column('death_save_successes', sa.Integer(), default=0),
        sa.Column('death_save_failures', sa.Integer(), default=0),
        sa.Column('exhaustion_level', sa.Integer(), default=0),
        sa.Column('inspiration', sa.Boolean(), default=False),
        
        # Proficiencies
        sa.Column('languages', ARRAY(sa.String()), default=list),
        sa.Column('weapon_proficiencies', ARRAY(sa.String()), default=list),
        sa.Column('armor_proficiencies', ARRAY(sa.String()), default=list),
        sa.Column('tool_proficiencies', ARRAY(sa.String()), default=list),
        sa.Column('saving_throw_proficiencies', ARRAY(sa.String()), default=list),
        sa.Column('skill_proficiencies', ARRAY(sa.String()), default=list),
        
        # Character Personality
        sa.Column('personality_traits', ARRAY(sa.String()), default=list),
        sa.Column('ideals', ARRAY(sa.String()), default=list),
        sa.Column('bonds', ARRAY(sa.String()), default=list),
        sa.Column('flaws', ARRAY(sa.String()), default=list),
        
        # Rich Text Fields
        sa.Column('backstory', sa.Text(), default=''),
        sa.Column('notes', sa.Text(), default=''),
        
        # Foreign Keys
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('character.themes.id')),
        sa.Column('campaign_id', UUID(as_uuid=True)),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        
        # Metadata and State
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('metadata', JSON, default=dict),
        schema='character'
    )

    # Create character_conditions table
    op.create_table('character_conditions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('condition_name', sa.String(), nullable=False),
        sa.Column('source', sa.String()),
        sa.Column('duration', sa.Integer()),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime()),
        sa.Column('notes', sa.String()),
        schema='character'
    )

    # Create class_resources table
    op.create_table('class_resources',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('maximum', sa.Integer(), nullable=False),
        sa.Column('current', sa.Integer(), nullable=False),
        sa.Column('recharge', sa.Enum('short_rest', 'long_rest', 'dawn',
                                    name='resource_recharge_type', schema='character'),
                 nullable=False, default='long_rest'),
        schema='character'
    )

    # Create inventories table
    op.create_table('inventories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), 
                 nullable=False, unique=True),
        sa.Column('copper', sa.Integer(), default=0),
        sa.Column('silver', sa.Integer(), default=0),
        sa.Column('electrum', sa.Integer(), default=0),
        sa.Column('gold', sa.Integer(), default=0),
        sa.Column('platinum', sa.Integer(), default=0),
        sa.Column('armor_slot', UUID(as_uuid=True)),
        sa.Column('shield_slot', UUID(as_uuid=True)),
        sa.Column('weapon_slots', ARRAY(UUID(as_uuid=True)), default=list),
        sa.Column('attuned_items', ARRAY(UUID(as_uuid=True)), default=list),
        schema='character'
    )

    # Create inventory_items table
    op.create_table('inventory_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('inventory_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.inventories.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('weight', sa.Float(), default=0.0),
        sa.Column('value_cp', sa.Integer(), default=0),
        sa.Column('properties', JSON, default=dict),
        sa.Column('is_equipped', sa.Boolean(), default=False),
        sa.Column('requires_attunement', sa.Boolean(), default=False),
        sa.Column('is_attuned', sa.Boolean(), default=False),
        schema='character'
    )

    # Create spellcasting table
    op.create_table('spellcasting',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), 
                 nullable=False, unique=True),
        sa.Column('spellcasting_ability', sa.String(), nullable=False),
        sa.Column('spell_class', sa.String(), nullable=False),
        sa.Column('slots_total', JSON, default=dict),
        sa.Column('slots_expended', JSON, default=dict),
        sa.Column('spells_known', ARRAY(UUID(as_uuid=True)), default=list),
        sa.Column('spells_prepared', ARRAY(UUID(as_uuid=True)), default=list),
        sa.Column('concentrating', sa.Boolean(), default=False),
        sa.Column('concentration_spell_id', UUID(as_uuid=True)),
        schema='character'
    )

    # Create journal_entries table
    op.create_table('journal_entries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('xp_gained', sa.Integer(), default=0),
        sa.Column('milestones', ARRAY(sa.String()), default=list),
        sa.Column('dm_notes', sa.String()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='character'
    )

    # Create character_versions table
    op.create_table('character_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.characters.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('theme_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.themes.id')),
        sa.Column('parent_version_id', UUID(as_uuid=True), 
                 sa.ForeignKey('character.character_versions.id')),
        sa.Column('data', JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('changes', ARRAY(sa.String()), default=list),
        sa.Column('reason', sa.String()),
        schema='character'
    )

def downgrade() -> None:
    # Drop all tables in the correct order
    op.drop_table('character_versions', schema='character')
    op.drop_table('journal_entries', schema='character')
    op.drop_table('spellcasting', schema='character')
    op.drop_table('inventory_items', schema='character')
    op.drop_table('inventories', schema='character')
    op.drop_table('class_resources', schema='character')
    op.drop_table('character_conditions', schema='character')
    op.drop_table('characters', schema='character')
    op.drop_table('themes', schema='character')

    # Drop enum types
    op.execute('DROP TYPE character.resource_recharge_type')
    op.execute('DROP TYPE character.alignment_type')

    # Drop schema
    op.execute('DROP SCHEMA character')