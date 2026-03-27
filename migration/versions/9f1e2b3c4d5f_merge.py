"""
Alembic merge migration to unify branches: 8a1e2b3c4d5f and another branch
"""
from alembic import op
import sqlalchemy as sa

revision = '9f1e2b3c4d5f_merge'
down_revision = ('8a1e2b3c4d5f',)
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
