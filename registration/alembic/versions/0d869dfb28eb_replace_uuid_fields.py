"""Replace UUID fields

Revision ID: 0d869dfb28eb
Revises: 472a983a2284
Create Date: 2024-07-19 12:40:21.546734

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d869dfb28eb"
down_revision: Union[str, None] = "472a983a2284"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "registration",
        "id",
        existing_type=sa.UUID(),
        type_=sa.String(length=36),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "registration",
        "id",
        existing_type=sa.String(length=36),
        type_=sa.UUID(),
        existing_nullable=False,
    )
