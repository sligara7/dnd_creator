"""Create storage models.

Revision ID: 20250906_storage_models
Create Date: 2025-09-06 20:30:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250906_storage_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for image storage and relationships."""
    # Image types enum
    op.execute("""
        CREATE TYPE image_type AS ENUM (
            'map_tactical',
            'map_campaign',
            'character_portrait',
            'item',
            'monster',
            'overlay'
        )
    """)

    # Image formats enum
    op.execute("""
        CREATE TYPE image_format AS ENUM (
            'png',
            'jpeg',
            'webp'
        )
    """)

    # Storage locations enum
    op.execute("""
        CREATE TYPE storage_location AS ENUM (
            's3',
            'cdn',
            'local'
        )
    """)

    # Images table
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('type', sa.Enum('map_tactical', 'map_campaign',
                                'character_portrait', 'item', 'monster',
                                'overlay', name='image_type'),
                  nullable=False),
        sa.Column('format', sa.Enum('png', 'jpeg', 'webp',
                                  name='image_format'),
                  nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('location',
                 sa.Enum('s3', 'cdn', 'local', name='storage_location'),
                 nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('cdn_url', sa.String(), nullable=True),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False,
                 server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False,
                 server_default='{}'),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True),
                 sa.ForeignKey('images.id'), nullable=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True),
        sa.Column('cache_key', sa.String(), nullable=True),
        sa.Column('cache_ttl', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(),
                 server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                 server_default=sa.func.now(),
                 onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(),
                 server_default='false', nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )

    # Create indices
    op.create_index('ix_images_content_hash',
                   'images', ['content_hash'])
    op.create_index('ix_images_source_id',
                   'images', ['source_id'])
    op.create_index('ix_images_cache_key',
                   'images', ['cache_key'])

    # Image relationships table
    op.create_table(
        'image_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True),
                 sa.ForeignKey('images.id'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True),
                 sa.ForeignKey('images.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False,
                 server_default='{}'),
        sa.Column('created_at', sa.DateTime(),
                 server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                 server_default=sa.func.now(),
                 onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(),
                 server_default='false', nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )

    # Create indices
    op.create_index('ix_image_relationships_source_id',
                   'image_relationships', ['source_id'])
    op.create_index('ix_image_relationships_target_id',
                   'image_relationships', ['target_id'])
    op.create_index('ix_image_relationships_type',
                   'image_relationships', ['type'])

    # Image access logs table
    op.create_table(
        'image_access',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('image_id', postgresql.UUID(as_uuid=True),
                 sa.ForeignKey('images.id'), nullable=False),
        sa.Column('access_type', sa.String(), nullable=False),
        sa.Column('source_service', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('cache_hit', sa.Boolean(),
                 server_default='false', nullable=False),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('accessed_at', sa.DateTime(),
                 server_default=sa.func.now(), nullable=False)
    )

    # Create indices
    op.create_index('ix_image_access_image_id',
                   'image_access', ['image_id'])
    op.create_index('ix_image_access_accessed_at',
                   'image_access', ['accessed_at'])

    # Create updated_at triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers to tables
    op.execute("""
        CREATE TRIGGER update_images_modtime
            BEFORE UPDATE ON images
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_image_relationships_modtime
            BEFORE UPDATE ON image_relationships
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Remove storage-related tables and types."""
    # Drop tables
    op.drop_table('image_access')
    op.drop_table('image_relationships')
    op.drop_table('images')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS storage_location')
    op.execute('DROP TYPE IF EXISTS image_format')
    op.execute('DROP TYPE IF EXISTS image_type')
