"""Модели для связных таблиц."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTabitModel

if TYPE_CHECKING:
    from src.models import CompanyUser, Meeting, Problem, Task, UserTag


class AssociationUserProblem(BaseTabitModel):
    """
    Связная таблица CompanyUser и Problem, для поля members таблицы Problem.

    Назначение:
        Обеспечить связь Many to Many между двумя другими таблицами.

    Поля:
        left_id: FK, ссылается на пользователя, часть составного PK.
        right_id: FK, ссылается на проблему, часть составного PK.
        status: bool - принял ли пользователь приглашение к решению проблемы.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser;
        problem - Problem.
    """

    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        primary_key=True,
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('problem.id', ondelete='CASCADE'),
        primary_key=True,
    )
    user: Mapped['CompanyUser'] = relationship(back_populates='problems')
    problem: Mapped['Problem'] = relationship(back_populates='members')
    status: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'status={self.status!r}, '
            f'user id {self.left_id!r} <-> problem id {self.right_id!r})'
        )


class AssociationUserMeeting(BaseTabitModel):
    """
    Связная таблица CompanyUser и Meeting, для поля members таблицы Meeting.

    Поля:
        left_id: FK, ссылается на пользователя, часть составного PK.
        right_id: FK, ссылается на встречу, часть составного PK.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser;
        meeting - Meeting.
    """

    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        primary_key=True,
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('meeting.id', ondelete='CASCADE'),
        primary_key=True,
    )
    user: Mapped['CompanyUser'] = relationship(back_populates='meetings')
    meeting: Mapped['Meeting'] = relationship(back_populates='members')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(user id {self.left_id!r} <-> meeting id {self.right_id!r})'
        )


class AssociationUserTask(BaseTabitModel):
    """
    Связная таблица CompanyUser и Task, для поля executors таблицы Task.

    Поля:
        left_id: FK, ссылается на пользователя, часть составного PK.
        right_id: FK, ссылается на задачу, часть составного PK.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser;
        task - Task.
    """

    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        primary_key=True,
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('task.id', ondelete='CASCADE'),
        primary_key=True,
    )
    user: Mapped['CompanyUser'] = relationship(back_populates='tasks')
    task: Mapped['Task'] = relationship(back_populates='executors')

    def __repr__(self):
        return f'{self.__class__.__name__}(user id {self.left_id!r} <-> task id {self.right_id!r})'


class AssociationUserComment(BaseTabitModel):
    """
    Связная таблица CompanyUser и CommentFeed для учёта лайков.

    Поля:
        left_id: FK, ссылается на пользователя, часть составного PK.
        right_id: FK, ссылается на комментарий, часть составного PK.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser;
    """

    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        primary_key=True,
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('commentfeed.id', ondelete='CASCADE'),
        primary_key=True,
    )
    user: Mapped['CompanyUser'] = relationship(back_populates='comments_likes')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(user id {self.left_id!r} <-> comment id {self.right_id!r})'
        )


class AssociationUserTag(BaseTabitModel):
    """
    Связная таблица CompanyUser и Tag.

    Назначение:
        Обеспечить связь Many to Many между двумя другими таблицами.

    Поля:
        left_id: FK, ссылается на пользователя, часть составного PK.
        right_id: FK, ссылается на комментарий, часть составного PK.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser;
        tag - UserTag.
    """

    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        primary_key=True,
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('usertag.id', ondelete='CASCADE'),
        primary_key=True,
    )
    user: Mapped['CompanyUser'] = relationship(back_populates='tags')
    tag: Mapped['UserTag'] = relationship(back_populates='user')

    def __repr__(self):
        return f'{self.__class__.__name__}(user id {self.left_id!r} <-> tag id {self.right_id!r})'
