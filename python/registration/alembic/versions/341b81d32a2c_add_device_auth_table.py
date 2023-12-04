"""Add device_auth table

Revision ID: 341b81d32a2c
Revises: 9285c49de171
Create Date: 2023-12-03 23:29:04.275591

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "341b81d32a2c"
down_revision = "9285c49de171"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_auth",
        sa.Column("device_code", sa.String(length=64), nullable=False),
        sa.Column("user_code", sa.String(length=12), nullable=False),
        sa.Column("client_id", sa.String(length=300), nullable=False),
        sa.Column("scope", sa.String(length=300), nullable=False),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_expires", sa.DateTime(timezone=True), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("device_code", name=op.f("pk_device_auth")),
        sa.UniqueConstraint("user_code", name=op.f("uq_device_auth_user_code")),
    )


def downgrade() -> None:
    op.drop_table("device_auth")
