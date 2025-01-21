from sqlalchemy import Boolean, Date, DateTime, Integer, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import BaseFieldName, BaseModel, BaseLinkedTable, BaseTabitModel
# импорт моделей это пока заглушки


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
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey('user_tabit.uuid'))
    date: Mapped[Date] = mapped_column(Date)
    status: Mapped[int] = mapped_column(Integer, ForeignKey('status_meeting.id'))
    place: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(String)
    interest: Mapped[bool] = mapped_column(Boolean, default=False)
    found_solution: Mapped[bool] = mapped_column(Boolean, default=False)
    file: Mapped[int | None] = mapped_column(Integer, ForeignKey('file_meeting.id'))
    comments = relationship('CommentMeeting', back_populates='meeting')
    members = relationship(
        'UserTabit', secondary=meeting_members, back_populates='meetings'
    )


class StatusMeeting(BaseTabitModel):
    """
    Модель статус мероприятия.
    """

    __tablename__ = 'status_meeting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class ResultMeeting(BaseTabitModel):
    """
    Модель результаты мероприятия.
    """

    __tablename__ = 'result_meeting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class CommentMeeting(BaseTabitModel):
    """
    Модель, комментарии к мероприятиям.
    """

    __tablename__ = 'comment_meeting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey('user_tabit.uuid'))
    result: Mapped[int | None] = mapped_column(Integer, ForeignKey('result_meeting.id'))
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey('meeting.id'))
    interest: Mapped[bool] = mapped_column(Boolean, default=False)
    found_solution: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[str] = mapped_column(Text)
    meeting = relationship('Meeting', back_populates='comments')


class Survey(BaseModel):
    """
    Модель для опросов.
    """

    __tablename__ = 'survey'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[int] = mapped_column(Integer, ForeignKey('status_survey.id'))
    result: Mapped[int | None] = mapped_column(Integer, ForeignKey('result_survey.id'))
    created_at: Mapped[DateTime] = mapped_column(DateTime)


class SurveyUser(BaseLinkedTable):
    """
    Модель связи между опросами и пользователями.
    """

    __tablename__ = 'survey_user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('survey.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_tabit.uuid'))


class DateSurvey(BaseModel):
    """
    Модель даты связанные с опросами.
    """

    __tablename__ = 'date_survey'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date)
    survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('survey.id'))


class StatusSurvey(BaseFieldName):
    """
    Модель статуса опроса.
    """

    __tablename__ = 'status_survey'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class ResultSurvey(BaseFieldName):
    """
    Модель, результаты опросов.
    """

    __tablename__ = 'result_survey'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
