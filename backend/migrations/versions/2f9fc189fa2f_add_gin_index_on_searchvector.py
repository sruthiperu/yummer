"""add gin index on searchvector

Revision ID: 2f9fc189fa2f
Revises: 865bac809dc0
Create Date: 2026-04-27 22:58:17.137846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f9fc189fa2f'
down_revision: Union[str, None] = '865bac809dc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_recipes_search_vector
        ON recipes USING GIN(search_vector)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_recipes_search_vector")
