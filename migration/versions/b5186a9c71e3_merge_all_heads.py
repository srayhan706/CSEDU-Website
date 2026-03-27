"""merge all heads

Revision ID: b5186a9c71e3
Revises: 70fbf1c287b0, 96c75a9eb45f
Create Date: 2025-07-06 22:20:00.443913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = 'b5186a9c71e3'
down_revision: Union[str, None] = ('70fbf1c287b0', '96c75a9eb45f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
