"""add neural forge tables

Revision ID: a1b2c3d4e5f6
Revises: 7a1b3c2d4e5f
Create Date: 2026-03-27 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '7a1b3c2d4e5f'
branch_labels = None
depends_on = None

def upgrade():
    # Create neural_skills table
    op.create_table('neural_skills',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_neural_skills_name'), 'neural_skills', ['name'], unique=False)
    op.create_index(op.f('ix_neural_skills_user_id'), 'neural_skills', ['user_id'], unique=False)

    # Create agent_performance table
    op.create_table('agent_performance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=True),
        sa.Column('task_category', sa.String(), nullable=True),
        sa.Column('fitness_score', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_performance_agent_name'), 'agent_performance', ['agent_name'], unique=False)
    op.create_index(op.f('ix_agent_performance_user_id'), 'agent_performance', ['user_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_agent_performance_user_id'), table_name='agent_performance')
    op.drop_index(op.f('ix_agent_performance_agent_name'), table_name='agent_performance')
    op.drop_table('agent_performance')
    op.drop_index(op.f('ix_neural_skills_user_id'), table_name='neural_skills')
    op.drop_index(op.f('ix_neural_skills_name'), table_name='neural_skills')
    op.drop_table('neural_skills')
