"""Add registration_check_in table

Revision ID: d5ff8178864b
Revises: 1b6678c319ec
Create Date: 2023-12-08 15:55:37.517324

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d5ff8178864b"
down_revision = "1b6678c319ec"
branch_labels = None
depends_on = None

registration = sa.table(
    "registration",
    sa.column("checked_in", sa.Integer),
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "registration_check_in",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("registration_id", sa.UUID(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=True),
        sa.Column("email", sa.String(length=300), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["account.id"],
            name=op.f("fk_registration_check_in_account_id_account"),
        ),
        sa.ForeignKeyConstraint(
            ["registration_id"],
            ["registration.id"],
            name=op.f("fk_registration_check_in_registration_id_registration"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_registration_check_in")),
    )
    op.create_index(
        op.f("ix_registration_check_in_registration_id"),
        "registration_check_in",
        ["registration_id"],
        unique=False,
    )
    op.add_column("registration", sa.Column("checked_in", sa.Integer()))
    # ### end Alembic commands ###

    op.execute(registration.update().values(checked_in=0))
    op.alter_column("registration", "checked_in", nullable=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("registration", "checked_in")
    op.drop_index(
        op.f("ix_registration_check_in_registration_id"),
        table_name="registration_check_in",
    )
    op.drop_table("registration_check_in")
    # ### end Alembic commands ###