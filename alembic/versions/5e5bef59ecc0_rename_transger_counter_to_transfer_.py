"""rename transger_counter to transfer_counter in Meeting and Task models

Revision ID: 5e5bef59ecc0
Revises: 111ccacdc7f7
Create Date: 2025-02-10 16:52:39.256350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e5bef59ecc0'
down_revision: Union[str, None] = '111ccacdc7f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('meeting', sa.Column('transfer_counter', sa.Integer(), nullable=False))
    op.drop_column('meeting', 'transger_counter')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('meeting', sa.Column('transger_counter', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('meeting', 'transfer_counter')
    # ### end Alembic commands ###
