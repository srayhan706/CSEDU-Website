"""
Migration to fix equipment_bookings.user_id to be Integer and a ForeignKey to users.id
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = 'a50706fixequipid'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Drop existing foreign key constraint if it exists
    with op.batch_alter_table('equipment_bookings') as batch_op:
        batch_op.alter_column('user_id',
            type_=sa.Integer(),
            existing_type=sa.VARCHAR(),
            existing_nullable=False,
            postgresql_using="user_id::integer"
        )
        batch_op.create_foreign_key(
            'equipment_bookings_user_id_fkey',
            'users',
            ['user_id'], ['id']
        )

def downgrade():
    # Step 1: Drop new foreign key constraint
    with op.batch_alter_table('equipment_bookings') as batch_op:
        batch_op.drop_constraint('equipment_bookings_user_id_fkey', type_='foreignkey')
        batch_op.alter_column('user_id',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(),
            existing_nullable=False
        )
        # Optionally recreate old constraint if needed
        # batch_op.create_foreign_key('equipment_bookings_user_id_fkey', 'users', ['user_id'], ['id'])
