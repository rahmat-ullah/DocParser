"""Add markdown_path column to documents table

Revision ID: 86ea82d35c42
Revises: e9789268d113
Create Date: 2025-07-10 01:22:01.333300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86ea82d35c42'
down_revision: Union[str, None] = 'e9789268d113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add markdown_path column to documents table
    op.add_column('documents', sa.Column('markdown_path', sa.String(500), nullable=True))


def downgrade() -> None:
    # Remove markdown_path column from documents table
    op.drop_column('documents', 'markdown_path')
