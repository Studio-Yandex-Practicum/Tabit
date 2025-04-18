from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import license_type_crud


async def validate_license_exists(session: AsyncSession, license_id: int) -> None:
    """
    Проверяет, существует ли лицензия с переданным license_id в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        license_id (int): Идентификатор лицензии.

    Raises:
        HTTPException: Если лицензия с данным license_id не найдена.
    """
    license_exists = await license_type_crud.get(session, license_id)
    if not license_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Лицензия с id {license_id} не найдена.',
        )


async def validate_license_name(session: AsyncSession, license_name: str):
    """
    Проверяет, существует ли лицензия с данным именем.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        license_name (str): Название лицензии, которую нужно проверить.

    Raises:
        HTTPException: Если лицензия с таким именем уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if await license_type_crud.is_license_name_exists(session, license_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Лицензия с именем '{license_name}' уже существует.",
        )
