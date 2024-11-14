"""Initial revision

Revision ID: 27ebc79e0df5
Revises:
Create Date: 2024-11-14 15:18:22.340458

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "27ebc79e0df5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checkin",
        sa.Column("id", sa.String(length=14), nullable=False),
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("session_id", sa.String(length=300), nullable=True),
        sa.Column("date_started", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("date_finished", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("registration_id", sa.String(length=300), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checkin")),
    )
    op.create_index(
        "ix_checkin_session_id", "checkin", ["event_id", "session_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_checkin_session_id", table_name="checkin")
    op.drop_table("checkin")
