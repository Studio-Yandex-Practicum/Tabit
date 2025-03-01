"""the_company's_connection_to_the_problem_via_company_id

Revision ID: 05
Revises: 04
Create Date: 2025-02-22 10:53:14.449751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05'
down_revision: Union[str, None] = '04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'meeting', ['id'])
    op.add_column('problem', sa.Column('company_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'problem', 'company', ['company_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'problem', type_='foreignkey')
    op.drop_column('problem', 'company_id')
    op.drop_constraint(None, 'meeting', type_='unique')
    # ### end Alembic commands ###
