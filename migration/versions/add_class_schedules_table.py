"""add class schedules table

Revision ID: 9f3a2c1d5e8b
Revises: 8fa68ae
Create Date: 2025-07-10 22:57:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f3a2c1d5e8b'
down_revision = 'fix_project_column_names'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Import text for raw SQL
    from sqlalchemy import text
    
    # Create table directly with string type columns instead of enums
    op.create_table(
        'class_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_code', sa.String(), nullable=False),
        sa.Column('course_name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),  # Use string instead of enum
        sa.Column('batch', sa.String(), nullable=False),
        sa.Column('semester', sa.String(), nullable=False),
        sa.Column('day', sa.String(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('room', sa.String(), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('instructor_name', sa.String(), nullable=False),
        sa.Column('instructor_designation', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),  # Use string instead of enum
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_code'], ['courses.code'], ),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_class_schedules_id'), 'class_schedules', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_class_schedules_id'), table_name='class_schedules')
    op.drop_table('class_schedules')
    op.execute("DROP TYPE classstatus")
    op.execute("DROP TYPE classtype")
