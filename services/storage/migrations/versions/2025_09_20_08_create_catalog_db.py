"""Create catalog database schema.

This migration creates the catalog database schema and all required tables
within the catalog schema in the storage service. The schema handles the storage
and management of D&D 5e 2024 game content including items, spells, rules, and
other game assets.

Revision ID: 2025_09_20_08
Revises: 2025_09_20_07
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_08'
down_revision: Union[str, None] = '2025_09_20_07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create catalog schema and all required tables."""
    # Create catalog schema
    op.execute('CREATE SCHEMA IF NOT EXISTS catalog')
    
    # Create enums
    op.execute("""
        CREATE TYPE catalog.item_rarity AS ENUM (
            'common',
            'uncommon',
            'rare',
            'very_rare',
            'legendary',
            'artifact'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.item_type AS ENUM (
            'weapon',
            'armor',
            'potion',
            'scroll',
            'ring',
            'rod',
            'staff',
            'wand',
            'wondrous',
            'ammunition',
            'container',
            'currency',
            'other'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.attunement_state AS ENUM (
            'none',
            'attuned',
            'attuning',
            'broken'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.effect_type AS ENUM (
            'passive',
            'active',
            'triggered',
            'charged',
            'curse'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.effect_duration AS ENUM (
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
        CREATE TYPE catalog.spell_school AS ENUM (
            'abjuration',
            'conjuration',
            'divination',
            'enchantment',
            'evocation',
            'illusion',
            'necromancy',
            'transmutation'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.spell_component AS ENUM (
            'verbal',
            'somatic',
            'material'
        )
    """)

    op.execute("""
        CREATE TYPE catalog.content_state AS ENUM (
            'draft',
            'review',
            'approved',
            'published',
            'deprecated'
        )
    """)

    # Create base content table - parent table for all content types
    op.create_table('content',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('parent_id', UUID(as_uuid=True)),  # For content derivation/versioning
        sa.Column('content_type', sa.String(50), nullable=False),  # Discriminator
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('source', sa.String(255), nullable=False),  # Book/supplement/custom
        sa.Column('theme', sa.String(50), nullable=False, server_default='traditional'),
        sa.Column('theme_data', JSONB, nullable=False, server_default='{}'),
        sa.Column('state', sa.Enum('draft', 'review', 'approved', 'published', 'deprecated',
                            name='content_state', schema='catalog'),
                 nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('tags', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('search_vector', sa.text('tsvector')),  # Full text search
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='catalog'
    )

    # Create items table
    op.create_table('items',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id'), primary_key=True),
        sa.Column('item_type', sa.Enum('weapon', 'armor', 'potion', 'scroll', 'ring', 'rod', 'staff',
                                'wand', 'wondrous', 'ammunition', 'container', 'currency', 'other',
                                name='item_type', schema='catalog'),
                 nullable=False),
        sa.Column('rarity', sa.Enum('common', 'uncommon', 'rare', 'very_rare', 'legendary', 'artifact',
                            name='item_rarity', schema='catalog'),
                 nullable=False),
        sa.Column('requires_attunement', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('attunement_requirements', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('attunement_state', sa.Enum('none', 'attuned', 'attuning', 'broken',
                                    name='attunement_state', schema='catalog'),
                 nullable=False, server_default='none'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='0'),
        sa.Column('value', sa.Integer(), nullable=False, server_default='0'),  # In copper pieces
        sa.Column('properties', JSONB, nullable=False, server_default='{}'),
        sa.Column('effects', ARRAY(UUID(as_uuid=True)), nullable=False, server_default='{}'),
        schema='catalog'
    )

    # Create item effects table
    op.create_table('item_effects',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('effect_type', sa.Enum('passive', 'active', 'triggered', 'charged', 'curse',
                                name='effect_type', schema='catalog'),
                 nullable=False),
        sa.Column('duration_type', sa.Enum('instant', 'permanent', 'temporary', 'until_dawn',
                                'until_dusk', 'until_long_rest', 'until_short_rest', 'charges',
                                name='effect_duration', schema='catalog'),
                 nullable=False),
        sa.Column('duration_value', sa.Integer()),  # For charges or time-based
        sa.Column('activation_type', sa.String(50)),  # action, bonus, reaction
        sa.Column('activation_cost', JSONB),  # Resources required
        sa.Column('saving_throw', JSONB),  # Save type and DC
        sa.Column('effect_data', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='catalog'
    )

    # Create spells table
    op.create_table('spells',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id'), primary_key=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('school', sa.Enum('abjuration', 'conjuration', 'divination', 'enchantment',
                            'evocation', 'illusion', 'necromancy', 'transmutation',
                            name='spell_school', schema='catalog'),
                 nullable=False),
        sa.Column('casting_time', sa.String(50), nullable=False),
        sa.Column('range', sa.String(50), nullable=False),
        sa.Column('components', ARRAY(sa.Enum('verbal', 'somatic', 'material',
                                   name='spell_component', schema='catalog')),
                 nullable=False),
        sa.Column('material_components', sa.Text()),
        sa.Column('material_cost', sa.Integer()),  # In copper pieces
        sa.Column('duration', sa.String(50), nullable=False),
        sa.Column('concentration', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ritual', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('classes', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('effect_data', JSONB, nullable=False, server_default='{}'),
        schema='catalog'
    )

    # Create rules table
    op.create_table('rules',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id'), primary_key=True),
        sa.Column('rule_type', sa.String(50), nullable=False),  # combat, skill, class, etc.
        sa.Column('category', sa.String(50), nullable=False),  # Sub-categorization
        sa.Column('applicability', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('prerequisites', JSONB, nullable=False, server_default='{}'),
        sa.Column('rule_text', sa.Text(), nullable=False),
        sa.Column('examples', ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('rule_data', JSONB, nullable=False, server_default='{}'),
        schema='catalog'
    )

    # Create content_relations table for tracking relationships between content
    op.create_table('content_relations',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('source_id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id', ondelete='CASCADE'),
                 nullable=False),
        sa.Column('target_id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id', ondelete='CASCADE'),
                 nullable=False),
        sa.Column('relation_type', sa.String(50), nullable=False),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='catalog'
    )

    # Create content_validations table for tracking validation results
    op.create_table('content_validations',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('content_id', UUID(as_uuid=True), sa.ForeignKey('catalog.content.id', ondelete='CASCADE'),
                 nullable=False),
        sa.Column('validation_type', sa.String(50), nullable=False),
        sa.Column('validator', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('issues', ARRAY(JSONB), nullable=False, server_default='{}'),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        schema='catalog'
    )

    # Create indices
    op.execute("""
        CREATE INDEX idx_catalog_content_search ON catalog.content
        USING gin(search_vector)
    """)

    op.create_index('ix_catalog_content_name', 'content', ['name'], schema='catalog')
    op.create_index('ix_catalog_content_source', 'content', ['source'], schema='catalog')
    op.create_index('ix_catalog_content_theme', 'content', ['theme'], schema='catalog')
    op.create_index('ix_catalog_content_state', 'content', ['state'], schema='catalog')
    op.create_index('ix_catalog_items_type', 'items', ['item_type'], schema='catalog')
    op.create_index('ix_catalog_items_rarity', 'items', ['rarity'], schema='catalog')
    op.create_index('ix_catalog_spells_level', 'spells', ['level'], schema='catalog')
    op.create_index('ix_catalog_spells_school', 'spells', ['school'], schema='catalog')
    op.create_index('ix_catalog_rules_type', 'rules', ['rule_type'], schema='catalog')
    op.create_index('ix_catalog_rules_category', 'rules', ['category'], schema='catalog')

    # Create search triggers
    op.execute("""
        CREATE FUNCTION catalog.update_content_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.source, '')), 'C') ||
                setweight(to_tsvector('english', array_to_string(COALESCE(NEW.tags, ARRAY[]::text[]), ' ')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON catalog.content FOR EACH ROW
        EXECUTE FUNCTION catalog.update_content_search_vector();
    """)

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION catalog.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add update triggers
    for table in ['content', 'items', 'item_effects', 'spells', 'rules']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_modtime
                BEFORE UPDATE ON catalog.{table}
                FOR EACH ROW
                EXECUTE FUNCTION catalog.update_updated_at_column();
        """)

def downgrade() -> None:
    """Remove catalog schema and all tables."""
    # Drop triggers
    for table in ['content', 'items', 'item_effects', 'spells', 'rules']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_modtime ON catalog.{table}')
    op.execute('DROP FUNCTION IF EXISTS catalog.update_updated_at_column()')

    # Drop search triggers and functions
    op.execute('DROP TRIGGER IF EXISTS tsvectorupdate ON catalog.content')
    op.execute('DROP FUNCTION IF EXISTS catalog.update_content_search_vector()')

    # Drop indices
    op.drop_index('ix_catalog_rules_category', table_name='rules', schema='catalog')
    op.drop_index('ix_catalog_rules_type', table_name='rules', schema='catalog')
    op.drop_index('ix_catalog_spells_school', table_name='spells', schema='catalog')
    op.drop_index('ix_catalog_spells_level', table_name='spells', schema='catalog')
    op.drop_index('ix_catalog_items_rarity', table_name='items', schema='catalog')
    op.drop_index('ix_catalog_items_type', table_name='items', schema='catalog')
    op.drop_index('ix_catalog_content_state', table_name='content', schema='catalog')
    op.drop_index('ix_catalog_content_theme', table_name='content', schema='catalog')
    op.drop_index('ix_catalog_content_source', table_name='content', schema='catalog')
    op.drop_index('ix_catalog_content_name', table_name='content', schema='catalog')
    op.execute('DROP INDEX IF EXISTS idx_catalog_content_search')

    # Drop tables in correct order
    op.drop_table('content_validations', schema='catalog')
    op.drop_table('content_relations', schema='catalog')
    op.drop_table('rules', schema='catalog')
    op.drop_table('spells', schema='catalog')
    op.drop_table('item_effects', schema='catalog')
    op.drop_table('items', schema='catalog')
    op.drop_table('content', schema='catalog')

    # Drop enums
    op.execute('DROP TYPE catalog.content_state')
    op.execute('DROP TYPE catalog.spell_component')
    op.execute('DROP TYPE catalog.spell_school')
    op.execute('DROP TYPE catalog.effect_duration')
    op.execute('DROP TYPE catalog.effect_type')
    op.execute('DROP TYPE catalog.attunement_state')
    op.execute('DROP TYPE catalog.item_type')
    op.execute('DROP TYPE catalog.item_rarity')

    # Drop schema
    op.execute('DROP SCHEMA catalog')