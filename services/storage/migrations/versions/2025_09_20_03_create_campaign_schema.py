"""Create consolidated campaign schema.

This migration creates the complete campaign database schema and all required tables
within the campaign schema in the storage service, replacing the direct database access
that was previously in the Campaign Service.

Revision ID: 2025_09_20_03
Revises: 2025_09_20_02
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_03'
down_revision: Union[str, None] = '2025_09_20_02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create campaign schema and all required tables."""
    # Create campaign schema
    op.execute('CREATE SCHEMA IF NOT EXISTS campaign')
    
    # Create enums
    op.execute("""
        CREATE TYPE campaign.campaign_type AS ENUM (
            'traditional',
            'antitheticon'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.campaign_state AS ENUM (
            'draft',
            'active',
            'paused',
            'completed',
            'archived'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.chapter_type AS ENUM (
            'introduction',
            'story',
            'side_quest',
            'boss_battle',
            'finale'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.chapter_state AS ENUM (
            'draft',
            'ready',
            'in_progress',
            'completed'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.plot_type AS ENUM (
            'main',
            'side',
            'character',
            'faction',
            'mystery',
            'hidden'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.plot_state AS ENUM (
            'planned',
            'active',
            'resolved',
            'abandoned'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.story_arc_type AS ENUM (
            'campaign',
            'character',
            'world',
            'theme'
        )
    """)

    op.execute("""
        CREATE TYPE campaign.npc_relation_type AS ENUM (
            'ally',
            'enemy',
            'neutral',
            'rival',
            'mentor',
            'patron',
            'contact',
            'hidden'
        )
    """)

    # Create theme tables
    op.create_table('themes',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('elements', JSONB, nullable=False),  # List[ThemeElement]
        sa.Column('validation_rules', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='campaign'
    )

    op.create_table('theme_versions',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('campaign.themes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('modifications', JSONB, nullable=False),  # Dict[str, float]
        sa.Column('active', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='campaign'
    )

    # Create core campaign tables
    op.create_table('campaigns',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('campaign_type', sa.Enum('traditional', 'antitheticon', name='campaign_type', schema='campaign'), nullable=False),
        sa.Column('state', sa.Enum('draft', 'active', 'paused', 'completed', 'archived', name='campaign_state', schema='campaign'), nullable=False),
        sa.Column('theme_id', UUID(as_uuid=True), sa.ForeignKey('campaign.themes.id')),
        sa.Column('theme_data', JSONB, nullable=False, server_default='{}'),
        sa.Column('campaign_metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('creator_id', UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='campaign'
    )

    op.create_table('chapters',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('chapter_type', sa.Enum('introduction', 'story', 'side_quest', 'boss_battle', 'finale', name='chapter_type', schema='campaign'), nullable=False),
        sa.Column('state', sa.Enum('draft', 'ready', 'in_progress', 'completed', name='chapter_state', schema='campaign'), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('content', JSONB, nullable=False, server_default='{}'),
        sa.Column('chapter_metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('prerequisites', ARRAY(UUID(as_uuid=True)), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='campaign'
    )

    # Create story management tables
    op.create_table('story_arcs',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('arc_type', sa.Enum('campaign', 'character', 'world', 'theme', name='story_arc_type', schema='campaign'), nullable=False),
        sa.Column('content', JSONB, nullable=False, server_default='{}'),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='campaign'
    )

    op.create_table('plots',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('plot_type', sa.Enum('main', 'side', 'character', 'faction', 'mystery', 'hidden', name='plot_type', schema='campaign'), nullable=False),
        sa.Column('state', sa.Enum('planned', 'active', 'resolved', 'abandoned', name='plot_state', schema='campaign'), nullable=False),
        sa.Column('content', JSONB, nullable=False, server_default='{}'),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('parent_plot_id', UUID(as_uuid=True), sa.ForeignKey('campaign.plots.id')),
        sa.Column('arc_id', UUID(as_uuid=True), sa.ForeignKey('campaign.story_arcs.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='campaign'
    )

    op.create_table('plot_chapters',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('plot_id', UUID(as_uuid=True), sa.ForeignKey('campaign.plots.id'), nullable=False),
        sa.Column('chapter_id', UUID(as_uuid=True), sa.ForeignKey('campaign.chapters.id'), nullable=False),
        sa.Column('plot_content', JSONB, nullable=False, server_default='{}'),
        sa.Column('plot_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='campaign'
    )

    # Create themed content tables
    op.create_table('themed_npcs',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('theme_elements', JSONB, nullable=False),  # Dict[str, Dict[str, float]]
        sa.Column('inherit_theme', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='campaign'
    )

    op.create_table('themed_locations',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('theme_elements', JSONB, nullable=False),  # Dict[str, Dict[str, float]]
        sa.Column('inherit_theme', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        schema='campaign'
    )

    op.create_table('npc_relationships',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaign.campaigns.id'), nullable=False),
        sa.Column('npc_id', UUID(as_uuid=True), nullable=False),  # References NPC in catalog
        sa.Column('relation_type', sa.Enum('ally', 'enemy', 'neutral', 'rival', 'mentor', 'patron', 'contact', 'hidden', name='npc_relation_type', schema='campaign'), nullable=False),
        sa.Column('plot_id', UUID(as_uuid=True), sa.ForeignKey('campaign.plots.id')),
        sa.Column('arc_id', UUID(as_uuid=True), sa.ForeignKey('campaign.story_arcs.id')),
        sa.Column('description', sa.Text()),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='campaign'
    )

    # Create indices
    op.create_index('ix_campaign_campaigns_owner_id', 'campaigns', ['owner_id'], schema='campaign')
    op.create_index('ix_campaign_campaigns_creator_id', 'campaigns', ['creator_id'], schema='campaign')
    op.create_index('ix_campaign_chapters_campaign_id', 'chapters', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_chapters_sequence_number', 'chapters', ['sequence_number'], schema='campaign')
    op.create_index('ix_campaign_plots_campaign_id', 'plots', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_plots_arc_id', 'plots', ['arc_id'], schema='campaign')
    op.create_index('ix_campaign_story_arcs_campaign_id', 'story_arcs', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_story_arcs_sequence_number', 'story_arcs', ['sequence_number'], schema='campaign')
    op.create_index('ix_campaign_plot_chapters_plot_id', 'plot_chapters', ['plot_id'], schema='campaign')
    op.create_index('ix_campaign_plot_chapters_chapter_id', 'plot_chapters', ['chapter_id'], schema='campaign')
    op.create_index('ix_campaign_themed_npcs_campaign_id', 'themed_npcs', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_themed_locations_campaign_id', 'themed_locations', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_npc_relationships_campaign_id', 'npc_relationships', ['campaign_id'], schema='campaign')
    op.create_index('ix_campaign_npc_relationships_plot_id', 'npc_relationships', ['plot_id'], schema='campaign')
    op.create_index('ix_campaign_npc_relationships_arc_id', 'npc_relationships', ['arc_id'], schema='campaign')

def downgrade() -> None:
    """Remove campaign schema and all tables."""
    # Drop indices
    op.drop_index('ix_campaign_npc_relationships_arc_id', table_name='npc_relationships', schema='campaign')
    op.drop_index('ix_campaign_npc_relationships_plot_id', table_name='npc_relationships', schema='campaign')
    op.drop_index('ix_campaign_npc_relationships_campaign_id', table_name='npc_relationships', schema='campaign')
    op.drop_index('ix_campaign_themed_locations_campaign_id', table_name='themed_locations', schema='campaign')
    op.drop_index('ix_campaign_themed_npcs_campaign_id', table_name='themed_npcs', schema='campaign')
    op.drop_index('ix_campaign_plot_chapters_chapter_id', table_name='plot_chapters', schema='campaign')
    op.drop_index('ix_campaign_plot_chapters_plot_id', table_name='plot_chapters', schema='campaign')
    op.drop_index('ix_campaign_story_arcs_sequence_number', table_name='story_arcs', schema='campaign')
    op.drop_index('ix_campaign_story_arcs_campaign_id', table_name='story_arcs', schema='campaign')
    op.drop_index('ix_campaign_plots_arc_id', table_name='plots', schema='campaign')
    op.drop_index('ix_campaign_plots_campaign_id', table_name='plots', schema='campaign')
    op.drop_index('ix_campaign_chapters_sequence_number', table_name='chapters', schema='campaign')
    op.drop_index('ix_campaign_chapters_campaign_id', table_name='chapters', schema='campaign')
    op.drop_index('ix_campaign_campaigns_creator_id', table_name='campaigns', schema='campaign')
    op.drop_index('ix_campaign_campaigns_owner_id', table_name='campaigns', schema='campaign')

    # Drop tables in correct order
    op.drop_table('npc_relationships', schema='campaign')
    op.drop_table('themed_locations', schema='campaign')
    op.drop_table('themed_npcs', schema='campaign')
    op.drop_table('plot_chapters', schema='campaign')
    op.drop_table('plots', schema='campaign')
    op.drop_table('story_arcs', schema='campaign')
    op.drop_table('chapters', schema='campaign')
    op.drop_table('campaigns', schema='campaign')
    op.drop_table('theme_versions', schema='campaign')
    op.drop_table('themes', schema='campaign')

    # Drop enums
    op.execute('DROP TYPE campaign.npc_relation_type')
    op.execute('DROP TYPE campaign.story_arc_type')
    op.execute('DROP TYPE campaign.plot_state')
    op.execute('DROP TYPE campaign.plot_type')
    op.execute('DROP TYPE campaign.chapter_state')
    op.execute('DROP TYPE campaign.chapter_type')
    op.execute('DROP TYPE campaign.campaign_state')
    op.execute('DROP TYPE campaign.campaign_type')

    # Drop schema
    op.execute('DROP SCHEMA campaign')