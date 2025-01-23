from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.schemas import (
    CompanyCreate,
    CompanyDB,
    CompanyDBForUser,
    CompanyUpdate,
    CompanyUpdateForUser,
)
from src.database.db_depends import get_async_session
from src.users.models import UserTabit

current_user = None  # TODO: сделать проверку на авторизированного юзера
current_superuser = None  # TODO: сделать проверку на супер юзера

router = APIRouter()


@router.get(
    '/',
    response_model=list[CompanyDB],
    # dependencies=[Depends(current_superuser)],
    summary='Получить список всех компаний. Только для суперюзера.',
)
async def get_all_companies(session: AsyncSession = Depends(get_async_session)):
    """Выводит список всех компаний. Доступно только супер юзеру."""
    # TODO: реализовать ответ от БД
    # return await companies_crud.get_multi(session)
    return {
        'companies': [
            'company_1',
            'company_2',
            'company_3',
        ]
    }


@router.get(
    '/{company_id}',
    response_model=CompanyDB,
    # dependencies=[Depends(current_superuser)],
)
async def get_company_by_id(
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Выводит описание конкретной компании. Доступно только супер юзеру."""
    # TODO: реализовать ответ от БД
    # return await companies_crud.get(company_id, session)
    return {'companies': f'company_{company_id}'}


@router.post(
    '',
    response_model=CompanyDB,
)
async def create_company(
    company: CompanyCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создаст новую компанию. Доступно только супер юзеру."""
    # TODO: реализовать ответ от БД
    return {'companies': 'company_new'}


@router.patch(
    '/{company_id}',
    response_model=CompanyUpdate,
    # dependencies=[Depends(current_superuser)],
)
async def partially_update_company(
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Частично поменяет данные компании. Доступно только супер юзеру."""
    # TODO: реализовать ответ от БД
    return {'companies': f'company_{company_id}'}


@router.delete(
    '/{company_id}',
    response_model=CompanyDB,
    # dependencies=[Depends(current_superuser)],
)
async def remove_company(
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаляет компанию. Доступно только супер юзеру. Нельзя удалять компанию, срок лицензии ещё не
    истек."""
    # TODO: реализовать ответ от БД
    return {'companies': f'company_{company_id}'}


@router.get(
    '/my',
    response_model=CompanyDBForUser,
    # dependencies=[Depends(current_user)],
)
async def get_my_company(
    user: UserTabit = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Выводит описание компании, в которой работает запросивший юзер."""
    # TODO: реализовать ответ от БД
    # company_id = get_id_company(user)
    # return await companies_crud.get(company_id, session)
    return {'companies': 'company_my'}


@router.patch(
    '/my',
    response_model=CompanyUpdateForUser,
    # dependencies=[Depends(current_user)],
)
async def partially_update_my_company(
    user: UserTabit = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Изменяет данные компании, в которой работает запросивший юзер."""
    # TODO: реализовать ответ от БД
    return {'companies': 'company_my'}
