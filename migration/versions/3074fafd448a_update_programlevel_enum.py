"""
Update programlevel enum values to capitalized in PostgreSQL

Revision ID: 3074fafd448a_update_enum
Revises: 3074fafd448a
Create Date: 2025-07-10 21:41:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3074fafd448a_update_enum'
down_revision = '3074fafd448a'
branch_labels = None
depends_on = None

def upgrade():
    # First, check if the old enum type exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'programlevel') THEN
            -- Drop any existing constraints that use this enum
            ALTER TABLE programs ALTER COLUMN level DROP DEFAULT;
            ALTER TABLE programs ALTER COLUMN level TYPE VARCHAR USING level::VARCHAR;
            
            -- Drop the old enum type
            DROP TYPE programlevel;
        END IF;
    END $$;
    """)
    
    # Create the enum with the exact values used in the code
    op.execute("""
        CREATE TYPE programlevel AS ENUM ('Undergraduate', 'Graduate', 'Postgraduate');
    """)
    
    # Update the column to use the new enum type
    op.execute("""
        ALTER TABLE programs ALTER COLUMN level TYPE programlevel USING 
        CASE 
            WHEN level ILIKE '%undergrad%' THEN 'Undergraduate'::programlevel
            WHEN level ILIKE '%grad%' AND level NOT ILIKE '%post%' THEN 'Graduate'::programlevel
            WHEN level ILIKE '%post%' THEN 'Postgraduate'::programlevel
            ELSE 'Undergraduate'::programlevel
        END;
    """)

def downgrade():
    # First, convert to VARCHAR to avoid type issues
    op.execute("""
    ALTER TABLE programs ALTER COLUMN level TYPE VARCHAR USING level::VARCHAR;
    DROP TYPE programlevel;
    """)
    
    # Create the enum with lowercase values
    op.execute("""
        CREATE TYPE programlevel AS ENUM ('undergraduate', 'graduate', 'postgraduate');
    """)
    
    # Update the column to use the lowercase enum type
    op.execute("""
        ALTER TABLE programs ALTER COLUMN level TYPE programlevel USING 
        CASE 
            WHEN level ILIKE '%undergrad%' THEN 'undergraduate'::programlevel
            WHEN level ILIKE '%grad%' AND level NOT ILIKE '%post%' THEN 'graduate'::programlevel
            WHEN level ILIKE '%post%' THEN 'postgraduate'::programlevel
            ELSE 'undergraduate'::programlevel
        END;
    """)
