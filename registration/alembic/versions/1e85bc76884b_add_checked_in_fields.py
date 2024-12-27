"""Add checked in fields

Revision ID: 1e85bc76884b
Revises: df43d7cee34a
Create Date: 2024-12-21 18:46:44.152274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e85bc76884b"
down_revision: Union[str, None] = "df43d7cee34a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("registration", sa.Column("checked_in", sa.Boolean(), nullable=True))
    op.add_column(
        "registration",
        sa.Column("date_checked_in", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_checked_in", "registration", ["event_id", "checked_in"], unique=False
    )
    op.create_index(
        "ix_date_checked_in", "registration", ["date_checked_in"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_date_checked_in", table_name="registration")
    op.drop_index("ix_checked_in", table_name="registration")
    op.drop_column("registration", "date_checked_in")
    op.drop_column("registration", "checked_in")
