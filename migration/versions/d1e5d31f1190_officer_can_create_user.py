"""officer can create user

Revision ID: d1e5d31f1190
Revises: 0045e4df859c
Create Date: 2025-07-06 11:46:15.787436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = 'd1e5d31f1190'
down_revision: Union[str, None] = '0045e4df859c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.sql import table, column
    role_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    # Find the next available id for roles_permissions, use 102 for safety
    op.bulk_insert(role_permissions_table, [
        {'id': 102, 'role_id': 4, 'permission_id': 1}
    ])


def downgrade() -> None:
    op.execute("DELETE FROM roles_permissions WHERE role_id=4 AND permission_id=1")
