import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDLicenseType(CRUDBase):
    """CRUD операций для моделей лицензий компаний."""

    async def is_license_name_exists(self, session: AsyncSession, name: str) -> bool:
        """Проверяет, существует ли лицензия с данным именем."""
        result = await session.execute(sa.select(LicenseType).where(LicenseType.name == name))
        return result.scalars().first() is not None


license_type_crud = CRUDLicenseType(LicenseType)
