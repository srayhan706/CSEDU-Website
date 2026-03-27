"""merge heads

Revision ID: f21f740f2988
Revises: fix_project_supervisor, merge_all_heads_class
Create Date: 2025-07-15 00:56:36.840861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = 'f21f740f2988'
down_revision: Union[str, None] = ('fix_project_supervisor', 'merge_all_heads_class')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
