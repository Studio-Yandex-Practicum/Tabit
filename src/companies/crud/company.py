from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.companies.models import Company
from src.crud import CRUDBase


# TODO Этот метод был создан, чтобы исключить изменения в базовом crud, в методе get_by_slug
# Было принято решение покf не менять метод get_by_slug, а создать этот метод
# В методе get_by_slug допущена ошибка в условии проверке. Там проверяют not result
# хотя на самом деле нам нужно проверять, был ли найден объект в базе данных.
# result — это объект, полученный от запроса к базе данных, и даже если он пустой,
# у него все равно будет значение (например, объект запроса), поэтому not result
# не обязательно будет истинным, когда данные не найдены.
# Вместо этого нам нужно проверять obj_model, который содержит реальный результат запроса.
class CRUDCompany(CRUDBase):
    """CRUD операции для модели компании."""

    async def get_by_company_slug(self, session: AsyncSession, company_slug: str):
        """Получает компанию по slug.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            obj_slug: Строка, представляющая slug компании.
        Возвращаемое значение:
            Найденный объект компании или None.
        """
        company = await session.execute(select(Company).where(Company.slug == company_slug))
        return company.scalar_one_or_none()


company_crud = CRUDCompany(Company)
