from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDLicenseType(CRUDBase):
    """CRUD операций для моделей лицензий компаний."""

    async def is_license_name_exists(self, session: AsyncSession, name: str) -> None:
        """
        Проверяет, существует ли лицензия с данным именем.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            name (str): Название лицензии, которую нужно проверить.

        Raises:
            HTTPException: Если лицензия с таким именем уже существует,
                           возвращает ошибку 400 (BAD REQUEST).
        """
        result = await session.execute(select(LicenseType).where(LicenseType.name == name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Лицензия с именем '{name}' уже существует.",
            )

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
