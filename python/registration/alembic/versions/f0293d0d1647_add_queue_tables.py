"""Add queue tables

Revision ID: f0293d0d1647
Revises: fe385646c13c
Create Date: 2024-01-03 16:51:17.193561

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f0293d0d1647"
down_revision = "fe385646c13c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "queue_group",
        sa.Column("id", sa.String(length=300), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_group")),
    )
    op.create_table(
        "queue_item",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("group_id", sa.String(length=300), nullable=False),
        sa.Column("station_id", sa.String(length=300), nullable=True),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_started", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_completed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_item")),
    )
    op.create_index(
        op.f("ix_queue_item_date_completed"),
        "queue_item",
        ["date_completed"],
        unique=False,
    )
    op.create_table(
        "queue_station",
        sa.Column("id", sa.String(length=300), nullable=False),
        sa.Column("group_id", sa.String(length=300), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_station")),
    )
    op.create_table(
        "queue_station_print_request",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("station_id", sa.String(length=300), nullable=False),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_completed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_station_print_request")),
    )
    op.create_index(
        op.f("ix_queue_station_print_request_date_created"),
        "queue_station_print_request",
        ["date_created"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_queue_station_print_request_date_created"),
        table_name="queue_station_print_request",
    )
    op.drop_table("queue_station_print_request")
    op.drop_table("queue_station")
    op.drop_index(op.f("ix_queue_item_date_completed"), table_name="queue_item")
    op.drop_table("queue_item")
    op.drop_table("queue_group")
