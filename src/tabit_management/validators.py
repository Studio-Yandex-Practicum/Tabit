from http import HTTPStatus

from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.tabit_management.constants import ERROR_UPDATE_METHOD
from src.tabit_management.crud.admin_user import admin_user_crud


async def check_admin_email_and_number(new_email: str, new_number: str, session: AsyncSession):
    """
    Проверяет наличие совпадений новых значений email и phone_number в таблице TabitAdminUser.

    Если совпадения найдены, то возвращает ошибку.
    """
    if await admin_user_crud.get_by_email_or_number(new_email, new_number, session):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_UPDATE_METHOD)
