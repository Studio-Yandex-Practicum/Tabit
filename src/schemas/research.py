from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionOption(BaseModel):
    """Схема для варианта ответа на вопрос."""

    id: str = Field(..., description='Уникальный идентификатор варианта')
    text: str = Field(..., description='Текст варианта ответа')
    value: Optional[Union[str, int, bool]] = Field(None, description='Значение варианта ответа')


class QuestionSchema(BaseModel):
    """Схема для вопроса в опросе."""

    id: str = Field(..., description='Уникальный идентификатор вопроса')
    text: str = Field(..., description='Текст вопроса')
    type: str = Field(..., description="Тип вопроса: 'radio', 'checkbox', 'text', 'textarea'")
    required: bool = Field(default=True, description='Обязательный ли вопрос')
    options: Optional[List[QuestionOption]] = Field(
        None, description='Варианты ответов для radio/checkbox'
    )
    placeholder: Optional[str] = Field(None, description='Placeholder для текстовых полей')
    max_length: Optional[int] = Field(None, description='Максимальная длина для текстовых полей')


class ResearchTypeBaseSchema(BaseModel):
    """Базовая схема для типа опроса."""

    title: str = Field(..., min_length=1, max_length=255, description='Заголовок опроса')
    description: Optional[str] = Field(None, max_length=1000, description='Описание опроса')
    questions: List[QuestionSchema] = Field(..., min_items=1, description='Список вопросов')
    is_active: bool = Field(default=True, description='Активен ли тип опроса')

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v: List[QuestionSchema]) -> List[QuestionSchema]:
        """Проверяет корректность вопросов."""
        if not v:
            raise ValueError('Список вопросов не может быть пустым')

        question_ids = [q.id for q in v]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError('ID вопросов должны быть уникальными')

        for question in v:
            if question.type in ['radio', 'checkbox'] and not question.options:
                raise ValueError(
                    f"Вопрос типа '{question.type}' должен содержать варианты ответов"
                )
            if question.type in ['text', 'textarea'] and question.options:
                raise ValueError(
                    f"Вопрос типа '{question.type}' не должен содержать варианты ответов"
                )

        return v


class ResearchTypeCreateSchema(ResearchTypeBaseSchema):
    """Схема для создания типа опроса."""

    model_config = ConfigDict(extra='forbid')


class ResearchTypeUpdateSchema(BaseModel):
    """Схема для обновления типа опроса."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    questions: Optional[List[QuestionSchema]] = Field(None, min_items=1)
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('questions')
    @classmethod
    def validate_questions(
        cls, v: Optional[List[QuestionSchema]]
    ) -> Optional[List[QuestionSchema]]:
        """Проверяет корректность вопросов."""
        if v is not None:
            if not v:
                raise ValueError('Список вопросов не может быть пустым')

            question_ids = [q.id for q in v]
            if len(question_ids) != len(set(question_ids)):
                raise ValueError('ID вопросов должны быть уникальными')

            for question in v:
                if question.type in ['radio', 'checkbox'] and not question.options:
                    raise ValueError(
                        f"Вопрос типа '{question.type}' должен содержать варианты ответов"
                    )
                if question.type in ['text', 'textarea'] and question.options:
                    raise ValueError(
                        f"Вопрос типа '{question.type}' не должен содержать варианты ответов"
                    )

        return v


class ResearchTypeResponseSchema(ResearchTypeBaseSchema):
    """Схема для ответа с типом опроса."""

    id: int
    company_id: int
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchInstanceBaseSchema(BaseModel):
    """Базовая схема для экземпляра опроса."""

    research_type_id: int
    user_id: UUID


class ResearchInstanceCreateSchema(ResearchInstanceBaseSchema):
    """Схема для создания экземпляра опроса."""

    model_config = ConfigDict(extra='forbid')


class ResearchInstanceUpdateSchema(BaseModel):
    """Схема для обновления экземпляра опроса."""

    status: Optional[str] = None
    answers: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(extra='forbid')


class ResearchInstanceResponseSchema(ResearchInstanceBaseSchema):
    """Схема для ответа с экземпляром опроса."""

    id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    answers: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class ResearchInstanceWithTypeSchema(ResearchInstanceResponseSchema):
    """Схема для ответа с экземпляром опроса и его типом."""

    research_type: ResearchTypeResponseSchema

    model_config = ConfigDict(from_attributes=True)


class ResearchResultsSchema(BaseModel):
    """Схема для результатов опроса."""

    research_type_id: int
    research_type_title: str
    total_responses: int
    completed_responses: int
    in_progress_responses: int
    average_completion_time: Optional[float] = None
    question_statistics: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
