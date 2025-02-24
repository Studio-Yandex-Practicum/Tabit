from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.companies.models.models import Company
from src.problems.constants import ERROR_COMPANY_NOT_FOUND


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

    company = await session.execute(select(Company).where(Company.slug == company_slug))
    company = company.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=ERROR_COMPANY_NOT_FOUND)
