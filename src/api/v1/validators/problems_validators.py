from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud.company import company_crud
from src.problems.constants import ERROR_COMPANY_NOT_FOUND


# TODO Вместо get_by_company_slug можно использовать метод базового crud
# get_by_slug если исправть как описано в src/companies/crud/company
async def check_company_exists(company_slug: str, session: AsyncSession):
    """Проверяет существование компании по slug.

    Назначение:
        Валидирует, что компания существует в базе данных по заданному slug.
    Параметры:
        company_slug: Строка, представляющая slug компании для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная компания, если она существует.
    Исключения:
        HTTPException: Если компания не найдена.
    """

    if not await company_crud.get_by_company_slug(session, company_slug):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_COMPANY_NOT_FOUND)
