from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AssociationUserComment


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


async def get_association_objects_iterator(
    session: AsyncSession, model, left_id, right_id
) -> ChunkedIteratorResult:
    """
    Возвращает ChunkedIteratorResult c объектами ассоциативной модели по заданным left_id/right_id.
    Возвращается в таком формате, если к итератору нужно будет применять разные методы в зависимоти
    от задачи.
    """
    return await session.execute(
        select(model).where(and_(model.left_id == left_id, model.right_id == right_id))
    )


async def like_a_comment(async_session, employee, comment):
    """Фикстура для лайка комментария comment."""

    like_obj = AssociationUserComment(left_id=employee.id, right_id=comment.id)
    async_session.add(like_obj)
    comment.rating += 1
    async_session.add(comment)
    await async_session.commit()
    await async_session.refresh(comment)
