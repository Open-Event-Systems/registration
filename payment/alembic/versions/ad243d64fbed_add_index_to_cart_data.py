"""Add index to cart_data

Revision ID: ad243d64fbed
Revises: 4a5b20883385
Create Date: 2024-11-27 00:34:24.817592

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ad243d64fbed"
down_revision: Union[str, None] = "4a5b20883385"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_cart_data",
        "payment",
        [sa.text("cart_data jsonb_path_ops")],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_cart_data", table_name="payment", postgresql_using="gin")
