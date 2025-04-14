"""Модели для встреч и результатов встреч."""

from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import (
    BaseTabitModel,
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
    StatusMeeting,
)
from src.models.annotations import (
    description,
    int_pk,
    int_pk_autoincrement,
    int_zero,
    name_problem,
    owner,
)
from src.models.constants import LENGTH_NAME_MEETING_PLACE

if TYPE_CHECKING:
    from src.models import (
        AssociationUserMeeting,
        CompanyUser,
        FileMeeting,
        Problem,
    )


class Meeting(BaseTabitModel):
    """
    Модель встреч.

    Назначение:
        Содержит информацию о назначенных встречах для решения проблемы.

    Поля:
        id: Идентификатор.
        title: Заголовок встречи.
        description: Описание.
        problem_id: Идентификатор проблемы, к которой относится встреча.
        owner_id: Автор встречи. Внешний ключ.
        date_meeting: Дата встречи.
        status: Статус встречи.
        place: Место встречи.
        transfer_counter: Счетчик переносов даты встречи.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        problem - Problem;
        owner - CompanyUser;
        members - AssociationUserMeeting -> CompanyUser: участники встречи;
        result - MeetingResult: связь к анкетам, которые заполняются по завершению встречи;
        file - FileMeeting: к встречи могут быть прикреплены файлы.
    """

    id: Mapped[int_pk]
    title: Mapped[name_problem]
    description: Mapped[description]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='meetings')
    owner_id: Mapped[owner]
    owner: Mapped['CompanyUser'] = relationship(back_populates='meeting_owner')
    date_meeting: Mapped[date] = mapped_column(nullable=False)
    status: Mapped['StatusMeeting']
    place: Mapped[str] = mapped_column(String(LENGTH_NAME_MEETING_PLACE), nullable=False)
    members: Mapped[List['AssociationUserMeeting']] = relationship(
        back_populates='meeting',
        cascade='all, delete-orphan',
        viewonly=True,
        lazy='joined',
    )
    result: Mapped['MeetingResult'] = relationship(
        back_populates='meeting', cascade='all, delete-orphan'
    )
    transfer_counter: Mapped[int_zero]
    file: Mapped[List['FileMeeting']] = relationship(
        back_populates='meeting', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'title={self.title!r}, '
            f'problem_id={self.problem_id!r}, '
            f'status={self.status!r})'
        )


class MeetingResult(BaseTabitModel):
    """
    Модель результатов встреч.

    Назначение:
        Содержит информацию заполненную в анкеты, заполняемые по завершению встречи.

    Поля:
        id: Идентификатор.
        meeting_id: Идентификатор встречи, к которой относится анкета.
        owner_id: Автор встречи. Внешний ключ.
        meeting_result: Как прошла встреча.
        participant_engagement: Заинтересованность участников.
        problem_solution: Удалось ли решить проблему.
        meeting_feedback: Комментарий к встрече.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        meeting - Meeting;
        owner - CompanyUser.
    """

    id: Mapped[int_pk_autoincrement]
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'), primary_key=True)
    meeting: Mapped['Meeting'] = relationship(back_populates='result', lazy='joined')
    owner_id: Mapped[owner]
    owner: Mapped['CompanyUser'] = relationship(back_populates='meeting_result')
    meeting_result: Mapped['MeetingResultEnum']
    participant_engagement: Mapped['MeetingResultEngagementEnum'] = mapped_column(
        Enum(MeetingResultEngagementEnum, name='resultmeetingengagementenum'),
    )
    problem_solution: Mapped['MeetingResultSolutionEnum'] = mapped_column(
        Enum(MeetingResultSolutionEnum, name='resultmeetingsolutionenum'),
    )
    meeting_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'owner_id={self.owner_id!r}, '
            f'meeting_id={self.meeting_id!r})'
        )
