"""add_programs_courses_and_permission

Revision ID: 3074fafd448a
Revises: 8f9d2e3c1a7b
Create Date: 2025-07-10 17:53:35

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3074fafd448a'
down_revision: Union[str, None] = '8f9d2e3c1a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add MANAGE_COURSE_PROGRAMS permission
    op.execute("""
    INSERT INTO permissions (id, name, category)
    SELECT 42, 'MANAGE_COURSE_PROGRAMS', 'POST'
    WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE id = 42);
    """)
    
    # Assign permission to officer role (assuming officer role_id is 2)
    op.execute("""
    INSERT INTO roles_permissions (role_id, permission_id)
    SELECT 4, 42
    WHERE NOT EXISTS (SELECT 1 FROM roles_permissions WHERE role_id = 4 AND permission_id = 42);
    """)
    
    # Create ProgramLevel enum type
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'programlevel') THEN
            CREATE TYPE programlevel AS ENUM ('UNDERGRADUATE', 'GRADUATE', 'POSTGRADUATE');
        END IF;
    END
    $$;
    """)
    
    # Create CourseDifficulty enum type
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'coursedifficulty') THEN
            CREATE TYPE coursedifficulty AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED');
        END IF;
    END
    $$;
    """)
    
    # Create programs table
    op.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        id SERIAL PRIMARY KEY,
        title VARCHAR NOT NULL,
        level programlevel NOT NULL,
        duration VARCHAR NOT NULL,
        total_students INTEGER DEFAULT 0,
        total_courses INTEGER DEFAULT 0,
        total_credits INTEGER DEFAULT 0,
        short_description VARCHAR NOT NULL,
        description TEXT,
        specializations JSONB,
        learning_objectives JSONB,
        career_prospects JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS ix_programs_id ON programs (id);
    """)
    
    # Create courses table
    op.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id SERIAL PRIMARY KEY,
        code VARCHAR NOT NULL UNIQUE,
        title VARCHAR NOT NULL,
        description TEXT,
        credits INTEGER NOT NULL,
        duration VARCHAR NOT NULL,
        difficulty coursedifficulty NOT NULL DEFAULT 'INTERMEDIATE',
        rating FLOAT DEFAULT 0.0,
        enrolled_students INTEGER DEFAULT 0,
        prerequisites JSONB,
        specialization VARCHAR,
        semester INTEGER NOT NULL,
        year INTEGER NOT NULL,
        program_id INTEGER NOT NULL REFERENCES programs(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS ix_courses_id ON courses (id);
    """)


def downgrade() -> None:
    # Remove permission assignment from officer role
    op.execute("""
    DELETE FROM roles_permissions
    WHERE permission_id = 42 AND role_id = 4;
    """)
    
    # Remove the MANAGE_COURSE_PROGRAMS permission
    op.execute("""
    DELETE FROM permissions
    WHERE id = 42 AND name = 'MANAGE_COURSE_PROGRAMS';
    """)
    
    # Drop courses table
    op.execute("DROP TABLE IF EXISTS courses;")
    
    # Drop programs table
    op.execute("DROP TABLE IF EXISTS programs;")
    
    # Drop enum types
    op.execute("""
    DROP TYPE IF EXISTS coursedifficulty;
    DROP TYPE IF EXISTS programlevel;
    """)
