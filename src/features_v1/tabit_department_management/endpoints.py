"""
Конечные точки управления отделами компаний (Tabit Management - Department).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_admin_tabit
from src.core.database.db_depends import get_async_session
from src.crud.crud_company import company_crud
from src.crud.crud_department import department_crud
from src.features_v1.constants import OPENAPI_EXTRA_ADMIN_AUTH, Description, Summary
from src.features_v1.validators import (
    check_department_in_company,
    check_empty_department,
    check_name_department_in_company,
)
from src.models import Department
from src.schemas.company import (
    CompanyDepartmentCreateSchema,
    CompanyDepartmentResponseSchema,
    CompanyDepartmentUpdateSchema,
)

router = APIRouter(dependencies=[Depends(current_admin_tabit)])


@router.get(
    '/',
    response_model=list[CompanyDepartmentResponseSchema],
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_MANAGEMENT_DEPARTMENTS_LIST,
    description=Description.TABIT_MANAGEMENT_DEPARTMENTS_LIST,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def get_departments_by_company_slug(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> list[Department]:
    """
    Описывает работу конечной точки получения списка отделов компании администраторами сервиса.

    Аргументы декоратора:
        path (str): URL-путь конечной точки.
        response_model (Type[BaseModel]): Модель Pydantic для подготовки ответа.
        status_code (int): HTTP статус код для успешного ответа.
        summary (str): Краткое описание конечной точки.
        description (str): Подробное описание функциональности.
        openapi_extra (dict): дополнительные настройки для открытой документации API.

    Аргументы функции:
        company_slug (str): slug компании, указанный в пути.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        dict: Результат выполнения операции в формате JSON.

    Исключения:
        HTTPException: Возникает при ошибках валидации или обработки запроса.

    Доступ:
        Доступен только администраторам сервиса.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    return await department_crud.get_multi(
        session,
        filters={'company_id': company.id},
    )


@router.post(
    '/',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary=Summary.TABIT_MANAGEMENT_DEPARTMENT_CREATE,
    description=Description.TABIT_MANAGEMENT_DEPARTMENT_CREATE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def create_department_by_company_slug(
    company_slug: str,
    department: CompanyDepartmentCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Department:
    """
    Описывает работу конечной точки создания отдела для компании администраторами сервиса.

    Аргументы декоратора:
        path (str): URL-путь конечной точки.
        response_model (Type[BaseModel]): Модель Pydantic для подготовки ответа.
        status_code (int): HTTP статус код для успешного ответа.
        summary (str): Краткое описание конечной точки.
        description (str): Подробное описание функциональности.
        openapi_extra (dict): дополнительные настройки для открытой документации API.

    Аргументы функции:
        company_slug (str): slug компании, указанный в пути.
        department (Type[BaseModel]): Модель Pydantic для валидации тела запроса.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        dict: Результат выполнения операции в формате JSON.

    Исключения:
        HTTPException: Возникает при ошибках валидации или обработки запроса.

    Доступ:
        Доступен только администраторам сервиса.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await check_name_department_in_company(
        session=session,
        company_id=company.id,
        new_name=department.name,
    )
    return await department_crud.create_for_company(session, department, company.id)


@router.get(
    '/{department_slug}',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary=Summary.TABIT_MANAGEMENT_DEPARTMENT,
    description=Description.TABIT_MANAGEMENT_DEPARTMENT,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def get_department_by_slug(
    company_slug: str,
    department_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> Department:
    """
    Описывает работу конечной точки получения информации о конкретном отделе компании
    администраторами сервиса.

    Аргументы декоратора:
        path (str): URL-путь конечной точки.
        response_model (Type[BaseModel]): Модель Pydantic для подготовки ответа.
        status_code (int): HTTP статус код для успешного ответа.
        summary (str): Краткое описание конечной точки.
        description (str): Подробное описание функциональности.
        openapi_extra (dict): дополнительные настройки для открытой документации API.

    Аргументы функции:
        company_slug (str): slug компании, указанный в пути.
        department_slug (str): slug отдела, указанный в пути.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        dict: Результат выполнения операции в формате JSON.

    Исключения:
        HTTPException: Возникает при ошибках валидации или обработки запроса.

    Доступ:
        Доступен только администраторам сервиса.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    department = await department_crud.get_by_slug(session, department_slug, raise_404=True)
    check_department_in_company(department=department, company=company)
    return department


@router.patch(
    '/{department_slug}',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_MANAGEMENT_DEPARTMENT_UPDATE,
    description=Description.TABIT_MANAGEMENT_DEPARTMENT_UPDATE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def update_department_by_company_slug(
    company_slug: str,
    department_slug: str,
    department_in: CompanyDepartmentUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Department:
    """
    Описывает работу конечной точки изменении информации о конкретном отделе компании
    администраторами сервиса.

    Аргументы декоратора:
        path (str): URL-путь конечной точки.
        response_model (Type[BaseModel]): Модель Pydantic для подготовки ответа.
        status_code (int): HTTP статус код для успешного ответа.
        summary (str): Краткое описание конечной точки.
        description (str): Подробное описание функциональности.
        openapi_extra (dict): дополнительные настройки для открытой документации API.

    Аргументы функции:
        company_slug (str): slug компании, указанный в пути.
        department_slug (str): slug отдела, указанный в пути.
        department_in (Type[BaseModel]): Модель Pydantic для валидации тела запроса.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        dict: Результат выполнения операции в формате JSON.

    Исключения:
        HTTPException: Возникает при ошибках валидации или обработки запроса.

    Доступ:
        Доступен только администраторам сервиса.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    department = await department_crud.get_by_slug(session, department_slug, raise_404=True)
    check_department_in_company(department=department, company=company)
    await check_name_department_in_company(
        session=session,
        company_id=company.id,
        new_name=department_in.name,
        old_name=department.name,
    )
    return await department_crud.update(session, department, department_in)


@router.delete(
    '/{department_slug}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary=Summary.TABIT_MANAGEMENT_DEPARTMENT_DELETE,
    description=Description.TABIT_MANAGEMENT_DEPARTMENT_DELETE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def remove_department_by_company_slug(
    company_slug: str,
    department_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Описывает работу конечной точки удалении информации о конкретном отделе компании
    администраторами сервиса.

    Аргументы декоратора:
        path (str): URL-путь конечной точки.
        status_code (int): HTTP статус код для успешного ответа.
        summary (str): Краткое описание конечной точки.
        description (str): Подробное описание функциональности.
        openapi_extra (dict): дополнительные настройки для открытой документации API.

    Аргументы функции:
        company_slug (str): slug компании, указанный в пути.
        department_slug (str): slug отдела, указанный в пути.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        None: Без контента.

    Исключения:
        HTTPException: Возникает при ошибках валидации или обработки запроса.

    Доступ:
        Доступен только администраторам сервиса.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    department = await department_crud.get_by_slug(session, department_slug, raise_404=True)
    check_department_in_company(department=department, company=company)
    await check_empty_department(session, department)
    await department_crud.remove(session, department)
