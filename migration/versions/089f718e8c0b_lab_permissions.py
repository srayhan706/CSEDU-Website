"""lab permissions

Revision ID: 089f718e8c0b
Revises: 9f1e2b3c4d5f_merge
Create Date: 2025-07-10 17:18:09.458295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from typing import Union, Sequence


# revision identifiers, used by Alembic.
revision: str = '089f718e8c0b'
down_revision: Union[str, None] = '6b4a2c1e7d8a'  # Point to the labs migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    
    # Use PostgreSQL's ON CONFLICT DO NOTHING for idempotent inserts
    op.execute("""
    INSERT INTO roles_permissions (id, role_id, permission_id)
    VALUES 
        (1000, 4, 40),  -- officer - CREATE_LAB
        (1001, 1, 41),  -- chairman - BOOK_LAB
        (1002, 5, 41)   -- faculty - BOOK_LAB
    ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    # Remove all role-permission assignments added in this migration
    op.execute("""
    DELETE FROM roles_permissions 
    WHERE (role_id=4 AND permission_id=40) OR
          (role_id=1 AND permission_id=41) OR
          (role_id=5 AND permission_id=41) OR
          id IN (1000, 1001, 1002)
    """)

