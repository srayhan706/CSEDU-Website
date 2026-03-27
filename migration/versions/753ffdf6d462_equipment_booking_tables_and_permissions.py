"""equipment booking tables and permissions

Revision ID: 753ffdf6d462
Revises: 9d98658a9b35
Create Date: 2025-07-06 12:46:10.324590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = '753ffdf6d462'
down_revision: Union[str, None] = '9d98658a9b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create equipment_categories table
    op.create_table(
        'equipment_categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True)
    )

    # Insert default CSE categories (idempotent)
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO equipment_categories (id, name, icon, description) VALUES
        (1, 'Computing Hardware', 'Cpu', 'High-performance computing resources including GPUs, servers, and specialized processors'),
        (2, 'Sensors & IoT', 'Wifi', 'Sensors, actuators, and IoT devices for research and projects'),
        (3, 'Storage & Memory', 'Database', 'Storage devices and memory modules for data-intensive applications'),
        (4, 'Mobile & Embedded', 'Smartphone', 'Mobile devices and embedded systems for testing and development'),
        (5, 'Networking', 'Layers', 'Networking equipment for communication and distributed systems research')
        ON CONFLICT (id) DO NOTHING;
    """))

    # Create equipment table
    op.create_table(
        'equipment',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('equipment_categories.id'), nullable=False),
        sa.Column('specifications', sa.String(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('available', sa.Integer(), nullable=False),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, default=False)
    )

    # Create equipment_bookings table
    op.create_table(
        'equipment_bookings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('equipment_id', sa.Integer(), sa.ForeignKey('equipment.id'), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('user_name', sa.String(), nullable=False),
        sa.Column('user_role', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('purpose', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('rejection_reason', sa.String(), nullable=True)
    )

    # Add permissions and assign to roles
    from sqlalchemy.sql import table, column
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('category', sa.String)
    )
    op.bulk_insert(permissions_table, [
        {'id': 200, 'name': 'BOOK_EQUIPMENT', 'category': 'POST'},
        {'id': 201, 'name': 'APPROVE_EQUIPMENT_BOOKING', 'category': 'POST'},
        {'id': 202, 'name': 'MANAGE_EQUIPMENT', 'category': 'POST'}
    ])
    # Assign BOOK_EQUIPMENT to TEACHER (2), STUDENT (3), FACULTY (5)
    role_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    op.bulk_insert(role_permissions_table, [
        {'id': 110, 'role_id': 2, 'permission_id': 200},
        {'id': 111, 'role_id': 3, 'permission_id': 200},
        {'id': 112, 'role_id': 5, 'permission_id': 200},
        {'id': 113, 'role_id': 4, 'permission_id': 201}, # OFFICER can approve
        {'id': 114, 'role_id': 4, 'permission_id': 202}  # OFFICER can manage equipment
    ])


def downgrade() -> None:
    op.drop_table('equipment_bookings')
    op.drop_table('equipment')
    op.execute("DELETE FROM equipment_categories WHERE id IN (1,2,3,4,5)")
    op.drop_table('equipment_categories')
    op.execute("DELETE FROM permissions WHERE id IN (200, 201, 202)")
    op.execute("DELETE FROM roles_permissions WHERE permission_id IN (200, 201, 202)")
