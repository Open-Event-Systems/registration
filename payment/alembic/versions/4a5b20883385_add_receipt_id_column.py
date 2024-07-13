"""Add receipt_id column

Revision ID: 4a5b20883385
Revises: bcb0f3682d8b
Create Date: 2024-07-13 16:49:05.099774

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a5b20883385"
down_revision: Union[str, None] = "bcb0f3682d8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "payment", sa.Column("receipt_id", sa.String(length=12), nullable=True)
    )
    op.create_unique_constraint(
        op.f("uq_payment_receipt_id"), "payment", ["receipt_id"]
    )


def downgrade() -> None:
    op.drop_constraint(op.f("uq_payment_receipt_id"), "payment", type_="unique")
    op.drop_column("payment", "receipt_id")
