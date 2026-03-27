"""
Add MANAGE_NOTICES permission for officers

Revision ID: add_manage_notices_permission
Revises: 38c361dd5660
Create Date: 2025-07-06 23:40:40
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'add_manage_notices_permission'
down_revision = '38c361dd5660'
branch_labels = None
depends_on = None

def upgrade():
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('category', sa.String)
    )
    # Insert MANAGE_NOTICES permission (choose a unique id, e.g., 20)
    op.bulk_insert(permissions_table, [
        {'id': 20, 'name': 'MANAGE_NOTICES', 'category': 'POST'}
    ])

    role_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    # Find the next available id for roles_permissions, use 102 for safety
    op.bulk_insert(role_permissions_table, [
        {'id': 13, 'role_id': 4, 'permission_id': 20}
    ])

def downgrade():
    op.execute("DELETE FROM permissions WHERE name='MANAGE_NOTICES'")
    op.execute("DELETE FROM roles_permissions WHERE role_id=4 AND permission_id=20")
