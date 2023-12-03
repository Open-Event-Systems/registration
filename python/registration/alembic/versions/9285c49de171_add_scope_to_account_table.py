"""Add scope to account table

Revision ID: 9285c49de171
Revises: 58797483bb1c
Create Date: 2023-12-03 16:24:43.868948

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import String, column, table

# revision identifiers, used by Alembic.
revision = "9285c49de171"
down_revision = "58797483bb1c"
branch_labels = None
depends_on = None

account = table(
    "account",
    column("scope", String),
)


def upgrade() -> None:
    op.add_column("account", sa.Column("scope", sa.String(length=300)))
    op.execute(account.update().values(scope="cart self-service"))
    op.alter_column("account", "scope", nullable=False)


def downgrade() -> None:
    op.drop_column("account", "scope")
