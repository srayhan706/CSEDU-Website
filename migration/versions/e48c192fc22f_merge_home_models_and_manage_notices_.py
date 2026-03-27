"""Merge home models and manage notices permission heads

Revision ID: e48c192fc22f
Revises: 6d0e25a3b71d, add_manage_notices_permission
Create Date: 2025-07-07 14:24:31.197809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = 'e48c192fc22f'
down_revision: Union[str, None] = ('6d0e25a3b71d', 'add_manage_notices_permission')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
