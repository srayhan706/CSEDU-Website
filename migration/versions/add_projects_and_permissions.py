"""add_projects_and_permissions

Revision ID: add_projects_perms
Revises: custom_convert_difficulty
Create Date: 2025-07-10 22:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = 'add_projects_perms'
down_revision: Union[str, None] = 'custom_convert_difficulty'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=False),
        sa.Column('supervisor', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('team', postgresql.JSON(), nullable=True),
        sa.Column('course', sa.String(), nullable=True),
        sa.Column('team_size', sa.Integer(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=False),
        sa.Column('technologies', postgresql.JSON(), nullable=True),
        sa.Column('key_features', postgresql.JSON(), nullable=True),
        sa.Column('achievements', postgresql.JSON(), nullable=True),
        sa.Column('demo_link', sa.String(), nullable=True),
        sa.Column('github_link', sa.String(), nullable=True),
        sa.Column('paper_link', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )
    
    # Create permissions table reference
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('category', sa.String)
    )
    
    # Get the max permission ID
    connection = op.get_bind()
    max_id_result = connection.execute(sa.text("SELECT MAX(id) FROM permissions")).fetchone()
    max_id = max_id_result[0] if max_id_result and max_id_result[0] is not None else 0
    next_id = max_id + 1
    
    # Insert new permission
    op.bulk_insert(permissions_table,
        [
            {'id': next_id, 'name': 'MANAGE_PROJECTS', 'category': 'POST'}
        ]
    )
    
    # Create role_permissions table reference
    role_permissions_table = table('roles_permissions',
        column('id', sa.Integer),
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    
    # Get the max role_permission ID
    max_rp_id_result = connection.execute(sa.text("SELECT MAX(id) FROM roles_permissions")).fetchone()
    max_rp_id = max_rp_id_result[0] if max_rp_id_result and max_rp_id_result[0] is not None else 0
    next_rp_id = max_rp_id + 1
    
    # Assign permission to ADMIN role (role_id = 0) and OFFICER role (role_id = 4)
    op.bulk_insert(role_permissions_table, [
        {'id': next_rp_id, 'role_id': 0, 'permission_id': next_id},  # Admin
        {'id': next_rp_id + 1, 'role_id': 4, 'permission_id': next_id}  # Officer
    ])


def downgrade() -> None:
    # Drop projects table
    op.drop_table('projects')
    
    # Find and remove the MANAGE_PROJECTS permission
    connection = op.get_bind()
    permission_id_result = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'MANAGE_PROJECTS'")
    ).fetchone()
    
    if permission_id_result and permission_id_result[0]:
        permission_id = permission_id_result[0]
        
        # Remove role permissions
        connection.execute(
            sa.text(f"DELETE FROM roles_permissions WHERE permission_id = {permission_id}")
        )
        
        # Remove permission
        connection.execute(
            sa.text(f"DELETE FROM permissions WHERE id = {permission_id}")
        )
