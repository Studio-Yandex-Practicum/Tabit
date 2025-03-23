from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.crud.user import user_crud


async def validate_field_members(
    session: AsyncSession,
    uuid_members: list[UUID] | None,
    company_id: int | None = None
) -> None:
    """
    Проверяет, существует ли компания с таким slug в базе.

    :param session: Асинхронная сессия SQLAlchemy
    :param slug: Проверяемый slug
    :raises HTTPException: Если slug уже существует в БД
    """
    if not uuid_members:
        return
    for uuid in uuid_members:
        user = await user_crud.get(session, uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'UUID в поле members не корректен или пользователя с таким UUID нет: {uuid}',
                )
            )
        if company_id is not None and company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'UUID в поле members принадлежит пользователю от другой компании: {uuid}',
                )
            )
