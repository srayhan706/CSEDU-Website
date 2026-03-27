"""
Final merge migration to unify all heads
"""
from alembic import op
import sqlalchemy as sa
from typing import Union, Sequence

# revision identifiers, used by Alembic.
revision: str = '8f9d2e3c1a7b'
down_revision: Union[tuple, None] = ('7c3d2a4b5e6f_merge_final', '9f1e2b3c4d5f_merge')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
