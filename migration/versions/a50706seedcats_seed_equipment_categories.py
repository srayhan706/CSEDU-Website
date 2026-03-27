"""
Alembic migration to seed default CSE equipment categories if missing.
"""
revision = 'a50706seedcats'
down_revision = '20213ceff01a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
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

def downgrade():
    # Optionally delete seeded categories by ID (if desired)
    conn = op.get_bind()
    conn.execute(sa.text("""
        DELETE FROM equipment_categories WHERE id IN (1,2,3,4,5);
    """))
