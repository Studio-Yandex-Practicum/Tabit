from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import Description, Summary
from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/{company_slug}/surveys',
    summary=Summary.SURVEYS_LIST,
    description=Description.SURVEYS_LIST,
    dependencies=[Depends(get_async_session)],
)
async def get_surveys(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает список всех опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Список опросов компании пока пуст'}


@router.post(
    '/{company_slug}/surveys',
    summary=Summary.SURVEYS_CREATE,
    description=Description.SURVEYS_CREATE,
    dependencies=[Depends(get_async_session)],
)
async def create_survey(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Создает новый опрос."""
    # TODO: Проверить существование компании
    return {'message': 'Создание опроса для компании временно недоступно'}


@router.get(
    '/{company_slug}/surveys/{uuid}',
    summary=Summary.SURVEYS_EMPLOYEE,
    description=Description.SURVEYS_EMPLOYEE,
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
    '/{company_slug}/surveys/{uuid}/{survey_id}',
    summary=Summary.SURVEY_EMPLOYEE,
    description=Description.SURVEY_EMPLOYEE,
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
    '/{company_slug}/surveys/results/general',
    summary=Summary.SURVEYS_RESULT,
    description=Description.SURVEYS_RESULT,
    dependencies=[Depends(get_async_session)],
)
async def get_general_survey_results(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает общий результат опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Общий результат опросов компании пока пуст'}


@router.get(
    '/{company_slug}/surveys/results/personalized',
    summary=Summary.SURVEYS_RESULT_PERSONALIZED,
    description=Description.SURVEYS_RESULT_PERSONALIZED,
    dependencies=[Depends(get_async_session)],
)
async def get_personalized_survey_results(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает персонализированный результат опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Персонализированный результат опросов компании пока пуст'}


@router.get(
    '/{company_slug}/surveys/results/dynamics',
    summary=Summary.SURVEYS_RESULT_DYNAMICS,
    description=Description.SURVEYS_RESULT_DYNAMICS,
    dependencies=[Depends(get_async_session)],
)
async def get_dynamics_survey_results_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Получает динамику результатов опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Динамика результатов опросов компании пока пуст'}


@router.post(
    '/{company_slug}/surveys/manage',
    summary=Summary.SURVEYS_MANAGE,
    description=Description.SURVEYS_MANAGE,
    dependencies=[Depends(get_async_session)],
)
async def manage_surveys_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Управление опросами компании."""
    # TODO: Проверить существование компании
    return {'message': 'Управление опросами компании временно недоступно'}


@router.delete(
    '/{company_slug}/surveys/manage/',
    summary=Summary.SURVEYS_DELETE,
    description=Description.SURVEYS_DELETE,
    dependencies=[Depends(get_async_session)],
)
async def delete_surveys_company(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Удаление опросов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Удаление опросов компании временно недоступно'}
