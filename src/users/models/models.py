from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import LENGTH_TELEGRAM_USERNAME
from src.models import BaseTabitModel, BaseTag, BaseUser, int_pk, url_link_field
from src.users.models.enum import RoleUserTabit


class AssociationUserTags(BaseTabitModel):
    """Связная таблица UserTabit и Tag."""

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('taguser.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='tags')
    tag: Mapped['TagUser'] = relationship(back_populates='user')


class TagUser(BaseTag):
    """Модель тэгов пользователей."""

    # TODO: Задумывалось, что админы компаний будут заводить свои теги сами. Нужно ввести
    # распределение по компаниям, чтоб не было "каши".
    user: Mapped[List['AssociationUserTags']] = relationship(back_populates='tag')


class UserTabit(BaseUser):
    """Модель пользователей ресурс Tabit."""

    birthday: Mapped[date]
    telegram_username: Mapped[str] = mapped_column(String(LENGTH_TELEGRAM_USERNAME), unique=True)
    role: Mapped['RoleUserTabit']
    start_date_employment: Mapped[date]
    end_date_employment: Mapped[date]
    tags: Mapped[List['AssociationUserTags']] = relationship(back_populates='user')

    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='employees')  # noqa: F821

    current_department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    current_department: Mapped['Department'] = relationship(  # noqa: F821
        back_populates='employees'
    )
    last_department_id: Mapped[Optional[int]] = mapped_column(ForeignKey('department.id'))
    last_department: Mapped['Department'] = relationship(  # noqa: F821
        back_populates='employees_lost'
    )
    supervisor: Mapped['Department'] = relationship(back_populates='supervisor')  # noqa: F821

    problem_owner: Mapped[List['Problem']] = relationship(back_populates='owner')  # noqa: F821
    problems: Mapped[List['AssociationUserProblem']] = relationship(  # noqa: F821
        back_populates='user'
    )
    meeting_owner: Mapped[List['Meeting']] = relationship(back_populates='owner')  # noqa: F821
    meetings: Mapped[List['AssociationUserMeeting']] = relationship(  # noqa: F821
        back_populates='user'
    )
    meeting_result: Mapped['ResultMeeting'] = relationship(back_populates='owner')  # noqa: F821
    tasks: Mapped[List['AssociationUserTask']] = relationship(back_populates='user')  # noqa: F821
    message: Mapped['MessageFeed'] = relationship(back_populates='owner')  # noqa: F821
    comment: Mapped['CommentFeed'] = relationship(back_populates='owner')  # noqa: F821
    voting_by: Mapped['VotingByUser'] = relationship(back_populates='user')  # noqa: F821

    department_transition_date: Mapped[date]
    employee_position: Mapped[str]
    avatar_link: Mapped[url_link_field]
