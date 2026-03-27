"""add student, officer, faculty roles

Revision ID: c8527c01b6bf
Revises: a0e3d5045d81
Create Date: 2025-07-06 10:07:35.696723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from database import Base


# revision identifiers, used by Alembic.
revision: str = 'c8527c01b6bf'
down_revision: Union[str, None] = 'a0e3d5045d81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert roles only if they do not already exist
    conn = op.get_bind()
    conn.execute(sa.text("INSERT INTO roles (id, name) VALUES (3, 'STUDENT') ON CONFLICT (id) DO NOTHING;"))
    conn.execute(sa.text("INSERT INTO roles (id, name) VALUES (4, 'OFFICER') ON CONFLICT (id) DO NOTHING;"))
    conn.execute(sa.text("INSERT INTO roles (id, name) VALUES (5, 'FACULTY') ON CONFLICT (id) DO NOTHING;"))


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id IN (3, 4, 5)")
