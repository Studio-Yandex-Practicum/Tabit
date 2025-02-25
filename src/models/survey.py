# TODO Требуется проработка ERD


# from sqlalchemy import Boolean, Date, DateTime, Integer, ForeignKey, String, Table, Text
# from sqlalchemy.orm import relationship, Mapped, mapped_column

# from src.models import BaseTabitModel


# class Survey(BaseTabitModel):
#     """
#     Модель для опросов.
#     """

#     __tablename__ = 'survey'

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String)
#     description: Mapped[str | None] = mapped_column(Text)
#     slug: Mapped[str] = mapped_column(String, unique=True)
#     status: Mapped[int] = mapped_column(Integer, ForeignKey('status_survey.id'))
#     result: Mapped[int | None] = mapped_column(Integer, ForeignKey('result_survey.id'))
#     created_at: Mapped[DateTime] = mapped_column(DateTime)


# class SurveyUser(BaseTabitModel):
#     """
#     Модель связи между опросами и пользователями.
#     """

#     __tablename__ = 'survey_user'

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('survey.id'))
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_tabit.uuid'))


# class DateSurvey(BaseTabitModel):
#     """
#     Модель даты связанные с опросами.
#     """

#     __tablename__ = 'date_survey'

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     date: Mapped[Date] = mapped_column(Date)
#     survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('survey.id'))


# class StatusSurvey(BaseTabitModel):
#     """
#     Модель статуса опроса.
#     """

#     __tablename__ = 'status_survey'

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String)
