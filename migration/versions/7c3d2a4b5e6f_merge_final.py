"""
Alembic merge migration to unify heads: 089f718e8c0b and e48c192fc22f
"""
from alembic import op
import sqlalchemy as sa

revision = '7c3d2a4b5e6f_merge_final'
down_revision = ('089f718e8c0b', 'e48c192fc22f')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
