"""merge multiple heads

Revision ID: 5ac45949126a
Revises: 123456789abc, d1e5d31f1190
Create Date: 2025-07-06 12:10:17.211390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = '5ac45949126a'
down_revision: Union[str, None] = ('123456789abc', 'd1e5d31f1190')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
