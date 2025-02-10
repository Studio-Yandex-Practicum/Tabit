from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.tabit_management.crud import license_type_crud
from src.tabit_management.schemas import (
    LicenseTypeCreateSchema,
    LicenseTypeResponseSchema,
    LicenseTypeUpdateSchema,
)
from src.tabit_management.schemas.license_type import (
    LicenseTypeFilterSchema,
    LicenseTypeListResponseSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=LicenseTypeListResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Получить список всех лицензий с фильтрацией и сортировкой',
)
async def get_licenses(
    session: AsyncSession = Depends(get_async_session),
    filters: LicenseTypeFilterSchema = Depends(),
):
    """
    Возвращает список всех лицензий.
    """
    return await license_type_crud.get_filtered(session, filters)


@router.post(
    '/',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новую лицензию',
)
async def create_license(
    license: LicenseTypeCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создание новой лицензии.
    """
    if await license_type_crud.is_license_name_exists(session, license.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Лицензия с именем '{license.name}' уже существует.",
        )
    return await license_type_crud.create(session=session, obj_in=license)


@router.get(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Получить данные лицензии',
)
async def get_license(license_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получение данных лицензии по идентификатору.
    """
    return await license_type_crud.get_or_404(session=session, obj_id=license_id)


@router.patch(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_200_OK,
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
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)

    if license.name and license.name != db_license.name:
        if await license_type_crud.is_license_name_exists(session, license.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Лицензия с именем '{license.name}' уже существует.",
            )

    return await license_type_crud.update(session=session, db_obj=db_license, obj_in=license)


@router.delete(
    '/{license_id}', response_model=LicenseTypeResponseSchema, summary='Удалить лицензию'
)
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаление лицензии по идентификатору.
    """
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)
    await license_type_crud.remove(session=session, db_object=db_license)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
