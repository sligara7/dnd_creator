"""add evolution models

Revision ID: be205c5d4137
Revises: 4fea20078aa0
Create Date: 2025-09-05 22:27:56.704947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be205c5d4137'
down_revision: Union[str, None] = '4fea20078aa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
