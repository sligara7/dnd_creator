"""Add inventory item model

Revision ID: 2024_08_31_inventory_items
Create Date: 2024-08-31 08:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_08_31_inventory_items'
down_revision = '2024_08_24_initial_schema'  # Depends on initial schema
branch_labels = None
depends_on = None

def upgrade():
    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('character_id', sa.String(), nullable=False),
        sa.Column('item_data', postgresql.JSONB(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('equipped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('container', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_inventory_items_character_id', 
        'inventory_items', 
        ['character_id']
    )

def downgrade():
    op.drop_index('ix_inventory_items_character_id')
    op.drop_table('inventory_items')
