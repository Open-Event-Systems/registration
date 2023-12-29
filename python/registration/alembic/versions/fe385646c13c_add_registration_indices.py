"""Add registration indices

Revision ID: fe385646c13c
Revises: d5ff8178864b
Create Date: 2023-12-29 15:33:37.481268

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe385646c13c"
down_revision = "d5ff8178864b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_registration_first_name",
        "registration",
        [sa.text("lower(first_name)")],
        unique=False,
    )
    op.create_index(
        "ix_registration_last_name",
        "registration",
        [sa.text("lower(last_name)")],
        unique=False,
    )
    op.create_index(
        "ix_registration_nickname",
        "registration",
        [sa.text("lower(extra_data ->> 'nickname')")],
        unique=False,
    )
    op.create_index(
        "ix_registration_pref_name",
        "registration",
        [sa.text("lower(preferred_name)")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_registration_pref_name", table_name="registration")
    op.drop_index("ix_registration_nickname", table_name="registration")
    op.drop_index("ix_registration_last_name", table_name="registration")
    op.drop_index("ix_registration_first_name", table_name="registration")
