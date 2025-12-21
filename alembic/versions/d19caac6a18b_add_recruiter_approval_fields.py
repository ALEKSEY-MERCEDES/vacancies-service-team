"""add recruiter approval fields

Revision ID: d19caac6a18b
Revises: 20e243cf37ca
Create Date: 2025-12-21 14:45:58.383292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd19caac6a18b'
down_revision: Union[str, Sequence[str], None] = '20e243cf37ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "recruiters",
        sa.Column("full_name_position", sa.String(255), nullable=True),
    )
    op.add_column(
        "recruiters",
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "recruiters",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_column("recruiters", "created_at")
    op.drop_column("recruiters", "is_approved")
    op.drop_column("recruiters", "full_name_position")

