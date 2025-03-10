from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import LENGTH_NAME_MEETING_PLACE
from src.database.annotations import description, int_pk, int_zero, name_problem, owner
from src.database.models import BaseTabitModel
from src.problems.models.enums import ResultMeetingEnum, StatusMeeting

if TYPE_CHECKING:
    from src.problems.models import AssociationUserMeeting, FileMeeting, Problem
    from src.users.models import UserTabit


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
        owner - UserTabit;
        members - AssociationUserMeeting -> UserTabit: участники встречи;
        result - ResultMeeting: связь к анкетам, которые заполняются по завершению встречи;
        file - FileMeeting: к встречи могут быть прикреплены файлы.
    """

    id: Mapped[int_pk]
    title: Mapped[name_problem]
    description: Mapped[description]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='meetings')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='meeting_owner')
    date_meeting: Mapped[date] = mapped_column(nullable=False)
    status: Mapped['StatusMeeting']
    place: Mapped[str] = mapped_column(String(LENGTH_NAME_MEETING_PLACE), nullable=False)
    members: Mapped[List['AssociationUserMeeting']] = relationship(
        back_populates='meeting', cascade='all, delete-orphan'
    )
    result: Mapped['ResultMeeting'] = relationship(
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


class ResultMeeting(BaseTabitModel):
    """
    Модель результатов встреч.

    Назначение:
        Содержит информацию заполненную в анкеты, заполняемые по завершению встречи.

    Поля:
        id: Идентификатор.
        meeting_id: Идентификатор встречи, к которой относится анкета.
        owner_id: Автор встречи. Внешний ключ.
        meeting_result: Как прошла встреча.
        participant_engagement: bool - Заинтересовала ли встреча.
        problem_solution: bool - Удалось ли решить проблему.
        meeting_feedback: Комментарий к встрече.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        meeting - Meeting;
        owner - UserTabit.
    """

    id: Mapped[int_pk]
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'), primary_key=True)
    meeting: Mapped['Meeting'] = relationship(back_populates='result')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='meeting_result')
    meeting_result: Mapped['ResultMeetingEnum']
    participant_engagement: Mapped[bool] = mapped_column(nullable=False)
    problem_solution: Mapped[bool] = mapped_column(nullable=False)
    meeting_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'owner_id={self.owner_id!r}, '
            f'meeting_id={self.meeting_id!r})'
        )
