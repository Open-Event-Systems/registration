"""Add device_auth table

Revision ID: 008c665f04fd
Revises: 972656493800
Create Date: 2024-08-03 00:50:32.416348

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "008c665f04fd"
down_revision: Union[str, None] = "972656493800"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_auth",
        sa.Column("device_code", sa.String(length=12), nullable=False),
        sa.Column("user_code", sa.String(length=8), nullable=False),
        sa.Column("date_expires", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("auth_id", sa.String(length=14), nullable=True),
        sa.ForeignKeyConstraint(
            ["auth_id"], ["auth.id"], name=op.f("fk_device_auth_auth_id_auth")
        ),
        sa.PrimaryKeyConstraint("device_code", name=op.f("pk_device_auth")),
        sa.UniqueConstraint("user_code", name=op.f("uq_device_auth_user_code")),
    )

    tbl = sa.table(
        "auth",
        sa.column("scope", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("path_length", sa.Integer()),
    )
    op.execute(sa.update(tbl).values(scope=[]).where(tbl.c.scope == sa.null()))
    op.execute(
        sa.update(tbl).values(path_length=0).where(tbl.c.path_length == sa.null())
    )

    op.alter_column(
        "auth",
        "scope",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
    )
    op.alter_column("auth", "path_length", existing_type=sa.INTEGER(), nullable=False)


def downgrade() -> None:
    op.alter_column("auth", "path_length", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "auth",
        "scope",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    )
    op.drop_table("device_auth")
