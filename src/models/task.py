"""Модели для задач."""

from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTabitModel, TaskStatus
from src.models.annotations import description, int_pk, int_zero, name_problem, owner

if TYPE_CHECKING:
    from src.models import AssociationUserTask, CompanyUser, FileTask, Problem


class Task(BaseTabitModel):
    """
    Модель задач.

    Назначение:
        Содержит информацию о установленных задач для решения проблемы.

    Поля:
        id: Идентификатор.
        name: Название задачи.
        description: Описание.
        date_completion: Крайняя дата исполнения задачи.
        owner_id: Автор задачи. Внешний ключ.
        problem_id: Идентификатор проблемы, к которой относится задача.
        status: Статус выполнения задачи.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
        transfer_counter: Счетчик переносов даты решения задач.

    Связи (атрибут - Модель):
        owner - CompanyUser;
        problem - Problem;
        executors - AssociationUserTask -> CompanyUser: исполнители задачи;
        file - FileTask: к задаче могут быть прикреплены файлы.
    """

    id: Mapped[int_pk]
    name: Mapped[name_problem]
    description: Mapped[description]
    date_completion: Mapped[date] = mapped_column(nullable=False)
    owner_id: Mapped[owner]
    owner: Mapped['CompanyUser'] = relationship(back_populates='task_owner')
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id', ondelete='CASCADE'))
    problem: Mapped['Problem'] = relationship(back_populates='tasks')
    executors: Mapped[List['AssociationUserTask']] = relationship(
        back_populates='task',
        cascade='all, delete-orphan',
        viewonly=True,
        lazy='joined',
    )
    status: Mapped['TaskStatus']
    transfer_counter: Mapped[int_zero]
    file: Mapped[List['FileTask']] = relationship(
        back_populates='task', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'owner_id={self.owner_id!r}, '
            f'status={self.status!r})'
        )
