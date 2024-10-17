"""participant_id

Revision ID: e4a51a0e225f
Revises: 648ec19ed9e5
Create Date: 2024-10-06 08:28:01.827633

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4a51a0e225f"
down_revision: Union[str, None] = "648ec19ed9e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "participants",
        sa.Column("participant_id", sa.Integer(), nullable=True),
    )
    op.drop_index("ix_participants_custom_id", table_name="participants")
    op.create_index(
        op.f("ix_participants_participant_id"),
        "participants",
        ["participant_id"],
        unique=True,
    )
    op.drop_column("participants", "custom_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("participants", sa.Column("custom_id", sa.VARCHAR(), nullable=True))
    op.drop_index(op.f("ix_participants_participant_id"), table_name="participants")
    op.create_index(
        "ix_participants_custom_id", "participants", ["custom_id"], unique=1
    )
    op.drop_column("participants", "participant_id")
    # ### end Alembic commands ###
