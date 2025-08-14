from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.luscher import get_response_result
from src.business_logic.sociometric_question_selector import SociometricQuestionSelector
from src.business_logic.sociometrics import check_user_is_moderator
from src.constants.sociometric import QuestionSelectionStrategy
from src.core.auth.dependencies import (
    current_company_moderator,
    current_user_tabit,
)
from src.core.database.db_depends import get_async_session
from src.crud.crud_company import company_crud
from src.crud.crud_surveys import (
    luscher_color_first_crud,
    luscher_color_second_crud,
    sociometric_choice_crud,
    sociometric_criterion_crud,
    survey_cycle_for_company_crud,
    survey_cycle_for_user_crud,
)
from src.features_v1.validators import (
    check_cycle_not_completed,
    check_cycle_overdue_date,
    check_survey_this_week,
    validator_survey_in_cycle_exists,
)
from src.schemas.sociometric import (
    CombinedAnalysisSchema,
    SociometricChoiceCreateSchema,
    SociometricChoiceResponseSchema,
    SociometricCriterionCreateSchema,
    SociometricCriterionResponseSchema,
    SociometricCriterionUpdateSchema,
    SociometricResultsSchema,
)
from src.schemas.survey import (
    CycleForCompanyCreateSchema,
    CycleForCompanyResponseSchema,
    CycleForCompanyUpdateSchema,
    CycleForUserResponseSchema,
    LuscherCreateSchema,
    LuscherResponseSchema,
)
from src.services.sociometric_criteria_factory import SociometricCriteriaFactory

router = APIRouter(prefix='/{company_slug}/surveys')


# TODO: Во всех энпоинтах нужно тонко настроить уровень доступа.
# Например. Смотреть результаты теста можно только модеру от компании и тому, кто тест проходил.
@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/luscher_first/{luscher_id}',
    response_model=LuscherResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить ответы пользователя на первый тест Люшера',
    description='По id теста Люшера получить ответы, которые сделал пользователь.',
    status_code=status.HTTP_200_OK,
)
async def get_luscher_first(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    luscher_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> LuscherResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    return await luscher_color_first_crud.get_or_404(session, luscher_id)


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/luscher_first',
    response_model=LuscherResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Сохранить ответы пользователя на первый тест Люшера',
    description='Создаст новую запись с ответами пользователя на тест Люшера.',
    status_code=status.HTTP_201_CREATED,
)
async def create_luscher_first(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    luscher: LuscherCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LuscherResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    await validator_survey_in_cycle_exists(session, luscher_color_first_crud, cycle_user_id)
    return await luscher_color_first_crud.create_survey(
        session,
        luscher,
        cycle_for_user=cycle_user_id,
    )


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/luscher_second/{luscher_id}',
    response_model=LuscherResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить ответы пользователя на второй тест Люшера',
    description='По id теста Люшера получить ответы, которые сделал пользователь.',
    status_code=status.HTTP_200_OK,
)
async def get_luscher_second(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    luscher_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> LuscherResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    return await luscher_color_second_crud.get_or_404(session, luscher_id)


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/luscher_second',
    response_model=LuscherResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Сохранить ответы пользователя на второй тест Люшера',
    description='Создаст новую запись с ответами пользователя на тест Люшера.',
    status_code=status.HTTP_201_CREATED,
)
async def create_luscher_second(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    luscher: LuscherCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LuscherResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    await validator_survey_in_cycle_exists(session, luscher_color_second_crud, cycle_user_id)
    return await luscher_color_second_crud.create_survey(
        session,
        luscher,
        cycle_for_user=cycle_user_id,
    )


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/luscher_result',
    dependencies=[Depends(current_user_tabit)],
    summary='Получить результат прохождения теста Люшера.',
    description='Получить результат прохождения теста Люшера.',
    status_code=status.HTTP_200_OK,
)
async def get_luscher_result(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
    return await get_response_result(session, cycle_user_id)


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}',
    response_model=CycleForUserResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить цикл тестов для пользователя по id цикла',
    description='Получить цикл тестов для пользователя по id цикла',
    status_code=status.HTTP_200_OK,
)
async def get_cycle_for_user_by_id(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CycleForUserResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    return await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)


@router.get(
    '/cycle_for_user/{user_id}',
    response_model=list[CycleForUserResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить все циклы тестов для пользователя',
    description='Получить все циклы тестов для пользователя по id пользователя.',
    status_code=status.HTTP_200_OK,
)
async def get_cycles_for_user_by_user_id(
    company_slug: str,
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> list[CycleForUserResponseSchema]:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await survey_cycle_for_user_crud.get_multi(session, filters={'user_id': user_id})


@router.get(
    '/cycle',
    response_model=list[CycleForCompanyResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить все циклы тестов компании',
    description='Получить все циклы тестов компании',
    status_code=status.HTTP_200_OK,
)
async def get_cycles_for_companies(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[CycleForCompanyResponseSchema]:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await survey_cycle_for_company_crud.get_multi(
        session, filters={'company_id': company.id}, order_by=['-date']
    )


@router.get(
    '/cycle/{cycle_company_id}',
    response_model=CycleForCompanyResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить цикл тестов для компании по id цикла',
    description='Получить цикл тестов для компании по id цикла',
    status_code=status.HTTP_200_OK,
)
async def get_cycle_for_company_by_id(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CycleForCompanyResponseSchema:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)


# TODO: Пока создавать может только модератор. Ещё должен способен создавать начальник отдела.
@router.post(
    '/cycle',
    response_model=CycleForCompanyResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Создать цикл тестов для компании',
    description=(
        'Создать цикл тестов для компании, одновременно создадутся '
        'тесты циклов для пользователей внутри данной компании.'
    ),
    status_code=status.HTTP_201_CREATED,
)
async def create_cycle_for_company(
    company_slug: str,
    cycle: CycleForCompanyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CycleForCompanyResponseSchema:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await check_survey_this_week(session, cycle.date, company.id)
    return await survey_cycle_for_company_crud.create_cycle(session, cycle, company_id=company.id)


# TODO: Пока изменять и удалять может любой модератор от компании, а не только тот который создал.
@router.patch(
    '/cycle/{cycle_company_id}',
    response_model=CycleForCompanyResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Изменить цикл тестов для компании',
    description=(
        'Изменит цикл тестов для компании, одновременно изменятся '
        'тесты циклов для пользователей внутри данной компании.'
    ),
    status_code=status.HTTP_200_OK,
)
async def update_cycle_for_company(
    company_slug: str,
    cycle_company_id: int,
    cycle: CycleForCompanyUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CycleForCompanyResponseSchema:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    cycle_db = await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    check_cycle_not_completed(cycle_db)
    check_cycle_overdue_date(cycle_db)
    await check_survey_this_week(session, cycle.date, company.id, cycle_db)
    return await survey_cycle_for_company_crud.update_cycle(session, cycle_db, cycle)


@router.delete(
    '/cycle/{cycle_company_id}',
    dependencies=[Depends(current_company_moderator)],
    summary='Удалить цикл тестов для компании',
    description=(
        'Удалит цикл тестов для компании, одновременно удалит '
        'тесты циклов для пользователей внутри данной компании '
        'и все их ответы, внутри данных циклов.'
    ),
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cycle_for_company(
    company_slug: str,
    cycle_company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    cycle_db = await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    check_cycle_not_completed(cycle_db)
    await survey_cycle_for_company_crud.remove(session, cycle_db)


# ============================================================================
# СОЦИОМЕТРИЧЕСКИЕ ЭНДПОИНТЫ
# ============================================================================


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
    response_model=list[SociometricCriterionResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить критерии социометрии',
    description='Получить все критерии социометрии для компании.',
)
async def get_sociometric_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[SociometricCriterionResponseSchema]:
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


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric',
    response_model=list[SociometricChoiceResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Сохранить социометрические выборы',
    description='Создать социометрические выборы для пользователя в цикле.',
    status_code=status.HTTP_201_CREATED,
)
async def create_sociometric_choices(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    choices: list[SociometricChoiceCreateSchema],
    session: AsyncSession = Depends(get_async_session),
) -> list[SociometricChoiceResponseSchema]:
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
    response_model=list[SociometricChoiceResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить социометрические выборы пользователя',
    description='Получить все социометрические выборы пользователя в цикле.',
)
async def get_sociometric_choices(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> list[SociometricChoiceResponseSchema]:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    return await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)


@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions',
    dependencies=[Depends(current_user_tabit)],
    summary='Получить вопросы для социометрического теста',
    description=(
        'Получить 4 вопроса для текущей итерации социометрического теста. '
        'Обычные пользователи используют только сбалансированную стратегию.'
    ),
)
async def get_sociometric_questions(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_user_tabit),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Получаем доступные критерии для компании
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    available_criteria = await sociometric_criterion_crud.get_by_company(session, company.id)

    # Получаем предыдущие вопросы (если есть)
    previous_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
    previous_questions = list(set(choice.criterion_id for choice in previous_choices))

    # Определяем, является ли пользователь модератором
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    # Для обычных пользователей всегда используем сбалансированную стратегию
    strategy = QuestionSelectionStrategy.BALANCED
    if is_moderator:
        # Если модератор ранее сохранял стратегию - используем её
        from src.crud.crud_surveys import sociometric_strategy_preference_crud

        pref = await sociometric_strategy_preference_crud.get_preference(session, cycle_user_id)
        if pref:
            strategy = QuestionSelectionStrategy(pref.strategy)

    selector = SociometricQuestionSelector(strategy, is_moderator=is_moderator)
    selected_questions = await selector.select_questions(
        session=session,
        available_criteria=available_criteria,
        questions_per_iteration=4,
        previous_questions=previous_questions,
        user_preferences=None,
    )

    return {
        'iteration': len(previous_questions) // 4 + 1,
        'total_iterations': len(available_criteria) // 4,
        'strategy': strategy,
        'is_moderator': is_moderator,
        'questions': [
            {
                'criterion_id': q['criterion_id'],
                'name': q['name'],
                'description': q['description'],
                'choice_type': q['choice_type'],
                'max_choices': q['max_choices'],
                'category': q['category'],
            }
            for q in selected_questions
        ],
    }


@router.post(
    '/sociometric/criteria/default',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать стандартные критерии социометрии',
    description=(
        'Создать полный набор стандартных критериев социометрии для компании. '
        'Доступно только модераторам.'
    ),
    status_code=status.HTTP_201_CREATED,
)
async def create_default_sociometric_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    ids = await SociometricCriteriaFactory.create_default_criteria_for_company(session, company.id)
    return {
        'message': 'Стандартные критерии социометрии созданы',
        'created_criteria_count': len(ids),
        'criteria_ids': ids,
    }


@router.post(
    '/sociometric/criteria/tactical',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать критерии тактического лидерства',
    description=(
        'Создать критерии тактического лидерства для компании. Доступно только модераторам.'
    ),
    status_code=status.HTTP_201_CREATED,
)
async def create_tactical_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    ids = await SociometricCriteriaFactory.create_tactical_criteria_for_company(
        session, company.id
    )
    return {
        'message': 'Критерии тактического лидерства созданы',
        'created_criteria_count': len(ids),
        'criteria_ids': ids,
    }


@router.post(
    '/sociometric/criteria/strategic',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать критерии стратегического лидерства',
    description=(
        'Создать критерии стратегического лидерства для компании. Доступно только модераторам.'
    ),
    status_code=status.HTTP_201_CREATED,
)
async def create_strategic_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    ids = await SociometricCriteriaFactory.create_strategic_criteria_for_company(
        session, company.id
    )
    return {
        'message': 'Критерии стратегического лидерства созданы',
        'created_criteria_count': len(ids),
        'criteria_ids': ids,
    }


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions/strategy',
    dependencies=[Depends(current_company_moderator)],
    summary='Изменить стратегию выбора вопросов',
    description=(
        'Изменить стратегию выбора вопросов для социометрического теста. '
        'Доступно только модераторам.'
    ),
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

    # Сохраняем предпочтение стратегии
    from src.crud.crud_surveys import sociometric_strategy_preference_crud

    await sociometric_strategy_preference_crud.upsert_preference(session, cycle_user_id, strategy)

    return {
        'message': f'Стратегия изменена на {strategy}',
        'strategy': strategy,
        'note': 'Изменение стратегии доступно только модераторам',
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
    current_user=Depends(current_user_tabit),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Определяем, является ли пользователь модератором
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    from src.business_logic.sociometrics import get_user_test_completion_status

    completion_status = await get_user_test_completion_status(session, cycle_user_id, is_moderator)

    return completion_status


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

    from src.business_logic.sociometrics import generate_sociometric_report

    report_data = await generate_sociometric_report(session, cycle_company_id)

    return SociometricResultsSchema(
        cycle_info=report_data['cycle_info'],
        individual_scores=report_data['individual_scores'],
        group_metrics=report_data['group_metrics'],
        special_identifications=report_data['special_identifications'],
        recommendations=report_data['recommendations'],
    )


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

    from src.business_logic.sociometrics import (
        analyze_emotional_context_for_cycle,
        correlate_emotions_with_sociometric_choices,
        generate_combined_recommendations,
        generate_sociometric_report,
    )

    # Получаем результаты социометрии
    sociometric_results = await generate_sociometric_report(session, cycle_company_id)

    # Получаем результаты Люшера
    emotional_context = await analyze_emotional_context_for_cycle(session, cycle_company_id)

    # Корреляционный анализ
    correlations = await correlate_emotions_with_sociometric_choices(session, cycle_company_id)

    return CombinedAnalysisSchema(
        emotional_context=emotional_context,
        sociometric_results=sociometric_results,
        correlations=correlations,
        recommendations=generate_combined_recommendations(
            emotional_context, sociometric_results, correlations
        ),
    )
