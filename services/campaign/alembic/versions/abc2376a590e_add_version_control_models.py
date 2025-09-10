"""Add version control models

Revision ID: abc2376a590e
Revises: dd7f296ff218
Create Date: 2025-09-09 22:00:13.573559

"""
from typing import Sequence
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc2376a590e'
down_revision: str | None = 'dd7f296ff218'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
