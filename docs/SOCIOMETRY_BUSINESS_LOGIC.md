# Бизнес-логика модуля социометрии для Tabit

## Исполнительное резюме

Данный документ описывает бизнес-логику для реализации модуля социометрии в приложении Tabit. Модуль интегрируется в существующую систему тестирования сотрудников, дополняя цветовой тест Люшера.
Особое внимание уделяется последовательной оценке: Люшер → Социометрия → Люшер, что позволяет анализировать влияние эмоционального состояния на социальные выборы и обратное влияние социальных взаимодействий на эмоциональное состояние.

## 1. Интеграция с существующей архитектурой Tabit

### 1.1 Текущая структура системы

Tabit имеет развитую систему для проведения тестов с четкой иерархией:

**Основные модели:**
- `Company` - компании
- `CompanyUser` - пользователи компаний (связь many-to-many)
- `SurveyCycleForCompany` - циклы опросов на уровне компании
- `SurveyCycleForUser` - циклы опросов для конкретных пользователей
- `LuscherColorFirst` - первый проход теста Люшера
- `LuscherColorSecond` - второй проход теста Люшера

**Существующие связи:**
- `Company` → `SurveyCycleForCompany` (1:N)
- `SurveyCycleForCompany` → `SurveyCycleForUser` (1:N)
- `SurveyCycleForUser` → `LuscherColorFirst/LuscherColorSecond` (1:1)

### 1.2 Расширение для социометрии

Социометрия будет интегрирована как дополнительный тип тестирования в существующую систему:

```python
# Новые модели для социометрии
class SociometricCriterion(BaseTabitModel):
    """Критерии социометрического тестирования"""
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str]
    choice_type: Mapped[ChoiceType]  # POSITIVE, NEGATIVE, NEUTRAL
    max_choices: Mapped[int]
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))

class SociometricChoice(BaseTabitModel):
    """Выборы в социометрическом тесте"""
    id: Mapped[int_pk]
    participant_id: Mapped[UUID] = mapped_column(ForeignKey('companyuser.id'))
    chosen_employee_id: Mapped[UUID] = mapped_column(ForeignKey('companyuser.id'))
    criterion_id: Mapped[int] = mapped_column(ForeignKey('sociometriccriterion.id'))
    cycle_user_id: Mapped[int] = mapped_column(ForeignKey('surveycycleforuser.id'))
    preference_rank: Mapped[int | None]
    choice_type: Mapped[ChoiceType]
```

**Новые связи:**
- `Company` → `SociometricCriterion` (1:N)
- `SurveyCycleForUser` → `SociometricChoice` (1:N)
- `CompanyUser` → `SociometricChoice` (как participant) (1:N)
- `CompanyUser` → `SociometricChoice` (как chosen_employee) (1:N)

## 2. Определение социометрических критериев

### 2.1 Структура критериев

Критерии социометрии должны быть гибкими и настраиваемыми для каждой компании:

```python
# Примеры критериев для Tabit
SOCIOMETRIC_CRITERIA = {
    "task_oriented": {
        "critical_project": "С кем бы вы выбрали работать над критически важным проектом?",
        "technical_help": "К кому бы вы обратились за помощью в решении сложной технической проблемы?",
        "leadership": "Кого бы вы выбрали для руководства новой инициативой?"
    },
    "social_emotional": {
        "personal_support": "К кому бы вы обратились за личным советом?",
        "mentoring": "Кого бы вы выбрали в качестве наставника?",
        "informal_time": "С кем вам нравится проводить неформальное время?"
    },
    "influence_dynamics": {
        "informal_influence": "Кто обладает наибольшим неформальным влиянием в команде?",
        "information_flow": "На кого вы полагаетесь для получения точной информации?"
    }
}
```

### 2.2 Правила валидации

```python
# Бизнес-правила для социометрических выборов
SOCIOMETRIC_RULES = {
    "self_exclusion": "Участник не может выбирать себя",
    "max_choices_per_criterion": "Максимальное количество выборов по критерию",
    "unique_choices": "Уникальность выборов в рамках критерия",
    "ranking_consistency": "Последовательность ранжирования"
}
```

## 3. Последовательная оценка: Люшер → Социометрия → Люшер

### 3.1 Интеграция с существующей логикой

Расширение существующей бизнес-логики `luscher.py`:

```python
# Новые функции в luscher.py
async def analyze_emotional_context(session: AsyncSession, cycle_user_id: int) -> dict:
    """Анализ эмоционального контекста перед социометрией"""
    luscher_first = await luscher_color_first_crud.get_by_cycle(session, cycle_user_id)
    return {
        'stress_level': get_stress_level(luscher_first),
        'emotional_state': get_emotional_state(luscher_first),
        'social_readiness': assess_social_readiness(luscher_first)
    }

async def compare_emotional_changes(
    session: AsyncSession,
    cycle_user_id: int
) -> dict:
    """Сравнение эмоционального состояния до и после социометрии"""
    luscher_first = await luscher_color_first_crud.get_by_cycle(session, cycle_user_id)
    luscher_second = await luscher_color_second_crud.get_by_cycle(session, cycle_user_id)

    return {
        'before_sociometry': analyze_emotional_context(session, cycle_user_id),
        'after_sociometry': analyze_emotional_context(session, cycle_user_id),
        'changes': calculate_emotional_changes(luscher_first, luscher_second)
    }
```

### 3.2 Корреляционный анализ

```python
async def correlate_emotions_with_sociometric_choices(
    session: AsyncSession,
    cycle_company_id: int
) -> dict:
    """Корреляция эмоционального состояния с социометрическими выборами"""
    # Получаем все результаты Люшера и социометрии для цикла
    emotional_data = await get_all_luscher_results(session, cycle_company_id)
    sociometric_data = await get_all_sociometric_results(session, cycle_company_id)

    return {
        'stress_impact_on_choices': analyze_stress_impact(emotional_data, sociometric_data),
        'social_position_impact': analyze_social_position_impact(emotional_data, sociometric_data),
        'isolation_effects': analyze_isolation_effects(emotional_data, sociometric_data)
    }

async def validate_user_test_completion(
    session: AsyncSession,
    cycle_user_id: int,
    company_id: int,
    is_moderator: bool = False
) -> bool:
    """Проверить, может ли пользователь завершить тест"""
    progress = await get_test_progress(session, cycle_user_id, company_id)

    # Порог завершения теста
    # Модераторы не проходят тесты - они их создают и управляют
    min_percentage = 100.0  # Все пользователи должны ответить на все вопросы

    return progress["progress_percentage"] >= min_percentage

async def get_user_strategy_restrictions(is_moderator: bool) -> dict:
    """Получить ограничения стратегий для пользователя"""
    if is_moderator:
        return {
            "available_strategies": ["balanced", "category_focused", "type_focused", "random", "adaptive"],
            "default_strategy": "balanced",
            "can_change_strategy": True,
            "can_use_preferences": True
        }
    else:
        return {
            "available_strategies": ["balanced"],
            "default_strategy": "balanced",
            "can_change_strategy": False,
            "can_use_preferences": False
        }

async def validate_user_completed_all_questions(
    session: AsyncSession,
    cycle_user_id: int
) -> bool:
    """Проверить, что пользователь ответил на все вопросы социометрии"""

    # Получаем все критерии для цикла пользователя
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    cycle_company = await survey_cycle_for_company_crud.get_or_404(
        session, cycle_user.survey_cycle_for_company_id
    )

    # Получаем все критерии компании
    all_criteria = await sociometric_criterion_crud.get_by_company(session, cycle_company.company_id)
    total_criteria = len(all_criteria)

    # Получаем отвеченные вопросы пользователя
    answered_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
    answered_criteria = list(set(choice.criterion_id for choice in answered_choices))
    answered_count = len(answered_criteria)

    # Проверяем, что пользователь ответил на все вопросы
    return answered_count >= total_criteria

async def get_user_test_completion_status(
    session: AsyncSession,
    cycle_user_id: int,
    is_moderator: bool = False
) -> dict:
    """Получить статус завершения теста для пользователя"""

    # Получаем прогресс теста
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    cycle_company = await survey_cycle_for_company_crud.get_or_404(
        session, cycle_user.survey_cycle_for_company_id
    )

    all_criteria = await sociometric_criterion_crud.get_by_company(session, cycle_company.company_id)
    answered_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
    answered_criteria = list(set(choice.criterion_id for choice in answered_choices))

    total_criteria = len(all_criteria)
    answered_count = len(answered_criteria)
    progress_percentage = (answered_count / total_criteria) * 100 if total_criteria > 0 else 0

    # Определяем минимальный порог завершения теста
    # Модераторы не проходят тесты - они их создают и управляют
    min_percentage = 100.0
    can_complete = progress_percentage >= min_percentage

    return {
        "total_questions": total_criteria,
        "answered_questions": answered_count,
        "remaining_questions": total_criteria - answered_count,
        "progress_percentage": progress_percentage,
        "min_required_percentage": min_percentage,
        "can_complete_test": can_complete,
        "is_moderator": is_moderator,
        "completion_message": (
            "Тест завершен" if can_complete else
            f"Необходимо ответить еще на {total_criteria - answered_count} вопросов"
        )
    }
```

## 4. Социометрические индексы и расчеты

### 4.1 Основные индексы

```python
class SociometricIndices:
    """Класс для расчета социометрических индексов"""

    @staticmethod
    def calculate_popularity(choices_data: list) -> dict:
        """Расчет популярности (степень входа)"""
        popularity_scores = {}
        for choice in choices_data:
            if choice.choice_type == ChoiceType.POSITIVE:
                popularity_scores[choice.chosen_employee_id] = \
                    popularity_scores.get(choice.chosen_employee_id, 0) + 1
        return popularity_scores

    @staticmethod
    def calculate_rejection(choices_data: list) -> dict:
        """Расчет отторжения (отрицательная степень входа)"""
        rejection_scores = {}
        for choice in choices_data:
            if choice.choice_type == ChoiceType.NEGATIVE:
                rejection_scores[choice.chosen_employee_id] = \
                    rejection_scores.get(choice.chosen_employee_id, 0) + 1
        return rejection_scores

    @staticmethod
    def calculate_expansiveness(choices_data: list) -> dict:
        """Расчет экспансивности (степень выхода)"""
        expansiveness_scores = {}
        for choice in choices_data:
            expansiveness_scores[choice.participant_id] = \
                expansiveness_scores.get(choice.participant_id, 0) + 1
        return expansiveness_scores

    @staticmethod
    def calculate_mutual_choices(choices_data: list) -> list:
        """Расчет взаимных выборов"""
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
    def calculate_group_cohesion(choices_data: list, total_participants: int) -> float:
        """Расчет сплоченности группы"""
        total_possible_choices = total_participants * (total_participants - 1)
        actual_positive_choices = len([
            c for c in choices_data
            if c.choice_type == ChoiceType.POSITIVE
        ])
        return actual_positive_choices / total_possible_choices if total_possible_choices > 0 else 0
```

### 4.2 Выявление изолятов и звезд

```python
def identify_sociometric_stars_and_isolates(
    popularity_scores: dict,
    rejection_scores: dict,
    threshold: float = 0.3
) -> dict:
    """Выявление социометрических звезд и изолятов"""
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

## 5. API эндпоинты для социометрии

### 5.1 Управление критериями

```python
@router.post(
    '/sociometric/criteria',
    response_model=SociometricCriterionResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Создать социометрический критерий',
    status_code=status.HTTP_201_CREATED,
)
async def create_sociometric_criterion(
    company_slug: str,
    criterion: SociometricCriterionCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> SociometricCriterionResponseSchema:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await sociometric_criterion_crud.create(
        session, criterion, company_id=company.id
    )

@router.get(
    '/sociometric/criteria',
    response_model=list[SociometricCriterionResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить критерии социометрии',
)
async def get_sociometric_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[SociometricCriterionResponseSchema]:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await sociometric_criterion_crud.get_multi(
        session, filters={'company_id': company.id}
    )
```

### 5.2 Сохранение социометрических выборов

```python
@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric',
    response_model=SociometricChoiceResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Сохранить социометрические выборы',
    status_code=status.HTTP_201_CREATED,
)
async def create_sociometric_choices(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    choices: list[SociometricChoiceCreateSchema],
    session: AsyncSession = Depends(get_async_session),
) -> SociometricChoiceResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Валидация выборов
    await validate_sociometric_choices(session, choices, cycle_user_id)

    return await sociometric_choice_crud.create_choices(
        session, choices, cycle_user_id=cycle_user_id
    )
```

### 5.3 Получение результатов социометрии

```python
@router.get(
    '/cycle/{cycle_company_id}/sociometric/results',
    dependencies=[Depends(current_company_moderator)],
    summary='Получить результаты социометрии для цикла',
)
async def get_sociometric_results(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)

    return await calculate_sociometric_results(session, cycle_company_id)

@router.get(
    '/cycle/{cycle_company_id}/sociometric/combined-analysis',
    dependencies=[Depends(current_company_moderator)],
    summary='Комбинированный анализ Люшера и социометрии',
)
async def get_combined_analysis(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)

    return await correlate_emotions_with_sociometric_choices(session, cycle_company_id)
```

## 6. Схемы данных

### 6.1 Схемы для социометрии

```python
# schemas/sociometric.py
class SociometricCriterionBaseSchema(BaseModel):
    name: str
    description: str
    choice_type: ChoiceType
    max_choices: int

class SociometricCriterionCreateSchema(SociometricCriterionBaseSchema):
    model_config = ConfigDict(extra='forbid')

class SociometricCriterionResponseSchema(SociometricCriterionBaseSchema):
    id: int
    company_id: int
    model_config = ConfigDict(from_attributes=True)

class SociometricChoiceBaseSchema(BaseModel):
    chosen_employee_id: UUID
    criterion_id: int
    preference_rank: int | None = None
    choice_type: ChoiceType

class SociometricChoiceCreateSchema(SociometricChoiceBaseSchema):
    @model_validator(mode='after')
    def validate_choice(self):
        """Валидация социометрического выбора"""
        if self.preference_rank is not None and self.preference_rank < 1:
            raise ValueError("Ранг предпочтения должен быть положительным")
        return self

class SociometricChoiceResponseSchema(SociometricChoiceBaseSchema):
    id: int
    participant_id: UUID
    cycle_user_id: int
    model_config = ConfigDict(from_attributes=True)
```

## 7. Валидация и бизнес-правила

### 7.1 Валидация выборов

```python
async def validate_sociometric_choices(
    session: AsyncSession,
    choices: list[SociometricChoiceCreateSchema],
    cycle_user_id: int
) -> None:
    """Валидация социометрических выборов"""

    # Получаем информацию о пользователе
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    participant_id = cycle_user.user_id

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
```

## 8. Интерпретация результатов

### 8.1 Генерация отчетов

```python
async def generate_sociometric_report(
    session: AsyncSession,
    cycle_company_id: int
) -> dict:
    """Генерация полного отчета по социометрии"""

    # Получаем все данные
    choices_data = await sociometric_choice_crud.get_by_cycle_company(
        session, cycle_company_id
    )
    participants = await get_cycle_participants(session, cycle_company_id)

    # Рассчитываем индексы
    popularity_scores = SociometricIndices.calculate_popularity(choices_data)
    rejection_scores = SociometricIndices.calculate_rejection(choices_data)
    expansiveness_scores = SociometricIndices.calculate_expansiveness(choices_data)
    mutual_choices = SociometricIndices.calculate_mutual_choices(choices_data)
    group_cohesion = SociometricIndices.calculate_group_cohesion(
        choices_data, len(participants)
    )

    # Выявляем звезд и изолятов
    stars_and_isolates = identify_sociometric_stars_and_isolates(
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
```

### 8.2 Рекомендации для HR

```python
def generate_recommendations(
    popularity_scores: dict,
    rejection_scores: dict,
    stars_and_isolates: dict,
    group_cohesion: float
) -> list[str]:
    """Генерация рекомендаций для HR на основе социометрических данных"""

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

## 9. Этические соображения и конфиденциальность

### 9.1 Принципы обработки данных

1. **Информированное согласие**: Все участники должны быть проинформированы о целях тестирования
2. **Добровольность участия**: Участие в социометрии должно быть добровольным
3. **Конфиденциальность**: Индивидуальные результаты доступны только HR и руководству
4. **Ограничение использования**: Данные используются только для развития команды, не для оценки производительности

### 9.2 Ограничения интерпретации

```python
# Предупреждения в отчетах
INTERPRETATION_WARNINGS = [
    "Результаты социометрии отражают восприятие на момент тестирования",
    "Эмоциональное состояние может влиять на социальные выборы",
    "Необходимо учитывать контекст и другие факторы",
    "Избегайте упрощенных интерпретаций и навешивания ярлыков"
]
```

## 10. Безопасность и ограничения для пользователей

### 10.1 Ограничения для обычных пользователей

В системе социометрии Tabit установлены строгие ограничения для обычных пользователей:

1. **Стратегия выбора вопросов**: Только сбалансированная стратегия (BALANCED)
2. **Изменение параметров теста**: Недоступно
3. **Пользовательские предпочтения**: Отключены
4. **Минимальный порог завершения**: 100% вопросов (все вопросы должны быть отвечены)
5. **Адаптивные алгоритмы**: Отключены

### 10.2 Возможности модераторов

Модераторы компании имеют расширенные возможности для управления тестированием:

1. **Все стратегии**: Доступны все типы стратегий выбора вопросов для настройки тестов
2. **Изменение параметров**: Могут настраивать стратегии тестирования
3. **Адаптивные алгоритмы**: Могут использовать адаптивный выбор вопросов для настройки
4. **Управление критериями**: Могут создавать, редактировать и удалять критерии социометрии
5. **Пользовательские предпочтения**: Могут сохранять и использовать для настройки тестирования
6. **Модераторы не проходят тесты**: Они их создают и управляют

### 10.3 Техническая реализация ограничений

```python
# Пример проверки прав доступа в API
async def get_sociometric_questions(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    # Проверяем права пользователя
    current_user = await get_current_user(session)
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    # Принудительно устанавливаем сбалансированную стратегию для обычных пользователей
    if not is_moderator:
        strategy = QuestionSelectionStrategy.BALANCED
        user_preferences = None
        # Проверяем, что пользователь ответил на все вопросы
        if not await validate_user_completed_all_questions(session, cycle_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для завершения теста необходимо ответить на все вопросы"
            )
    else:
        # Модераторы не проходят тесты - они их создают и управляют
        # Но могут настраивать стратегии для тестирования других пользователей
        strategy = user_requested_strategy
        user_preferences = await get_moderator_preferences(session, cycle_user_id)

    # Выбираем вопросы с учетом ограничений
    selector = SociometricQuestionSelector(strategy, is_moderator=is_moderator)
    questions = await selector.select_questions(
        available_criteria=criteria,
        user_preferences=user_preferences
    )

    return {
        "questions": questions,
        "strategy": strategy,
        "is_moderator": is_moderator,
        "can_change_strategy": is_moderator
    }
```

## 11. План внедрения

### 11.1 Этапы разработки

1. **Этап 1**: Создание моделей данных и схем
2. **Этап 2**: Реализация CRUD операций
3. **Этап 3**: Разработка бизнес-логики и валидации
4. **Этап 4**: Создание API эндпоинтов
5. **Этап 5**: Интеграция с существующей системой Люшера
6. **Этап 6**: Тестирование и валидация
7. **Этап 7**: Развертывание и обучение пользователей

### 10.2 Технические требования

- Расширение существующих моделей `survey.py`
- Создание новых CRUD классов в `crud_surveys.py`
- Добавление схем в `schemas/survey.py`
- Создание новых эндпоинтов в `endpoints.py`
- Расширение бизнес-логики в `luscher.py`

### 11.3 Метрики успеха

- Увеличение понимания командной динамики
- Снижение конфликтов в командах
- Улучшение социальной интеграции изолятов
- Повышение эффективности командной работы
- Положительная обратная связь от HR-специалистов

### 11.4 Безопасность и стандартизация

Реализованные ограничения обеспечивают:

- **Стандартизацию тестирования**: Все обычные пользователи проходят одинаковый тест
- **Защиту от манипуляций**: Пользователи не могут влиять на выбор вопросов
- **Объективность результатов**: Исключена возможность адаптации под предпочтения
- **Контроль качества**: Модераторы могут настраивать тестирование при необходимости
- **Соответствие этическим нормам**: Соблюдение принципов научного тестирования
