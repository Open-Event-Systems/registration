"""Add access_code table

Revision ID: 472a983a2284
Revises: 41af70eeb3ce
Create Date: 2024-06-02 17:05:45.560755

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "472a983a2284"
down_revision: Union[str, None] = "41af70eeb3ce"
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


def downgrade() -> None:
    op.drop_table("access_code")
