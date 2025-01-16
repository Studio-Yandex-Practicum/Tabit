from sqlalchemy import (Boolean,
                        Date,
                        DateTime,
                        Integer,
                        String,
                        Text)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import BaseModel


class BaseActivity(BaseModel):
    """
    Базовая модель для деятельности.
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class BaseFieldName(BaseModel):
    """
    Базовая модель для справочных данных.
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Meeting(BaseActivity):
    """
    Модель для мероприятий.
    """
    __tablename__ = "meeting"

    owner: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    place: Mapped[str] = mapped_column(Text, nullable=True)
    file: Mapped[str] = mapped_column(Text, nullable=True)
    comments = relationship("CommentMeeting", back_populates="meeting")
    messages = relationship("MessageMeeting", back_populates="meeting")


class StatusMeeting(BaseFieldName):
    """
    Модель статус мероприятия.
    """
    __tablename__ = "status_meeting"


class ResultMeeting(BaseFieldName):
    """
    Модель результаты мероприятия.
    """
    __tablename__ = "result_meeting"


class Survey(BaseModel):
    """
    Модель для опросов.
    """
    __tablename__ = "survey"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    users = relationship("SurveyUser", back_populates="survey")


class SurveyUser(BaseModel):
    """
    Модель связи между опросами и пользователями.
    """
    __tablename__ = "survey_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    survey_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    survey = relationship("Survey", back_populates="users")


class DateSurvey(BaseModel):
    """
    Модель даты связанные с опросами.
    """
    __tablename__ = "date_survey"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    survey: Mapped[int] = mapped_column(Integer, nullable=False)


class StatusSurvey(BaseFieldName):
    """
    Модель статуса опроса.
    """
    __tablename__ = "status_survey"


class ResultSurvey(BaseFieldName):
    """
    Модель, результаты опросов.
    """
    __tablename__ = "result_survey"


class CommentMeeting(BaseModel):
    """
    Модель, комментарии к мероприятиям.
    """
    __tablename__ = "comment_meeting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    result: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False)
    interest: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                           default=False)
    found_solution: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                                 default=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    meeting = relationship("Meeting", back_populates="comments")


class MessageMeeting(BaseModel):
    """
    Модель сообщения, связанные с мероприятиями.
    """
    __tablename__ = "message_meeting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    owner: Mapped[int] = mapped_column(Integer, nullable=False)
    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    meeting = relationship("Meeting", back_populates="messages")
