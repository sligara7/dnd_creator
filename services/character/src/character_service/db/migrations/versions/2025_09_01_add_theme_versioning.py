"""add theme versioning

Revision ID: 2025_09_01_02
Revises: 2025_09_01_01
Create Date: 2025-09-01 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2025_09_01_02'
down_revision: str = '2025_09_01_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add theme fields to character and inventory item tables
    op.add_column('characters',
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column('characters',
        sa.Column('theme', sa.String(), server_default='traditional', nullable=False)
    )
    op.create_index(op.f('ix_characters_parent_id'), 'characters', ['parent_id'],
                   unique=False)
    op.create_foreign_key('fk_character_parent', 'characters', 'characters',
                         ['parent_id'], ['id'])

    # Create version graph tables
    op.create_table(
        'version_graphs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now())
    )

    op.create_table(
        'version_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('graph_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('theme', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False,
                  server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['graph_id'], ['version_graphs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_version_nodes_entity_id_type_theme',
                   'version_nodes', ['entity_id', 'type', 'theme'], unique=True)

    op.create_table(
        'version_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('graph_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False,
                  server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['graph_id'], ['version_graphs.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['version_nodes.id'], ),
        sa.ForeignKeyConstraint(['target_id'], ['version_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_version_edges_source_target_type',
                   'version_edges', ['source_id', 'target_id', 'type'],
                   unique=True)


def downgrade() -> None:
    # Drop version graph tables and indexes
    op.drop_index('ix_version_edges_source_target_type', table_name='version_edges')
    op.drop_table('version_edges')
    op.drop_index('ix_version_nodes_entity_id_type_theme',
                 table_name='version_nodes')
    op.drop_table('version_nodes')
    op.drop_table('version_graphs')

    # Drop theme fields
    op.drop_constraint('fk_character_parent', 'characters', type_='foreignkey')
    op.drop_index('ix_characters_parent_id', table_name='characters')
    op.drop_column('characters', 'theme')
    op.drop_column('characters', 'parent_id')
