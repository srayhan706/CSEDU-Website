"""custom_convert_coursedifficulty_to_string

Revision ID: custom_convert_difficulty
Revises: custom_convert_level
Create Date: 2025-07-10 22:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'custom_convert_difficulty'
down_revision: Union[str, None] = 'custom_convert_level'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, create a temporary column to store the enum values as strings
    op.add_column('courses', sa.Column('difficulty_str', sa.String(), nullable=True))
    
    # Copy data from enum column to string column, capitalizing the first letter
    op.execute("""
    UPDATE courses SET difficulty_str = CASE 
        WHEN difficulty::text = 'beginner' THEN 'Beginner'
        WHEN difficulty::text = 'intermediate' THEN 'Intermediate'
        WHEN difficulty::text = 'advanced' THEN 'Advanced'
        ELSE difficulty::text
    END
    """)
    
    # Drop the enum column
    op.drop_column('courses', 'difficulty')
    
    # Rename the string column to the original column name
    op.alter_column('courses', 'difficulty_str', new_column_name='difficulty', nullable=False)
    
    # Drop the enum type if it exists
    op.execute("DROP TYPE IF EXISTS coursedifficulty;")


def downgrade() -> None:
    # Create the enum type
    op.execute("CREATE TYPE coursedifficulty AS ENUM ('beginner', 'intermediate', 'advanced')")
    
    # Create a temporary column with the enum type
    op.add_column('courses', sa.Column('difficulty_enum', postgresql.ENUM('beginner', 'intermediate', 'advanced', name='coursedifficulty'), nullable=True))
    
    # Copy data from string column to enum column, converting to lowercase
    op.execute("""
    UPDATE courses SET difficulty_enum = CASE 
        WHEN LOWER(difficulty) = 'beginner' THEN 'beginner'::coursedifficulty
        WHEN LOWER(difficulty) = 'intermediate' THEN 'intermediate'::coursedifficulty
        WHEN LOWER(difficulty) = 'advanced' THEN 'advanced'::coursedifficulty
        ELSE 'intermediate'::coursedifficulty
    END
    """)
    
    # Drop the string column
    op.drop_column('courses', 'difficulty')
    
    # Rename the enum column to the original column name
    op.alter_column('courses', 'difficulty_enum', new_column_name='difficulty', nullable=False)
