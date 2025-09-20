"""Create consolidated image schema.

This migration creates the complete image database schema and all required tables
within the image schema in the storage service, replacing the direct database access
that was previously in the Image Service.

Revision ID: 2025_09_20_04
Revises: 2025_09_20_03
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_04'
down_revision: Union[str, None] = '2025_09_20_03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create image schema and all required tables."""
    # Create image schema
    op.execute('CREATE SCHEMA IF NOT EXISTS image')

    # Create enums
    op.execute("""
        CREATE TYPE image.image_type AS ENUM (
            'map_tactical',
            'map_campaign',
            'character_portrait',
            'item',
            'monster',
            'overlay'
        )
    """)

    op.execute("""
        CREATE TYPE image.image_format AS ENUM (
            'png',
            'jpeg',
            'webp'
        )
    """)

    op.execute("""
        CREATE TYPE image.storage_location AS ENUM (
            's3',
            'cdn',
            'local'
        )
    """)

    # Create images table
    op.create_table('images',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('type', sa.Enum('map_tactical', 'map_campaign', 'character_portrait', 'item', 'monster', 'overlay',
                                name='image_type', schema='image'), nullable=False),
        sa.Column('format', sa.Enum('png', 'jpeg', 'webp',
                                name='image_format', schema='image'), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('location', sa.Enum('s3', 'cdn', 'local',
                                    name='storage_location', schema='image'), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('cdn_url', sa.String()),
        sa.Column('theme', sa.String()),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('tags', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('image.images.id')),
        sa.Column('source_id', UUID(as_uuid=True)),
        sa.Column('source_type', sa.String()),
        sa.Column('cache_key', sa.String()),
        sa.Column('cache_ttl', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='image'
    )

    # Create image relationships table
    op.create_table('image_relationships',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('source_id', UUID(as_uuid=True), sa.ForeignKey('image.images.id'), nullable=False),
        sa.Column('target_id', UUID(as_uuid=True), sa.ForeignKey('image.images.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime()),
        schema='image'
    )

    # Create image access table
    op.create_table('image_access',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('image_id', UUID(as_uuid=True), sa.ForeignKey('image.images.id'), nullable=False),
        sa.Column('access_type', sa.String(), nullable=False),
        sa.Column('source_service', sa.String(), nullable=False),
        sa.Column('request_id', sa.String()),
        sa.Column('response_time_ms', sa.Integer()),
        sa.Column('cache_hit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('error', sa.String()),
        sa.Column('accessed_at', sa.DateTime(), nullable=False),
        schema='image'
    )

    # Create indices
    op.create_index('ix_image_images_content_hash', 'images', ['content_hash'], schema='image')
    op.create_index('ix_image_images_source_id', 'images', ['source_id'], schema='image')
    op.create_index('ix_image_images_cache_key', 'images', ['cache_key'], schema='image')
    op.create_index('ix_image_relationships_source_id', 'image_relationships', ['source_id'], schema='image')
    op.create_index('ix_image_relationships_target_id', 'image_relationships', ['target_id'], schema='image')
    op.create_index('ix_image_relationships_type', 'image_relationships', ['type'], schema='image')
    op.create_index('ix_image_access_image_id', 'image_access', ['image_id'], schema='image')
    op.create_index('ix_image_access_accessed_at', 'image_access', ['accessed_at'], schema='image')

    # Create updated_at trigger function if it doesn't exist
    op.execute("""
        CREATE OR REPLACE FUNCTION image.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers
    op.execute("""
        CREATE TRIGGER update_images_modtime
            BEFORE UPDATE ON image.images
            FOR EACH ROW
            EXECUTE FUNCTION image.update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_image_relationships_modtime
            BEFORE UPDATE ON image.image_relationships
            FOR EACH ROW
            EXECUTE FUNCTION image.update_updated_at_column();
    """)

def downgrade() -> None:
    """Remove image schema and all tables."""
    # Drop triggers first
    op.execute('DROP TRIGGER IF EXISTS update_images_modtime ON image.images')
    op.execute('DROP TRIGGER IF EXISTS update_image_relationships_modtime ON image.image_relationships')
    op.execute('DROP FUNCTION IF EXISTS image.update_updated_at_column()')

    # Drop indices
    op.drop_index('ix_image_access_accessed_at', table_name='image_access', schema='image')
    op.drop_index('ix_image_access_image_id', table_name='image_access', schema='image')
    op.drop_index('ix_image_relationships_type', table_name='image_relationships', schema='image')
    op.drop_index('ix_image_relationships_target_id', table_name='image_relationships', schema='image')
    op.drop_index('ix_image_relationships_source_id', table_name='image_relationships', schema='image')
    op.drop_index('ix_image_images_cache_key', table_name='images', schema='image')
    op.drop_index('ix_image_images_source_id', table_name='images', schema='image')
    op.drop_index('ix_image_images_content_hash', table_name='images', schema='image')

    # Drop tables
    op.drop_table('image_access', schema='image')
    op.drop_table('image_relationships', schema='image')
    op.drop_table('images', schema='image')

    # Drop enums
    op.execute('DROP TYPE image.storage_location')
    op.execute('DROP TYPE image.image_format')
    op.execute('DROP TYPE image.image_type')

    # Drop schema
    op.execute('DROP SCHEMA image')