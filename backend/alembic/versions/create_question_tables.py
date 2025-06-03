"""create question tables

Revision ID: create_question_tables
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_question_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=False),
        sa.Column('options', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('chapter_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    
    # Create question_attempts table to track user attempts
    op.create_table(
        'question_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('chosen_answer', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_attempts_id'), 'question_attempts', ['id'], unique=False)
    
    # Add questions relationship to chapters table if it doesn't exist
    op.add_column('chapters', sa.Column('has_questions', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    # Drop question_attempts table
    op.drop_index(op.f('ix_question_attempts_id'), table_name='question_attempts')
    op.drop_table('question_attempts')
    
    # Drop questions table
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    
    # Remove questions relationship from chapters
    op.drop_column('chapters', 'has_questions') 