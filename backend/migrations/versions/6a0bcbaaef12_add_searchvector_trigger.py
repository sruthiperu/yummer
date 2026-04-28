"""add searchvector trigger

Revision ID: 6a0bcbaaef12
Revises: 2f9fc189fa2f
Create Date: 2026-04-27 23:07:48.735064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0bcbaaef12'
down_revision: Union[str, None] = '2f9fc189fa2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.drop_index('idx_recipes_search_vector', table_name='recipes', postgresql_using='gin')
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english',
                coalesce(NEW.name, '') || ' ' ||
                coalesce(NEW.description, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER recipes_search_vector_trigger
        BEFORE INSERT OR UPDATE ON recipes
        FOR EACH ROW
        EXECUTE FUNCTION update_search_vector();
        """
    )


def downgrade() -> None:
    # op.create_index('idx_recipes_search_vector', 'recipes', ['search_vector'], unique=False, postgresql_using='gin')
    op.execute("DROP TRIGGER IF EXISTS recipes_search_vector_trigger ON recipes")
    op.execute("DROP FUNCTION IF EXISTS update_search_vector")
