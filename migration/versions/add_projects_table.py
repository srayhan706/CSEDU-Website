"""add_projects_table

Revision ID: add_projects_table
Revises: custom_convert_difficulty
Create Date: 2025-07-10 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_projects_table'
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
        sa.Column('supervisor_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
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
    
    # Add MANAGE_PROJECTS permission
    op.execute("""
    INSERT INTO permissions (name, category) 
    VALUES ('MANAGE_PROJECTS', 'POST')
    """)
    
    # Get the permission ID
    permission_id_result = op.get_bind().execute(
        "SELECT id FROM permissions WHERE name = 'MANAGE_PROJECTS'"
    ).fetchone()
    
    if permission_id_result:
        permission_id = permission_id_result[0]
        
        # Assign permission to ADMIN role (role_id = 0)
        op.execute(f"""
        INSERT INTO roles_permissions (role_id, permission_id)
        VALUES (0, {permission_id})
        """)
        
        # Assign permission to OFFICER role (role_id = 4) if it exists
        officer_exists = op.get_bind().execute(
            "SELECT id FROM roles WHERE id = 4"
        ).fetchone()
        
        if officer_exists:
            op.execute(f"""
            INSERT INTO roles_permissions (role_id, permission_id)
            VALUES (4, {permission_id})
            """)


def downgrade() -> None:
    # Drop projects table
    op.drop_table('projects')
    
    # Find and remove the MANAGE_PROJECTS permission
    permission_id_result = op.get_bind().execute(
        "SELECT id FROM permissions WHERE name = 'MANAGE_PROJECTS'"
    ).fetchone()
    
    if permission_id_result:
        permission_id = permission_id_result[0]
        
        # Remove role permissions
        op.execute(f"DELETE FROM roles_permissions WHERE permission_id = {permission_id}")
        
        # Remove permission
        op.execute(f"DELETE FROM permissions WHERE id = {permission_id}")
