"""merge event and officer permission branches

Revision ID: 9d98658a9b35
Revises: 123456789abc, d1e5d31f1190
Create Date: 2025-07-06 12:03:58.363636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = '9d98658a9b35'
down_revision: Union[str, None] = ('123456789abc', 'd1e5d31f1190')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
