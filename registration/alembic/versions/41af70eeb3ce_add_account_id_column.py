"""Add account_id column

Revision ID: 41af70eeb3ce
Revises: ec352ca24f58
Create Date: 2024-05-31 17:11:59.205047

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "41af70eeb3ce"
down_revision: Union[str, None] = "ec352ca24f58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "registration", sa.Column("account_id", sa.String(length=300), nullable=True)
    )
    op.create_index("ix_email", "registration", [sa.text("LOWER(email)")], unique=False)
    op.create_index(
        op.f("ix_registration_account_id"), "registration", ["account_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_registration_account_id"), table_name="registration")
    op.drop_index("ix_email", table_name="registration")
    op.drop_column("registration", "account_id")
