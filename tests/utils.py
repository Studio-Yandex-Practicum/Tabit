from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def is_valid_uuid(value: Any) -> bool:
    """Вернет True если переданное значение является UUID, иначе вернет False."""
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False


async def update_object(session: AsyncSession, db_obj) -> dict:
    """
    Обновляет атрибуты передаваемого объекта модели в рамках одной сессии и возвращает
    его словарное предстваление.
    """
    session.expire(db_obj)
    await session.refresh(db_obj)
    return jsonable_encoder(db_obj)


async def get_count(session: AsyncSession, model) -> int:
    """Возвращает текущее количество объектов в БД для переданной модели."""
    count = await session.execute(select(model))
    return len(count.all())
