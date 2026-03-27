"""
Alembic migration for Lab, LabTimeSlot, LabBooking tables and new permissions (CREATE_LAB, BOOK_LAB)
"""

revision = '6b4a2c1e7d8a'
down_revision = 'a0e3d5045d81'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

def upgrade():
    # Create labs table
    op.create_table(
        'labs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('location', sa.String, nullable=False),
        sa.Column('capacity', sa.Integer, nullable=False),
        sa.Column('facilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('image', sa.String, nullable=True),
    )
    # Create lab_time_slots table
    op.create_table(
        'lab_time_slots',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lab_id', sa.Integer, sa.ForeignKey('labs.id'), nullable=False),
        sa.Column('day', sa.String, nullable=False),
        sa.Column('start_time', sa.String, nullable=False),
        sa.Column('end_time', sa.String, nullable=False),
    )
    # Create lab_bookings table
    op.create_table(
        'lab_bookings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lab_id', sa.Integer, sa.ForeignKey('labs.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('time_slot_id', sa.Integer, sa.ForeignKey('lab_time_slots.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('purpose', sa.String, nullable=True),
        sa.Column('status', sa.String, nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    # Insert new permissions (idempotent)
    op.execute("""
        INSERT INTO permissions (id, name, category)
        SELECT 40, 'CREATE_LAB', 'POST'
        WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE id=40)
    """)
    op.execute("""
        INSERT INTO permissions (id, name, category)
        SELECT 41, 'BOOK_LAB', 'POST'
        WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE id=41)
    """)
    # Assign CREATE_LAB to officer (role_id=4) (idempotent)
    op.execute("""
        INSERT INTO roles_permissions (role_id, permission_id)
        VALUES (4, 40)
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)
    # Assign BOOK_LAB to chairman (1), faculty (5), and students (3) (idempotent)
    op.execute("""
        INSERT INTO roles_permissions (role_id, permission_id)
        VALUES (1, 41)
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)
    op.execute("""
        INSERT INTO roles_permissions (role_id, permission_id)
        VALUES (5, 41)
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)
    op.execute("""
        INSERT INTO roles_permissions (role_id, permission_id)
        VALUES (3, 41)
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)

def downgrade():
    op.execute("DELETE FROM roles_permissions WHERE permission_id IN (40, 41)")
    op.execute("DELETE FROM permissions WHERE id IN (40, 41)")
    op.drop_table('lab_bookings')
    op.drop_table('lab_time_slots')
    op.drop_table('labs')
