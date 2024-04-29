"""Initial revision

Revision ID: e1863894f5a5
Revises:
Create Date: 2024-04-28 21:57:12.221258

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e1863894f5a5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cart",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.String(length=300), nullable=False),
        sa.Column("date_created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("cart_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart")),
    )


def downgrade() -> None:
    op.drop_table("cart")
