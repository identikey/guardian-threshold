"""Participants

Revision ID: 648ec19ed9e5
Revises: 1b5ac36715ca
Create Date: 2024-10-06 06:55:09.864269

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "648ec19ed9e5"
down_revision: Union[str, None] = "1b5ac36715ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("custom_id", sa.String(), nullable=True),
        sa.Column("open_commitment", sa.String(), nullable=True),
        sa.Column("closed_commitment", sa.String(), nullable=True),
        sa.Column("key_share", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_participants_custom_id"),
        "participants",
        ["custom_id"],
        unique=True,
    )
    op.create_index(op.f("ix_participants_id"), "participants", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_participants_id"), table_name="participants")
    op.drop_index(op.f("ix_participants_custom_id"), table_name="participants")
    op.drop_table("participants")
    # ### end Alembic commands ###
