"""users_auth_provider_fields

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auth_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("provider_user_id", sa.String(), nullable=True))

    op.execute(
        """
        UPDATE users
        SET auth_provider = 'google',
            provider_user_id = google_id
        WHERE google_id IS NOT NULL
        """
    )

    op.alter_column("users", "auth_provider", nullable=False)
    op.alter_column("users", "provider_user_id", nullable=False)

    op.drop_constraint("users_google_id_key", "users", type_="unique")
    op.drop_column("users", "google_id")

    op.create_unique_constraint(
        "uq_users_auth_provider_provider_user_id",
        "users",
        ["auth_provider", "provider_user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_auth_provider_provider_user_id", "users", type_="unique")

    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True))
    op.execute(
        """
        UPDATE users
        SET google_id = provider_user_id
        WHERE auth_provider = 'google'
        """
    )
    op.execute(
        """
        UPDATE users
        SET google_id = 'migrated-' || id::text
        WHERE google_id IS NULL
        """
    )
    op.alter_column("users", "google_id", nullable=False)
    op.create_unique_constraint("users_google_id_key", "users", ["google_id"])

    op.drop_column("users", "provider_user_id")
    op.drop_column("users", "auth_provider")
