"""
Add VIEW_EQUIPMENT_BOOKINGS permission and assign to STUDENT, TEACHER, FACULTY, OFFICER
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ab1234567890'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade():
    from sqlalchemy.sql import table, column
    # Table references
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('category', sa.String)
    )
    roles_table = table('roles',
        column('id', sa.Integer),
        column('name', sa.String)
    )
    roles_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    conn = op.get_bind()
    # Check if permission exists
    result = conn.execute(sa.text("SELECT id FROM permissions WHERE name='VIEW_EQUIPMENT_BOOKINGS'"))
    permission_row = result.first()
    if permission_row:
        permission_id = permission_row[0]
    else:
        # Find max id and use next id
        max_id = conn.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM permissions")).scalar()
        permission_id = max_id + 1
        op.bulk_insert(permissions_table, [
            {'id': permission_id, 'name': 'VIEW_EQUIPMENT_BOOKINGS', 'category': 'EQUIPMENT'}
        ])
    # Assign to roles
    role_names = ['STUDENT', 'TEACHER', 'FACULTY', 'OFFICER']
    for role_name in role_names:
        result = conn.execute(sa.text("SELECT id FROM roles WHERE name=:role_name"), {'role_name': role_name})
        role_row = result.first()
        if role_row:
            role_id = role_row[0]
            # Check if assignment exists
            exists = conn.execute(sa.text("SELECT 1 FROM roles_permissions WHERE role_id=:role_id AND permission_id=:permission_id"), {'role_id': role_id, 'permission_id': permission_id}).first()
            if not exists:
                # Find max id for roles_permissions
                max_rp_id = conn.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM roles_permissions")).scalar()
                rp_id = max_rp_id + 1
                op.bulk_insert(roles_permissions_table, [
                    {'id': rp_id, 'role_id': role_id, 'permission_id': permission_id}
                ])


def downgrade():
    # Remove permission from roles_permissions
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM permissions WHERE name='VIEW_EQUIPMENT_BOOKINGS'"))
    permission_id = result.scalar()
    if permission_id:
        op.execute(sa.text("DELETE FROM roles_permissions WHERE permission_id=:permission_id"), {'permission_id': permission_id})
        op.execute(sa.text("DELETE FROM permissions WHERE id=:permission_id"), {'permission_id': permission_id})
