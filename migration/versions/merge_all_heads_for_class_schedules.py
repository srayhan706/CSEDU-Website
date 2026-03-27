"""merge all heads for class schedules

Revision ID: merge_all_heads_class
Revises: 9f3a2c1d5e8b, be54a3092f06, fix_project_column_names
Create Date: 2025-07-10 22:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_all_heads_class'
down_revision = ('9f3a2c1d5e8b', 'be54a3092f06', 'fix_project_column_names')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
