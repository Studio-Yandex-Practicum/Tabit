from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.tabit_management.schemas import (
    LicenseTypeCreateSchema,
    LicenseTypeResponseSchema,
    LicenseTypeUpdateSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[LicenseTypeResponseSchema],
    summary='Получить список всех лицензий',
)
async def get_licenses(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех лицензий.
    """
    # TODO: Реализовать получение данных из базы
    return [
        {
            'id': 1,
            'name': 'Внимание! Это заглушка!',
            'license_tern': 'P1D',
            'max_admins_count': 1,
            'max_employees_count': 1,
        }
    ]


@router.post('/', response_model=LicenseTypeResponseSchema, summary='Создать новую лицензию')
async def create_license(
    license: LicenseTypeCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создание новой лицензии.
    """
    # TODO: Реализовать создание лицензии
    return {
        'id': 1,
        'name': f'{license.name} - Внимание! Это заглушка!',
        'license_tern': license.license_tern,
        'max_admins_count': license.max_admins_count,
        'max_employees_count': license.max_employees_count,
    }


@router.get(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    summary='Получить данные лицензии',
)
async def get_license(license_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получение данных лицензии по идентификатору.
    """
    # TODO: Реализовать получение лицензии по идентификатору
    return {
        'id': license_id,
        'name': 'Внимание! Это заглушка!',
        'license_tern': 'P1D',
        'max_admins_count': 1,
        'max_employees_count': 1,
    }


@router.patch(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    summary='Обновить данные лицензии',
)
async def update_license(
    license_id: int,
    license: LicenseTypeUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновление данных лицензии по идентификатору.
    """
    # TODO: Реализовать обновление лицензии
    return {
        'id': license_id,
        'name': f'{license.name} - Внимание! Это заглушка!',
        'license_tern': license.license_tern,
        'max_admins_count': license.max_admins_count,
        'max_employees_count': license.max_employees_count,
    }


@router.delete(
    '/{license_slug}', response_model=LicenseTypeResponseSchema, summary='Удалить лицензию'
)
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаление лицензии по идентификатору.
    """
    # TODO: Реализовать удаление лицензии
    return {
        'id': license_id,
        'name': 'Внимание! Это заглушка!',
        'license_tern': 'P1D',
        'max_admins_count': 1,
        'max_employees_count': 1,
    }
