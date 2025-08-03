# Технические спецификации модуля социометрии для Tabit

## 1. Модели данных

### 1.1 Новые модели для социометрии

```python
# src/models/survey.py - добавления

from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseTabitModel, int_pk


class ChoiceType(str, Enum):
    """Типы социометрических выборов"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SociometricCriterion(BaseTabitModel):
    """
    Критерии социометрического тестирования.

    Назначение:
    - Определяет вопросы и параметры для социометрического тестирования.

    Поля:
    - id: Идентификатор критерия.
    - name: Название критерия.
    - description: Описание критерия.
    - choice_type: Тип выбора (положительный, отрицательный, нейтральный).
    - max_choices: Максимальное количество выборов.
    - company_id: Идентификатор компании.
    """

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    choice_type: Mapped[ChoiceType] = mapped_column(
        SQLAlchemyEnum(ChoiceType), nullable=False
    )
    max_choices: Mapped[int] = mapped_column(nullable=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'),
        nullable=False,
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'choice_type={self.choice_type!r}, '
            f'company_id={self.company_id!r})'
        )


class SociometricChoice(BaseTabitModel):
    """
    Выборы в социометрическом тесте.

    Назначение:
    - Сохраняет выборы участников социометрического тестирования.

    Поля:
    - id: Идентификатор выбора.
    - participant_id: Идентификатор участника, делающего выбор.
    - chosen_employee_id: Идентификатор выбранного сотрудника.
    - criterion_id: Идентификатор критерия.
    - cycle_user_id: Идентификатор цикла пользователя.
    - preference_rank: Ранг предпочтения (для ранжированных выборов).
    - choice_type: Тип выбора.
    """

    id: Mapped[int_pk]
    participant_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    chosen_employee_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    criterion_id: Mapped[int] = mapped_column(
        ForeignKey('sociometriccriterion.id', ondelete='CASCADE'),
        nullable=False,
    )
    cycle_user_id: Mapped[int] = mapped_column(
        ForeignKey('surveycycleforuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    preference_rank: Mapped[Optional[int]] = mapped_column(nullable=True)
    choice_type: Mapped[ChoiceType] = mapped_column(
        SQLAlchemyEnum(ChoiceType), nullable=False
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'participant_id={self.participant_id!r}, '
            f'chosen_employee_id={self.chosen_employee_id!r}, '
            f'criterion_id={self.criterion_id!r}, '
            f'cycle_user_id={self.cycle_user_id!r})'
        )
```

### 1.2 Обновление существующих моделей

```python
# src/models/enum.py - добавления

class ChoiceTypeEnum(StrEnum):
    """Типы социометрических выборов для перечислений."""

    POSITIVE = 'Положительный'
    NEGATIVE = 'Отрицательный'
    NEUTRAL = 'Нейтральный'
```

## 2. Схемы данных

### 2.1 Схемы для социометрии

```python
# src/schemas/sociometric.py

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from src.models.enum import ChoiceTypeEnum


class SociometricCriterionBaseSchema(BaseModel):
    """Базовая схема критерия социометрии."""

    name: str
    description: str
    choice_type: ChoiceTypeEnum
    max_choices: int


class SociometricCriterionCreateSchema(SociometricCriterionBaseSchema):
    """Схема для создания критерия социометрии."""

    model_config = ConfigDict(extra='forbid')


class SociometricCriterionUpdateSchema(SociometricCriterionBaseSchema):
    """Схема для обновления критерия социометрии."""

    model_config = ConfigDict(extra='forbid')


class SociometricCriterionResponseSchema(SociometricCriterionBaseSchema):
    """Схема для вывода критерия социометрии."""

    id: int
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class SociometricChoiceBaseSchema(BaseModel):
    """Базовая схема социометрического выбора."""

    chosen_employee_id: UUID
    criterion_id: int
    preference_rank: Optional[int] = None
    choice_type: ChoiceTypeEnum


class SociometricChoiceCreateSchema(SociometricChoiceBaseSchema):
    """Схема для создания социометрического выбора."""

    @model_validator(mode='after')
    def validate_choice(self):
        """Валидация социометрического выбора."""
        if self.preference_rank is not None and self.preference_rank < 1:
            raise ValueError("Ранг предпочтения должен быть положительным")
        return self

    model_config = ConfigDict(extra='forbid')


class SociometricChoiceResponseSchema(SociometricChoiceBaseSchema):
    """Схема для вывода социометрического выбора."""

    id: int
    participant_id: UUID
    cycle_user_id: int

    model_config = ConfigDict(from_attributes=True)


class SociometricResultsSchema(BaseModel):
    """Схема результатов социометрии."""

    cycle_info: dict
    individual_scores: dict
    group_metrics: dict
    special_identifications: dict
    recommendations: list[str]

    model_config = ConfigDict(from_attributes=True)


class CombinedAnalysisSchema(BaseModel):
    """Схема комбинированного анализа Люшера и социометрии."""

    emotional_context: dict
    sociometric_results: dict
    correlations: dict
    recommendations: list[str]

    model_config = ConfigDict(from_attributes=True)
```

## 3. CRUD операции

### 3.1 CRUD для критериев социометрии

```python
# src/crud/crud_surveys.py - добавления

from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.models.survey import SociometricCriterion, SociometricChoice
from src.schemas.sociometric import (
    SociometricCriterionCreateSchema,
    SociometricCriterionUpdateSchema,
    SociometricChoiceCreateSchema,
)


class CRUDSociometricCriterion(CRUDBase):
    """CRUD операции для критериев социометрии."""

    async def get_by_company(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> List[SociometricCriterion]:
        """Получить все критерии компании."""
        result = await session.execute(
            select(self.model).where(self.model.company_id == company_id)
        )
        return result.scalars().all()

    async def create_criterion(
        self,
        session: AsyncSession,
        criterion_in: SociometricCriterionCreateSchema,
        company_id: int,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> SociometricCriterion:
        """Создать критерий социометрии."""
        criterion_data = criterion_in.model_dump()
        criterion_data['company_id'] = company_id
        criterion_db = self.model(**criterion_data)

        try:
            session.add(criterion_db)
            if auto_commit:
                await session.commit()
                await session.refresh(criterion_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

        return criterion_db


class CRUDSociometricChoice(CRUDBase):
    """CRUD операции для социометрических выборов."""

    async def get_by_cycle_user(
        self,
        session: AsyncSession,
        cycle_user_id: int,
    ) -> List[SociometricChoice]:
        """Получить все выборы пользователя в цикле."""
        result = await session.execute(
            select(self.model).where(self.model.cycle_user_id == cycle_user_id)
        )
        return result.scalars().all()

    async def get_by_cycle_company(
        self,
        session: AsyncSession,
        cycle_company_id: int,
    ) -> List[SociometricChoice]:
        """Получить все выборы в цикле компании."""
        result = await session.execute(
            select(self.model)
            .join(SurveyCycleForUser, self.model.cycle_user_id == SurveyCycleForUser.id)
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle_company_id)
        )
        return result.scalars().all()

    async def create_choices(
        self,
        session: AsyncSession,
        choices_in: List[SociometricChoiceCreateSchema],
        cycle_user_id: int,
        participant_id: UUID,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> List[SociometricChoice]:
        """Создать несколько социометрических выборов."""
        choices_db = []

        for choice_in in choices_in:
            choice_data = choice_in.model_dump()
            choice_data['cycle_user_id'] = cycle_user_id
            choice_data['participant_id'] = participant_id
            choice_db = self.model(**choice_data)
            choices_db.append(choice_db)

        try:
            session.add_all(choices_db)
            if auto_commit:
                await session.commit()
                for choice in choices_db:
                    await session.refresh(choice)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

        return choices_db

    async def validate_choices(
        self,
        session: AsyncSession,
        choices: List[SociometricChoiceCreateSchema],
        cycle_user_id: int,
        participant_id: UUID,
    ) -> None:
        """Валидация социометрических выборов."""
        # Получаем информацию о пользователе
        cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

        # Группируем выборы по критериям
        choices_by_criterion = {}
        for choice in choices:
            if choice.criterion_id not in choices_by_criterion:
                choices_by_criterion[choice.criterion_id] = []
            choices_by_criterion[choice.criterion_id].append(choice)

        for criterion_id, criterion_choices in choices_by_criterion.items():
            # Получаем критерий
            criterion = await sociometric_criterion_crud.get_or_404(session, criterion_id)

            # Проверка максимального количества выборов
            if len(criterion_choices) > criterion.max_choices:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Превышено максимальное количество выборов для критерия '{criterion.name}'"
                )

            # Проверка уникальности выбранных сотрудников
            chosen_employees = [c.chosen_employee_id for c in criterion_choices]
            if len(chosen_employees) != len(set(chosen_employees)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Дублирование выборов в критерии '{criterion.name}'"
                )

            # Проверка самоисключения
            if participant_id in chosen_employees:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Участник не может выбирать себя"
                )

            # Проверка последовательности ранжирования
            if criterion_choices[0].preference_rank is not None:
                ranks = [c.preference_rank for c in criterion_choices if c.preference_rank is not None]
                if len(ranks) != len(criterion_choices):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Все выборы должны иметь ранг предпочтения"
                    )
                if len(set(ranks)) != len(ranks):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ранги предпочтения должны быть уникальными"
                    )


# Создание экземпляров CRUD
sociometric_criterion_crud = CRUDSociometricCriterion(SociometricCriterion)
sociometric_choice_crud = CRUDSociometricChoice(SociometricChoice)
```

## 4. Бизнес-логика социометрии

### 4.1 Класс для расчета социометрических индексов

```python
# src/business_logic/sociometric.py

from typing import Dict, List, Tuple
from uuid import UUID

from src.models.enum import ChoiceTypeEnum
from src.models.survey import SociometricChoice


class SociometricIndices:
    """Класс для расчета социометрических индексов."""

    @staticmethod
    def calculate_popularity(choices_data: List[SociometricChoice]) -> Dict[UUID, int]:
        """Расчет популярности (степень входа)."""
        popularity_scores = {}
        for choice in choices_data:
            if choice.choice_type == ChoiceTypeEnum.POSITIVE:
                popularity_scores[choice.chosen_employee_id] = \
                    popularity_scores.get(choice.chosen_employee_id, 0) + 1
        return popularity_scores

    @staticmethod
    def calculate_rejection(choices_data: List[SociometricChoice]) -> Dict[UUID, int]:
        """Расчет отторжения (отрицательная степень входа)."""
        rejection_scores = {}
        for choice in choices_data:
            if choice.choice_type == ChoiceTypeEnum.NEGATIVE:
                rejection_scores[choice.chosen_employee_id] = \
                    rejection_scores.get(choice.chosen_employee_id, 0) + 1
        return rejection_scores

    @staticmethod
    def calculate_expansiveness(choices_data: List[SociometricChoice]) -> Dict[UUID, int]:
        """Расчет экспансивности (степень выхода)."""
        expansiveness_scores = {}
        for choice in choices_data:
            expansiveness_scores[choice.participant_id] = \
                expansiveness_scores.get(choice.participant_id, 0) + 1
        return expansiveness_scores

    @staticmethod
    def calculate_mutual_choices(choices_data: List[SociometricChoice]) -> List[Tuple]:
        """Расчет взаимных выборов."""
        mutual_pairs = []
        choices_dict = {}

        for choice in choices_data:
            key = (choice.participant_id, choice.chosen_employee_id)
            choices_dict[key] = choice

            reverse_key = (choice.chosen_employee_id, choice.participant_id)
            if reverse_key in choices_dict:
                mutual_pairs.append((key, reverse_key))

        return mutual_pairs

    @staticmethod
    def calculate_group_cohesion(choices_data: List[SociometricChoice], total_participants: int) -> float:
        """Расчет сплоченности группы."""
        total_possible_choices = total_participants * (total_participants - 1)
        actual_positive_choices = len([
            c for c in choices_data
            if c.choice_type == ChoiceTypeEnum.POSITIVE
        ])
        return actual_positive_choices / total_possible_choices if total_possible_choices > 0 else 0

    @staticmethod
    def identify_stars_and_isolates(
        popularity_scores: Dict[UUID, int],
        rejection_scores: Dict[UUID, int],
        threshold: float = 0.3
    ) -> Dict:
        """Выявление социометрических звезд и изолятов."""
        total_participants = len(popularity_scores)
        stars = []
        isolates = []

        for employee_id, popularity in popularity_scores.items():
            rejection = rejection_scores.get(employee_id, 0)
            net_score = popularity - rejection

            # Звезды: высокий положительный баланс
            if net_score >= total_participants * threshold:
                stars.append({
                    'employee_id': employee_id,
                    'popularity': popularity,
                    'rejection': rejection,
                    'net_score': net_score
                })

            # Изоляты: низкий или отрицательный баланс
            if net_score <= 0 or (popularity == 0 and rejection == 0):
                isolates.append({
                    'employee_id': employee_id,
                    'popularity': popularity,
                    'rejection': rejection,
                    'net_score': net_score
                })

        return {'stars': stars, 'isolates': isolates}
```

### 4.2 Функции для генерации отчетов

```python
# src/business_logic/sociometric.py - продолжение

async def generate_sociometric_report(
    session: AsyncSession,
    cycle_company_id: int
) -> Dict:
    """Генерация полного отчета по социометрии."""

    # Получаем все данные
    choices_data = await sociometric_choice_crud.get_by_cycle_company(
        session, cycle_company_id
    )

    # Получаем участников цикла
    cycle_users = await survey_cycle_for_user_crud.get_by_cycle_company(
        session, cycle_company_id
    )
    participants = [cycle_user.user_id for cycle_user in cycle_users]

    # Рассчитываем индексы
    popularity_scores = SociometricIndices.calculate_popularity(choices_data)
    rejection_scores = SociometricIndices.calculate_rejection(choices_data)
    expansiveness_scores = SociometricIndices.calculate_expansiveness(choices_data)
    mutual_choices = SociometricIndices.calculate_mutual_choices(choices_data)
    group_cohesion = SociometricIndices.calculate_group_cohesion(
        choices_data, len(participants)
    )

    # Выявляем звезд и изолятов
    stars_and_isolates = SociometricIndices.identify_stars_and_isolates(
        popularity_scores, rejection_scores
    )

    return {
        'cycle_info': {
            'cycle_company_id': cycle_company_id,
            'total_participants': len(participants),
            'total_choices': len(choices_data)
        },
        'individual_scores': {
            'popularity': popularity_scores,
            'rejection': rejection_scores,
            'expansiveness': expansiveness_scores
        },
        'group_metrics': {
            'cohesion': group_cohesion,
            'mutual_choices_count': len(mutual_choices),
            'stars_count': len(stars_and_isolates['stars']),
            'isolates_count': len(stars_and_isolates['isolates'])
        },
        'special_identifications': stars_and_isolates,
        'recommendations': generate_recommendations(
            popularity_scores, rejection_scores,
            stars_and_isolates, group_cohesion
        )
    }


def generate_recommendations(
    popularity_scores: Dict[UUID, int],
    rejection_scores: Dict[UUID, int],
    stars_and_isolates: Dict,
    group_cohesion: float
) -> List[str]:
    """Генерация рекомендаций для HR на основе социометрических данных."""

    recommendations = []

    # Анализ изолятов
    if stars_and_isolates['isolates']:
        recommendations.append(
            "Выявлены социально изолированные сотрудники. "
            "Рекомендуется провести индивидуальные беседы и "
            "разработать программы интеграции."
        )

    # Анализ звезд
    if stars_and_isolates['stars']:
        recommendations.append(
            "Выявлены неформальные лидеры. "
            "Рекомендуется привлечь их к наставничеству "
            "и развитию командных навыков."
        )

    # Анализ сплоченности
    if group_cohesion < 0.3:
        recommendations.append(
            "Низкая сплоченность группы. "
            "Рекомендуется провести тимбилдинг мероприятия."
        )
    elif group_cohesion > 0.7:
        recommendations.append(
            "Высокая сплоченность группы. "
            "Можно использовать для сложных проектов."
        )

    # Анализ отторжения
    high_rejection = [
        emp_id for emp_id, score in rejection_scores.items()
        if score > 2
    ]
    if high_rejection:
        recommendations.append(
            "Выявлены сотрудники с высоким уровнем отторжения. "
            "Рекомендуется провести конфликтологический анализ."
        )

    return recommendations
```

## 5. API эндпоинты

### 5.1 Эндпоинты для управления критериями

```python
# src/features_v1/company_survey_management/endpoints.py - добавления

@router.post(
    '/sociometric/criteria',
    response_model=SociometricCriterionResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Создать социометрический критерий',
    description='Создать новый критерий для социометрического тестирования.',
    status_code=status.HTTP_201_CREATED,
)
async def create_sociometric_criterion(
    company_slug: str,
    criterion: SociometricCriterionCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> SociometricCriterionResponseSchema:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await sociometric_criterion_crud.create_criterion(
        session, criterion, company_id=company.id
    )


@router.get(
    '/sociometric/criteria',
    response_model=List[SociometricCriterionResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить критерии социометрии',
    description='Получить все критерии социометрии для компании.',
)
async def get_sociometric_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[SociometricCriterionResponseSchema]:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await sociometric_criterion_crud.get_by_company(session, company.id)


@router.patch(
    '/sociometric/criteria/{criterion_id}',
    response_model=SociometricCriterionResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Обновить социометрический критерий',
    description='Обновить существующий критерий социометрии.',
)
async def update_sociometric_criterion(
    company_slug: str,
    criterion_id: int,
    criterion: SociometricCriterionUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> SociometricCriterionResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    criterion_db = await sociometric_criterion_crud.get_or_404(session, criterion_id)
    return await sociometric_criterion_crud.update(session, criterion_db, criterion)


@router.delete(
    '/sociometric/criteria/{criterion_id}',
    dependencies=[Depends(current_company_moderator)],
    summary='Удалить социометрический критерий',
    description='Удалить критерий социометрии.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sociometric_criterion(
    company_slug: str,
    criterion_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    criterion_db = await sociometric_criterion_crud.get_or_404(session, criterion_id)
    await sociometric_criterion_crud.remove(session, criterion_db)
```

### 5.2 Эндпоинты для социометрических выборов

```python
@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric',
    response_model=List[SociometricChoiceResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Сохранить социометрические выборы',
    description='Создать социометрические выборы для пользователя в цикле.',
    status_code=status.HTTP_201_CREATED,
)
async def create_sociometric_choices(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    choices: List[SociometricChoiceCreateSchema],
    session: AsyncSession = Depends(get_async_session),
) -> List[SociometricChoiceResponseSchema]:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Валидация выборов
    await sociometric_choice_crud.validate_choices(
        session, choices, cycle_user_id, cycle_user.user_id
    )

    return await sociometric_choice_crud.create_choices(
        session, choices, cycle_user_id=cycle_user_id, participant_id=cycle_user.user_id
    )


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric',
    response_model=List[SociometricChoiceResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить социометрические выборы пользователя',
    description='Получить все социометрические выборы пользователя в цикле.',
)
async def get_sociometric_choices(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> List[SociometricChoiceResponseSchema]:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    return await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions',
    dependencies=[Depends(current_user_tabit)],
    summary='Получить вопросы для социометрического теста',
    description='Получить 4 вопроса для текущей итерации социометрического теста. Обычные пользователи используют только сбалансированную стратегию.',
)
async def get_sociometric_questions(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Получаем доступные критерии для компании
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    available_criteria = await sociometric_criterion_crud.get_by_company(session, company.id)

    # Получаем предыдущие вопросы (если есть)
    previous_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
    previous_questions = list(set(choice.criterion_id for choice in previous_choices))

    # Определяем, является ли пользователь модератором
    current_user = await get_current_user(session)
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    # Для обычных пользователей всегда используем сбалансированную стратегию
    strategy = QuestionSelectionStrategy.BALANCED

    # Выбираем вопросы
    selector = SociometricQuestionSelector(strategy, is_moderator=is_moderator)
    selected_questions = await selector.select_questions(
        session=session,
        available_criteria=available_criteria,
        questions_per_iteration=4,
        previous_questions=previous_questions,
        user_preferences=None  # Убираем пользовательские предпочтения
    )

    return {
        "iteration": len(previous_questions) // 4 + 1,
        "total_iterations": len(available_criteria) // 4,
        "strategy": strategy,
        "is_moderator": is_moderator,
        "questions": [
            {
                "criterion_id": question["criterion_id"],
                "name": question["name"],
                "description": question["description"],
                "choice_type": question["choice_type"],
                "max_choices": question["max_choices"],
                "category": question["category"]
            }
            for question in selected_questions
        ]
    }


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions/strategy',
    dependencies=[Depends(current_company_moderator)],  # Только для модераторов
    summary='Изменить стратегию выбора вопросов',
    description='Изменить стратегию выбора вопросов для социометрического теста. Доступно только модераторам.',
)
async def change_question_strategy(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    strategy: QuestionSelectionStrategy,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Сохраняем предпочтение модератора
    await save_moderator_strategy_preference(session, cycle_user_id, strategy)

    return {
        "message": f"Стратегия изменена на {strategy}",
        "strategy": strategy,
        "note": "Изменение стратегии доступно только модераторам"
    }


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/completion-status',
    dependencies=[Depends(current_user_tabit)],
    summary='Получить статус завершения социометрического теста',
    description='Получить информацию о прогрессе и возможности завершения теста.',
)
async def get_sociometric_completion_status(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Определяем, является ли пользователь модератором
    current_user = await get_current_user(session)
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    # Получаем статус завершения
    completion_status = await get_user_test_completion_status(
        session, cycle_user_id, is_moderator
    )

    return completion_status
```

### 5.3 Эндпоинты для результатов

```python
@router.get(
    '/cycle/{cycle_company_id}/sociometric/results',
    response_model=SociometricResultsSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Получить результаты социометрии',
    description='Получить полные результаты социометрии для цикла.',
)
async def get_sociometric_results(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> SociometricResultsSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)

    return await generate_sociometric_report(session, cycle_company_id)


@router.get(
    '/cycle/{cycle_company_id}/sociometric/combined-analysis',
    response_model=CombinedAnalysisSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Комбинированный анализ',
    description='Комбинированный анализ результатов Люшера и социометрии.',
)
async def get_combined_analysis(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CombinedAnalysisSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)

    # Получаем результаты социометрии
    sociometric_results = await generate_sociometric_report(session, cycle_company_id)

    # Получаем результаты Люшера
    emotional_context = await analyze_emotional_context_for_cycle(
        session, cycle_company_id
    )

    # Корреляционный анализ
    correlations = await correlate_emotions_with_sociometric_choices(
        session, cycle_company_id
    )

    return CombinedAnalysisSchema(
        emotional_context=emotional_context,
        sociometric_results=sociometric_results,
        correlations=correlations,
        recommendations=generate_combined_recommendations(
            emotional_context, sociometric_results, correlations
        )
    )
```

## 6. Миграции базы данных

### 6.1 Создание миграции

```python
# alembic/versions/05_add_sociometric_tables.py

"""Add sociometric tables

Revision ID: 05_add_sociometric_tables
Revises: 04_fix_slug_length
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '05_add_sociometric_tables'
down_revision = '04_fix_slug_length'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание enum для типов выборов
    op.execute("CREATE TYPE choicetype AS ENUM ('positive', 'negative', 'neutral')")

    # Создание таблицы критериев социометрии
    op.create_table('sociometriccriterion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('choice_type', postgresql.ENUM('positive', 'negative', 'neutral', name='choicetype'), nullable=False),
        sa.Column('max_choices', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='sociometriccriterion_company_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='sociometriccriterion_pkey')
    )

    # Создание таблицы социометрических выборов
    op.create_table('sociometricchoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chosen_employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criterion_id', sa.Integer(), nullable=False),
        sa.Column('cycle_user_id', sa.Integer(), nullable=False),
        sa.Column('preference_rank', sa.Integer(), nullable=True),
        sa.Column('choice_type', postgresql.ENUM('positive', 'negative', 'neutral', name='choicetype'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['criterion_id'], ['sociometriccriterion.id'], name='sociometricchoice_criterion_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cycle_user_id'], ['surveycycleforuser.id'], name='sociometricchoice_cycle_user_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['companyuser.id'], name='sociometricchoice_participant_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chosen_employee_id'], ['companyuser.id'], name='sociometricchoice_chosen_employee_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='sociometricchoice_pkey')
    )

    # Создание индексов
    op.create_index('ix_sociometriccriterion_company_id', 'sociometriccriterion', ['company_id'])
    op.create_index('ix_sociometricchoice_cycle_user_id', 'sociometricchoice', ['cycle_user_id'])
    op.create_index('ix_sociometricchoice_participant_id', 'sociometricchoice', ['participant_id'])
    op.create_index('ix_sociometricchoice_criterion_id', 'sociometricchoice', ['criterion_id'])


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('ix_sociometricchoice_criterion_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometricchoice_participant_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometricchoice_cycle_user_id', table_name='sociometricchoice')
    op.drop_index('ix_sociometriccriterion_company_id', table_name='sociometriccriterion')

    # Удаление таблиц
    op.drop_table('sociometricchoice')
    op.drop_table('sociometriccriterion')

    # Удаление enum
    op.execute("DROP TYPE choicetype")
```

## 7. Тестирование

### 7.1 Тесты для социометрии

```python
# tests/test_sociometric.py

import pytest
from uuid import uuid4

from src.models.enum import ChoiceTypeEnum
from src.schemas.sociometric import SociometricCriterionCreateSchema, SociometricChoiceCreateSchema


class TestSociometricCriterion:
    """Тесты для критериев социометрии."""

    async def test_create_sociometric_criterion(self, client, moderator_token, company_slug):
        """Тест создания критерия социометрии."""
        criterion_data = {
            "name": "Тестовый критерий",
            "description": "Описание тестового критерия",
            "choice_type": ChoiceTypeEnum.POSITIVE,
            "max_choices": 3
        }

        response = await client.post(
            f"/api/v1/{company_slug}/surveys/sociometric/criteria",
            json=criterion_data,
            headers={"Authorization": f"Bearer {moderator_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == criterion_data["name"]
        assert data["choice_type"] == criterion_data["choice_type"]

    async def test_get_sociometric_criteria(self, client, user_token, company_slug):
        """Тест получения критериев социометрии."""
        response = await client.get(
            f"/api/v1/{company_slug}/surveys/sociometric/criteria",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSociometricChoices:
    """Тесты для социометрических выборов."""

    async def test_create_sociometric_choices(self, client, user_token, company_slug, cycle_data):
        """Тест создания социометрических выборов."""
        choices_data = [
            {
                "chosen_employee_id": str(uuid4()),
                "criterion_id": 1,
                "preference_rank": 1,
                "choice_type": ChoiceTypeEnum.POSITIVE
            },
            {
                "chosen_employee_id": str(uuid4()),
                "criterion_id": 1,
                "preference_rank": 2,
                "choice_type": ChoiceTypeEnum.POSITIVE
            }
        ]

        response = await client.post(
            f"/api/v1/{company_slug}/surveys/cycle/{cycle_data['cycle_company_id']}/{cycle_data['cycle_user_id']}/sociometric",
            json=choices_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data) == 2

    async def test_validate_self_choice(self, client, user_token, company_slug, cycle_data):
        """Тест валидации выбора самого себя."""
        choices_data = [
            {
                "chosen_employee_id": "self_user_id",  # ID текущего пользователя
                "criterion_id": 1,
                "choice_type": ChoiceTypeEnum.POSITIVE
            }
        ]

        response = await client.post(
            f"/api/v1/{company_slug}/surveys/cycle/{cycle_data['cycle_company_id']}/{cycle_data['cycle_user_id']}/sociometric",
            json=choices_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 400
        assert "не может выбирать себя" in response.json()["detail"]


class TestSociometricResults:
    """Тесты для результатов социометрии."""

    async def test_get_sociometric_results(self, client, moderator_token, company_slug, cycle_data):
        """Тест получения результатов социометрии."""
        response = await client.get(
            f"/api/v1/{company_slug}/surveys/cycle/{cycle_data['cycle_company_id']}/sociometric/results",
            headers={"Authorization": f"Bearer {moderator_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "cycle_info" in data
        assert "individual_scores" in data
        assert "group_metrics" in data
        assert "recommendations" in data

    async def test_get_combined_analysis(self, client, moderator_token, company_slug, cycle_data):
        """Тест получения комбинированного анализа."""
        response = await client.get(
            f"/api/v1/{company_slug}/surveys/cycle/{cycle_data['cycle_company_id']}/sociometric/combined-analysis",
            headers={"Authorization": f"Bearer {moderator_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "emotional_context" in data
        assert "sociometric_results" in data
        assert "correlations" in data
```

## 8. Документация API

### 8.1 OpenAPI спецификация

Добавить в `src/openapi.py`:

```python
# Дополнительные теги для OpenAPI
tags_metadata = [
    # ... существующие теги ...
    {
        "name": "sociometric",
        "description": "Операции с социометрическим тестированием",
    },
]

# Дополнительные схемы
additional_schemas = {
    "ChoiceType": {
        "type": "string",
        "enum": ["positive", "negative", "neutral"],
        "description": "Тип социометрического выбора"
    },
    "SociometricCriterion": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "choice_type": {"$ref": "#/components/schemas/ChoiceType"},
            "max_choices": {"type": "integer"},
            "company_id": {"type": "integer"}
        }
    }
}
```

## 9. Безопасность и ограничения

### 9.1 Ограничения для обычных пользователей

```python
# src/core/config/sociometric.py - добавления

class SociometricSecurityConfig(BaseModel):
    """Конфигурация безопасности социометрии."""

    # Ограничения для обычных пользователей
    USER_STRATEGY_RESTRICTION: bool = True  # Только BALANCED стратегия
    USER_PREFERENCE_DISABLED: bool = True   # Отключить пользовательские предпочтения
    USER_MIN_COMPLETION: float = 100.0      # Обычные пользователи должны ответить на все вопросы
    USER_ADAPTIVE_DISABLED: bool = True     # Отключить адаптивные алгоритмы

    # Возможности модераторов
    MODERATOR_ALL_STRATEGIES: bool = True   # Все стратегии доступны для настройки тестов
    MODERATOR_ADAPTIVE_ENABLED: bool = True # Адаптивные алгоритмы включены для настройки
    # Модераторы не проходят тесты - они их создают и управляют
```

### 9.2 Функции проверки прав доступа

```python
# src/core/auth/sociometric_permissions.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import CompanyUser
from src.models.enum import UserRoleEnum


async def check_user_is_moderator(
    session: AsyncSession,
    user_id: int,
    company_id: int
) -> bool:
    """Проверить, является ли пользователь модератором компании."""

    result = await session.execute(
        select(CompanyUser)
        .where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_id,
                CompanyUser.role == UserRoleEnum.MODERATOR
            )
        )
    )

    return result.scalar_one_or_none() is not None


async def validate_user_strategy_access(
    strategy: str,
    is_moderator: bool
) -> bool:
    """Проверить доступ пользователя к стратегии."""

    if is_moderator:
        return True  # Модераторы имеют доступ ко всем стратегиям

    # Обычные пользователи могут использовать только BALANCED
    return strategy == "balanced"


async def get_user_completion_threshold(is_moderator: bool) -> float:
    """Получить минимальный порог завершения теста для пользователя."""

    # Модераторы не проходят тесты - они их создают и управляют
    # Все пользователи должны ответить на все вопросы
    return 100.0
```

### 9.3 Валидация в бизнес-логике

```python
# src/business_logic/sociometric_question_selector.py - дополнения

class SociometricQuestionSelector:
    """Класс для выбора вопросов социометрического теста."""

    def __init__(self, strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.BALANCED, is_moderator: bool = False):
        self.strategy = strategy
        self.is_moderator = is_moderator

        # Принудительно устанавливаем BALANCED для обычных пользователей
        if not self.is_moderator:
            self.strategy = QuestionSelectionStrategy.BALANCED

    async def select_questions(
        self,
        session,
        available_criteria: List[Dict],
        questions_per_iteration: int = 4,
        previous_questions: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """Выбрать вопросы для текущей итерации теста."""

        # Дополнительная проверка безопасности
        if not self.is_moderator and user_preferences:
            user_preferences = None  # Игнорируем предпочтения обычных пользователей

        # Остальная логика остается без изменений...
```

## 10. Развертывание

### 10.1 Обновление зависимостей

```toml
# pyproject.toml - добавления
[tool.poetry.dependencies]
# ... существующие зависимости ...
networkx = "^3.0"  # Для анализа социальных сетей
matplotlib = "^3.7.0"  # Для визуализации социограмм
```

### 9.2 Конфигурация

```python
# src/core/config/app.py - добавления

class Settings(BaseSettings):
    # ... существующие настройки ...

    # Настройки социометрии
    SOCIOMETRIC_MAX_CHOICES_PER_CRITERION: int = 5
    SOCIOMETRIC_STAR_THRESHOLD: float = 0.3
    SOCIOMETRIC_ISOLATE_THRESHOLD: float = 0.0
    SOCIOMETRIC_LOW_COHESION_THRESHOLD: float = 0.3
    SOCIOMETRIC_HIGH_COHESION_THRESHOLD: float = 0.7
```

Этот документ предоставляет полные технические спецификации для реализации модуля социометрии в проекте Tabit, учитывая реальную архитектуру системы и существующие модели данных.
