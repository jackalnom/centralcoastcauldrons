"""create global inventory

Revision ID: e91d0c24f7d0
Revises:
Create Date: 2025-03-30 11:23:36.782933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e91d0c24f7d0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "global_inventory",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("gold", sa.Integer, nullable=False),
        sa.CheckConstraint("gold >= 0", name="check_gold_positive"),
    )

    op.execute(sa.text("INSERT INTO global_inventory (gold) VALUES (100)"))


def downgrade():
    op.drop_table("global_inventory")
