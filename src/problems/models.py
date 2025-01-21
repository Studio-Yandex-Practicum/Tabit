from sqlalchemy import Date, Enum, Integer, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.models import BaseTabitModel
from src.problems.schemas import (
    MeetingStatus,
    MeetingResult,
    MeetingProblemSolution,
    MeetingParticipiantEngagement,
)


meeting_members = Table(
    'meeting_members',
    BaseTabitModel.metadata,
    mapped_column('meeting_id', Integer, ForeignKey('meeting.id'), primary_key=True),
    mapped_column('user_id', Integer, ForeignKey('user_tabit.uuid'), primary_key=True),
)


class Meeting(BaseTabitModel):
    """
    Модель для мероприятий.
    """

    __tablename__ = 'meeting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey('user_tabit.uuid'))
    date: Mapped[Date] = mapped_column(Date)
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus), default=MeetingStatus.NEW
    )
    place: Mapped[str | None] = mapped_column(String)
    result: Mapped[str | None] = mapped_column(Integer, ForeignKey('result_meeting.id'))
    transfer_counter: Mapped[int] = mapped_column(Integer, default=0)
    # TODO Реализовать file модель
    file: Mapped[int | None] = mapped_column(Integer, ForeignKey('file_meeting.id'))
    members = relationship(
        'UserTabit', secondary=meeting_members, back_populates='meetings'
    )


class ResultMeeting(BaseTabitModel):
    """
    Модель результаты мероприятия.
    """

    __tablename__ = 'result_meeting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_result: Mapped[MeetingResult] = mapped_column(
        Enum(MeetingResult), default=MeetingResult.GOOD
    )
    participant_engagement: Mapped[MeetingParticipiantEngagement] = mapped_column(
        Enum(MeetingParticipiantEngagement), default=MeetingParticipiantEngagement.YES
    )
    problem_solution: Mapped[MeetingProblemSolution] = mapped_column(
        Enum(MeetingProblemSolution), default=MeetingProblemSolution.YES
    )
    meeting_feedback: Mapped[str] = mapped_column(Text)
