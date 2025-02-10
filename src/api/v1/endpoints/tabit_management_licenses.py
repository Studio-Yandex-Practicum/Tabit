from fastapi import APIRouter, Depends, Response, status
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
) -> LicenseTypeListResponseSchema:
    """
    Возвращает список всех лицензий.
    """
    # licenses = await license_type_crud.get_multi(
    #     session=session,
    #     skip=filters.page_size * (filters.page - 1),
    #     limit=filters.page_size,
    #     filters=filters.dict(exclude_unset=True),
    #     order_by=[filters.ordering] if filters.ordering else None,
    # )
    # return LicenseTypeListResponseSchema(
    #     items=licenses,
    #     total=len(licenses),
    #     page=filters.page,
    #     page_size=filters.page_size,
    # )
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
) -> LicenseTypeResponseSchema:
    """
    Создание новой лицензии.
    """
    await license_type_crud.is_license_name_exists(session, license.name)
    return await license_type_crud.create(session=session, obj_in=license)


@router.get(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Получить данные лицензии',
)
async def get_license(
    license_id: int, session: AsyncSession = Depends(get_async_session)
) -> LicenseTypeResponseSchema:
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
) -> LicenseTypeResponseSchema:
    """
    Обновление данных лицензии по идентификатору.
    """
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)

    if license.name and license.name != db_license.name:
        await license_type_crud.is_license_name_exists(session, license.name)

    return await license_type_crud.update(session=session, db_obj=db_license, obj_in=license)


@router.delete('/{license_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Удалить лицензию')
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Удаление лицензии по идентификатору.
    """
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)
    await license_type_crud.remove(session=session, db_object=db_license)
