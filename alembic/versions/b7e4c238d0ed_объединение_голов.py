"""Объединение голов

Revision ID: b7e4c238d0ed
Revises: 5e5bef59ecc0, dae11c5cc7c1
Create Date: 2025-02-20 01:12:09.393865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e4c238d0ed'
down_revision: Union[str, None] = ('5e5bef59ecc0', 'dae11c5cc7c1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
