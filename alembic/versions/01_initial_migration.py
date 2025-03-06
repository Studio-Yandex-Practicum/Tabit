"""initial migration

Revision ID: 01
Revises:
Create Date: 2025-03-06 13:12:00.748127

"""
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('landingpage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number_1', sa.String(), nullable=True),
    sa.Column('phone_number_2', sa.String(), nullable=True),
    sa.Column('phone_number_3', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('whatsapp', sa.String(), nullable=True),
    sa.Column('telegram', sa.String(), nullable=True),
    sa.Column('vk', sa.String(), nullable=True),
    sa.Column('price_1', sa.String(), nullable=True),
    sa.Column('price_2', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('licensetype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('license_term', sa.Interval(), nullable=False),
    sa.Column('max_admins_count', sa.Integer(), nullable=False),
    sa.Column('max_employees_count', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tabitadminuser',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('patronymic', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tabitadminuser_email'), 'tabitadminuser', ['email'], unique=True)
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo', sa.String(length=2048), nullable=True),
    sa.Column('license_id', sa.Integer(), nullable=True),
    sa.Column('max_admins_count', sa.Integer(), nullable=False),
    sa.Column('max_employees_count', sa.Integer(), nullable=False),
    sa.Column('start_license_time', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('end_license_time', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('slug', sa.String(length=25), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['license_id'], ['licensetype.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('department',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(length=25), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'name', name='uq_company_department_name'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('taguser',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('usertabit',
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('telegram_username', sa.String(length=100), nullable=True),
    sa.Column('role', sa.Enum('ADMIN', 'EMPLOYEE', name='roleusertabit'), nullable=False),
    sa.Column('start_date_employment', sa.Date(), nullable=True),
    sa.Column('end_date_employment', sa.Date(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('supervisor', sa.Boolean(), nullable=True),
    sa.Column('current_department_id', sa.Integer(), nullable=True),
    sa.Column('last_department_id', sa.Integer(), nullable=True),
    sa.Column('department_transition_date', sa.Date(), nullable=True),
    sa.Column('employee_position', sa.String(), nullable=True),
    sa.Column('avatar_link', sa.String(length=2048), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('patronymic', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['current_department_id'], ['department.id'], ),
    sa.ForeignKeyConstraint(['last_department_id'], ['department.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('supervisor', 'current_department_id', name='unique_supervisor'),
    sa.UniqueConstraint('telegram_username')
    )
    op.create_index(op.f('ix_usertabit_email'), 'usertabit', ['email'], unique=True)
    op.create_table('associationusertags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('left_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['taguser.id'], ),
    sa.PrimaryKeyConstraint('id', 'left_id', 'right_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('problem',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('color', sa.Enum('RED', 'ORANGE', 'YELLOW', 'GREEN', 'BLUE', 'DARK_BLUE', 'VIOLET', 'BROWN', 'GRAY', 'BLACK', 'WHITE', 'PINK', 'BEIGE', 'VINOUS', 'PURPLE', name='colorproblem'), nullable=False),
    sa.Column('type', sa.Enum('A', 'B', 'C', 'D', 'E', 'F', 'G', name='typeproblem'), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'SUSPENDED', 'COMPLETED', name='statusproblem'), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('associationuserproblem',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('left_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['problem.id'], ),
    sa.PrimaryKeyConstraint('id', 'left_id', 'right_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('fileproblem',
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=2048), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('meeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('date_meeting', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'NOT_HELD', 'HELD', 'SUSPENDED', name='statusmeeting'), nullable=False),
    sa.Column('place', sa.String(length=255), nullable=False),
    sa.Column('transfer_counter', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('messagefeed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('important', sa.Boolean(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date_completion', sa.Date(), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'NOT_ACCEPTED', 'COMPLETED', name='statustask'), nullable=False),
    sa.Column('transfer_counter', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('associationusermeeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('left_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['meeting.id'], ),
    sa.PrimaryKeyConstraint('id', 'left_id', 'right_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('associationusertask',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('left_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['usertabit.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['right_id'], ['task.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('commentfeed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messagefeed.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('filemeeting',
    sa.Column('meeting_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=2048), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('filemessage',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=2048), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messagefeed.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('filetask',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=2048), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('resultmeeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meeting_id', sa.Integer(), nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('meeting_result', sa.Enum('EXCELLENT', 'GOOD', 'BADLY', 'DISGUSTING', name='resultmeetingenum'), nullable=False),
    sa.Column('participant_engagement', sa.Boolean(), nullable=False),
    sa.Column('problem_solution', sa.Boolean(), nullable=False),
    sa.Column('meeting_feedback', sa.Text(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['usertabit.id'], ),
    sa.PrimaryKeyConstraint('id', 'meeting_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('votingfeed',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messagefeed.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('associationusercomment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('left_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['commentfeed.id'], ),
    sa.PrimaryKeyConstraint('id', 'left_id', 'right_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('votingbyuser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('voting_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['usertabit.id'], ),
    sa.ForeignKeyConstraint(['voting_id'], ['votingfeed.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votingbyuser')
    op.drop_table('associationusercomment')
    op.drop_table('votingfeed')
    op.drop_table('resultmeeting')
    op.drop_table('filetask')
    op.drop_table('filemessage')
    op.drop_table('filemeeting')
    op.drop_table('commentfeed')
    op.drop_table('associationusertask')
    op.drop_table('associationusermeeting')
    op.drop_table('task')
    op.drop_table('messagefeed')
    op.drop_table('meeting')
    op.drop_table('fileproblem')
    op.drop_table('associationuserproblem')
    op.drop_table('problem')
    op.drop_table('associationusertags')
    op.drop_index(op.f('ix_usertabit_email'), table_name='usertabit')
    op.drop_table('usertabit')
    op.drop_table('taguser')
    op.drop_table('department')
    op.drop_table('company')
    op.drop_index(op.f('ix_tabitadminuser_email'), table_name='tabitadminuser')
    op.drop_table('tabitadminuser')
    op.drop_table('licensetype')
    op.drop_table('landingpage')
    # ### end Alembic commands ###
