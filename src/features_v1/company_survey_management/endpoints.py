from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.luscher import get_response_result
from src.core.auth.dependencies import current_company_moderator, current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud.crud_company import company_crud
from src.crud.crud_surveys import (
    luscher_color_first_crud,
    luscher_color_second_crud,
    survey_cycle_for_company_crud,
    survey_cycle_for_user_crud,
)
from src.features_v1.validators import (
    check_cycle_not_completed,
    check_cycle_overdue_date,
    check_survey_this_week,
    validator_survey_in_cycle_exists,
)
from src.schemas.survey import (
    CycleForCompanyCreateSchema,
    CycleForCompanyResponseSchema,
    CycleForCompanyUpdateSchema,
    CycleForUserResponseSchema,
    LuscherCreateSchema,
    LuscherResponseSchema,
)

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
