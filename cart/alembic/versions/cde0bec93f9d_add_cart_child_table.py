"""Add cart_child table

Revision ID: cde0bec93f9d
Revises: e1863894f5a5
Create Date: 2024-04-28 22:28:16.960363

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cde0bec93f9d"
down_revision: Union[str, None] = "e1863894f5a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cart_child",
        sa.Column("parent_id", sa.String(length=64), nullable=False),
        sa.Column("child_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["child_id"], ["cart.id"], name=op.f("fk_cart_child_child_id_cart")
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["cart.id"], name=op.f("fk_cart_child_parent_id_cart")
        ),
        sa.PrimaryKeyConstraint("parent_id", "child_id", name=op.f("pk_cart_child")),
    )


def downgrade() -> None:
    op.drop_table("cart_child")
