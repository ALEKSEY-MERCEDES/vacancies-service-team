"""db generates company uuid

Revision ID: 1966bfd899dc
Revises: df7b892a554a
Create Date: 2025-12-15 16:56:31.218537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1966bfd899dc'
down_revision: Union[str, Sequence[str], None] = 'df7b892a554a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.alter_column(
        "companies",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "companies",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        server_default=None,
        existing_nullable=False,
    )
