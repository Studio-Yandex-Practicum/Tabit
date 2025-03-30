"""Change resultmeeting

Revision ID: 05
Revises: 04
Create Date: 2025-03-30 20:30:00.910274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '05'
down_revision: Union[str, None] = '04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


resultmeetingengagementenum = postgresql.ENUM(
    'YES', 'MORE_THAN_HALF', 'LESS_THAN_HALF', 'NOBODY',
    name='resultmeetingengagementenum',
    create_type=False  # Будем явно управлять созданием/удалением
)

resultmeetingsolutionenum = postgresql.ENUM(
    'YES', 'MORE_YES', 'MORE_NO', 'NO',
    name='resultmeetingsolutionenum',
    create_type=False
)

def upgrade():
    op.drop_column('resultmeeting', 'participant_engagement')
    op.drop_column('resultmeeting', 'problem_solution')

    # Создаем ENUM-типы
    resultmeetingengagementenum.create(op.get_bind(), checkfirst=True)
    resultmeetingsolutionenum.create(op.get_bind(), checkfirst=True)

    # Добавление новых колонок с ENUM
    op.add_column('resultmeeting',
        sa.Column('participant_engagement', resultmeetingengagementenum, nullable=False)
    )
    op.add_column('resultmeeting',
        sa.Column('problem_solution', resultmeetingsolutionenum, nullable=False)
    )
    # Явное создание последовательности и привязка к id
    op.execute(sa.DDL("CREATE SEQUENCE IF NOT EXISTS resultmeeting_id_seq"))
    op.execute(sa.DDL("""
        ALTER TABLE resultmeeting 
        ALTER COLUMN id 
        SET DEFAULT nextval('resultmeeting_id_seq'::regclass)
    """))


def downgrade():
    #  Удаляем новые колонки
    op.drop_column('resultmeeting', 'participant_engagement')
    op.drop_column('resultmeeting', 'problem_solution')

    # Удаляем ENUM-типы
    resultmeetingengagementenum.drop(op.get_bind(), checkfirst=True)
    resultmeetingsolutionenum.drop(op.get_bind(), checkfirst=True)

    # Восстанавливаем оригинальные boolean-колонки
    op.add_column('resultmeeting',
        sa.Column('participant_engagement', sa.BOOLEAN(), nullable=False)
    )
    op.add_column('resultmeeting',
        sa.Column('problem_solution', sa.BOOLEAN(), nullable=False)
    )
    # Удаление последовательности
    op.execute(sa.DDL("DROP SEQUENCE IF EXISTS resultmeeting_id_seq"))
    op.alter_column(
        "resultmeeting",
        "id",
        server_default=None
    )
    # ### end Alembic commands ###
