import random

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud import company_crud
from src.tabit_management.crud import license_type_crud


async def validate_company_slug(session: AsyncSession, slug: str) -> None:
    """
    Проверяет, существует ли компания с таким slug в базе.

    :param session: Асинхронная сессия SQLAlchemy
    :param slug: Проверяемый slug
    :raises HTTPException: Если slug уже существует в БД
    """
    if await company_crud.is_company_slug_exists(session, slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Компания с таким slug '{slug}' уже существует.",
        )


async def generate_slug(session: AsyncSession, name: str) -> str:
    """
    Генерирует уникальный slug из имени компании. Если сгенерированный slug уже существует в БД,
    добавляет случайное число в конец и повторяет проверку.

    :param session: Асинхронная сессия SQLAlchemy
    :param name: Название компании, из которого создается slug
    :return: Уникальный slug
    """
    new_slug = slugify(name)
    while await company_crud.is_company_slug_exists(session, new_slug):
        new_slug = f'{slugify(name)}-{random.randint(1000, 9999)}'

    return new_slug


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
