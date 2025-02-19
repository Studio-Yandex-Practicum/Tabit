from datetime import date
from typing import List, TYPE_CHECKING
# from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import description, int_pk, int_zero, owner, name_problem
from src.database.models import BaseTabitModel
from src.problems.models.enums import StatusTask

if TYPE_CHECKING:
    from src.problems.models import AssociationUserTask, FileTask, Problem
    from src.users.models import UserTabit


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

    Связи (атрибут - Модель):
        owner - UserTabit;
        problem - Problem;
        executors - AssociationUserTask -> UserTabit: исполнители задачи;
        file - FileTask: к задаче могут быть прикреплены файлы.

        Добавлено поле transfer_counter
    """

    id: Mapped[int_pk]
    name: Mapped[name_problem]
    description: Mapped[description]
    date_completion: Mapped[date] = mapped_column(nullable=False)
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='task_owner')
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'), primary_key=True)
    problem: Mapped['Problem'] = relationship(back_populates='tasks')
    executors: Mapped[List['AssociationUserTask']] = relationship(back_populates='task')
    status: Mapped['StatusTask']
    transfer_counter: Mapped[int_zero]  # Добавлено поле transfer_counter
    file: Mapped[List['FileTask']] = relationship(
        back_populates='task', cascade='all, delete-orphan'
    )

    # @property
    # def executor_ids(self) -> List[UUID]:
    #     return [executor.left_id for executor in self.executors]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'owner_id={self.owner_id!r}, '
            f'status={self.status!r})'
        )
