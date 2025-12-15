"""db generates user uuid

Revision ID: e747ea9ed843
Revises: 20cb745c7d94
Create Date: 2025-12-15 15:48:18.304451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e747ea9ed843'
down_revision: Union[str, Sequence[str], None] = '20cb745c7d94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # на всякий случай (если БД где-то ещё поднимают без ручного шага)
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.alter_column(
        "users",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        server_default=None,
        existing_nullable=False,
    )
