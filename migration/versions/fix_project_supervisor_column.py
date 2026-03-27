"""fix_project_supervisor_column

Revision ID: fix_project_supervisor
Revises: add_projects_table
Create Date: 2025-07-10 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_project_supervisor'
down_revision: Union[str, None] = 'add_projects_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column supervisor to supervisor_id
    op.alter_column('projects', 'supervisor', new_column_name='supervisor_id')


def downgrade() -> None:
    # Rename column supervisor_id back to supervisor
    op.alter_column('projects', 'supervisor_id', new_column_name='supervisor')
