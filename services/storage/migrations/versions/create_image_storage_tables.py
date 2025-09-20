"""Create image storage database tables.

Revision ID: create_image_storage_tables
Create Date: 2025-09-20 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime


# revision identifiers, used by Alembic
revision = 'create_image_storage'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables for image storage

    # Images table
    op.create_table(
        'images',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('subtype', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Image data
        sa.Column('url', sa.String(1024), nullable=False),
        sa.Column('format', sa.String(50), nullable=False, server_default='png'),
        sa.Column('width', sa.Integer, nullable=False),
        sa.Column('height', sa.Integer, nullable=False),
        sa.Column('size', sa.Integer, nullable=False),  # in bytes
        
        # Theme and style information
        sa.Column('theme', sa.String(50), nullable=False),
        sa.Column('style_data', JSONB, nullable=True),
        
        # Generation metadata
        sa.Column('generation_params', JSONB, nullable=True),
        sa.Column('source_id', UUID, nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
    )

    # Add indexes for images table
    op.create_index('idx_images_type', 'images', ['type'])
    op.create_index('idx_images_theme', 'images', ['theme'])
    op.create_index('idx_images_deleted', 'images', ['is_deleted'])

    # Image overlays table
    op.create_table(
        'image_overlays',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('image_id', UUID, sa.ForeignKey('images.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Overlay data
        sa.Column('data', JSONB, nullable=False),
        sa.Column('style', JSONB, nullable=False),
    )

    # Add indexes for image_overlays table
    op.create_index('idx_image_overlays_image_id', 'image_overlays', ['image_id'])
    op.create_index('idx_image_overlays_type', 'image_overlays', ['type'])
    op.create_index('idx_image_overlays_deleted', 'image_overlays', ['is_deleted'])

    # Map grids table
    op.create_table(
        'map_grids',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Configuration
        sa.Column('image_id', UUID, sa.ForeignKey('images.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('size', sa.Integer, nullable=False, server_default='50'),
        sa.Column('color', sa.String(50), nullable=False, server_default='#000000'),
        sa.Column('opacity', sa.Float, nullable=False, server_default='0.5'),
    )

    # Add indexes and unique constraint for map_grids table
    op.create_index('idx_map_grids_image_id', 'map_grids', ['image_id'])
    op.create_unique_constraint('uq_map_grids_image_id', 'map_grids', ['image_id'])
    op.create_index('idx_map_grids_deleted', 'map_grids', ['is_deleted'])

    # Generation tasks table
    op.create_table(
        'generation_tasks',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Task information
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('priority', sa.Integer, nullable=False),
        
        # Task data
        sa.Column('params', JSONB, nullable=False),
        sa.Column('result', JSONB, nullable=True),
        
        # Error tracking
        sa.Column('attempts', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text, nullable=True),
        sa.Column('last_attempt', sa.DateTime(timezone=True), nullable=True),
        
        # Retry configuration
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer, nullable=False, server_default='3'),
        sa.Column('retry_delay', sa.Integer, nullable=False, server_default='5')
    )

    # Add indexes for generation_tasks table
    op.create_index('idx_generation_tasks_type', 'generation_tasks', ['type'])
    op.create_index('idx_generation_tasks_status', 'generation_tasks', ['status'])
    op.create_index('idx_generation_tasks_priority', 'generation_tasks', ['priority'])
    op.create_index('idx_generation_tasks_deleted', 'generation_tasks', ['is_deleted'])

    # Themes table
    op.create_table(
        'themes',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Configuration
        sa.Column('config', JSONB, nullable=False),
        sa.Column('variables', JSONB, nullable=False),
        sa.Column('prompts', JSONB, nullable=False),
        sa.Column('styles', JSONB, nullable=False)
    )

    # Add indexes for themes table
    op.create_index('idx_themes_name', 'themes', ['name'])
    op.create_index('idx_themes_deleted', 'themes', ['is_deleted'])

    # Theme variations table
    op.create_table(
        'theme_variations',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('theme_id', UUID, sa.ForeignKey('themes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Configuration
        sa.Column('config_override', JSONB, nullable=False),
        sa.Column('variable_override', JSONB, nullable=False)
    )

    # Add indexes for theme_variations table
    op.create_index('idx_theme_variations_theme_id', 'theme_variations', ['theme_id'])
    op.create_index('idx_theme_variations_deleted', 'theme_variations', ['is_deleted'])

    # Style presets table
    op.create_table(
        'style_presets',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        
        # Configuration
        sa.Column('config', JSONB, nullable=False),
        sa.Column('prompts', JSONB, nullable=False),
        sa.Column('compatibility', JSONB, nullable=False)
    )

    # Add indexes for style_presets table
    op.create_index('idx_style_presets_name', 'style_presets', ['name'])
    op.create_index('idx_style_presets_category', 'style_presets', ['category'])
    op.create_index('idx_style_presets_deleted', 'style_presets', ['is_deleted'])

    # Theme elements table
    op.create_table(
        'theme_elements',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        
        # Basic information
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Configuration
        sa.Column('config', JSONB, nullable=False),
        sa.Column('prompts', JSONB, nullable=False),
        sa.Column('compatibility', JSONB, nullable=False)
    )

    # Add unique constraint and indexes for theme_elements table
    op.create_unique_constraint('uq_theme_elements_category_name', 'theme_elements', ['category', 'name'])
    op.create_index('idx_theme_elements_category', 'theme_elements', ['category'])
    op.create_index('idx_theme_elements_deleted', 'theme_elements', ['is_deleted'])


def downgrade():
    """Drop all created tables in reverse order."""
    op.drop_table('theme_elements')
    op.drop_table('style_presets')
    op.drop_table('theme_variations')
    op.drop_table('themes')
    op.drop_table('generation_tasks')
    op.drop_table('map_grids')
    op.drop_table('image_overlays')
    op.drop_table('images')