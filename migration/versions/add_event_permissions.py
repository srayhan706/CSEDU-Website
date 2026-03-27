"""add_event_permissions

Revision ID: 123456789abc
Revises: 9d1936caeb39
Create Date: 2025-07-06 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = '123456789abc'
down_revision: Union[str, None] = '9d1936caeb39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create permissions table reference
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('category', sa.String)
    )
    
    # Insert event-related permissions
    op.bulk_insert(permissions_table,
        [
            {'id': 100, 'name': 'MANAGE_EVENTS', 'category': 'POST'},
            {'id': 101, 'name': 'REGISTER_EVENT', 'category': 'POST'}
        ]
    )
    
    # Get the next available ID for roles_permissions
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT MAX(id) FROM roles_permissions")).fetchone()
    next_id = (result[0] or 0) + 1
    
    # Create role_permissions table reference with explicit IDs
    role_permissions = [
        # Officer can manage events
        {'id': next_id, 'role_id': 4, 'permission_id': 100},  # MANAGE_EVENTS
        # Student can register for events
        {'id': next_id + 1, 'role_id': 3, 'permission_id': 101},  # REGISTER_EVENT
    ]
    
    # Insert role-permission mappings with explicit IDs
    op.bulk_insert(
        table('roles_permissions',
            column('id', sa.Integer),
            column('role_id', sa.Integer),
            column('permission_id', sa.Integer)
        ),
        role_permissions
    )

def downgrade() -> None:
    # Remove role-permission mappings
    op.execute("DELETE FROM roles_permissions WHERE permission_id IN (100, 101)")
    
    # Remove permissions
    op.execute("DELETE FROM permissions WHERE id IN (100, 101)")
