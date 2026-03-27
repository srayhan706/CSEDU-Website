"""
Alembic migration to ensure MANAGE_EQUIPMENT permission exists and is assigned to OFFICER.
"""
revision = 'a50706addmanageequip'
down_revision = 'a50706seedcats'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    conn = op.get_bind()
    # Insert MANAGE_EQUIPMENT permission if missing
    conn.execute(sa.text("""
        INSERT INTO permissions (id, name, category)
        VALUES (202, 'MANAGE_EQUIPMENT', 'POST')
        ON CONFLICT (id) DO NOTHING;
    """))
    # Assign to OFFICER (role_id 4) if missing
    conn.execute(sa.text("""
        INSERT INTO roles_permissions (id, role_id, permission_id)
        VALUES (114, 4, 202)
        ON CONFLICT (id) DO NOTHING;
    """))

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM roles_permissions WHERE id = 114 AND role_id = 4 AND permission_id = 202;"))
    conn.execute(sa.text("DELETE FROM permissions WHERE id = 202 AND name = 'MANAGE_EQUIPMENT';"))
