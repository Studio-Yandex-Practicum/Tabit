from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import TextError
from src.users.crud.user import user_crud


async def validate_field_members(
    session: AsyncSession,
    uuid_members: list[UUID] | None,
    company_id: int | None = None,
) -> None:
    """
    Проверит переданный список uuid пользователей на корректность uuid
    и принадлежность пользователей к переданной компании.

    Параметры
        session: Асинхронная сессия SQLAlchemy;
        uuid_members: список uuid пользователей;
        company_id: число - id компании из которой пользователи.
    """
    if not uuid_members:
        return
    for uuid in uuid_members:
        user = await user_crud.get(session, uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.UUID_INVALID.format(uuid),
            )
        if company_id is not None and company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.USER_NOT_FROM_COMPANY.format(uuid),
            )
