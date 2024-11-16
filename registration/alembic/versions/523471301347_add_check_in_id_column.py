"""Add check_in_id column

Revision ID: 523471301347
Revises: 3ca543489971
Create Date: 2024-11-16 16:31:40.812227

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "523471301347"
down_revision: Union[str, None] = "3ca543489971"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "registration", sa.Column("check_in_id", sa.String(length=8), nullable=True)
    )
    op.create_index(
        "ix_check_in_id", "registration", ["event_id", "check_in_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_check_in_id", table_name="registration")
    op.drop_column("registration", "check_in_id")
