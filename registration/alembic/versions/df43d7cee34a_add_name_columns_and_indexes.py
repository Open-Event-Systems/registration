"""Add name columns and indexes

Revision ID: df43d7cee34a
Revises: 523471301347
Create Date: 2024-11-21 12:24:47.555083

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "df43d7cee34a"
down_revision: Union[str, None] = "523471301347"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    tbl = sa.table(
        "registration",
        sa.column("preferred_name", sa.Text),
        sa.column("nickname", sa.Text),
        sa.column("extra_data", postgresql.JSONB),
    )
    op.add_column(
        "registration",
        sa.Column("preferred_name", sa.String(length=300), nullable=True),
    )
    op.add_column(
        "registration", sa.Column("nickname", sa.String(length=300), nullable=True)
    )
    op.create_index(
        "ix_first_name", "registration", [sa.text("LOWER(first_name)")], unique=False
    )
    op.create_index(
        "ix_last_name", "registration", [sa.text("LOWER(last_name)")], unique=False
    )
    op.create_index(
        "ix_nickname", "registration", [sa.text("LOWER(nickname)")], unique=False
    )
    op.create_index("ix_number", "registration", ["event_id", "number"], unique=False)
    op.create_index(
        "ix_preferred_name",
        "registration",
        [sa.text("LOWER(preferred_name)")],
        unique=False,
    )
    op.create_index(
        "ix_pagination",
        "registration",
        ["date_created", "id"],
        unique=False,
    )
    op.execute(
        sa.update(tbl)
        .values(preferred_name=tbl.c.extra_data["preferred_name"].as_string())
        .where(tbl.c.extra_data["preferred_name"] != postgresql.JSONB.NULL)
    )
    op.execute(
        sa.update(tbl)
        .values(nickname=tbl.c.extra_data["nickname"].as_string())
        .where(tbl.c.extra_data["nickname"] != postgresql.JSONB.NULL)
    )
    op.execute(sa.update(tbl).values(extra_data=tbl.c.extra_data - "preferred_name"))
    op.execute(sa.update(tbl).values(extra_data=tbl.c.extra_data - "nickname"))


def downgrade() -> None:
    tbl = sa.table(
        "registration",
        sa.column("preferred_name", sa.Text),
        sa.column("nickname", sa.Text),
        sa.column("extra_data", postgresql.JSONB),
    )
    op.execute(
        sa.update(tbl).values(
            extra_data=tbl.c.extra_data
            + sa.text(
                "jsonb_build_object('preferred_name', preferred_name, 'nickname', nickname)"
            )
        )
    )
    op.drop_index("ix_pagination", table_name="registration")
    op.drop_index("ix_preferred_name", table_name="registration")
    op.drop_index("ix_number", table_name="registration")
    op.drop_index("ix_nickname", table_name="registration")
    op.drop_index("ix_last_name", table_name="registration")
    op.drop_index("ix_first_name", table_name="registration")
    op.drop_column("registration", "nickname")
    op.drop_column("registration", "preferred_name")
