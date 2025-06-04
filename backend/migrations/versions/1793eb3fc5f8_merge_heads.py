"""merge_heads

Revision ID: 1793eb3fc5f8
Revises: c3045dc23e22, update_uploads_table
Create Date: 2025-06-04 16:23:57.346907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1793eb3fc5f8'
down_revision: Union[str, None] = ('c3045dc23e22', 'update_uploads_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
