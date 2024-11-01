"""Update auth table

Revision ID: 972656493800
Revises: 54805d339b34
Create Date: 2024-06-29 16:11:05.984381

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from oes.utils.orm import JSONB

# revision identifiers, used by Alembic.
revision: str = "972656493800"
down_revision: Union[str, None] = "54805d339b34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "auth",
        "max_path_length",
        existing_type=sa.Integer(),
        existing_nullable=False,
        new_column_name="path_length",
    )

    # TODO: eventually just squash/recreate these migrations
    op.drop_column("auth", "scope")
    op.add_column("auth", sa.Column("scope", JSONB))


def downgrade() -> None:
    op.alter_column(
        "auth",
        "path_length",
        existing_type=sa.Integer(),
        existing_nullable=False,
        new_column_name="max_path_length",
    )

    # TODO: eventually just squash/recreate these migrations
    op.drop_column("auth", "scope")
    op.add_column("auth", sa.Column("scope", sa.VARCHAR(length=300)))
    op.execute("UPDATE auth SET scope=''")
    op.alter_column(
        "auth", "scope", existing_type=sa.VARCHAR(length=300), nullable=False
    )
