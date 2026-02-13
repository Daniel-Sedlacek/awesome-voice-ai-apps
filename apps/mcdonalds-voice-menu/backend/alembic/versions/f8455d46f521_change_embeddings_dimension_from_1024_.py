"""change embeddings dimension from 1024 to 384

Revision ID: f8455d46f521
Revises: 0b4752c330a2
Create Date: 2026-02-13 19:20:32.220931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


# revision identifiers, used by Alembic.
revision: str = 'f8455d46f521'
down_revision: Union[str, Sequence[str], None] = '0b4752c330a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('menu_items', 'embedding')
    op.add_column('menu_items', sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('menu_items', 'embedding')
    op.add_column('menu_items', sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1024), nullable=True))
