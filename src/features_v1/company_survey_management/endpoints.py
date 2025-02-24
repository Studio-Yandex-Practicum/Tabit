from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех опросов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_surveys(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает список всех опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Список опросов компании пока пуст'}


@router.post(
    '/',
    summary='Создать новый опрос для компании',
    dependencies=[Depends(get_async_session)],
)
async def create_survey(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Создает новый опрос."""
    # TODO: Проверить существование компании
    return {'message': 'Создание опроса для компании временно недоступно'}


@router.get(
    '/{uuid}',
    summary='Получить историю опросов сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def get_employee_survey_history(
    company_slug: str, uuid: UUID, session: AsyncSession = Depends(get_async_session)
):
    """Получает историю опросов сотрудника компании."""
    # TODO: Проверить существование компании
    # TODO: Проверить существование сотрудника
    return {'message': 'История опросов сотрудника компании пока пуста'}


@router.get(
    '/{uuid}/{survey_id}',
    summary='Получить информацию об опросе сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def get_employee_survey_info(
    company_slug: str,
    uuid: UUID,
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию об опросе сотрудника компании."""
    # TODO: Проверить существование компании
    # TODO: Проверить существование сотрудника
    # TODO: Проверить существование опроса
    return {'message': 'Информация об опросе сотрудника компании пока недоступна'}


@router.get(
    '/results/general',
    summary='Получить общий результат опросов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_general_survey_results(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает общий результат опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Общий результат опросов компании пока пуст'}


@router.get(
    '/results/personalized',
    summary='Получить персонализированный результат опросов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_personalized_survey_results(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает персонализированный результат опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Персонализированный результат опросов компании пока пуст'}


@router.get(
    '/results/dynamics',
    summary='Получить динамику результатов опросов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_dynamics_survey_results_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает динамику результатов опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Динамика результатов опросов компании пока пуст'}


@router.post(
    '/manage',
    summary='Управление опросами компании',
    dependencies=[Depends(get_async_session)],
)
async def manage_surveys_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Управление опросами компании."""
    # TODO: Проверить существование компании
    return {'message': 'Управление опросами компании временно недоступно'}


@router.delete(
    '/manage',
    summary='Удалить опросы компании',
    dependencies=[Depends(get_async_session)],
)
async def delete_surveys_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Удаление опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Удаление опросов компании временно недоступно'}
