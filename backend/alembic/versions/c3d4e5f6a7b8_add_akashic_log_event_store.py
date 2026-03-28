"""add akashic log event store

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-28 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('knowledge_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_events_event_type'), 'knowledge_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_knowledge_events_user_id'), 'knowledge_events', ['user_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_knowledge_events_user_id'), table_name='knowledge_events')
    op.drop_index(op.f('ix_knowledge_events_event_type'), table_name='knowledge_events')
    op.drop_table('knowledge_events')
