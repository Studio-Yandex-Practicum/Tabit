from sqlalchemy import (Boolean,
                        Date,
                        DateTime,
                        Integer,
                        ForeignKey,
                        String,
                        Table,
                        Text)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import BaseFieldName, BaseModel, BaseLinkedTable, BaseTabitModel

# Таблица для связи Meeting и UserTabit (members)
meeting_members = Table(
    "meeting_members",
    BaseModel.metadata,
    mapped_column("meeting_id",
                  Integer, ForeignKey("meeting.id"),
                  primary_key=True),
    mapped_column("user_id", Integer,
                  ForeignKey("user_tabit.uuid"),
                  primary_key=True)
)


class Meeting(BaseTabitModel):
    """
    Модель для мероприятий.
    """
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)
    description: Mapped[str | None] = mapped_column(Text,
                                                    nullable=True)
    owner: Mapped[int] = mapped_column(Integer,
                                       ForeignKey("user_tabit.uuid"),
                                       nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[int] = mapped_column(Integer,
                                        ForeignKey("status_meeting.id"),
                                        nullable=False)
    place: Mapped[str | None] = mapped_column(Text,
                                              nullable=True)
    result: Mapped[str | None] = mapped_column(String,
                                               nullable=True)
    interest: Mapped[bool] = mapped_column(Boolean,
                                           default=False)
    found_solution: Mapped[bool] = mapped_column(Boolean,
                                                 default=False)
    file: Mapped[int | None] = mapped_column(Integer,
                                             ForeignKey("file_meeting.id"),
                                             nullable=True)
    comments = relationship("CommentMeeting",
                            back_populates="meeting")
    messages = relationship("MessageMeeting",
                            back_populates="meeting")
    members = relationship("UserTabit",
                           secondary=meeting_members,
                           back_populates="meetings")


class StatusMeeting(BaseTabitModel):
    """
    Модель статус мероприятия.
    """
    __tablename__ = "status_meeting"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)


class ResultMeeting(BaseTabitModel):
    """
    Модель результаты мероприятия.
    """
    __tablename__ = "result_meeting"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)


class CommentMeeting(BaseTabitModel):
    """
    Модель, комментарии к мероприятиям.
    """
    __tablename__ = "comment_meeting"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    owner: Mapped[int] = mapped_column(Integer,
                                       ForeignKey("user_tabit.uuid"),
                                       nullable=False)
    result: Mapped[int | None] = mapped_column(Integer,
                                               ForeignKey("result_meeting.id"),
                                               nullable=True)
    meeting_id: Mapped[int] = mapped_column(Integer,
                                            ForeignKey("meeting.id"),
                                            nullable=False)
    interest: Mapped[bool] = mapped_column(Boolean,
                                           default=False)
    found_solution: Mapped[bool] = mapped_column(Boolean,
                                                 default=False)
    comment: Mapped[str] = mapped_column(Text,
                                         nullable=False)
    meeting = relationship("Meeting",
                           back_populates="comments")


# class MessageMeeting(BaseModel):
#    """
#    Модель сообщения, связанные с мероприятиями.
#    """
#    __tablename__ = "message_meeting"
#
#    id: Mapped[int] = mapped_column(Integer,
#                                    primary_key=True,
#                                    autoincrement=True)
#    owner: Mapped[int] = mapped_column(Integer, nullable=False)
#    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False)
#    text: Mapped[str] = mapped_column(Text, nullable=False)
#    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
#    meeting = relationship("Meeting", back_populates="messages")
# Модель убрана из ERD-схемы.


class Survey(BaseModel):
    """
    Модель для опросов.
    """
    __tablename__ = "survey"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)
    description: Mapped[str | None] = mapped_column(Text,
                                                    nullable=True)
    slug: Mapped[str] = mapped_column(String,
                                      unique=True,
                                      nullable=False)
    status: Mapped[int] = mapped_column(Integer,
                                        ForeignKey("status_survey.id"),
                                        nullable=False)
    result: Mapped[int | None] = mapped_column(Integer,
                                               ForeignKey("result_survey.id"),
                                               nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class SurveyUser(BaseLinkedTable):
    """
    Модель связи между опросами и пользователями.
    """
    __tablename__ = "survey_user"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    survey_id: Mapped[int] = mapped_column(Integer,
                                           ForeignKey("survey.id"),
                                           nullable=False)
    user_id: Mapped[int] = mapped_column(Integer,
                                         ForeignKey("user_tabit.uuid"),
                                         nullable=False)


class DateSurvey(BaseModel):
    """
    Модель даты связанные с опросами.
    """
    __tablename__ = "date_survey"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    date: Mapped[Date] = mapped_column(Date,
                                       nullable=False)
    survey_id: Mapped[int] = mapped_column(Integer,
                                           ForeignKey("survey.id"),
                                           nullable=False)


class StatusSurvey(BaseFieldName):
    """
    Модель статуса опроса.
    """
    __tablename__ = "status_survey"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)


class ResultSurvey(BaseFieldName):
    """
    Модель, результаты опросов.
    """
    __tablename__ = "result_survey"

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String,
                                      nullable=False)
