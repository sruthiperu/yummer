"""create_daily_token_usage

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_token_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_key", sa.String(), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("subject_key", "usage_date", name="uq_daily_token_usage_subject_date"),
    )
    op.create_index("ix_daily_token_usage_subject_key", "daily_token_usage", ["subject_key"])


def downgrade() -> None:
    op.drop_index("ix_daily_token_usage_subject_key", table_name="daily_token_usage")
    op.drop_table("daily_token_usage")
