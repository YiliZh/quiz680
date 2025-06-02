"""add title to uploads

Revision ID: add_title_to_uploads
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_title_to_uploads'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add title, description, and status columns to uploads table
    op.add_column('uploads', sa.Column('title', sa.String(), nullable=True))
    op.add_column('uploads', sa.Column('description', sa.String(), nullable=True))
    op.add_column('uploads', sa.Column('status', sa.String(), nullable=True))
    
    # Update existing rows to have default values
    op.execute("UPDATE uploads SET title = filename WHERE title IS NULL")
    op.execute("UPDATE uploads SET status = 'completed' WHERE status IS NULL")
    
    # Make title and status not nullable after setting defaults
    op.alter_column('uploads', 'title', nullable=False)
    op.alter_column('uploads', 'status', nullable=False)

def downgrade():
    # Remove the columns
    op.drop_column('uploads', 'status')
    op.drop_column('uploads', 'description')
    op.drop_column('uploads', 'title') 