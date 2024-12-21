"""Add role column

Revision ID: 3f60a0fd2505
Revises: 008c665f04fd
Create Date: 2024-08-03 19:43:57.995245

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f60a0fd2505"
down_revision: Union[str, None] = "008c665f04fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("auth", sa.Column("role", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("auth", "role")
