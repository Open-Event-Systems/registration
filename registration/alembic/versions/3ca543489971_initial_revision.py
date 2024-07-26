"""Initial revision

Revision ID: 3ca543489971
Revises:
Create Date: 2024-07-25 23:02:57.749187

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3ca543489971"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_code",
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("date_created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("date_expires", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_access_code")),
    )
    op.create_table(
        "event_stats",
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_event_stats")),
    )
    op.create_table(
        "registration",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "created", "canceled", name="status"),
            nullable=False,
        ),
        sa.Column("date_created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("date_updated", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("first_name", sa.String(length=300), nullable=True),
        sa.Column("last_name", sa.String(length=300), nullable=True),
        sa.Column("email", sa.String(length=300), nullable=True),
        sa.Column("account_id", sa.String(length=300), nullable=True),
        sa.Column(
            "extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_registration")),
    )
    op.create_index("ix_email", "registration", [sa.text("LOWER(email)")], unique=False)
    op.create_index(
        "ix_extra_data",
        "registration",
        [sa.text("extra_data jsonb_path_ops")],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        op.f("ix_registration_account_id"), "registration", ["account_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_registration_account_id"), table_name="registration")
    op.drop_index("ix_extra_data", table_name="registration", postgresql_using="gin")
    op.drop_index("ix_email", table_name="registration")
    op.drop_table("registration")
    op.drop_table("event_stats")
    op.drop_table("access_code")
