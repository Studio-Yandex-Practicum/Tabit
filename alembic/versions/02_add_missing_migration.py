"""add_missing_migration

Revision ID: 02
Revises: 01
Create Date: 2025-02-07 12:42:15.483523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02'
down_revision: Union[str, None] = '01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'commentfeed', ['id'])
    op.create_unique_constraint(None, 'company', ['id'])
    op.create_unique_constraint(None, 'department', ['id'])
    op.create_unique_constraint(None, 'filemeeting', ['id'])
    op.create_unique_constraint(None, 'filemessage', ['id'])
    op.create_unique_constraint(None, 'fileproblem', ['id'])
    op.create_unique_constraint(None, 'filetask', ['id'])
    op.create_unique_constraint(None, 'landingpage', ['id'])
    op.create_unique_constraint(None, 'licensetype', ['id'])
    op.create_unique_constraint(None, 'messagefeed', ['id'])
    op.create_unique_constraint(None, 'problem', ['id'])
    op.create_unique_constraint(None, 'taguser', ['id'])
    op.create_unique_constraint(None, 'votingbyuser', ['id'])
    op.create_unique_constraint(None, 'votingfeed', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'votingfeed', type_='unique')
    op.drop_constraint(None, 'votingbyuser', type_='unique')
    op.drop_constraint(None, 'taguser', type_='unique')
    op.drop_constraint(None, 'problem', type_='unique')
    op.drop_constraint(None, 'messagefeed', type_='unique')
    op.drop_constraint(None, 'licensetype', type_='unique')
    op.drop_constraint(None, 'landingpage', type_='unique')
    op.drop_constraint(None, 'filetask', type_='unique')
    op.drop_constraint(None, 'fileproblem', type_='unique')
    op.drop_constraint(None, 'filemessage', type_='unique')
    op.drop_constraint(None, 'filemeeting', type_='unique')
    op.drop_constraint(None, 'department', type_='unique')
    op.drop_constraint(None, 'company', type_='unique')
    op.drop_constraint(None, 'commentfeed', type_='unique')
    # ### end Alembic commands ###
