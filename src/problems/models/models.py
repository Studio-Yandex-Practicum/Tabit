from datetime import date
from typing import Annotated, List
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseFileLink, BaseTabitModel, BaseTag, description, int_pk, owner, int_zero
from src.problems.models.enums import (
    ColorProblem,
    StatusMeeting,
    StatusTask,
    StatusProblem,
    TypeProblem,
    ResultMeetingEnum,
)
from src.constants import LENGTH_NAME_PROBLEM, LENGTH_NAME_MEETING_PLACE

name_problem = Annotated[str, mapped_column(String(LENGTH_NAME_PROBLEM), nullable=False)]


class AssociationUserProblem(BaseTabitModel):
    """Связная таблица UserTabit и Problem, для поля members таблицы Problem."""

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('problem.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='problems')  # noqa: F821
    problem: Mapped['Problem'] = relationship(back_populates='members')
    status: Mapped[bool] = mapped_column(default=False)


class AssociationUserMeeting(BaseTabitModel):
    """Связная таблица UserTabit и Meeting, для поля members таблицы Meeting."""

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='meetings')  # noqa: F821
    meeting: Mapped['Meeting'] = relationship(back_populates='members')


class AssociationUserTask(BaseTabitModel):
    """Связная таблица UserTabit и Task, для поля executors таблицы Task."""

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(ForeignKey('usertabit.id'), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey('task.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='tasks')  # noqa: F821
    task: Mapped['Task'] = relationship(back_populates='executors')


class Problem(BaseTabitModel):
    """Модель проблемы."""

    id: Mapped[int_pk]
    name: Mapped[name_problem]
    description: Mapped[description]
    color: Mapped['ColorProblem']
    type: Mapped['TypeProblem']
    status: Mapped['StatusProblem']
    # TODO: Не думаю, что нужно удалять проблему, если будет удален пользователь, создавший её.
    # Но вот если удалят компанию - должна удалятся. Сложно.
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='problem_owner')  # noqa: F821
    members: Mapped[List['AssociationUserProblem']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    meetings: Mapped[List['Meeting']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    tasks: Mapped[List['Task']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    messages: Mapped[List['MessageFeed']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    file: Mapped[List['FileProblem']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )


class Meeting(BaseTabitModel):
    """Модель встреч."""

    id: Mapped[int_pk]
    title: Mapped[name_problem]
    description: Mapped[description]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'), primary_key=True)
    problem: Mapped['Problem'] = relationship(back_populates='meetings')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='meeting_owner')  # noqa: F821
    date_meeting: Mapped[date] = mapped_column(nullable=False)
    status: Mapped['StatusMeeting']
    place: Mapped[str] = mapped_column(String(LENGTH_NAME_MEETING_PLACE), nullable=False)
    members: Mapped[List['AssociationUserMeeting']] = relationship(
        back_populates='meeting', cascade='all, delete-orphan'
    )
    result: Mapped['ResultMeeting'] = relationship(
        back_populates='meering', cascade='all, delete-orphan'
    )
    transger_counter: Mapped[int_zero]
    file: Mapped[List['FileMeeting']] = relationship(
        back_populates='meeting', cascade='all, delete-orphan'
    )


class ResultMeeting(BaseTabitModel):
    """Модель результатов встреч."""

    id: Mapped[int_pk]
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'), primary_key=True)
    meeting: Mapped['Meeting'] = relationship(back_populates='result')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='meeting_result')  # noqa: F821
    meeting_result: Mapped['ResultMeetingEnum']
    participant_engagement: Mapped[bool] = mapped_column(nullable=False)
    problem_solution: Mapped[bool] = mapped_column(nullable=False)
    meeting_feedback: Mapped[str] = mapped_column(Text, nullable=True)


class Task(BaseTabitModel):
    """Модель задач."""

    id: Mapped[int_pk]
    name: Mapped[name_problem]
    description: Mapped[description]
    date_completion: Mapped[date] = mapped_column(nullable=False)
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='task')  # noqa: F821
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'), primary_key=True)
    problem: Mapped['Problem'] = relationship(back_populates='tasks')
    executors: Mapped[List['AssociationUserTask']] = relationship(back_populates='task')
    status: Mapped['StatusTask']
    file: Mapped[List['FileTask']] = relationship(
        back_populates='task', cascade='all, delete-orphan'
    )


class MessageFeed(BaseTabitModel):
    """Модель ленты сообщений к проблеме."""

    id: Mapped[int_pk]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='messages')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='message')  # noqa: F821
    text: Mapped[str]
    important: Mapped[bool] = mapped_column(default=False)
    comments: Mapped[List['CommentFeed']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )
    voting: Mapped[List['VotingFeed']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )
    file: Mapped[List['FileMessage']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )


class CommentFeed(BaseTabitModel):
    """Модель комментариев к сообщению, оставленного к проблеме."""

    id: Mapped[int_pk]
    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='comments')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='comment')  # noqa: F821
    text: Mapped[str]


class VotingFeed(BaseTag):
    """Модель вариантов голосований в сообщениях, оставленных к проблеме."""

    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='voting')
    by_user: Mapped['VotingByUser'] = relationship(
        back_populates='voting', cascade='all, delete-orphan'
    )


class VotingByUser(BaseTabitModel):
    """
    Модель выборов  пользователями вариантов голосований в сообщениях, оставленных к проблеме.
    """

    id: Mapped[int_pk]
    user_id: Mapped[owner]
    user: Mapped['UserTabit'] = relationship(back_populates='voting_by')  # noqa: F821
    voting_id: Mapped[int] = mapped_column(ForeignKey('votingfeed.id'))
    voting: Mapped['VotingFeed'] = relationship(back_populates='by_user')


class FileProblem(BaseFileLink):
    """Модель хранения ссылок на файлы проблем."""

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='file')


class FileMeeting(BaseFileLink):
    """Модель хранения ссылок на файлы встреч."""

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'))
    meeting: Mapped['Meeting'] = relationship(back_populates='file')


class FileTask(BaseFileLink):
    """Модель хранения ссылок на файлы задач."""

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped['Task'] = relationship(back_populates='file')


class FileMessage(BaseFileLink):
    """Модель хранения ссылок на файлы сообщений."""

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='file')
