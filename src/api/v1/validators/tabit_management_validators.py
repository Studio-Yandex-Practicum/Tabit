from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.tabit_management.constants import ERROR_INVALID_TELEGRAM_USERNAME
from src.tabit_management.crud import admin_user_crud


async def check_telegram_username_for_duplicates(username: str, session: AsyncSession) -> None:
    """
    Функция проверяет, что в БД не существует пользователя с переданным telegram_username.
    В случае, если польщователь существует, то выбрасывается ошибка HTTP 400.
    Параметры:
        username: telegram_username, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if username:
        if await admin_user_crud.get_by_telegram_username(username, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_TELEGRAM_USERNAME
            )
