"""Add tags column to images table.

Revision ID: c1a2b3d4e5f6
Revises: ${previous_revision_id}
Create Date: 2024-03-11 11:11:11.111111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a2b3d4e5f6'
down_revision = None  # Update this to point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('images',
        sa.Column('tags', sa.JSON(), nullable=True)
    )


def downgrade():
    op.drop_column('images', 'tags')
