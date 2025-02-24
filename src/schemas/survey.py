# TODO Требуется проработка ERD

# from pydantic import BaseModel
# from typing import Optional
# from datetime import date, datetime


# class SurveyBaseSchema(BaseModel):
#     """
#     Базовая Pydantic-схема для опросов.
#     """
#     name: str
#     description: Optional[str]
#     slug: str
#     status: int
#     result: Optional[int]
#     created_at: datetime


# class SurveyCreateSchema(SurveyBaseSchema):
#     """
#     Pydantic-схема для создания опроса.
#     """
#     pass


# class SurveyUpdateSchema(SurveyBaseSchema):
#     """
#     Pydantic-схема для обновления информации об опросе.
#     """
#     pass


# class SurveySchema(SurveyBaseSchema):
#     """
#     Pydantic-схема для отображения информации об опросе.
#     """
#     id: int

#     model_config = ConfigDict(from_attributes=True)


# class SurveyUserSchema(BaseModel):
#     """
#     Pydantic-схема для связи пользователей с опросами.
#     """
#     id: int
#     survey_id: int
#     user_id: int

#     model_config = ConfigDict(from_attributes=True)


# class DateSurveySchema(BaseModel):
#     """
#     Pydantic-схема для дат, связанных с опросами.
#     """
#     id: int
#     date: date
#     survey_id: int

#     model_config = ConfigDict(from_attributes=True)

# class StatusSurveySchema(BaseModel):
#     """
#     Pydantic-схема для статусов опросов.
#     """
#     id: int
#     name: str

#     model_config = ConfigDict(from_attributes=True)
