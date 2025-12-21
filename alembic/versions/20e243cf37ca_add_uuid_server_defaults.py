"""add uuid server defaults

Revision ID: 20e243cf37ca
Revises: 2146745fe696
Create Date: 2025-12-21 14:23:52.060022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20e243cf37ca'
down_revision: Union[str, Sequence[str], None] = '2146745fe696'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op


def upgrade():
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
    """)

    op.execute("""
        ALTER TABLE recruiters
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
    """)

    op.execute("""
        ALTER TABLE vacancies
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
    """)

    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
    """)


def downgrade():
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN id DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE recruiters
        ALTER COLUMN id DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE vacancies
        ALTER COLUMN id DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE candidates
        ALTER COLUMN id DROP DEFAULT;
    """)

