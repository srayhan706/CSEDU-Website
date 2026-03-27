"""fix_project_column_names

Revision ID: fix_project_column_names
Revises: add_projects_perms
Create Date: 2025-07-10 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_project_column_names'
down_revision: Union[str, None] = 'add_projects_perms'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns from camelCase to snake_case
    op.alter_column('projects', 'supervisor', new_column_name='supervisor_id')
    op.alter_column('projects', 'teamSize', new_column_name='team_size')
    op.alter_column('projects', 'keyFeatures', new_column_name='key_features')
    op.alter_column('projects', 'demoLink', new_column_name='demo_link')
    op.alter_column('projects', 'githubLink', new_column_name='github_link')
    op.alter_column('projects', 'paperLink', new_column_name='paper_link')
    op.alter_column('projects', 'contactEmail', new_column_name='contact_email')
    op.alter_column('projects', 'createdAt', new_column_name='created_at')
    op.alter_column('projects', 'updatedAt', new_column_name='updated_at')


def downgrade() -> None:
    # Rename columns back from snake_case to camelCase
    op.alter_column('projects', 'supervisor_id', new_column_name='supervisor')
    op.alter_column('projects', 'team_size', new_column_name='teamSize')
    op.alter_column('projects', 'key_features', new_column_name='keyFeatures')
    op.alter_column('projects', 'demo_link', new_column_name='demoLink')
    op.alter_column('projects', 'github_link', new_column_name='githubLink')
    op.alter_column('projects', 'paper_link', new_column_name='paperLink')
    op.alter_column('projects', 'contact_email', new_column_name='contactEmail')
    op.alter_column('projects', 'created_at', new_column_name='createdAt')
    op.alter_column('projects', 'updated_at', new_column_name='updatedAt')
