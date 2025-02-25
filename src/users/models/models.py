from datetime import date
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import UniqueConstraint

from src.constants import LENGTH_TELEGRAM_USERNAME
from src.database.annotations import int_pk, url_link_field
from src.database.models import BaseTabitModel, BaseTag, BaseUser
from src.users.models.enum import RoleUserTabit

if TYPE_CHECKING:
    from src.companies.models import Company, Department
    from src.problems.models import (
        AssociationUserMeeting,
        AssociationUserProblem,
        AssociationUserTask,
        CommentFeed,
        Meeting,
        MessageFeed,
        Problem,
        ResultMeeting,
        Task,
        VotingByUser,
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


class TagUser(BaseTag):
    """
    Модель тэгов пользователей.

    Назначение:
        Админ от компании может для сотрудников своей компании придумывать свои тэги.

    Поля:
        id: Идентификационный номер тэга.
        name: Имя тега.
        company_id: Идентификатор компании, в которой будет использоваться тэг.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - AssociationUserTags -> UserTabit;
        company - Company.
    """

    user: Mapped[List['AssociationUserTags']] = relationship(back_populates='tag')
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='tags_users')


class UserTabit(BaseUser):
    """
    Модель пользователей ресурс Tabit.

    Назначение:
        Модель описывает таблицу, в которой будут хранится пользователи-сотрудники компаний.

    Поля:
        id: Идентификационный номер пользователя - UUID.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        birthday: День рождение пользователя.
        telegram_username: Имя пользователя в Telegram.
        role: Роль пользователя компании.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        start_date_employment: Дата начало работы сотрудника в компании.
        end_date_employment: Дата конца работы сотрудника в компании.
        hashed_password: Хэш пароля пользователя.
        is_active: bool - активен ли пользователь.
        is_superuser: bool - суперюзер ли пользователь.
        is_verified: bool - проверен ли пользователь.
        avatar_link: Ссылка на аватар пользователя.
        company_id: id компании, в которой работает пользователь.
        supervisor: начальник отдела, за которым закреплен (может быть True или None);
        current_department_id: id отдела, в котором работает пользователь.
        last_department_id: id отдела, в котором работал пользователь до этого.
        department_transition_date: Последняя дата перехода из одного отдела в другой.
        employee_position: Позиция в коллективе, указывается админом компании.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        tags - AssociationUserTags -> TagUser;
        company - Company;
        current_department - Department;
        last_department - Department;
        problem_owner - Problem: автором каких проблем является;
        problems - AssociationUserProblem -> Problem: участником решения каких проблем является;
        meeting_owner - Meeting: инициатором каких встреч является;
        meetings - AssociationUserMeeting -> Meeting: в каких встречах участвует;
        meeting_result - ResultMeeting: после встречи можно заполнить анкету - автор какой анкеты;
        task_owner - Task: автором какой задачи является;
        tasks - AssociationUserTask -> Task: ответственным за решения каких задач является;
        messages - MessageFeed: автором каких сообщений является;
        comments - CommentFeed: автором каких комментариев к сообщениям является;
        voting_by - VotingByUser: связь с выбранными вариантами голосования в сообщениях.
    """

    birthday: Mapped[Optional[date]]
    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(LENGTH_TELEGRAM_USERNAME), unique=True, nullable=True
    )
    role: Mapped['RoleUserTabit']
    start_date_employment: Mapped[Optional[date]]
    end_date_employment: Mapped[Optional[date]]
    tags: Mapped[List['AssociationUserTags']] = relationship(back_populates='user')

    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='employees')

    supervisor: Mapped[Optional[bool]] = mapped_column(default=None)

    current_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('department.id'), nullable=True
    )
    current_department: Mapped[Optional['Department']] = relationship(
        # back_populates='employees',
        foreign_keys=[current_department_id],
    )
    last_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('department.id'), nullable=True
    )
    last_department: Mapped[Optional['Department']] = relationship(
        # back_populates='employees_lost',
        foreign_keys=[last_department_id],
    )

    problem_owner: Mapped[List['Problem']] = relationship(back_populates='owner')
    problems: Mapped[List['AssociationUserProblem']] = relationship(back_populates='user')
    meeting_owner: Mapped[List['Meeting']] = relationship(back_populates='owner')
    meetings: Mapped[List['AssociationUserMeeting']] = relationship(back_populates='user')
    meeting_result: Mapped['ResultMeeting'] = relationship(back_populates='owner')
    task_owner: Mapped['Task'] = relationship(back_populates='owner')
    tasks: Mapped[List['AssociationUserTask']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    messages: Mapped[List['MessageFeed']] = relationship(back_populates='owner')
    comments: Mapped[List['CommentFeed']] = relationship(back_populates='owner')
    voting_by: Mapped[List['VotingByUser']] = relationship(back_populates='user')

    department_transition_date: Mapped[Optional[date]]
    employee_position: Mapped[Optional[str]]
    avatar_link: Mapped[url_link_field]

    __table_args__ = (
        UniqueConstraint('supervisor', 'current_department_id', name='unique_supervisor'),
    )

    # TODO: На уровне базы запретить ставить is_superuser = True.
