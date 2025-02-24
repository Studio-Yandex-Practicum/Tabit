from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.annotations import int_pk
from src.models import BaseTabitModel, TagUser

if TYPE_CHECKING:
    from src.models import Meeting, Problem, Task, UserTabit


class AssociationUserProblem(BaseTabitModel):
    """
    Связная таблица UserTabit и Problem, для поля members таблицы Problem.

    Назначение:
        Обеспечить связь Many to Many между двумя другими таблицами.

    Поля:
        id: Идентификатор.
        left_id: Внешний ключ первой таблицы.
        right_id: Внешний ключ второй таблицы.
        status: bool - принял ли пользователь приглашение к решению проблемы.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - UserTabit;
        problem - Problem.
    """

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('problem.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='problems')
    problem: Mapped['Problem'] = relationship(back_populates='members')
    status: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'status={self.status!r}, '
            f'user id {self.left_id!r} <-> problem id {self.right_id!r})'
        )


class AssociationUserMeeting(BaseTabitModel):
    """
    Связная таблица UserTabit и Meeting, для поля members таблицы Meeting.

    Поля:
        id: Идентификатор.
        left_id: Внешний ключ первой таблицы.
        right_id: Внешний ключ второй таблицы.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - UserTabit;
        meeting - Meeting.
    """

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='meetings')
    meeting: Mapped['Meeting'] = relationship(back_populates='members')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user id {self.left_id!r} <-> meeting id {self.right_id!r})'
        )


class AssociationUserTask(BaseTabitModel):
    """
    Связная таблица UserTabit и Task, для поля executors таблицы Task.

    Поля:
        id: Идентификатор.
        left_id: Внешний ключ первой таблицы.
        right_id: Внешний ключ второй таблицы.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - UserTabit;
        task - Task.
    """

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('task.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='tasks')
    task: Mapped['Task'] = relationship(back_populates='executors')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user id {self.left_id!r} <-> task id {self.right_id!r})'
        )


class AssociationUserTags(BaseTabitModel):
    """
    Связная таблица UserTabit и Tag.

    Назначение:
        Обеспечить связь Many to Many между двумя другими таблицами.

    Поля:
        id: Идентификатор.
        left_id: Внешний ключ первой таблицы.
        right_id: Внешний ключ второй таблицы.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - UserTabit;
        tag - TagUser.
    """

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('taguser.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='tags')
    tag: Mapped['TagUser'] = relationship(back_populates='user')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user id {self.left_id!r} <-> tag id {self.right_id!r})'
        )
