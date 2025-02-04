"""
Эндпоинты управления компаниями (Tabit Management - Companies).
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.companies.crud import company_crud
from src.companies.schemas import (
    CompanyCreateSchema,
    CompanyResponseForUserSchema,
    CompanyResponseSchema,
    CompanyUpdateSchema,
    CompanyUpdateForUserSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=List[CompanyResponseSchema],
    summary='Получить список всех компаний',
)
async def get_companies(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех компаний. Доступно только админам сервиса.
    """
    return await company_crud.get_multi(session)


@router.post(
    '/',
    response_model=CompanyResponseSchema,
    summary='Создать новую компанию',
)
async def create_company(
    company: CompanyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает новую компанию. Доступно только админам сервиса.
    """
    new_company = await company_crud.create(session, company)
    return new_company


@router.patch(
    '/{company_slug}/',
    summary='Обновить данные компании',
)
async def update_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные компании по её slug.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    # TODO: Реализовать обновление данных компании
    return {'message': f'Обновление компании {company_slug} временно недоступно'}


@router.delete(
    '/{company_slug}/',
    summary='Удалить компанию',
)
async def delete_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет компанию по её slug.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    # TODO: Реализовать удаление компании
    return {'message': f'Удаление компании {company_slug} временно недоступно'}
