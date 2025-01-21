from datetime import date

from sqlalchemy import ForeignKey, List, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseTabitModel
from src.models import UserTabit
from .enums import ConfirmationStatus


class Problem(BaseTabitModel):
    """Модель проблемы."""

    problem_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    color: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str] = mapped_column(unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    owner: Mapped['UserTabit'] = relationship(back_populates='problem_owner')
    members: Mapped[List['UserTabit']] = relationship(
        secondary='ProblemUser', back_populates='problem'
    )
    status: Mapped[str] = mapped_column(unique=True)
    file: Mapped[List['FileProblem']] = relationship(back_populates='problem_files')
    confirmation: Mapped['ConfirmationParticipation'] = relationship(
        back_populates='problem_confirmation'
    )
    __table_args__ = UniqueConstraint(('type_id'), ('owner_id'), ('status_id'))


class ProblemUser(BaseTabitModel):
    """Модель, связывающая пользователя с проблемой."""

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))


class ConfirmationParticipation(BaseTabitModel):
    """Модель для подтверждение участия в проблеме."""

    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='comfirmation')
    user_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    user: Mapped['UserTabit'] = relationship(back_populates='comfirmations')
    status: Mapped['ConfirmationStatus']
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
    status: Mapped[str] = mapped_column(unique=True)
    file: Mapped[List['FileTask']] = relationship(back_populates='task_files')
    __table_args__ = UniqueConstraint(
        ('owner_id'),
    )


class FileProblem(BaseTabitModel):
    """Модель файлов проблем."""

    link: Mapped[str]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='problem_file')


class FileTask(BaseTabitModel):
    """Модель файлов задач."""

    link: Mapped[str]
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped['Task'] = relationship(back_populates='task_file')
