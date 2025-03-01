"""first commit

Revision ID: b0bf7ea8a9a7
Revises: 
Create Date: 2025-03-01 22:57:29.281513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0bf7ea8a9a7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('decks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('subject', sa.String(length=50), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('weekly_goal', sa.Integer(), nullable=True),
    sa.Column('mastery_level', sa.Float(), nullable=True),
    sa.Column('study_streak', sa.Integer(), nullable=True),
    sa.Column('focus_score', sa.Float(), nullable=True),
    sa.Column('retention_rate', sa.Float(), nullable=True),
    sa.Column('cards_mastered', sa.Integer(), nullable=True),
    sa.Column('minutes_per_day', sa.Float(), nullable=True),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('flashcards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deck_id', sa.Integer(), nullable=False),
    sa.Column('front_text', sa.Text(), nullable=False),
    sa.Column('back_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('deck_id', sa.Integer(), nullable=False),
    sa.Column('flashcard_id', sa.Integer(), nullable=False),
    sa.Column('study_count', sa.Integer(), nullable=False),
    sa.Column('correct_attempts', sa.Integer(), nullable=False),
    sa.Column('incorrect_attempts', sa.Integer(), nullable=False),
    sa.Column('total_study_time', sa.Float(), nullable=False),
    sa.Column('last_studied_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('next_review_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('review_status', sa.Enum('new', 'learning', 'reviewing', 'mastered', name='review_status'), nullable=False),
    sa.Column('is_learned', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ),
    sa.ForeignKeyConstraint(['flashcard_id'], ['flashcards.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'flashcard_id', name='unique_user_flashcard_progress')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('progress')
    op.drop_table('flashcards')
    op.drop_table('user_stats')
    op.drop_table('decks')
    op.drop_table('users')
    # ### end Alembic commands ###
