"""update uploads table

Revision ID: update_uploads_table
Revises: add_title_to_uploads
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_uploads_table'
down_revision = 'add_title_to_uploads'
branch_labels = None
depends_on = None

def upgrade():
    # Rename file_path to stored_path
    op.alter_column('uploads', 'file_path', new_column_name='stored_path')
    
    # Add status column
    op.add_column('uploads', sa.Column('status', sa.String(), nullable=True))
    op.execute("UPDATE uploads SET status = 'completed' WHERE status IS NULL")
    op.alter_column('uploads', 'status', nullable=False)
    
    # Add description column
    op.add_column('uploads', sa.Column('description', sa.String(), nullable=True))
    
    # Rename created_at to uploaded_at
    op.alter_column('uploads', 'created_at', new_column_name='uploaded_at')

def downgrade():
    # Rename uploaded_at back to created_at
    op.alter_column('uploads', 'uploaded_at', new_column_name='created_at')
    
    # Remove description column
    op.drop_column('uploads', 'description')
    
    # Remove status column
    op.drop_column('uploads', 'status')
    
    # Rename stored_path back to file_path
    op.alter_column('uploads', 'stored_path', new_column_name='file_path') 