"""
Эндпоинты управления компаниями (Tabit Management - Companies).
"""

from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validator import validator_check_object_exists
from src.companies.crud import company_crud
from src.companies.schemas import (
    CompanyCreateSchema,
    CompanyResponseSchema,
    CompanyUpdateSchema,
)
from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    response_model=List[CompanyResponseSchema],
    # TODO: Зависимость супер_админ_табит.
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
    # TODO: Зависимость супер_админ_табит.
    status_code=HTTPStatus.CREATED,
    summary='Создать новую компанию',
)
async def create_company(
    company: CompanyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает новую компанию. Доступно только админам сервиса.
    """
    return await company_crud.create(session, company)


@router.patch(
    '/{company_slug}/',
    response_model=CompanyResponseSchema,
    # TODO: Зависимость супер_админ_табит.
    summary='Обновить данные компании',
)
async def update_company(
    company_slug: str,
    object_in: CompanyUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные компании по её slug. Доступно только админам сервиса.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_crud.update(session, company, object_in)


@router.delete(
    '/{company_slug}/',
    response_model=CompanyResponseSchema,
    summary='Удалить компанию',
)
async def delete_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет компанию по её slug. Доступно только админам сервиса.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_crud.remove(session, company)
