from datetime import date

from sqlalchemy import ForeignKey, List, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseTabitModel
from src.models import UserTabit


class Problem(BaseTabitModel):
    """Модель проблемы."""

    problem_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    color_id: Mapped[int] = mapped_column(ForeignKey('colorproblem.id'))
    color: Mapped['ColorProblem'] = relationship(back_populates='problem_color')
    type_id: Mapped[int] = mapped_column(ForeignKey('typeproblem.id'))
    type: Mapped['TypeProblem'] = relationship(back_populates='problem_type')
    owner_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    owner: Mapped['UserTabit'] = relationship(back_populates='problem_owner')
    members: Mapped[List['UserTabit']] = relationship(
        secondary='ProblemUser', back_populates='problem'
    )
    status_id: Mapped[int] = mapped_column(ForeignKey('statusproblem.id'))
    status: Mapped['StatusProblem'] = relationship(back_populates='problem_status')
    confirmation: Mapped['ConfirmationParticipation'] = relationship(
        back_populates='problem_confirmation'
    )
    __table_args__ = UniqueConstraint(('type_id'), ('owner_id'), ('status_id'))
    # TODO добавить поле file, пока не понятно где будет храниться модель.


class ProblemUser(BaseTabitModel):
    """Модель, связывающая пользователя с проблемой."""

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))


class TypeProblem(BaseTabitModel):
    """Модель для типов проблем."""

    type_name: Mapped[str] = mapped_column(unique=True)
    problem: Mapped['Problem'] = relationship(back_populates='type')


class ColorProblem(BaseTabitModel):
    """Модель для цветов проблем."""

    color_name: Mapped[str] = mapped_column(unique=True)
    problem: Mapped[List['Problem']] = relationship(back_populates='color')


class StatusProblem(BaseTabitModel):
    """Модель для статуса проблем."""

    status_name: Mapped[str] = mapped_column(unique=True)
    problem: Mapped[List['Problem']] = relationship(back_populates='status')


class ConfirmationParticipation(BaseTabitModel):
    """Модель для подтверждение участия в проблеме."""

    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='comfirmation')
    user_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    user: Mapped['UserTabit'] = relationship(back_populates='comfirmations')
    status: Mapped[str]
    __table_args__ = UniqueConstraint(
        ('problem_id'),
        ('user_id'),
    )


class Task(BaseTabitModel):
    """Модель задач."""

    task_name: Mapped[str] = mapped_column(unique=True)
    # TODO добавить связь M2O с Meeting
    description: Mapped[str]
    date: Mapped[date]
    owner_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    owner: Mapped['UserTabit'] = relationship(back_populates='task_owner')
    executor_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    executor: Mapped['UserTabit'] = relationship(back_populates='task_executor')
    status_id: Mapped[int] = mapped_column(ForeignKey('statusproblem.id'))
    status: Mapped['StatusTask'] = relationship(back_populates='task_status')
    # TODO добавить поле file, пока не понятно где будет храниться модель.
    __table_args__ = UniqueConstraint(
        ('owner_id'),
    )


class StatusTask(BaseTabitModel):
    """Модель для статусов задач."""

    status_name: Mapped[str] = mapped_column(unique=True)
    task: Mapped[List['Task']] = relationship(back_populates='status')
