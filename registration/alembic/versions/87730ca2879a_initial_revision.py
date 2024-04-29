"""Initial revision

Revision ID: 87730ca2879a
Revises:
Create Date: 2024-04-26 23:33:31.624682

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "87730ca2879a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "registration",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "created", "canceled", name="status"),
            nullable=False,
        ),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_name", sa.String(length=300), nullable=True),
        sa.Column("last_name", sa.String(length=300), nullable=True),
        sa.Column("email", sa.String(length=300), nullable=True),
        sa.Column(
            "extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("registration")
