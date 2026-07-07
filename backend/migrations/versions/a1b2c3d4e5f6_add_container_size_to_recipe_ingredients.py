"""add container_size to recipe_ingredients

Revision ID: a1b2c3d4e5f6
Revises: 6a0bcbaaef12
Create Date: 2026-07-05 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "6a0bcbaaef12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipe_ingredients", sa.Column("container_size", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("recipe_ingredients", "container_size")
