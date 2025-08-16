"""Add sociometric tables

Revision ID: 05_add_sociometric_tables
Revises: 04
Create Date: 2025-08-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '05_add_sociometric_tables'
down_revision: Union[str, None] = '04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # enums
    op.execute("CREATE TYPE choicetype AS ENUM ('positive', 'negative', 'neutral')")
    op.execute("CREATE TYPE sociometriccategory AS ENUM ('tactical_leadership', 'strategic_leadership')")

    # sociometriccriterion
    op.create_table(
        'sociometriccriterion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('choice_type', postgresql.ENUM('positive', 'negative', 'neutral', name='choicetype'), nullable=False),
        sa.Column('max_choices', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category', postgresql.ENUM('tactical_leadership', 'strategic_leadership', name='sociometriccategory'), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    # sociometricchoice
    op.create_table(
        'sociometricchoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chosen_employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criterion_id', sa.Integer(), nullable=False),
        sa.Column('cycle_user_id', sa.Integer(), nullable=False),
        sa.Column('preference_rank', sa.Integer(), nullable=True),
        sa.Column('choice_type', postgresql.ENUM('positive', 'negative', 'neutral', name='choicetype'), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['criterion_id'], ['sociometriccriterion.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cycle_user_id'], ['surveycycleforuser.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['companyuser.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chosen_employee_id'], ['companyuser.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    # indices
    op.create_index('ix_sociometriccriterion_company_id', 'sociometriccriterion', ['company_id'])
    op.create_index('ix_sociometricchoice_cycle_user_id', 'sociometricchoice', ['cycle_user_id'])
    op.create_index('ix_sociometricchoice_participant_id', 'sociometricchoice', ['participant_id'])
    op.create_index('ix_sociometricchoice_criterion_id', 'sociometricchoice', ['criterion_id'])

    # strategy preferences
    op.create_table(
        'sociometricstrategypreference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cycle_user_id', sa.Integer(), nullable=False),
        sa.Column('strategy', sa.String(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cycle_user_id'], ['surveycycleforuser.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('sociometricstrategypreference')
    op.drop_index('ix_sociometricchoice_criterion_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometricchoice_participant_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometricchoice_cycle_user_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometriccriterion_company_id', table_name='sociometriccriterion')

    op.drop_table('sociometricchoice')
    op.drop_table('sociometriccriterion')

    op.execute("DROP TYPE sociometriccategory")
    op.execute("DROP TYPE choicetype")
