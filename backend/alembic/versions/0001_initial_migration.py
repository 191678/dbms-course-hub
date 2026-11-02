"""Initial migration

Revision ID: 0001_initial_migration
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'chapters',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('order_index', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_chapters_order', 'chapters', ['order_index'])

    op.create_table(
        'knowledge_points',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('chapter_id', sa.Integer, sa.ForeignKey('chapters.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False, default='medium'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_knowledge_points_chapter', 'knowledge_points', ['chapter_id'])
    op.create_index('idx_knowledge_points_difficulty', 'knowledge_points', ['difficulty'])

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('knowledge_point_id', sa.Integer, sa.ForeignKey('knowledge_points.id'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('stem', sa.Text, nullable=False),
        sa.Column('options', sa.JSON, nullable=True),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('analysis', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_questions_knowledge_point', 'questions', ['knowledge_point_id'])
    op.create_index('idx_questions_type', 'questions', ['type'])


def downgrade() -> None:
    op.drop_table('questions')
    op.drop_table('knowledge_points')
    op.drop_table('chapters')
