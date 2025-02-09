"""
Эндпоинты управления компаниями (Tabit Management - Companies).
"""

from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_admin_tabit
from src.api.v1.constants import Summary
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
    dependencies=[Depends(current_admin_tabit)],
    summary=Summary.TABIT_MANAGEMENT_COMPANY_LIST,
)
async def get_companies(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех компаний. Доступно только администраторам сервиса.
    """
    return await company_crud.get_multi(session)


@router.post(
    '/',
    response_model=CompanyResponseSchema,
    dependencies=[Depends(current_admin_tabit)],
    status_code=HTTPStatus.CREATED,
    summary=Summary.TABIT_MANAGEMENT_COMPANY_CREATE,
)
async def create_company(
    company: CompanyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает новую компанию. Доступно только администраторам сервиса.
    """
    return await company_crud.create(session, company)


@router.patch(
    '/{company_slug}',
    response_model=CompanyResponseSchema,
    dependencies=[Depends(current_admin_tabit)],
    summary=Summary.TABIT_MANAGEMENT_COMPANY_UPDATE,
)
async def update_company(
    company_slug: str,
    object_in: CompanyUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные компании по её `slug`. Доступно только администраторам сервиса.
    :param `company_slug`: Уникальный идентификатор компании (`slug`).
    """
    company = await validator_check_object_exists(
        session, company_crud, object_slug=company_slug
    )
    return await company_crud.update(session, company, object_in)


@router.delete(
    '/{company_slug}',
    response_model=CompanyResponseSchema,
    dependencies=[Depends(current_admin_tabit)],
    summary=Summary.TABIT_MANAGEMENT_COMPANY_DELETE,
)
async def delete_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет компанию по её `slug`. Доступно только администраторам сервиса.
    :param `company_slug`: Уникальный идентификатор компании (`slug`).
    """
    company = await validator_check_object_exists(
        session, company_crud, object_slug=company_slug
    )
    return await company_crud.remove(session, company)
