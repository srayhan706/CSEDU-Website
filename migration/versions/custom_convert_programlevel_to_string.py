"""custom_convert_programlevel_to_string

Revision ID: custom_convert_level
Revises: 3074fafd448a_update_enum
Create Date: 2025-07-10 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'custom_convert_level'
down_revision: Union[str, None] = '3074fafd448a_update_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, create a temporary column to store the enum values as strings
    op.add_column('programs', sa.Column('level_str', sa.String(), nullable=True))
    
    # Copy data from enum column to string column
    op.execute("UPDATE programs SET level_str = level::text")
    
    # Drop the enum column
    op.drop_column('programs', 'level')
    
    # Rename the string column to the original column name
    op.alter_column('programs', 'level_str', new_column_name='level', nullable=False)
    
    # Drop the enum type if it exists
    op.execute("DROP TYPE IF EXISTS programlevel;")


def downgrade() -> None:
    # Create the enum type
    op.execute("CREATE TYPE programlevel AS ENUM ('Undergraduate', 'Graduate', 'Postgraduate')")
    
    # Create a temporary column with the enum type
    op.add_column('programs', sa.Column('level_enum', postgresql.ENUM('Undergraduate', 'Graduate', 'Postgraduate', name='programlevel'), nullable=True))
    
    # Copy data from string column to enum column
    op.execute("UPDATE programs SET level_enum = level::programlevel")
    
    # Drop the string column
    op.drop_column('programs', 'level')
    
    # Rename the enum column to the original column name
    op.alter_column('programs', 'level_enum', new_column_name='level', nullable=False)
