from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDLicenseType(CRUDBase):
    """CRUD операций для моделей лицензий компаний."""

    async def is_license_name_exists(self, session: AsyncSession, name: str) -> None:
        """
        Проверяет существование лицензии с указанным именем в базе данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для выполнения запроса.
            name (str): Название лицензии, которое требуется проверить.

        Returns:
            bool: `True`, если лицензия с таким именем существует, иначе `False`.
        """
        result = await session.execute(select(LicenseType).where(LicenseType.name == name))
        return result.scalar_one_or_none() is not None

    async def get_total_count(self, session: AsyncSession) -> int:
        """
        Возвращает общее количество записей в таблице LicenseType.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            int: Общее количество записей в таблице LicenseType.
        """
        result = await session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()


license_type_crud = CRUDLicenseType(LicenseType)
