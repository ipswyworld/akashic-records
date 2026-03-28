"""add ego expansion fields

Revision ID: 7a1b3c2d4e5f
Revises: cc025ca292b4
Create Date: 2026-03-27 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7a1b3c2d4e5f'
down_revision = 'cc025ca292b4'
branch_labels = None
depends_on = None

def upgrade():
    # Add columns to user_psychology
    op.add_column('user_psychology', sa.Column('core_values', sa.JSON(), nullable=True))
    op.add_column('user_psychology', sa.Column('current_goals', sa.JSON(), nullable=True))
    op.add_column('user_psychology', sa.Column('life_narrative', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('user_psychology') as batch_op:
        batch_op.drop_column('life_narrative')
        batch_op.drop_column('current_goals')
        batch_op.drop_column('core_values')
