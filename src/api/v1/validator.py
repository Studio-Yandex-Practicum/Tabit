"""
Валидаторы для эндпоинтов.
"""

from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (
    TEXT_ERROR_IS_SUPERUSER,
    TEXT_ERROR_NOT_FOUND,
)
from src.crud import CRUDBase


async def validator_check_object_exists(
    session: AsyncSession,
    model_crud: CRUDBase,
    object_id: int | UUID | None = None,
    object_slug: str | None = None,
    message: str = TEXT_ERROR_NOT_FOUND,
):
    """Проверит наличие и вернет объект из таблицы по id или slug."""
    object_model = (
        await model_crud.get_or_404(session, object_id)
        if object_id
        else (await model_crud.get_by_slug(session, object_slug, raise_404=True))
    )
    if object_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=message,
        )
    return object_model


def validator_check_is_superuser(
    user_model_object,
    message: str = TEXT_ERROR_IS_SUPERUSER,
) -> None:
    if user_model_object.is_superuser:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=message,
        )
