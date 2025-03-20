from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.constants import (
    COMPANY_NOT_FOUND,
    DEPARTMENT_NOT_FOUND,
    WRONG_COMPANY_DEPARTMENT,
)
from src.companies.crud import company_crud, company_departments_crud
from src.tabit_management.constants import ERROR_INVALID_TELEGRAM_USERNAME
from src.tabit_management.crud import admin_user_crud


async def check_telegram_username_for_duplicates(username: str, session: AsyncSession) -> None:
    """
    Функция проверяет, что в БД не существует пользователя с переданным telegram_username.
    В случае, если пользователь существует, то выбрасывается ошибка HTTP 400.
    Параметры:
        username: telegram_username, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if username:
        if await admin_user_crud.get_by_telegram_username(username, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_TELEGRAM_USERNAME
            )


async def check_company_and_department(
    company_id: int, department_id: int, session: AsyncSession
) -> None:
    """
    Функция проверяет существование объектов Company и Department с указанными id.
    Если объекты существуют, то далее проверяется наличие связи между ними.
    Параметры:
        company_id: id компании, переданный в запросе к API;
        department_id: id отдела, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if company_id:
        if not await company_crud.get(session, company_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=COMPANY_NOT_FOUND
            )
    if department_id:
        department = await company_departments_crud.get(session, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=DEPARTMENT_NOT_FOUND
            )
    else:
        return
    if department and department.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=WRONG_COMPANY_DEPARTMENT
        )
