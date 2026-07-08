"""add_rating_and_numratings_to_recipes

Revision ID: 3f48319a7dbf
Revises: b2c3d4e5f6a7
Create Date: 2026-07-08 09:42:48.520686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f48319a7dbf'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('recipes', sa.Column('rating', sa.Numeric(2, 1), nullable=True))
    op.add_column('recipes', sa.Column('num_ratings', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('recipes', 'num_ratings')
    op.drop_column('recipes', 'rating')
