"""
Эндпоинты управления компаниями (Tabit Management - Companies).
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_admin_tabit
from src.core.database.db_depends import get_async_session
from src.crud.crud_company import company_crud
from src.features_v1.constants import OPENAPI_EXTRA_ADMIN_AUTH, Description, Summary
from src.features_v1.validators import (
    validate_company_slug,
    validate_license_exists,
    validator_check_object_exists,
)
from src.schemas import (
    CompanyCreateSchema,
    CompanyResponseSchema,
    CompanyTypeFilterSchema,
    CompanyUpdateSchema,
)
from src.utils.company_slug_generator import generate_company_slug

router = APIRouter()


@router.get(
    '/',
    response_model=list[CompanyResponseSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary=Summary.TABIT_MANAGEMENT_COMPANY_LIST,
    description=Description.TABIT_MANAGEMENT_COMPANY_LIST,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def get_companies(
    session: AsyncSession = Depends(get_async_session),
    filters: CompanyTypeFilterSchema = Depends(),
) -> list[CompanyResponseSchema]:
    """
    Возвращает список всех компаний. Доступно только администраторам сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        session: асинхронная сессия через зависимость.
    """
    return await company_crud.get_multi(
        session,
        filters=filters.model_dump(exclude_unset=True),
        order_by=[filters.ordering] if filters.ordering else None,
    )


@router.post(
    '/',
    response_model=CompanyResponseSchema,
    dependencies=[Depends(current_admin_tabit)],
    status_code=HTTPStatus.CREATED,
    summary=Summary.TABIT_MANAGEMENT_COMPANY_CREATE,
    description=Description.TABIT_MANAGEMENT_COMPANY_CREATE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def create_company(
    company: CompanyCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyResponseSchema:
    """
    Создает новую компанию. Доступно только администраторам сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        status_code: в случае удачного завершения операции вернет данный статус ответа.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        company: схема для создания компании.
        session: асинхронная сессия через зависимость.
    """
    if company.license_id:
        await validate_license_exists(session, company.license_id)
    # TODO: slug не передается в теле запроса, он делается автоматически.
    # Убрать весь лишний функционал.
    # TODO: генерацию slug убрать в CRUD - это его работа, а не эндпоинта.
    if company.slug:
        await validate_company_slug(session, company.slug)
    else:
        company.slug = await generate_company_slug(session, company.name)

    return await company_crud.create(session, company)


@router.patch(
    '/{company_slug}',
    response_model=CompanyResponseSchema,
    dependencies=[Depends(current_admin_tabit)],
    summary=Summary.TABIT_MANAGEMENT_COMPANY_UPDATE,
    description=Description.TABIT_MANAGEMENT_COMPANY_UPDATE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def update_company(
    company_slug: str,
    object_in: CompanyUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyResponseSchema:
    """
    Обновляет данные компании по её `slug`. Доступно только администраторам сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        company_slug: уникальный идентификатор компании `slug`, указанный в path.
        object_in: данные переданные в запросе, предварительно подготовленные согласно схеме.
        session: асинхронная сессия через зависимость.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)

    if object_in.license_id:
        await validate_license_exists(session, object_in.license_id)
        end_license_time = await company_crud.save_end_license_time(
            session, object_in.start_license_time, object_in.license_id
        )
        object_in = object_in.model_copy(update={'end_license_time': end_license_time})

    return await company_crud.update(session, company, object_in)


@router.delete(
    '/{company_slug}',
    dependencies=[Depends(current_admin_tabit)],
    status_code=HTTPStatus.NO_CONTENT,
    summary=Summary.TABIT_MANAGEMENT_COMPANY_DELETE,
    description=Description.TABIT_MANAGEMENT_COMPANY_DELETE,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def delete_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удаляет компанию по её `slug`. Доступно только администраторам сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        dependencies: список зависимостей (с использованием `Depends()`).
        status_code: в случае удачного завершения операции вернет данный статус ответа.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_id: уникальный идентификатор компании `slug`, указанный в path.
        session: асинхронная сессия через зависимость.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    await company_crud.remove(session, company)
