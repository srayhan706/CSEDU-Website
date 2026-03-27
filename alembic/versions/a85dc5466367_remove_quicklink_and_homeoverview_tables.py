"""Remove QuickLink and HomeOverview tables

Revision ID: a85dc5466367
Revises: 
Create Date: 2025-07-07 00:35:33.579737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a85dc5466367'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the tables if they exist
    op.drop_table('quick_links', if_exists=True)
    op.drop_table('home_overview', if_exists=True)
    
    # Drop the enum types if they exist
    op.execute("DROP TYPE IF EXISTS announcementtype CASCADE")
    op.execute("DROP TYPE IF EXISTS prioritylevel CASCADE")


def downgrade() -> None:
    # Note: This is a one-way migration. If you need to restore these tables,
    # you should create a new migration with the table definitions.
    pass
