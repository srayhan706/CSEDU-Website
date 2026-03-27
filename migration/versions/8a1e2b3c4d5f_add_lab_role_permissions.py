"""
Add role-permission assignments for CREATE_LAB (id=40) and BOOK_LAB (id=41) to officer, chairman, faculty, and students roles.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = '8a1e2b3c4d5f'
down_revision: Union[str, None] = '6b4a2c1e7d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    roles_permissions_table = table('roles_permissions',
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    op.bulk_insert(roles_permissions_table, [
        {'role_id': 4, 'permission_id': 40},  # officer - CREATE_LAB
        {'role_id': 1, 'permission_id': 41},  # chairman - BOOK_LAB
        {'role_id': 5, 'permission_id': 41},  # faculty - BOOK_LAB
    ])


def downgrade() -> None:
    op.execute("DELETE FROM roles_permissions WHERE (role_id=4 AND permission_id=40)")
    op.execute("DELETE FROM roles_permissions WHERE (role_id=1 AND permission_id=41)")
    op.execute("DELETE FROM roles_permissions WHERE (role_id=5 AND permission_id=41)")
