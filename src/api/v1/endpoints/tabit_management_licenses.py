from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators.tabit_management_licenses_validators import validate_license_name
from src.database.db_depends import get_async_session
from src.tabit_management.constants import (
    SUMMARY_CREATE_LICENSE,
    SUMMARY_DELETE_LICENSE,
    SUMMARY_GET_LICENSE,
    SUMMARY_GET_LICENSES,
    SUMMARY_UPDATE_LICENSE,
)
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
    summary=SUMMARY_GET_LICENSES,
)
async def get_licenses(
    session: AsyncSession = Depends(get_async_session),
    filters: LicenseTypeFilterSchema = Depends(),
) -> LicenseTypeListResponseSchema:
    """
    Получает список лицензий с возможностью фильтрации, сортировки и пагинации.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        filters (LicenseTypeFilterSchema): Фильтры для выборки лицензий.

    Returns:
        LicenseTypeListResponseSchema: Объект со списком лицензий,
        общим числом записей, текущей страницей и размером страницы.
    """
    licenses = await license_type_crud.get_multi(
        session=session,
        skip=filters.page_size * (filters.page - 1),
        limit=filters.page_size,
        filters=filters.model_dump(exclude_unset=True),
        order_by=[filters.ordering] if filters.ordering else None,
    )
    total_count = await license_type_crud.get_total_count(session)

    return LicenseTypeListResponseSchema(
        items=licenses,
        total=total_count,
        page=filters.page,
        page_size=filters.page_size,
    )


@router.post(
    '/',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary=SUMMARY_CREATE_LICENSE,
)
async def create_license(
    license: LicenseTypeCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LicenseTypeResponseSchema:
    """
    Создаёт новую лицензию в системе.

    Args:
        license (LicenseTypeCreateSchema): Данные для создания новой лицензии.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        LicenseTypeResponseSchema: Созданная лицензия.

    Raises:
        HTTPException: Если лицензия с таким именем уже существует.
    """
    await validate_license_name(session, license.name)
    return await license_type_crud.create(session=session, obj_in=license)


@router.get(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary=SUMMARY_GET_LICENSE,
)
async def get_license(
    license_id: int, session: AsyncSession = Depends(get_async_session)
) -> LicenseTypeResponseSchema:
    """
    Получает данные лицензии по её идентификатору.

    Args:
        license_id (int): Уникальный идентификатор лицензии.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        LicenseTypeResponseSchema: Объект лицензии.

    Raises:
        HTTPException: Если лицензия не найдена.
    """
    return await license_type_crud.get_or_404(session=session, obj_id=license_id)


@router.patch(
    '/{license_id}',
    response_model=LicenseTypeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary=SUMMARY_UPDATE_LICENSE,
)
async def update_license(
    license_id: int,
    license: LicenseTypeUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> LicenseTypeResponseSchema:
    """
    Обновляет данные лицензии по её идентификатору.

    Args:
        license_id (int): Уникальный идентификатор лицензии.
        license (LicenseTypeUpdateSchema): Данные для обновления лицензии.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        LicenseTypeResponseSchema: Обновлённая лицензия.

    Raises:
        HTTPException: Если лицензия не найдена или лицензия с таким именем уже существует.
    """
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)

    if license.name and license.name != db_license.name:
        await validate_license_name(session, license.name)

    return await license_type_crud.update(session=session, db_obj=db_license, obj_in=license)


@router.delete(
    '/{license_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary=SUMMARY_DELETE_LICENSE,
)
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удаляет лицензию по её идентификатору.

    Args:
        license_id (int): Уникальный идентификатор лицензии.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        Пустой ответ с кодом 204 No Content.

    Raises:
        HTTPException: Если лицензия не найдена.
    """
    db_license = await license_type_crud.get_or_404(session=session, obj_id=license_id)
    await license_type_crud.remove(session=session, db_object=db_license)
