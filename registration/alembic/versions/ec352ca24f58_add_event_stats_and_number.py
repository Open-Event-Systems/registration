"""Add event stats and number

Revision ID: ec352ca24f58
Revises: 87730ca2879a
Create Date: 2024-04-27 21:55:21.419969

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec352ca24f58"
down_revision: Union[str, None] = "87730ca2879a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_stats",
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.add_column("registration", sa.Column("number", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("registration", "number")
    op.drop_table("event_stats")
