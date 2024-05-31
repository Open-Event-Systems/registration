"""Add email auth table

Revision ID: cec9198cba41
Revises: 8f1f34f51bb9
Create Date: 2024-05-30 19:53:15.693272

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cec9198cba41"
down_revision: Union[str, None] = "8f1f34f51bb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_auth",
        sa.Column("email", sa.String(length=300), nullable=False),
        sa.Column("date_sent", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("date_expires", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("email", name=op.f("pk_email_auth")),
    )


def downgrade() -> None:
    op.drop_table("email_auth")
